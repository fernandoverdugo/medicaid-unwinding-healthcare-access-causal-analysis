import json
from io import StringIO
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"

YEARS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]

STATE_NAMES = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

COLUMN_MAP = {
    "under_100_total_19_64": "C27016_E006",
    "under_100_uninsured_19_64": "C27016_E008",
    "fpl_100_137_total_19_64": "C27016_E016",
    "fpl_100_137_uninsured_19_64": "C27016_E018",
}


def summary_file_url(year):
    filename = f"acsdt1y{year}-c27016.dat"

    if year <= 2019:
        return (
            "https://www2.census.gov/programs-surveys/acs/summary_file/"
            f"{year}/prototype/1YRData/{filename}"
        )

    return (
        "https://www2.census.gov/programs-surveys/acs/summary_file/"
        f"{year}/table-based-SF/data/1YRData/{filename}"
    )


def fetch_year(year):
    url = summary_file_url(year)
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    frame = pd.read_csv(
        StringIO(response.text),
        sep="|",
        dtype=str,
    )

    legacy_renames = {
        "C27016_006E": "C27016_E006",
        "C27016_008E": "C27016_E008",
        "C27016_016E": "C27016_E016",
        "C27016_018E": "C27016_E018",
        "#GEO_ID": "GEO_ID",
        "GEOID": "GEO_ID",
        "GEOIDFQ": "GEO_ID",
    }
    frame = frame.rename(
        columns={
            old: new
            for old, new in legacy_renames.items()
            if old in frame.columns and new not in frame.columns
        }
    )

    required = {"GEO_ID", *COLUMN_MAP.values()}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(
            f"{year} C27016 summary file missing columns: "
            + ", ".join(sorted(missing))
            + f"; observed columns={frame.columns[:12].tolist()}"
        )

    state_rows = frame.loc[
        frame["GEO_ID"].str.match(r"^0400000US\d{2}$", na=False)
    ].copy()

    state_rows["state"] = state_rows["GEO_ID"].str[-2:]
    state_rows = state_rows.loc[
        state_rows["state"].isin(STATE_NAMES)
    ].copy()

    if len(state_rows) != 51:
        raise RuntimeError(
            f"{year} state table returned {len(state_rows)} states/DC."
        )

    for column in COLUMN_MAP.values():
        state_rows[column] = pd.to_numeric(
            state_rows[column],
            errors="coerce",
        )

    state_rows["year"] = year
    state_rows["NAME"] = state_rows["state"].map(STATE_NAMES)

    total_columns = [
        COLUMN_MAP["under_100_total_19_64"],
        COLUMN_MAP["fpl_100_137_total_19_64"],
    ]
    uninsured_columns = [
        COLUMN_MAP["under_100_uninsured_19_64"],
        COLUMN_MAP["fpl_100_137_uninsured_19_64"],
    ]

    state_rows["low_income_adults_19_64"] = state_rows[
        total_columns
    ].sum(axis=1, min_count=2)

    state_rows["uninsured_low_income_adults_19_64"] = state_rows[
        uninsured_columns
    ].sum(axis=1, min_count=2)

    state_rows["uninsured_rate_low_income_adults_19_64"] = (
        state_rows["uninsured_low_income_adults_19_64"]
        / state_rows["low_income_adults_19_64"]
    )

    keep = [
        "year",
        "state",
        "NAME",
        "low_income_adults_19_64",
        "uninsured_low_income_adults_19_64",
        "uninsured_rate_low_income_adults_19_64",
    ]

    return state_rows[keep], url


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    frames = []
    provenance = {
        "dataset": "ACS 1-Year Table-Based Summary File",
        "table": "C27016",
        "years": YEARS,
        "columns": COLUMN_MAP,
        "excluded_years": {
            "2020": (
                "Census released experimental 2020 ACS 1-year estimates "
                "and advises against comparison with standard ACS years."
            )
        },
        "year_sources": {},
    }

    for year in YEARS:
        frame, url = fetch_year(year)
        frames.append(frame)
        provenance["year_sources"][str(year)] = {"url": url}

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(
        ["state", "year"]
    ).reset_index(drop=True)

    output = RAW / "acs_low_income_adult_uninsured_state_year.csv"
    combined.to_csv(output, index=False)

    provenance["row_count"] = int(len(combined))
    provenance["states_per_year"] = {
        str(year): int(
            combined.loc[combined["year"].eq(year), "state"].nunique()
        )
        for year in YEARS
    }

    (
        META / "acs_outcome_provenance.json"
    ).write_text(
        json.dumps(provenance, indent=2),
        encoding="utf-8",
    )

    print(
        "Downloaded ACS low-income adult insurance outcomes: "
        f"{len(combined):,} state-year rows."
    )

    for year in YEARS:
        annual = combined.loc[combined["year"].eq(year)]
        print(
            f"  {year}: {len(annual)} states/DC, "
            f"median uninsured rate="
            f"{annual['uninsured_rate_low_income_adults_19_64'].median():.3f}"
        )


if __name__ == "__main__":
    main()
