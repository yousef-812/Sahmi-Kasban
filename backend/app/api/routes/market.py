import asyncio
from contextlib import suppress
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sahmi_kasban.ai import SahmiAIService

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.security import InvalidAccessTokenError, decode_access_token
from app.db.session import SessionLocal
from app.market_data.broadcaster import get_analysis_broadcaster, get_quote_broadcaster
from app.market_data.catalog import market_instrument_exists, search_market_instruments
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.fundamental import compare_stocks_investment, get_stock_investment_metric
from app.market_data.global_market import get_global_market
from app.market_data.indices import fetch_index_quote, fetch_market_indices, index_exists
from app.market_data.order_flow import (
    detect_whales,
    get_market_depth,
    get_order_book,
    get_recent_trades,
)
from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import fetch_market_quotes, fetch_single_quote
from app.market_data.top_of_book import get_top_of_book
from app.market_data.types import (
    MarketDataProvider,
    MarketDataUnavailableError,
    UnknownTickerError,
)
from app.models import User
from app.schemas.global_market import GlobalMarketResponse
from app.schemas.market import (
    MarketBreadthResponse,
    MarketIndicesResponse,
    MarketInstrumentListResponse,
    MarketInstrumentResponse,
    MarketQuoteResponse,
    MarketQuotesResponse,
    SessionReplayResponse,
    StockAnalysisRequest,
    StockAnalysisResponse,
    StockComparisonFailureResponse,
    StockComparisonItemResponse,
    StockComparisonRequest,
    StockComparisonResponse,
    StockFlowResponse,
    StockInvestmentAnalysisResponse,
    StockInvestmentComparisonRequest,
    StockInvestmentComparisonResponse,
    StockSignatureResponse,
    StockVolumeProfileResponse,
)
from app.schemas.market_status import MarketStatusResponse
from app.schemas.order_flow import (
    MarketDepthResponse,
    OrderBookResponse,
    RecentTradesResponse,
    TopOfBookResponse,
    WhaleDetectionResponse,
)
from app.schemas.sentiment import SymbolSentimentResponse
from app.services.market_breadth import compute_market_breadth
from app.services.market_status import market_status
from app.services.sentiment import compute_symbol_sentiment
from app.services.stock_analysis import (
    StockAnalysisExecution,
    StockAnalysisExecutionError,
    execute_index_analysis,
    execute_stock_analysis,
    get_stock_ai_service,
    latest_owned_stock_analysis,
)
from app.services.stock_comparisons import (
    ComparisonConflictError,
    ComparisonInsufficientResultsError,
    ComparisonPlanLimitError,
    StockComparisonExecution,
    execute_stock_comparison,
)
from app.services.stock_flow import compute_stock_flow
from app.services.volume_profile import compute_volume_profile
from app.services.wallet import InsufficientBalanceError, points_to_coins

router = APIRouter(tags=["market"])
MarketProvider = Annotated[MarketDataProvider, Depends(get_market_data_provider)]
StockAIService = Annotated[SahmiAIService, Depends(get_stock_ai_service)]


