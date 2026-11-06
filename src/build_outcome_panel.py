import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"

OUTCOME = "uninsured_rate_low_income_adults_19_64"
EXPECTED_YEARS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]


def validate_outcomes(frame):
    if frame[["state", "year"]].duplicated().any():
        raise RuntimeError("ACS outcome panel contains duplicate state-years.")

    if sorted(frame["year"].unique().tolist()) != EXPECTED_YEARS:
        raise RuntimeError("ACS outcome years do not match the analysis contract.")

    counts = frame.groupby("year")["state"].nunique()
    if not counts.eq(51).all():
        raise RuntimeError(
            "Every ACS outcome year must contain 50 states plus DC."
        )

    if frame[OUTCOME].isna().any():
        raise RuntimeError("Primary ACS outcome contains missing values.")

    if not frame[OUTCOME].between(0, 1).all():
        raise RuntimeError("Primary ACS outcome lies outside [0, 1].")

    if (
        frame["uninsured_low_income_adults_19_64"]
        > frame["low_income_adults_19_64"]
    ).any():
        raise RuntimeError(
            "Uninsured count exceeds the low-income adult denominator."
        )


def main():
    source = RAW / "acs_low_income_adult_uninsured_state_year.csv"
    if not source.exists():
        raise RuntimeError(
            "Missing ACS source. Run python src/fetch_acs_outcomes.py first."
        )

    frame = pd.read_csv(source, dtype={"state": str})
    validate_outcomes(frame)

    frame["period_role"] = "pre"
    frame.loc[frame["year"].eq(2023), "period_role"] = "transition"
    frame.loc[frame["year"].ge(2024), "period_role"] = "post"
    frame["post"] = frame["year"].ge(2024).astype(int)
    frame["transition"] = frame["year"].eq(2023).astype(int)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    frame.to_csv(
        PROCESSED / "acs_outcome_state_year.csv",
        index=False,
    )

    summary = {
        "primary_outcome": OUTCOME,
        "population": (
            "Civilian noninstitutionalized adults ages 19-64 "
            "with family income below 138% of the poverty threshold"
        ),
        "pre_years": [2018, 2019, 2021, 2022],
        "transition_year": 2023,
        "post_years": [2024, 2025],
        "excluded_years": [2020],
        "states_per_year": 51,
        "rows": int(len(frame)),
        "uninsured_rate_by_year": {
            str(year): float(
                frame.loc[frame["year"].eq(year), OUTCOME].median()
            )
            for year in EXPECTED_YEARS
        },
    }

    (
        META / "outcome_panel_summary.json"
    ).write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(
        "Built ACS state-year outcome panel: "
        f"{len(frame)} rows, {frame['state'].nunique()} states/DC."
    )


if __name__ == "__main__":
    main()
