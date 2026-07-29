from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.services import performance_recovery


def test_summary_recovery_returns_valid_empty_ledger(
    db_session: Session,
    monkeypatch,
) -> None:
    def fail(*_args, **_kwargs):
        raise RuntimeError("legacy row failure")

    monkeypatch.setattr(performance_recovery, "get_performance_summary", fail)

    payload = performance_recovery.safe_get_performance_summary(
        db_session,
        window_sessions=7,
    )

    assert payload["window_sessions"] == 7
    assert payload["sessions_found"] == 0
    assert payload["evaluated_items"] == 0
    assert len(payload["ranks"]) == 10
    assert payload["benchmark"]["status"] == "degraded"


def test_report_list_recovery_fills_missing_generated_at(
    db_session: Session,
    monkeypatch,
) -> None:
    target = date(2026, 7, 29)

    def reports(*_args, **_kwargs):
        return [
            {
                "report_id": "00000000-0000-0000-0000-000000000001",
                "target_session_date": target,
                "generated_at": None,
            }
        ], 1

    monkeypatch.setattr(performance_recovery, "list_performance_reports", reports)

    items, total = performance_recovery.safe_list_performance_reports(
        db_session,
        limit=30,
        offset=0,
    )

    assert total == 1
    assert items[0]["generated_at"] is not None
    assert items[0]["generated_at"].date() == target