def _analysis_response(execution: StockAnalysisExecution) -> StockAnalysisResponse:
    analysis = execution.analysis
    payload = analysis.payload if isinstance(analysis.payload, dict) else {}
    analysis_data = payload.get("analysis", {}) if isinstance(payload.get("analysis"), dict) else {}
    engines = analysis_data.get("engines", {}) if isinstance(analysis_data.get("engines"), dict) else {}

    sector_eng = (
        engines.get("sector_momentum", {}).get("details", {})
        if isinstance(engines.get("sector_momentum"), dict)
        else {}
    )
    risk_eng = engines.get("risk", {}).get("details", {}) if isinstance(engines.get("risk"), dict) else {}
    tech_eng = (
        engines.get("technical", {}).get("details", {}) if isinstance(engines.get("technical"), dict) else {}
    )

    sector_momentum_pct = sector_eng.get("sector_momentum_5d_pct") if isinstance(sector_eng, dict) else None
    sector_name = sector_eng.get("sector_name") if isinstance(sector_eng, dict) else None
    adaptive_atr_multiple = risk_eng.get("adaptive_atr_multiple") if isinstance(risk_eng, dict) else None
    market_regime_context = risk_eng.get("market_regime_context") if isinstance(risk_eng, dict) else None
    vwap_20 = tech_eng.get("vwap_20") if isinstance(tech_eng, dict) else None

    def _as_f(val: object) -> float | None:
        return float(val) if isinstance(val, (int, float)) else None

    sector_quality = payload.get("sector_quality")
    if not isinstance(sector_quality, dict):
        from app.services.sector_quality import compute_sector_quality

        score = float(analysis_data.get("final_score", 0)) if isinstance(analysis_data, dict) else 0.0
        ret_20d = tech_eng.get("return_20d_pct") if isinstance(tech_eng, dict) else None
        sector_quality = compute_sector_quality(
            analysis.ticker,
            score=score,
            return_20d=_as_f(ret_20d),
            sector_momentum_pct=_as_f(sector_momentum_pct),
            raw_sector=str(sector_name) if sector_name is not None else None,
        )

    return StockAnalysisResponse(
        analysis_id=analysis.id,
        ticker=analysis.ticker,
        cached=execution.cached,
        market_snapshot_cached=execution.market_snapshot_cached,
        charged_points=execution.charged_points,
        charged_coins=points_to_coins(execution.charged_points),
        balance_points=execution.balance_points,
        balance_coins=points_to_coins(execution.balance_points),
        data_as_of=analysis.data_as_of,
        payload=analysis.payload,
        sector_momentum_pct=_as_f(sector_momentum_pct),
        sector_name=str(sector_name) if sector_name is not None else None,
        adaptive_atr_multiple=_as_f(adaptive_atr_multiple),
        market_regime_context=str(market_regime_context) if market_regime_context is not None else None,
        vwap_20=_as_f(vwap_20),
        sector_quality=sector_quality,
    )


def _comparison_response(execution: StockComparisonExecution) -> StockComparisonResponse:
    comparison = execution.comparison
    payload = comparison.payload
    raw_items = payload.get("items", [])
    raw_failed_items = payload.get("failed_items", [])
    return StockComparisonResponse(
        comparison_id=comparison.id,
        request_key=comparison.request_key,
        tickers=comparison.tickers,
        best_ticker=str(payload.get("best_ticker", "")),
        summary=str(payload.get("summary", "")),
        items=[StockComparisonItemResponse(**item) for item in raw_items],
        failed_items=[StockComparisonFailureResponse(**item) for item in raw_failed_items],
        included_allowance=comparison.included_allowance,
        comparison_charged_points=comparison.charged_points,
        comparison_charged_coins=points_to_coins(comparison.charged_points),
        analysis_charged_points=comparison.analysis_charged_points,
        analysis_charged_coins=points_to_coins(comparison.analysis_charged_points),
        allowance_used=execution.allowance_used,
        allowance_remaining=execution.allowance_remaining,
        idempotent=execution.idempotent,
        balance_points=execution.balance_points,
        balance_coins=points_to_coins(execution.balance_points),
        disclaimer=str(payload.get("disclaimer", "")),
    )


@router.get("/market/instruments", response_model=MarketInstrumentListResponse)
async def get_market_instruments(
    db: DatabaseSession,
    query: str = Query(default="", max_length=64),
    limit: int = Query(default=30, ge=1, le=500),
) -> MarketInstrumentListResponse:
    source, total, instruments = await search_market_instruments(
        db,
        query=query,
        limit=limit,
    )
    return MarketInstrumentListResponse(
        source=source,
        total_registry_size=total,
        items=[MarketInstrumentResponse(**instrument.to_dict()) for instrument in instruments],
    )


@router.get("/market/status", response_model=MarketStatusResponse)
async def get_market_status() -> MarketStatusResponse:
    return MarketStatusResponse(**market_status())


@router.get("/market/global", response_model=GlobalMarketResponse)
async def get_global_market_snapshot(
    db: DatabaseSession,
    force_refresh: bool = Query(default=False),
) -> GlobalMarketResponse:
    """لقطة السوق العالمي/الماكرو (مؤشرات عالمية + فوركس + معادن/طاقة).

    عامة بلا مصادقة — بنفس قاعدة ``/market/status`` و``/market/instruments``:
    قراءة فقط للسياق العام، لا بيانات مستخدم ولا استهلاك رصيد.
    """
    return GlobalMarketResponse(**await get_global_market(db, force_refresh=force_refresh))


@router.get("/market/breadth", response_model=MarketBreadthResponse)
async def get_market_breadth(
    db: DatabaseSession,
) -> MarketBreadthResponse:
    """اتساع السوق — صاعد/هابط/ثابت + أداء قطاعي (عامة، بلا مصادقة)."""
    return MarketBreadthResponse(**await compute_market_breadth(db))


