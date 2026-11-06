import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_outcome_panel import OUTCOME, validate_outcomes


def valid_panel():
    rows = []
    for year in [2018, 2019, 2021, 2022, 2023, 2024, 2025]:
        for state in range(1, 52):
            rows.append(
                {
                    "year": year,
                    "state": f"{state:02d}",
                    "NAME": f"State {state}",
                    "low_income_adults_19_64": 1000,
                    "uninsured_low_income_adults_19_64": 100,
                    OUTCOME: 0.1,
                }
            )
    return pd.DataFrame(rows)


def test_valid_outcome_panel_contract():
    validate_outcomes(valid_panel())


def test_outcome_rate_must_be_bounded():
    frame = valid_panel()
    frame.loc[0, OUTCOME] = 1.2

    try:
        validate_outcomes(frame)
    except RuntimeError as exc:
        assert "outside [0, 1]" in str(exc)
    else:
        raise AssertionError("Expected invalid outcome rate to fail.")


def test_every_year_requires_all_states_and_dc():
    frame = valid_panel().iloc[1:].copy()

    try:
        validate_outcomes(frame)
    except RuntimeError as exc:
        assert "50 states plus DC" in str(exc)
    else:
        raise AssertionError("Expected incomplete year to fail.")
