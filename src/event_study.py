import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

from estimate_primary_did import (
    OUTCOME,
    TREATMENT,
    build_analysis_panel,
)


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "metadata"
YEARS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]
REFERENCE_YEAR = 2022


def main():
    panel = build_analysis_panel()
    panel = panel.loc[panel["year"].isin(YEARS)].copy()

    interaction_years = [
        year for year in YEARS if year != REFERENCE_YEAR
    ]

    for year in interaction_years:
        panel[f"exposure_x_{year}"] = (
            panel[TREATMENT] * panel["year"].eq(year).astype(int)
        )

    terms = " + ".join(
        f"exposure_x_{year}" for year in interaction_years
    )

    model = smf.ols(
        f"{OUTCOME} ~ C(state_abbr) + C(year) + {terms}",
        data=panel,
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": panel["state_abbr"]},
    )

    rows = []
    for year in YEARS:
        if year == REFERENCE_YEAR:
            rows.append(
                {
                    "year": year,
                    "coefficient_per_unit_exposure": 0.0,
                    "effect_per_10pp_exposure": 0.0,
                    "std_error_per_unit_exposure": 0.0,
                    "ci_95_per_10pp_exposure": [0.0, 0.0],
                    "p_value": None,
                    "reference": True,
                }
            )
            continue

        term = f"exposure_x_{year}"
        beta = float(model.params[term])
        se = float(model.bse[term])
        p = float(model.pvalues[term])
        low, high = model.conf_int().loc[term].tolist()

        rows.append(
            {
                "year": year,
                "coefficient_per_unit_exposure": beta,
                "effect_per_10pp_exposure": beta * 0.10,
                "std_error_per_unit_exposure": se,
                "ci_95_per_10pp_exposure": [
                    float(low) * 0.10,
                    float(high) * 0.10,
                ],
                "p_value": p,
                "reference": False,
            }
        )

    result = {
        "outcome": OUTCOME,
        "treatment": TREATMENT,
        "reference_year": REFERENCE_YEAR,
        "estimates": rows,
        "standard_errors": "clustered by state",
        "interpretation": (
            "Year-specific continuous-exposure interactions relative to "
            "2022. Pre-period estimates are identifying-assumption "
            "diagnostics; 2023 is a transition year; 2024-2025 are "
            "post-unwinding estimates."
        ),
    }

    META.mkdir(parents=True, exist_ok=True)
    (META / "event_study_result.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("Continuous-exposure event study (2022 reference):")
    for row in rows:
        if row["reference"]:
            print(f"  {row['year']}: reference")
            continue

        effect = row["effect_per_10pp_exposure"] * 100
        low, high = [
            value * 100
            for value in row["ci_95_per_10pp_exposure"]
        ]
        print(
            f"  {row['year']}: {effect:.3f} pp "
            f"(95% CI {low:.3f}, {high:.3f}), "
            f"p={row['p_value']:.3f}"
        )


if __name__ == "__main__":
    main()
