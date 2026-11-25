"""Depth-provider registry (WP-26).

Single wiring point between the order-flow endpoints and a level-2 depth feed.
``get_depth_provider`` resolves the provider configured via
``MARKET_DATA_DEPTH_PROVIDER`` (``"none"`` disables depth entirely); a provider
instance returned here must only be used after checking ``capabilities`` —
see ``app.market_data.types.DepthProvider``.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import get_settings
from app.market_data.tradingview_depth import build_tradingview_depth_provider
from app.market_data.types import DepthProvider

logger = logging.getLogger(__name__)


def _depth_provider_from_name(name: str) -> DepthProvider | None:
    normalized = name.strip().lower()
    if not normalized or normalized == "none":
        return None
    if normalized == "tradingview":
        return build_tradingview_depth_provider()
    logger.warning(
        "Configured depth provider is not implemented: %s",
        normalized,
    )
    return None


@lru_cache
def get_depth_provider() -> DepthProvider | None:
    """Return the configured depth provider, or ``None`` when depth is disabled."""
    settings = get_settings()
    return _depth_provider_from_name(settings.market_data_depth_provider)


def supports(provider: DepthProvider | None, capability: str) -> bool:
    return provider is not None and capability in provider.capabilities
