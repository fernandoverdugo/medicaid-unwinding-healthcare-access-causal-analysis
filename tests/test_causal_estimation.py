import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from estimate_primary_did import (
    PRIMARY_YEARS,
    TREATMENT,
    estimate_primary,
)


def synthetic_panel():
    rows = []
    for state_index in range(51):
        state = f"S{state_index:02d}"
        exposure = state_index / 100
        for year in [2018, 2019, 2021, 2022, 2024, 2025]:
            post = int(year >= 2024)
            rows.append(
                {
                    "state_abbr": state,
                    "year": year,
                    TREATMENT: exposure,
                    "post": post,
                    "treatment_x_post": exposure * post,
                    "uninsured_rate_low_income_adults_19_64": (
                        0.15
                        + 0.002 * (year - 2018)
                        + 0.04 * exposure * post
                    ),
                }
            )
    return pd.DataFrame(rows)


def test_primary_year_contract_excludes_transition_year():
    assert PRIMARY_YEARS == [2018, 2019, 2021, 2022, 2024, 2025]
    assert 2023 not in PRIMARY_YEARS


def test_primary_did_recovers_synthetic_effect_direction():
    result = estimate_primary(synthetic_panel())
    assert result["effect_per_10pp_higher_exposure"] > 0
    assert result["states"] == 51
    assert result["n_state_years"] == 306
