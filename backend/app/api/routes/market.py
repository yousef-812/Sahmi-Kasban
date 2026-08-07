from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_data.catalog import market_instrument_exists, search_market_instruments
from app.market_data.egx_symbols import normalize_egx_ticker
from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import fetch_market_quotes, fetch_single_quote
from app.market_data.types import (
    MarketDataProvider,
    MarketDataUnavailableError,
    UnknownTickerError,
)
from app.schemas.market import (
    MarketInstrumentListResponse,
    MarketInstrumentResponse,
    MarketQuoteResponse,
    MarketQuotesResponse,
    StockAnalysisRequest,
    StockAnalysisResponse,
    StockComparisonFailureResponse,
    StockComparisonItemResponse,
    StockComparisonRequest,
    StockComparisonResponse,
)
from app.services.stock_analysis import (
    StockAnalysisExecution,
    StockAnalysisExecutionError,
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
from app.services.wallet import InsufficientBalanceError, points_to_coins
from sahmi_kasban.ai import SahmiAIService

router = APIRouter(tags=["market"])
MarketProvider = Annotated[MarketDataProvider, Depends(get_market_data_provider)]
StockAIService = Annotated[SahmiAIService, Depends(get_stock_ai_service)]


def _analysis_response(execution: StockAnalysisExecution) -> StockAnalysisResponse:
    analysis = execution.analysis
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
        failed_items=[
            StockComparisonFailureResponse(**item) for item in raw_failed_items
        ],
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
            detail=(
                "لم يكتمل التحليل لأن تاريخ السهم أو بياناته لا تكفي "
                "للمحركات حاليًا."
            ),
        ) from exc

    return _analysis_response(execution)
