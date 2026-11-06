import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_unwinding_exposure import (
    DISENROLLED,
    DUE,
    INELIGIBLE,
    PENDING,
    PROCEDURAL,
    RENEWED,
    STATE,
    STATE_NAME,
    PERIOD,
    VERSION,
    add_initial_unwinding_window,
    canonicalize_monthly,
    summarize_state_exposure,
)


def sample_rows():
    return pd.DataFrame(
        [
            {
                STATE: "AA",
                STATE_NAME: "Alpha",
                PERIOD: 202303,
                VERSION: "O",
                DUE: 100,
                RENEWED: 70,
                DISENROLLED: 20,
                INELIGIBLE: 8,
                PROCEDURAL: 12,
                PENDING: 10,
            },
            {
                STATE: "AA",
                STATE_NAME: "Alpha",
                PERIOD: 202303,
                VERSION: "U",
                DUE: 100,
                RENEWED: 75,
                DISENROLLED: 20,
                INELIGIBLE: 8,
                PROCEDURAL: 12,
                PENDING: 5,
            },
            {
                STATE: "AA",
                STATE_NAME: "Alpha",
                PERIOD: 202304,
                VERSION: "O",
                DUE: 120,
                RENEWED: 80,
                DISENROLLED: 30,
                INELIGIBLE: 10,
                PROCEDURAL: 20,
                PENDING: 10,
            },
        ]
    )


def test_updated_record_overrides_original_outcomes():
    result = canonicalize_monthly(sample_rows())
    march = result.loc[result[PERIOD].eq(202303)].iloc[0]

    assert march[RENEWED] == 75
    assert march[DISENROLLED] == 20
    assert march[PENDING] == 5


def test_completed_renewal_denominator_excludes_pending():
    result = canonicalize_monthly(sample_rows())
    march = result.loc[result[PERIOD].eq(202303)].iloc[0]

    assert march["completed_renewals"] == 95
    assert march["disenrollment_rate_completed"] == 20 / 95


def test_initial_window_starts_with_first_completed_outcome_month():
    result = canonicalize_monthly(sample_rows())
    result = add_initial_unwinding_window(result)

    assert result["unwinding_start"].dt.strftime("%Y-%m").unique().tolist() == [
        "2023-03"
    ]


def test_state_summary_aggregates_counts_before_rates():
    result = canonicalize_monthly(sample_rows())
    result = add_initial_unwinding_window(result)
    state = summarize_state_exposure(result).iloc[0]

    assert state["completed_renewals"] == 205
    assert state["disenrolled"] == 50
    assert state["disenrollment_rate_completed"] == 50 / 205
