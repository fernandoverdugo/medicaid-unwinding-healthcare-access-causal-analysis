import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from robustness_checks import fit_twfe


def synthetic_panel():
    rows = []
    for state_index in range(20):
        state = f"S{state_index:02d}"
        exposure = state_index / 20
        for year in [2018, 2019, 2021, 2022, 2024, 2025]:
            post = int(year >= 2024)
            rows.append(
                {
                    "state_abbr": state,
                    "year": year,
                    "treatment": exposure,
                    "post": post,
                    "low_income_adults_19_64": 1000 + state_index * 10,
                    "uninsured_rate_low_income_adults_19_64": (
                        0.15
                        + 0.001 * (year - 2018)
                        + 0.03 * exposure * post
                    ),
                }
            )
    return pd.DataFrame(rows)


def test_fit_twfe_recovers_positive_signal():
    frame = synthetic_panel()
    result = fit_twfe(
        frame,
        "treatment",
        "post",
        weighted=False,
    )
    assert result["effect_per_10pp"] > 0
    assert result["states"] == 20


def test_weighted_fit_uses_same_contract():
    frame = synthetic_panel()
    result = fit_twfe(
        frame,
        "treatment",
        "post",
        weighted=True,
    )
    assert result["effect_per_10pp"] > 0
    assert result["n_state_years"] == 120
