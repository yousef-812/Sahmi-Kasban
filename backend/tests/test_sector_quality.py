import pytest
from app.services.sector_quality import compute_sector_quality


def test_compute_sector_quality_outperforming():
    res = compute_sector_quality("COMI", score=82.5, return_20d=4.5)
    assert res["sector_name"] == "البنوك"
    assert res["quality_status"] == "outperforming"
    assert "متفوق على قطاع البنوك" in res["quality_label"]
    assert res["score"] == 82.5
    assert res["return_20d_pct"] == 4.5
    assert "البنوك" in res["summary_ar"]


def test_compute_sector_quality_in_line():
    res = compute_sector_quality("TMGH", score=62.0, return_20d=1.2, raw_sector="Real Estate")
    assert res["sector_name"] == "العقارات"
    assert res["quality_status"] == "in_line"
    assert "متوافق مع قطاع العقارات" in res["quality_label"]


def test_compute_sector_quality_underperforming():
    res = compute_sector_quality("ETEL", score=42.0, return_20d=-2.1, raw_sector="Technology Services")
    assert res["sector_name"] == "الاتصالات والتكنولوجيا"
    assert res["quality_status"] == "underperforming"
    assert "أقل من متوسط قطاع الاتصالات والتكنولوجيا" in res["quality_label"]
