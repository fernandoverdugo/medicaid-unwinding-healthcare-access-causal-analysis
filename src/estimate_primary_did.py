import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"

OUTCOME = "uninsured_rate_low_income_adults_19_64"
TREATMENT = "disenrollment_rate_completed"
PRIMARY_YEARS = [2018, 2019, 2021, 2022, 2024, 2025]


def build_analysis_panel():
    outcomes = pd.read_csv(
        PROCESSED / "acs_outcome_state_year.csv",
        dtype={"state": str},
    )
    exposure = pd.read_csv(
        PROCESSED / "state_unwinding_exposure.csv"
    )

    treatment = exposure[
        ["State Abbreviation", "State Name", TREATMENT]
    ].rename(
        columns={
            "State Abbreviation": "state_abbr",
            "State Name": "NAME",
        }
    )

    panel = outcomes.merge(
        treatment,
        on="NAME",
        how="left",
        validate="many_to_one",
    )

    if panel[TREATMENT].isna().any():
        missing = sorted(panel.loc[panel[TREATMENT].isna(), "NAME"].unique())
        raise RuntimeError(
            "Missing treatment for outcome states: " + ", ".join(missing)
        )

    panel["post"] = panel["year"].ge(2024).astype(int)
    panel["treatment_x_post"] = panel[TREATMENT] * panel["post"]
    return panel


def estimate_primary(panel):
    analysis = panel.loc[panel["year"].isin(PRIMARY_YEARS)].copy()

    expected_rows = 51 * len(PRIMARY_YEARS)
    if len(analysis) != expected_rows:
        raise RuntimeError(
            f"Primary DiD panel has {len(analysis)} rows; "
            f"expected {expected_rows}."
        )

    model = smf.ols(
        f"{OUTCOME} ~ C(state_abbr) + C(year) + treatment_x_post",
        data=analysis,
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": analysis["state_abbr"]},
    )

    beta = float(model.params["treatment_x_post"])
    se = float(model.bse["treatment_x_post"])
    p = float(model.pvalues["treatment_x_post"])
    ci_low, ci_high = model.conf_int().loc["treatment_x_post"].tolist()

    exposure_increment = 0.10

    return {
        "coefficient_per_unit_exposure": beta,
        "std_error_per_unit_exposure": se,
        "p_value": p,
        "ci_95_per_unit_exposure": [float(ci_low), float(ci_high)],
        "effect_per_10pp_higher_exposure": beta * exposure_increment,
        "ci_95_per_10pp_higher_exposure": [
            float(ci_low) * exposure_increment,
            float(ci_high) * exposure_increment,
        ],
        "n_state_years": int(len(analysis)),
        "states": int(analysis["state_abbr"].nunique()),
        "pre_years": [2018, 2019, 2021, 2022],
        "post_years": [2024, 2025],
        "excluded_transition_year": 2023,
        "standard_errors": "clustered by state",
        "state_fixed_effects": True,
        "year_fixed_effects": True,
    }


def main():
    panel = build_analysis_panel()
    result = estimate_primary(panel)

    META.mkdir(parents=True, exist_ok=True)
    (META / "primary_did_result.json").write_text(
        json.dumps(
            {
                "outcome": OUTCOME,
                "treatment": TREATMENT,
                "specification": result,
                "interpretation": (
                    "The treatment interaction estimates the differential "
                    "post-unwinding change associated with higher state "
                    "disenrollment exposure. Causal interpretation remains "
                    "conditional on parallel-trend and no-differential-shock "
                    "assumptions."
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    effect = result["effect_per_10pp_higher_exposure"]
    ci_low, ci_high = result["ci_95_per_10pp_higher_exposure"]

    print("Primary continuous-exposure difference-in-differences:")
    print(
        "  Effect per 10 percentage-point higher disenrollment exposure: "
        f"{effect * 100:.3f} percentage points"
    )
    print(
        "  95% CI: "
        f"{ci_low * 100:.3f} to {ci_high * 100:.3f} percentage points"
    )
    print(f"  p={result['p_value']:.3f}")
    print(
        f"  N={result['n_state_years']} state-years; "
        f"{result['states']} states/DC"
    )


if __name__ == "__main__":
    main()
