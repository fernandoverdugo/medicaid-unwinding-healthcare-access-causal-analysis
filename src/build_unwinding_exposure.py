import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"

STATE = "State Abbreviation"
STATE_NAME = "State Name"
PERIOD = "Reporting Period"
VERSION = "Original or Updated"

RENEWED = "Beneficiaries Whose Coverage Was Renewed (Total)"
DISENROLLED = "Beneficiaries Disenrolled at Renewal (Total)"
INELIGIBLE = "Beneficiaries Determined Ineligible at Renewal"
PROCEDURAL = "Beneficiaries Disenrolled for Procedural Reasons at Renewal"
PENDING = "Beneficiaries with a Pending Renewal"
DUE = "Beneficiaries with a Renewal Due"

OUTCOME_COLUMNS = [
    DUE,
    RENEWED,
    DISENROLLED,
    INELIGIBLE,
    PROCEDURAL,
    PENDING,
]


def clean_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def canonicalize_monthly(frame):
    work = frame.copy()

    required = {STATE, STATE_NAME, PERIOD, VERSION, *OUTCOME_COLUMNS}
    missing = required - set(work.columns)
    if missing:
        raise RuntimeError(
            "CMS file is missing required columns: "
            + ", ".join(sorted(missing))
        )

    work[PERIOD] = clean_numeric(work[PERIOD]).astype("Int64")

    for column in OUTCOME_COLUMNS:
        work[column] = clean_numeric(work[column])

    originals = (
        work.loc[work[VERSION].eq("O"), [STATE, STATE_NAME, PERIOD, *OUTCOME_COLUMNS]]
        .drop_duplicates([STATE, PERIOD], keep="last")
        .set_index([STATE, PERIOD])
    )

    updates = (
        work.loc[work[VERSION].eq("U"), [STATE, STATE_NAME, PERIOD, *OUTCOME_COLUMNS]]
        .drop_duplicates([STATE, PERIOD], keep="last")
        .set_index([STATE, PERIOD])
    )

    index = originals.index.union(updates.index)
    canonical = pd.DataFrame(index=index).reset_index()

    for column in [STATE_NAME, *OUTCOME_COLUMNS]:
        updated = updates[column].reindex(index) if column in updates else None
        original = originals[column].reindex(index) if column in originals else None

        if updated is None:
            values = original
        elif original is None:
            values = updated
        else:
            values = updated.combine_first(original)

        canonical[column] = values.to_numpy()

    canonical["reporting_date"] = pd.to_datetime(
        canonical[PERIOD].astype(str) + "01",
        format="%Y%m%d",
        errors="coerce",
    )

    canonical["completed_renewals"] = (
        canonical[RENEWED] + canonical[DISENROLLED]
    )

    canonical["disenrollment_rate_completed"] = np.where(
        canonical["completed_renewals"] > 0,
        canonical[DISENROLLED] / canonical["completed_renewals"],
        np.nan,
    )

    canonical["procedural_rate_completed"] = np.where(
        canonical["completed_renewals"] > 0,
        canonical[PROCEDURAL] / canonical["completed_renewals"],
        np.nan,
    )

    canonical["procedural_share_disenrolled"] = np.where(
        canonical[DISENROLLED] > 0,
        canonical[PROCEDURAL] / canonical[DISENROLLED],
        np.nan,
    )

    canonical["pending_share_due"] = np.where(
        canonical[DUE] > 0,
        canonical[PENDING] / canonical[DUE],
        np.nan,
    )

    return canonical.sort_values([STATE, PERIOD]).reset_index(drop=True)


def add_initial_unwinding_window(monthly):
    result = monthly.copy()

    eligible = result[
        result[DISENROLLED].notna()
        & result["completed_renewals"].gt(0)
        & result["reporting_date"].notna()
    ]

    starts = (
        eligible.groupby(STATE, as_index=False)["reporting_date"]
        .min()
        .rename(columns={"reporting_date": "unwinding_start"})
    )

    result = result.merge(starts, on=STATE, how="left")
    result["unwinding_end"] = (
        result["unwinding_start"] + pd.DateOffset(months=13)
    )

    result["initial_unwinding_window"] = (
        result["reporting_date"].ge(result["unwinding_start"])
        & result["reporting_date"].le(result["unwinding_end"])
    )

    return result


