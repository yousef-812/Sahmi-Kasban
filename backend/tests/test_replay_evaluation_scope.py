from uuid import uuid4

from app.jobs.historical_replays import _with_evaluation_scope
from app.services.historical_replays import ReplayTickerComputation


def test_unqualified_replay_rows_do_not_count_as_directional_misses() -> None:
    computation = ReplayTickerComputation(
        ticker_task_id=uuid4(),
        ticker="AALR",
        provider="fake",
        data_fingerprint="f" * 64,
        candle_count=250,
        rows=(
            {
                "status": "evaluated",
                "qualified": False,
                "correct": False,
                "analysis_quality": {"consensus": 70.0},
            },
            {
                "status": "evaluated",
                "qualified": True,
                "correct": True,
                "analysis_quality": {"consensus": 75.0},
            },
        ),
    )

    scoped = _with_evaluation_scope(computation)

    excluded, directional = scoped.rows
    assert excluded["correct"] is None
    assert excluded["analysis_quality"]["evaluation_scope"] == "eligibility_exclusion"
    assert excluded["analysis_quality"]["directional_correct"] is None
    assert directional["correct"] is True
    assert directional["analysis_quality"]["evaluation_scope"] == "directional"
    assert directional["analysis_quality"]["directional_correct"] is True
