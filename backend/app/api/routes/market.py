from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sahmi_kasban.ai import SahmiAIService

from app.api.dependencies import CurrentUser, DatabaseSession
from app.market_data.egx_symbols import EGX_SEED_SYMBOLS, list_instruments
from app.market_data.provider import get_market_data_provider
from app.market_data.types import (
    MarketDataProvider,
    MarketDataUnavailableError,
    UnknownTickerError,
)
from app.schemas.market import (
    MarketInstrumentListResponse,
    MarketInstrumentResponse,
    StockAnalysisRequest,
    StockAnalysisResponse,
)
from app.services.stock_analysis import (
    StockAnalysisExecutionError,
    execute_stock_analysis,
    get_stock_ai_service,
)
from app.services.wallet import InsufficientBalanceError, points_to_coins

router = APIRouter(tags=["market"])
MarketProvider = Annotated[MarketDataProvider, Depends(get_market_data_provider)]
StockAIService = Annotated[SahmiAIService, Depends(get_stock_ai_service)]


@router.get("/market/instruments", response_model=MarketInstrumentListResponse)
def get_market_instruments(
    query: str = Query(default="", max_length=24),
    limit: int = Query(default=50, ge=1, le=200),
) -> MarketInstrumentListResponse:
    instruments = list_instruments(query=query, limit=limit)
    return MarketInstrumentListResponse(
        total_registry_size=len(EGX_SEED_SYMBOLS),
        items=[MarketInstrumentResponse(**instrument.to_dict()) for instrument in instruments],
    )


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
        execution = await execute_stock_analysis(
            db,
            user=current_user,
            ticker=ticker,
            provider=provider,
            ai_service=ai_service,
            language=request.language,
        )
    except UnknownTickerError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InsufficientBalanceError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient coin balance for this analysis",
        ) from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market data is temporarily unavailable",
        ) from exc
    except StockAnalysisExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The stock analysis could not be completed",
        ) from exc

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