def _quote_response(quote) -> MarketQuoteResponse:
    return MarketQuoteResponse(**quote.to_dict())


@router.get("/market/quotes", response_model=MarketQuotesResponse)
async def get_market_quotes(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketQuotesResponse:
    snapshot = await fetch_market_quotes(db)
    return MarketQuotesResponse(
        source=snapshot.source,
        generated_at=snapshot.generated_at,
        market_open=snapshot.market_open,
        next_session_open=snapshot.next_session_open,
        items=[_quote_response(item) for item in snapshot.items],
    )


@router.get("/market/indices", response_model=MarketIndicesResponse)
async def get_market_indices(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketIndicesResponse:
    from datetime import UTC, datetime

    quotes = await fetch_market_indices()
    snapshot = await fetch_market_quotes(db)
    return MarketIndicesResponse(
        generated_at=datetime.now(UTC),
        market_open=snapshot.market_open,
        items=[_quote_response(item) for item in quotes],
    )


@router.get("/market/indices/{ticker}/quote", response_model=MarketQuoteResponse)
async def get_market_index_quote(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MarketQuoteResponse:
    normalized = ticker.strip().upper()
    if not index_exists(normalized):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المؤشر غير مدعوم.",
        )
    quote = await fetch_index_quote(normalized)
    if quote is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="بيانات المؤشر غير متاحة مؤقتًا. أعد المحاولة بعد قليل.",
        )
    return _quote_response(quote)


@router.get(
    "/market/indices/{ticker}/analysis/latest",
    response_model=StockAnalysisResponse,
)
async def get_latest_owned_index_analysis(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> StockAnalysisResponse:
    normalized = ticker.strip().upper()
    if not index_exists(normalized):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المؤشر غير مدعوم.",
        )
    execution = latest_owned_stock_analysis(
        db,
        user=current_user,
        ticker=normalized,
    )
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لا يوجد تحليل محفوظ لهذا المؤشر في حسابك.",
        )
    return _analysis_response(execution)


@router.post(
    "/market/indices/{ticker}/analysis",
    response_model=StockAnalysisResponse,
)
async def analyze_market_index(
    ticker: str,
    request: StockAnalysisRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    provider: MarketProvider,
    ai_service: StockAIService,
) -> StockAnalysisResponse:
    try:
        normalized = ticker.strip().upper()
        if not index_exists(normalized):
            raise UnknownTickerError(f"Unsupported market index: {normalized}")
        execution = await execute_index_analysis(
            db,
            user=current_user,
            index_name=normalized,
            provider=provider,
            ai_service=ai_service,
            language=request.language,
        )
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المؤشر غير مدعوم.",
        ) from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="الرصيد لا يكفي لإجراء هذا التحليل.",
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="بيانات المؤشر غير متاحة مؤقتًا. أعد المحاولة بعد قليل.",
        ) from exc
    except StockAnalysisExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("لم يكتمل التحليل لأن تاريخ المؤشر أو بياناته لا تكفي للمحركات حاليًا."),
        ) from exc

    return _analysis_response(execution)


