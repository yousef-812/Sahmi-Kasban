from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data import global_market


def _payload(rows: list[tuple[str, list]]) -> dict:
    return {"data": [{"s": symbol, "d": values} for symbol, values in rows]}


STUB_PAYLOADS: dict[str, dict] = {
    "global": _payload(
        [
            ("SP:SPX", [7805.45, -0.0229, None]),
            ("NASDAQ:IXIC", [27204.38, -0.1524, None]),
            ("TADAWUL:TASI", [10318.14, 0.3324, None]),
            ("EVIL:FAKE", [1.0, 0.0, None]),
        ]
    ),
    "forex": _payload(
        [
            ("FX_IDC:USDEGP", [52.77, 0.3232, "EGP"]),
            ("FX:EURUSD", [1.11999, 0.0161, "USD"]),
            ("FX:USDJPY", [158.292, -0.0095, "JPY"]),
        ]
    ),
    "futures": _payload(
        [
            ("COMEX:GC1!", [4177.3, -0.3174, "USD"]),
            ("NYMEX:CL1!", [94.14, 0.4267, "USD"]),
            ("NYMEX:NG1!", [3.283, 3.6628, "USD"]),
        ]
    ),
}


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(global_market, "_cache", None)
    monkeypatch.setattr(global_market, "_cache_at", None)
    monkeypatch.setattr(global_market, "_cache_ttl", global_market.GLOBAL_MARKET_CACHE_TTL)


@pytest.fixture(autouse=True)
def block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_network(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("network calls are disabled in tests")

    monkeypatch.setattr(global_market, "_fetch_scanner_payload", _no_network)


def _stub_scanner(monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> None:
    async def _stub(market: str, tickers: list[str]) -> object:
        calls.append(market)
        return STUB_PAYLOADS[market]

    monkeypatch.setattr(global_market, "_fetch_scanner_payload", _stub)


def test_endpoint_returns_documented_shape(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    _stub_scanner(monkeypatch, calls)

    response = client.get("/api/v1/market/global")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"available", "source", "as_of", "indices", "fx", "commodities", "error"}
    assert body["available"] is True
    assert body["source"] == "tradingview_scanner"
    assert body["as_of"] is not None
    assert body["error"] is None
    assert sorted(calls) == ["forex", "futures", "global"]

    indices = {item["symbol"]: item for item in body["indices"]}
    assert set(indices) == {"SP:SPX", "NASDAQ:IXIC", "TADAWUL:TASI"}
    spx = indices["SP:SPX"]
    assert spx["value"] == pytest.approx(7805.45)
    assert spx["change_pct"] == pytest.approx(-0.0229)
    assert spx["currency"] is None
    assert spx["kind"] == "index"
    assert spx["name"] and spx["name_ar"]

    fx = {item["symbol"]: item for item in body["fx"]}
    usd_egp = fx["FX_IDC:USDEGP"]
    assert usd_egp["value"] == pytest.approx(52.77)
    assert usd_egp["change_pct"] == pytest.approx(0.3232)
    assert usd_egp["currency"] == "EGP"
    assert usd_egp["kind"] == "fx"
    assert fx["FX:EURUSD"]["currency"] == "USD"

    commodities = {item["symbol"]: item for item in body["commodities"]}
    assert commodities["COMEX:GC1!"]["kind"] == "metal"
    assert commodities["NYMEX:CL1!"]["kind"] == "energy"
    assert all(item["currency"] == "USD" for item in commodities.values())


def test_endpoint_degrades_to_available_false_on_source_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _boom(market: str, tickers: list[str]) -> object:
        raise RuntimeError("scanner down")

    monkeypatch.setattr(global_market, "_fetch_scanner_payload", _boom)

    response = client.get("/api/v1/market/global")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    assert body["source"] == "tradingview_scanner"
    assert body["as_of"] is None
    assert body["indices"] == []
    assert body["fx"] == []
    assert body["commodities"] == []
    assert body["error"] is not None
    assert body["error"].startswith("tradingview_scanner unavailable:")
    assert "RuntimeError" in body["error"]


def test_endpoint_reports_unavailable_when_scanner_returns_no_rows(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _empty(market: str, tickers: list[str]) -> object:
        return {"data": []}

    monkeypatch.setattr(global_market, "_fetch_scanner_payload", _empty)

    response = client.get("/api/v1/market/global")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    assert body["error"] == "tradingview_scanner returned no rows for the configured global symbols"


def test_second_call_serves_cache_without_refetching(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    _stub_scanner(monkeypatch, calls)

    first = client.get("/api/v1/market/global").json()
    second = client.get("/api/v1/market/global").json()

    assert sorted(calls) == ["forex", "futures", "global"]
    assert second == first


def test_force_refresh_bypasses_cache(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    _stub_scanner(monkeypatch, calls)

    client.get("/api/v1/market/global")
    client.get("/api/v1/market/global", params={"force_refresh": True})

    assert len(calls) == 6


def test_service_contract_uses_module_ttl_cache(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    _stub_scanner(monkeypatch, calls)

    async def _call_twice() -> tuple[dict, dict]:
        first = await global_market.get_global_market(db_session)
        second = await global_market.get_global_market(db_session)
        return first, second

    first, second = asyncio.run(_call_twice())

    assert first is second
    assert len(calls) == 3
    assert set(first) == {"available", "source", "as_of", "indices", "fx", "commodities", "error"}
    assert first["available"] is True
    assert len(db_session.new) == 0 and len(db_session.dirty) == 0
