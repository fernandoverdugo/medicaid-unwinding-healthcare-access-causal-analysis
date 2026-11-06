import json
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"

OUTCOME = "uninsured_rate_low_income_adults_19_64"
TREATMENT = "disenrollment_rate_completed"
PRE_YEARS = [2018, 2019, 2021, 2022]


def state_crosswalk(outcomes, exposure):
    left = (
        outcomes[["state", "NAME"]]
        .drop_duplicates()
        .rename(columns={"state": "state_fips"})
    )
    right = exposure[
        ["State Abbreviation", "State Name", TREATMENT]
    ].drop_duplicates()

    merged = left.merge(
        right,
        left_on="NAME",
        right_on="State Name",
        how="left",
    )

    if merged[TREATMENT].isna().any():
        missing = merged.loc[merged[TREATMENT].isna(), "NAME"].tolist()
        raise RuntimeError(
            "Unable to match ACS states to CMS treatment data: "
            + ", ".join(missing)
        )

    return merged[
        ["state_fips", "State Abbreviation", TREATMENT]
    ]


def main():
    outcomes = pd.read_csv(
        PROCESSED / "acs_outcome_state_year.csv",
        dtype={"state": str},
    )
    exposure = pd.read_csv(
        PROCESSED / "state_unwinding_exposure.csv"
    )

    crosswalk = state_crosswalk(outcomes, exposure)

    panel = outcomes.merge(
        crosswalk,
        left_on="state",
        right_on="state_fips",
        how="left",
    )

    pre = panel.loc[panel["year"].isin(PRE_YEARS)].copy()
    pre = pre.rename(
        columns={"State Abbreviation": "state_abbr"}
    )

    if len(pre) != 51 * len(PRE_YEARS):
        raise RuntimeError("Pre-period panel is incomplete.")

    diagnostic_years = [2019, 2021, 2022]

    for year in diagnostic_years:
        column = f"exposure_x_{year}"
        pre[column] = (
            pre[TREATMENT] * pre["year"].eq(year).astype(int)
        )

    interaction_terms = " + ".join(
        f"exposure_x_{year}" for year in diagnostic_years
    )

    model = smf.ols(
        f"{OUTCOME} ~ C(year) + C(state_abbr) + {interaction_terms}",
        data=pre,
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": pre["state_abbr"]},
    )

    interaction_rows = [
        {
            "year": 2018,
            "coefficient": 0.0,
            "std_error": 0.0,
            "p_value": None,
            "reference": True,
        }
    ]

    for year in diagnostic_years:
        term = f"exposure_x_{year}"
        interaction_rows.append(
            {
                "year": year,
                "coefficient": float(model.params[term]),
                "std_error": float(model.bse[term]),
                "p_value": float(model.pvalues[term]),
                "reference": False,
            }
        )

    joint = model.wald_test(
        "exposure_x_2019 = exposure_x_2021 = exposure_x_2022 = 0",
        scalar=True,
    )
    joint_statistic = float(joint.statistic)
    joint_p_value = float(joint.pvalue)

    first = (
        pre.loc[pre["year"].eq(2018), ["state_abbr", OUTCOME, TREATMENT]]
        .rename(columns={OUTCOME: "outcome_2018"})
    )
    last = (
        pre.loc[pre["year"].eq(2022), ["state_abbr", OUTCOME]]
        .rename(columns={OUTCOME: "outcome_2022"})
    )
    slopes = first.merge(last, on="state_abbr", how="inner")
    slopes["outcome_change_2018_2022"] = (
        slopes["outcome_2022"] - slopes["outcome_2018"]
    )

    correlation = float(
        slopes["outcome_change_2018_2022"].corr(slopes[TREATMENT])
    )

    result = {
        "outcome": OUTCOME,
        "treatment": TREATMENT,
        "pre_years": PRE_YEARS,
        "reference_year": PRE_YEARS[0],
        "interaction_estimates": interaction_rows,
        "correlation_exposure_with_2018_2022_change": correlation,
        "joint_pretrend_test": {
            "statistic": joint_statistic,
            "p_value": joint_p_value,
            "null": "All pre-period exposure interactions equal zero",
        },
        "interpretation_rule": (
            "Pre-period interactions are diagnostics, not a binary pass/fail "
            "test. Large systematic pre-trends would weaken a causal claim."
        ),
    }

    META.mkdir(parents=True, exist_ok=True)
    (
        META / "pretrend_diagnostic.json"
    ).write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("Pre-treatment exposure interaction diagnostics:")
    for row in interaction_rows:
        if row["reference"]:
            print(f"  {row['year']}: reference")
        else:
            print(
                f"  {row['year']}: beta={row['coefficient']:.4f}, "
                f"SE={row['std_error']:.4f}, p={row['p_value']:.3f}"
            )

    print(
        "Joint pre-trend test: "
        f"stat={joint_statistic:.3f}, p={joint_p_value:.3f}"
    )
    print(
        "Correlation between unwinding exposure and 2018-2022 "
        f"outcome change: {correlation:.3f}"
    )


if __name__ == "__main__":
    main()