@router.get("/market/session-replay", response_model=SessionReplayResponse)
async def get_session_replay(
    db: DatabaseSession,
    current_user: CurrentUser,
    provider: MarketProvider,
    ticker: str = Query(min_length=1, max_length=16),
    interval: str = Query(default="5m"),
) -> SessionReplayResponse:
    """Return intraday candles of the last closed session for chart replay.

    The Flutter player steps through these candles from session open to
    session close with adjustable playback speeds (1x..16x).
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from app.schemas.market import SessionReplayCandle

    allowed = {"1m", "5m", "15m", "30m"}
    normalized_interval = interval.strip().lower()
    if normalized_interval not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="الفاصل الزمني غير مدعوم. استخدم 1m أو 5m أو 15m أو 30m.",
        )
    normalized_ticker = normalize_egx_ticker(ticker)
    if not await market_instrument_exists(db, normalized_ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        )
    try:
        series = await provider.get_history(
            normalized_ticker,
            period="5d",
            interval=normalized_interval,
        )
    except (MarketDataUnavailableError, UnknownTickerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="بيانات الجلسة غير متاحة مؤقتًا. أعد المحاولة بعد قليل.",
        ) from exc

    cairo = ZoneInfo("Africa/Cairo")
    by_day: dict[str, list[dict]] = {}
    for raw in series.candles:
        try:
            ts = datetime.fromisoformat(str(raw.get("timestamp")))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=cairo)
            day_key = ts.astimezone(cairo).date().isoformat()
        except (ValueError, TypeError):
            continue
        by_day.setdefault(day_key, []).append(raw)
    if not by_day:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="لا توجد شموع لحظية كافية لإعادة المحاكاة.",
        )
    # Last day with enough candles = last closed session available.
    session_date = sorted(
        (day for day, rows in by_day.items() if len(rows) >= 5),
        reverse=True,
    )
    if not session_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="لا توجد جلسة مكتملة كافية لإعادة المحاكاة.",
        )
    chosen = session_date[0]
    rows = sorted(by_day[chosen], key=lambda c: str(c.get("timestamp")))
    candles = [
        SessionReplayCandle(
            timestamp=datetime.fromisoformat(str(c.get("timestamp"))),
            open=float(c.get("open", 0)),
            high=float(c.get("high", 0)),
            low=float(c.get("low", 0)),
            close=float(c.get("close", 0)),
            volume=float(c.get("volume", 0) or 0),
        )
        for c in rows
    ]
    return SessionReplayResponse(
        ticker=normalized_ticker,
        session_date=chosen,
        interval=normalized_interval,
        candles=candles,
    )


@router.websocket("/market/quotes/stream")
async def stream_market_quotes(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    # Authenticate token if present or query parameter
    if token:
        try:
            payload = decode_access_token(token)
            user_id = UUID(payload["sub"])
            token_version = int(payload["ver"])
            with SessionLocal() as db:
                user = db.get(User, user_id)
                if user is None or user.status != "active" or user.auth_version != token_version:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
        except (InvalidAccessTokenError, ValueError, TypeError, KeyError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    broadcaster = get_quote_broadcaster()
    await broadcaster.connect(websocket)
    try:
        while True:
            # Keep alive and receive any client-side ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        await broadcaster.disconnect(websocket)


@router.websocket("/market/analysis/stream")
async def stream_analysis_events(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    """Real-time analysis events: ``signal.updated`` (public) + ``alert.created`` (per user).

    Authentication mirrors ``/market/quotes/stream``: an optional JWT via the
    ``token`` query parameter. An invalid token rejects the connection
    (1008); without a token the subscriber still receives every
    ``signal.updated`` event but never user-scoped ``alert.created`` events.
    The server emits ``{"type": "ping"}`` heartbeats while idle and answers
    client ``"ping"`` frames with ``"pong"``.
    """
    user_id: UUID | None = None
    if token:
        try:
            payload = decode_access_token(token)
            uid = UUID(payload["sub"])
            token_version = int(payload["ver"])
            with SessionLocal() as db:
                user = db.get(User, uid)
                if user is None or user.status != "active" or user.auth_version != token_version:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
            user_id = uid
        except (InvalidAccessTokenError, ValueError, TypeError, KeyError):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    broadcaster = get_analysis_broadcaster()
    subscriber = await broadcaster.subscribe(user_id=user_id)
    try:
        await websocket.accept()
        await websocket.send_json(
            {
                "type": "connected",
                "authenticated": user_id is not None,
                "heartbeat_seconds": broadcaster.heartbeat_seconds,
            }
        )
        sender = asyncio.create_task(broadcaster.pump(websocket, subscriber))
        try:
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except (WebSocketDisconnect, Exception):
            pass
        finally:
            sender.cancel()
            with suppress(asyncio.CancelledError):
                await sender
    finally:
        await broadcaster.unsubscribe(subscriber)


@router.get("/market/quotes/{ticker}", response_model=MarketQuoteResponse)
async def get_market_quote_for_ticker(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
    force_refresh: bool = Query(default=False),
) -> MarketQuoteResponse:
    normalized_ticker = normalize_egx_ticker(ticker)
    quote = await fetch_single_quote(db, normalized_ticker, force_refresh=force_refresh)
    if quote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        )
    return _quote_response(quote)


@router.post("/market/comparisons", response_model=StockComparisonResponse)
async def compare_stocks(
    request: StockComparisonRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    provider: MarketProvider,
    ai_service: StockAIService,
) -> StockComparisonResponse:
    try:
        normalized: list[str] = []
        for ticker in request.tickers:
            symbol = normalize_egx_ticker(ticker)
            if not await market_instrument_exists(db, symbol):
                raise UnknownTickerError(f"Unsupported EGX ticker: {symbol}")
            normalized.append(symbol)

        execution = await execute_stock_comparison(
            db,
            user=current_user,
            request_key=request.request_key,
            tickers=normalized,
            provider=provider,
            ai_service=ai_service,
            language=request.language,
        )
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        ) from exc
    except ComparisonConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ComparisonPlanLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ComparisonInsufficientResultsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="الرصيد لا يكفي للمقارنة والتحليلات الجديدة المطلوبة.",
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="بيانات السوق غير متاحة مؤقتًا. أعد المحاولة بعد قليل.",
        ) from exc
    except StockAnalysisExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="تعذر إكمال تحليل الأسهم المختارة حاليًا.",
        ) from exc

    return _comparison_response(execution)


@router.get(
    "/stocks/{ticker}/analysis/latest",
    response_model=StockAnalysisResponse,
)
async def get_latest_owned_analysis(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> StockAnalysisResponse:
    normalized_ticker = normalize_egx_ticker(ticker)
    if not await market_instrument_exists(db, normalized_ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        )
    execution = latest_owned_stock_analysis(
        db,
        user=current_user,
        ticker=normalized_ticker,
    )
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لا يوجد تحليل محفوظ لهذا السهم في حسابك.",
        )
    return _analysis_response(execution)


@router.post(
    "/stocks/{ticker}/analysis",
    response_model=StockAnalysisResponse,
)
async def analyze_stock(
    ticker: str,
    request: StockAnalysisRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    provider: MarketProvider,
    ai_service: StockAIService,
) -> StockAnalysisResponse:
    try:
        normalized_ticker = normalize_egx_ticker(ticker)
        if not await market_instrument_exists(db, normalized_ticker):
            raise UnknownTickerError(f"Unsupported EGX ticker: {normalized_ticker}")
        execution = await execute_stock_analysis(
            db,
            user=current_user,
            ticker=normalized_ticker,
            provider=provider,
            ai_service=ai_service,
            language=request.language,
        )
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        ) from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="الرصيد لا يكفي لإجراء هذا التحليل.",
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="بيانات السهم غير متاحة مؤقتًا. أعد المحاولة بعد قليل.",
        ) from exc
    except StockAnalysisExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=("لم يكتمل التحليل لأن تاريخ السهم أو بياناته لا تكفي للمحركات حاليًا."),
        ) from exc

    return _analysis_response(execution)


@router.get("/stocks/{ticker}/investment", response_model=StockInvestmentAnalysisResponse)
async def get_stock_investment_analysis(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> StockInvestmentAnalysisResponse:
    metric = await get_stock_investment_metric(db, ticker)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="بيانات التحليل الاستثماري غير متاحة لهذا السهم حالياً.",
        )
    return StockInvestmentAnalysisResponse(**metric)


@router.get("/stocks/{ticker}/sentiment", response_model=SymbolSentimentResponse)
def get_stock_sentiment(
    ticker: str,
    db: DatabaseSession,
    days: int = Query(default=7, ge=1, le=90),
) -> SymbolSentimentResponse:
    """معنويات أخبار السهم خلال آخر ``days`` يومًا (عامة، بلا مصادقة — مثل /stocks/{ticker}/news)."""
    try:
        normalized_ticker = normalize_egx_ticker(ticker)
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير صالح.",
        ) from exc
    result = compute_symbol_sentiment(db, normalized_ticker, days=days)
    return SymbolSentimentResponse(**result)


@router.get("/stocks/{ticker}/flow", response_model=StockFlowResponse)
async def get_stock_flow(
    ticker: str,
    db: DatabaseSession,
    days: int = Query(default=90, ge=1, le=250),
) -> StockFlowResponse:
    """ضغط الشراء/البيع المقدّر من OHLCV (CLV×الحجم) — عامة، بلا مصادقة، مثل /sentiment."""
    try:
        normalized_ticker = normalize_egx_ticker(ticker)
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير صالح.",
        ) from exc
    return StockFlowResponse(**await compute_stock_flow(db, normalized_ticker, days=days))


@router.get("/stocks/{ticker}/volume-profile", response_model=StockVolumeProfileResponse)
async def get_stock_volume_profile(
    ticker: str,
    db: DatabaseSession,
    days: int = Query(default=250, ge=5, le=250),
) -> StockVolumeProfileResponse:
    """حجم السعر (POC/منطقة القيمة 70%) من OHLCV — عامة، مثل /flow."""
    try:
        normalized_ticker = normalize_egx_ticker(ticker)
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير صالح.",
        ) from exc
    return StockVolumeProfileResponse(**await compute_volume_profile(db, normalized_ticker, days=days))


@router.post("/market/comparisons/investment", response_model=StockInvestmentComparisonResponse)
async def compare_stocks_investment_route(
    request: StockInvestmentComparisonRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> StockInvestmentComparisonResponse:
    res = await compare_stocks_investment(db, request.tickers)
    return StockInvestmentComparisonResponse(
        items=[StockInvestmentAnalysisResponse(**item) for item in res["items"]],
        best_ticker=res["best_ticker"],
        summary=res["summary"],
    )


@router.get("/stocks/{ticker}/signature", response_model=StockSignatureResponse)
def get_stock_algorithmic_signature(
    ticker: str,
) -> StockSignatureResponse:
    from sahmi_kasban.fingerprint import StockSignatureRegistry

    registry = StockSignatureRegistry()
    symbol = ticker.strip().upper()
    sig = registry.get_signature(symbol)
    if sig is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="البصمة الخوارزمية غير مسجلة لهذا السهم حالياً.",
        )
    return StockSignatureResponse(
        ticker=symbol,
        updated_at=sig.updated_at,
        overall_quality_score=sig.overall_quality_score,
        approved_by_critic=sig.ai_critic.approved,
        critic_confidence=sig.ai_critic.confidence,
        critic_summary=sig.ai_critic.summary,
        dominant_cycle_sessions=sig.time_cycle.dominant_cycle_sessions,
        cycle_stability_score=sig.time_cycle.stability_score,
        avg_sweep_depth_pct=sig.accumulation_sweep.avg_sweep_depth_pct,
        bounce_probability_pct=sig.accumulation_sweep.bounce_probability_pct,
        fvg_fill_preference_pct=sig.accumulation_sweep.fvg_fill_preference_pct,
    )


async def _require_supported_ticker(db: DatabaseSession, ticker: str) -> str:
    try:
        normalized_ticker = normalize_egx_ticker(ticker)
    except UnknownTickerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير صالح.",
        ) from exc
    if not await market_instrument_exists(db, normalized_ticker):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="رمز السهم غير موجود في سوق EGX المدعوم.",
        )
    return normalized_ticker


@router.get("/market/orderbook/{ticker}", response_model=OrderBookResponse)
async def get_market_order_book(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> OrderBookResponse:
    """دفتر الأوامر — يرجع ``available: false`` صادقًا ما لم يوجد مزوّد عمق مدعوم."""
    normalized_ticker = await _require_supported_ticker(db, ticker)
    return OrderBookResponse(**await get_order_book(db, normalized_ticker))


@router.get("/market/trades/{ticker}", response_model=RecentTradesResponse)
async def get_market_recent_trades(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=200, ge=1, le=1000),
) -> RecentTradesResponse:
    """آخر الصفقات — يرجع ``available: false`` صادقًا ما لم يوجد مزوّد صفقات مدعوم."""
    normalized_ticker = await _require_supported_ticker(db, ticker)
    return RecentTradesResponse(**await get_recent_trades(db, normalized_ticker, limit=limit))


@router.get("/market/bulk-trades", response_model=WhaleDetectionResponse)
async def get_market_bulk_trades(
    db: DatabaseSession,
    current_user: CurrentUser,
    ticker: str = Query(min_length=1, max_length=16),
    value_threshold: float | None = Query(default=None, gt=0),
) -> WhaleDetectionResponse:
    """كشف الصفقات الضخمة كإشارة بديلة (دوران يومي استثنائي) — لا صفقات فردية."""
    normalized_ticker = await _require_supported_ticker(db, ticker)
    return WhaleDetectionResponse(
        **await detect_whales(db, normalized_ticker, value_threshold=value_threshold)
    )


@router.get("/market/depth/{ticker}", response_model=MarketDepthResponse)
async def get_market_depth_summary(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
    levels: int = Query(default=10, ge=1, le=50),
) -> MarketDepthResponse:
    """ملخّص عمق السوق — نفس قواعد الإتاحة الصادقة لدفتر الأوامر."""
    normalized_ticker = await _require_supported_ticker(db, ticker)
    return MarketDepthResponse(**await get_market_depth(db, normalized_ticker, levels=levels))


@router.get("/market/top-of-book/{ticker}", response_model=TopOfBookResponse)
async def get_market_top_of_book(
    ticker: str,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> TopOfBookResponse:
    """أفضل سعر bid/ask لحظي (بدون أحجام) — متاح عبر اشتراك TradingView WS."""
    normalized_ticker = await _require_supported_ticker(db, ticker)
    return TopOfBookResponse(**await get_top_of_book(normalized_ticker))
