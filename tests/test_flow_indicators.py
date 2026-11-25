from __future__ import annotations

import pandas as pd
import pytest

from sahmi_kasban.indicators import (
    accumulation_distribution,
    ad_trend,
    buy_sell_volume,
    close_location_value,
    flow_summary,
)


def _bars(closes: list[float], *, volumes: list[float] | None = None) -> pd.DataFrame:
    """شمعة H=C وL=O — CLV = ‎+1‎ إذا إغلاق صاعد، ‎-1‎ إذا هابط."""
    opens = [closes[0], *closes[:-1]]
    highs = [max(o, c) for o, c in zip(opens, closes, strict=True)]
    lows = [min(o, c) for o, c in zip(opens, closes, strict=True)]
    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes if volumes is not None else [1_000.0] * len(closes),
        }
    )


def test_close_location_value_bounds_and_zero_range() -> None:
    frame = pd.DataFrame(
        {
            "open": [10.0, 10.0, 10.0],
            "high": [11.0, 11.0, 10.0],
            "low": [9.0, 9.0, 10.0],
            "close": [11.0, 9.0, 10.0],
            "volume": [100.0, 100.0, 100.0],
        }
    )

    clv = close_location_value(frame)

    assert clv.iloc[0] == pytest.approx(1.0)
    assert clv.iloc[1] == pytest.approx(-1.0)
    assert clv.iloc[2] == 0.0  # مدى صفري → 0
    assert clv.between(-1.0, 1.0).all()


def test_buy_sell_volume_splits_each_bar() -> None:
    frame = _bars([100.0, 101.0, 100.0], volumes=[1_000.0, 2_000.0, 4_000.0])

    buy, sell = buy_sell_volume(frame)

    assert buy.iloc[0] == pytest.approx(0.0)  # شمعة أولى بلا اتجاه (CLV=0)
    assert buy.iloc[1] == pytest.approx(2_000.0)
    assert sell.iloc[1] == pytest.approx(0.0)
    assert sell.iloc[2] == pytest.approx(4_000.0)
    assert buy.iloc[2] == pytest.approx(0.0)
    # الشموع ذات المدى غير الصفري تُوزَّع حجمها كاملًا (CLV = ±1 هنا).
    assert (buy + sell).iloc[1:].tolist() == pytest.approx(
        frame["volume"].astype(float).iloc[1:].tolist()
    )


def test_accumulation_distribution_is_cumulative() -> None:
    frame = _bars([100.0, 101.0, 102.0], volumes=[1_000.0, 1_000.0, 1_000.0])

    line = accumulation_distribution(frame)

    assert line.iloc[0] == pytest.approx(0.0)  # شمعة أولى بلا اتجاه
    assert line.iloc[1] == pytest.approx(1_000.0)
    assert line.iloc[2] == pytest.approx(2_000.0)


def test_ad_trend_direction() -> None:
    rising = _bars([100.0 + index for index in range(30)])
    falling = _bars([100.0 - index for index in range(30)])

    assert ad_trend(rising, window=20) == 1
    assert ad_trend(falling, window=20) == -1


def test_flow_summary_accumulate_distribute_and_neutral() -> None:
    bullish = flow_summary(_bars([100.0 + index for index in range(40)]))
    assert bullish["verdict"] == "accumulate"
    assert bullish["buy_share_pct"] == pytest.approx(100.0)
    assert bullish["sell_share_pct"] == pytest.approx(0.0)
    assert bullish["net_volume"] > 0
    assert bullish["ad_trend"] == 1
    assert bullish["obv_trend"] == 1

    bearish = flow_summary(_bars([100.0 - index for index in range(40)]))
    assert bearish["verdict"] == "distribute"
    assert bearish["buy_share_pct"] == pytest.approx(0.0)
    assert bearish["net_volume"] < 0
    assert bearish["ad_trend"] == -1

    mixed_closes: list[float] = [100.0]
    for index in range(40):
        mixed_closes.append(mixed_closes[-1] + (1.0 if index % 2 == 0 else -0.5))
    mixed = flow_summary(_bars(mixed_closes))
    assert mixed["verdict"] == "neutral"
    assert 45.0 < mixed["buy_share_pct"] < 55.0


def test_flow_summary_reports_documented_keys_and_windows() -> None:
    frame = _bars([100.0 + index for index in range(30)])

    summary = flow_summary(frame, window=20)

    assert set(summary) == {
        "buy_volume",
        "sell_volume",
        "buy_share_pct",
        "sell_share_pct",
        "net_volume",
        "ad_trend",
        "mfi14",
        "obv_trend",
        "verdict",
    }
    assert 0.0 <= summary["mfi14"] <= 100.0


def test_flow_summary_window_is_clamped_to_history() -> None:
    frame = _bars([100.0, 101.0, 102.0])

    summary = flow_summary(frame, window=20)

    assert summary["verdict"] == "accumulate"
