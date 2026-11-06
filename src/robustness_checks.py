import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from estimate_primary_did import (
    OUTCOME,
    PRIMARY_YEARS,
    TREATMENT,
    build_analysis_panel,
)


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"

ALT_TREATMENT = "procedural_rate_completed"
WEIGHT = "low_income_adults_19_64"


def fit_twfe(
    frame,
    treatment,
    post_column,
    weighted=False,
):
    work = frame.copy()
    interaction = f"{treatment}_x_{post_column}"
    work[interaction] = work[treatment] * work[post_column]

    formula = (
        f"{OUTCOME} ~ C(state_abbr) + C(year) + {interaction}"
    )

    if weighted:
        model = smf.wls(
            formula,
            data=work,
            weights=work[WEIGHT],
        )
    else:
        model = smf.ols(
            formula,
            data=work,
        )

    fitted = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": work["state_abbr"]},
    )

    beta = float(fitted.params[interaction])
    se = float(fitted.bse[interaction])
    p = float(fitted.pvalues[interaction])
    low, high = fitted.conf_int().loc[interaction].tolist()

    return {
        "effect_per_10pp": beta * 0.10,
        "std_error_per_10pp": se * 0.10,
        "ci_95_per_10pp": [float(low) * 0.10, float(high) * 0.10],
        "p_value": p,
        "n_state_years": int(len(work)),
        "states": int(work["state_abbr"].nunique()),
    }


def add_alternative_treatment(panel):
    exposure = pd.read_csv(
        PROCESSED / "state_unwinding_exposure.csv"
    )[
        ["State Abbreviation", ALT_TREATMENT]
    ].rename(
        columns={"State Abbreviation": "state_abbr"}
    )

    result = panel.merge(
        exposure,
        on="state_abbr",
        how="left",
        validate="many_to_one",
    )

    if result[ALT_TREATMENT].isna().any():
        raise RuntimeError("Alternative treatment contains missing states.")

    return result


def population_weighted(panel):
    analysis = panel.loc[
        panel["year"].isin(PRIMARY_YEARS)
    ].copy()
    return fit_twfe(
        analysis,
        TREATMENT,
        "post",
        weighted=True,
    )


def procedural_exposure(panel):
    analysis = add_alternative_treatment(panel)
    analysis = analysis.loc[
        analysis["year"].isin(PRIMARY_YEARS)
    ].copy()

    return fit_twfe(
        analysis,
        ALT_TREATMENT,
        "post",
        weighted=False,
    )


def placebo_timing(panel):
    placebo_years = [2018, 2019, 2021, 2022]
    analysis = panel.loc[
        panel["year"].isin(placebo_years)
    ].copy()
    analysis["placebo_post"] = analysis["year"].isin(
        [2021, 2022]
    ).astype(int)

    return fit_twfe(
        analysis,
        TREATMENT,
        "placebo_post",
        weighted=False,
    )


def trimmed_exposure(panel):
    state_exposure = (
        panel[["state_abbr", TREATMENT]]
        .drop_duplicates()
        .sort_values(TREATMENT)
    )
    lower = float(state_exposure[TREATMENT].quantile(0.05))
    upper = float(state_exposure[TREATMENT].quantile(0.95))

    keep_states = state_exposure.loc[
        state_exposure[TREATMENT].between(lower, upper),
        "state_abbr",
    ]

    analysis = panel.loc[
        panel["state_abbr"].isin(keep_states)
        & panel["year"].isin(PRIMARY_YEARS)
    ].copy()

    result = fit_twfe(
        analysis,
        TREATMENT,
        "post",
        weighted=False,
    )
    result["exposure_bounds"] = [lower, upper]
    return result


def leave_one_state_out(panel):
    analysis = panel.loc[
        panel["year"].isin(PRIMARY_YEARS)
    ].copy()

    rows = []
    for state in sorted(analysis["state_abbr"].unique()):
        subset = analysis.loc[
            analysis["state_abbr"].ne(state)
        ].copy()

        estimate = fit_twfe(
            subset,
            TREATMENT,
            "post",
            weighted=False,
        )

        rows.append(
            {
                "excluded_state": state,
                "effect_per_10pp": estimate["effect_per_10pp"],
            }
        )

    values = np.array(
        [row["effect_per_10pp"] for row in rows]
    )

    minimum = min(rows, key=lambda row: row["effect_per_10pp"])
    maximum = max(rows, key=lambda row: row["effect_per_10pp"])

    return {
        "minimum_effect": minimum,
        "maximum_effect": maximum,
        "median_effect_per_10pp": float(np.median(values)),
        "mean_effect_per_10pp": float(np.mean(values)),
        "range_per_10pp": [
            float(values.min()),
            float(values.max()),
        ],
        "estimates": rows,
    }


def main():
    panel = build_analysis_panel()

    results = {
        "population_weighted": population_weighted(panel),
        "procedural_exposure": procedural_exposure(panel),
        "placebo_timing": placebo_timing(panel),
        "trimmed_exposure_5_95": trimmed_exposure(panel),
        "leave_one_state_out": leave_one_state_out(panel),
    }

    META.mkdir(parents=True, exist_ok=True)
    (META / "robustness_results.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("Robustness checks:")

    weighted = results["population_weighted"]
    print(
        "  Population-weighted primary: "
        f"{weighted['effect_per_10pp'] * 100:.3f} pp "
        f"(p={weighted['p_value']:.3f})"
    )

    procedural = results["procedural_exposure"]
    print(
        "  Procedural disenrollment exposure: "
        f"{procedural['effect_per_10pp'] * 100:.3f} pp "
        f"(p={procedural['p_value']:.3f})"
    )

    placebo = results["placebo_timing"]
    print(
        "  Placebo 2021-2022 timing: "
        f"{placebo['effect_per_10pp'] * 100:.3f} pp "
        f"(p={placebo['p_value']:.3f})"
    )

    trimmed = results["trimmed_exposure_5_95"]
    print(
        "  5th-95th percentile exposure trim: "
        f"{trimmed['effect_per_10pp'] * 100:.3f} pp "
        f"(p={trimmed['p_value']:.3f})"
    )

    loo = results["leave_one_state_out"]
    low, high = loo["range_per_10pp"]
    print(
        "  Leave-one-state-out range: "
        f"{low * 100:.3f} to {high * 100:.3f} pp"
    )
    print(
        "  Most negative exclusion: "
        f"{loo['minimum_effect']['excluded_state']} "
        f"({loo['minimum_effect']['effect_per_10pp'] * 100:.3f} pp)"
    )
    print(
        "  Most positive exclusion: "
        f"{loo['maximum_effect']['excluded_state']} "
        f"({loo['maximum_effect']['effect_per_10pp'] * 100:.3f} pp)"
    )


if __name__ == "__main__":
    main()