def summarize_state_exposure(monthly):
    window = monthly.loc[monthly["initial_unwinding_window"]].copy()

    grouped = (
        window.groupby([STATE, STATE_NAME], as_index=False)
        .agg(
            unwinding_start=("unwinding_start", "min"),
            unwinding_end=("unwinding_end", "max"),
            months_observed=(PERIOD, "nunique"),
            renewal_due=(DUE, "sum"),
            renewed=(RENEWED, "sum"),
            disenrolled=(DISENROLLED, "sum"),
            ineligible=(INELIGIBLE, "sum"),
            procedural=(PROCEDURAL, "sum"),
            pending=(PENDING, "sum"),
            completed_renewals=("completed_renewals", "sum"),
        )
    )

    grouped["disenrollment_rate_completed"] = np.where(
        grouped["completed_renewals"] > 0,
        grouped["disenrolled"] / grouped["completed_renewals"],
        np.nan,
    )

    grouped["procedural_rate_completed"] = np.where(
        grouped["completed_renewals"] > 0,
        grouped["procedural"] / grouped["completed_renewals"],
        np.nan,
    )

    grouped["procedural_share_disenrolled"] = np.where(
        grouped["disenrolled"] > 0,
        grouped["procedural"] / grouped["disenrolled"],
        np.nan,
    )

    grouped["pending_share_due"] = np.where(
        grouped["renewal_due"] > 0,
        grouped["pending"] / grouped["renewal_due"],
        np.nan,
    )

    return grouped.sort_values(STATE).reset_index(drop=True)


def validate_state_exposure(state):
    if state[STATE].duplicated().any():
        raise RuntimeError("State treatment summary contains duplicate states.")

    if len(state) < 50:
        raise RuntimeError("Treatment summary contains fewer than 50 states/DC.")

    rate_columns = [
        "disenrollment_rate_completed",
        "procedural_rate_completed",
        "procedural_share_disenrolled",
        "pending_share_due",
    ]

    for column in rate_columns:
        valid = state[column].dropna()
        if not valid.between(0, 1).all():
            raise RuntimeError(f"{column} contains values outside [0, 1].")

    if (state["procedural"] > state["disenrolled"]).any():
        raise RuntimeError(
            "Procedural disenrollments exceed total disenrollments."
        )

    if (state["months_observed"] > 14).any():
        raise RuntimeError("Initial unwinding window exceeds 14 months.")


def main():
    source = RAW / "cms_eligibility_processing.csv"
    if not source.exists():
        raise RuntimeError(
            "Missing CMS source file. Run "
            "python src/fetch_cms_eligibility_processing.py first."
        )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(source)
    monthly = canonicalize_monthly(raw)
    monthly = add_initial_unwinding_window(monthly)
    state = summarize_state_exposure(monthly)

    validate_state_exposure(state)

    monthly.to_csv(
        PROCESSED / "cms_renewal_monthly_canonical.csv",
        index=False,
    )
    state.to_csv(
        PROCESSED / "state_unwinding_exposure.csv",
        index=False,
    )

    summary = {
        "states": int(len(state)),
        "median_disenrollment_rate_completed": float(
            state["disenrollment_rate_completed"].median()
        ),
        "median_procedural_rate_completed": float(
            state["procedural_rate_completed"].median()
        ),
        "median_procedural_share_disenrolled": float(
            state["procedural_share_disenrolled"].median()
        ),
        "minimum_months_observed": int(state["months_observed"].min()),
        "maximum_months_observed": int(state["months_observed"].max()),
        "primary_treatment_candidate": "disenrollment_rate_completed",
        "window_definition": (
            "State-specific 14-month window beginning with the first "
            "reporting month containing completed renewal outcomes."
        ),
        "denominator_definition": (
            "completed_renewals = renewed + disenrolled; pending renewals "
            "are excluded from the primary treatment denominator."
        ),
    }

    (META / "treatment_exposure_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(
        "Built state unwinding exposure panel for "
        f"{len(state)} states/DC."
    )

    q = state["disenrollment_rate_completed"].quantile(
        [0.05, 0.25, 0.50, 0.75, 0.95]
    )

    print("Treatment exposure distribution:")
    print(
        "  5th={:.3f} 25th={:.3f} median={:.3f} "
        "75th={:.3f} 95th={:.3f}".format(
            q.loc[0.05],
            q.loc[0.25],
            q.loc[0.50],
            q.loc[0.75],
            q.loc[0.95],
        )
    )

    print("Highest disenrollment exposure states:")
    for _, row in state.nlargest(
        5, "disenrollment_rate_completed"
    ).iterrows():
        print(
            f"  {row[STATE]}: "
            f"{row['disenrollment_rate_completed']:.3f} "
            f"({int(row['months_observed'])} months)"
        )

    print("Lowest disenrollment exposure states:")
    for _, row in state.nsmallest(
        5, "disenrollment_rate_completed"
    ).iterrows():
        print(
            f"  {row[STATE]}: "
            f"{row['disenrollment_rate_completed']:.3f} "
            f"({int(row['months_observed'])} months)"
        )

    incomplete = state.loc[state["months_observed"].lt(14), [
        STATE,
        "months_observed",
        "disenrollment_rate_completed",
    ]]
    print(f"States with fewer than 14 observed months: {len(incomplete)}")
    if not incomplete.empty:
        print(incomplete.to_string(index=False))


if __name__ == "__main__":
    main()
