import json
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"

YEARS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]
GROUP = "C27016"


VARIABLES = {
    "under_100_total_19_64": "C27016_006E",
    "under_100_uninsured_19_64": "C27016_008E",
    "fpl_100_137_total_19_64": "C27016_016E",
    "fpl_100_137_uninsured_19_64": "C27016_018E",
}


def group_metadata(year):
    url = (
        f"https://api.census.gov/data/{year}/acs/acs1/groups/"
        f"{GROUP}.json"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json(), url


def validate_variable_labels(year, variables):
    expected = {
        "C27016_006E": [
            "Under 1.00 of poverty threshold",
            "19 to 64 years",
        ],
        "C27016_008E": [
            "Under 1.00 of poverty threshold",
            "19 to 64 years",
            "No health insurance coverage",
        ],
        "C27016_016E": [
            "1.00 to 1.37 of poverty threshold",
            "19 to 64 years",
        ],
        "C27016_018E": [
            "1.00 to 1.37 of poverty threshold",
            "19 to 64 years",
            "No health insurance coverage",
        ],
    }

    for name, required_tokens in expected.items():
        label = variables[name]["label"].replace(":", "")
        for token in required_tokens:
            if token not in label:
                raise RuntimeError(
                    f"{year} {name} label does not match contract: {label}"
                )


def variables_for_year(year):
    metadata, metadata_url = group_metadata(year)
    variables = metadata["variables"]
    validate_variable_labels(year, variables)

    return {
        "metadata_url": metadata_url,
        "groups": {
            "Under 1.00 of poverty threshold": {
                "total": VARIABLES["under_100_total_19_64"],
                "uninsured": VARIABLES["under_100_uninsured_19_64"],
            },
            "1.00 to 1.37 of poverty threshold": {
                "total": VARIABLES["fpl_100_137_total_19_64"],
                "uninsured": VARIABLES["fpl_100_137_uninsured_19_64"],
            },
        },
    }


def fetch_year(year):
    mapping = variables_for_year(year)
    variable_names = ["NAME"]

    for group in mapping["groups"].values():
        variable_names.extend(
            [group["total"], group["uninsured"]]
        )

    variable_names = list(dict.fromkeys(variable_names))

    base_url = f"https://api.census.gov/data/{year}/acs/acs1"
    params = {
        "get": ",".join(variable_names),
        "for": "state:*",
    }

    response = requests.get(base_url, params=params, timeout=60)
    response.raise_for_status()

    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            f"Census API returned non-JSON content for {year}: "
            f"{response.text[:300]}"
        ) from exc

    api_url = response.url

    frame = pd.DataFrame(payload[1:], columns=payload[0])
    frame["year"] = year

    total_columns = [
        group["total"] for group in mapping["groups"].values()
    ]
    uninsured_columns = [
        group["uninsured"] for group in mapping["groups"].values()
    ]

    for column in total_columns + uninsured_columns:
        frame[column] = pd.to_numeric(
            frame[column],
            errors="coerce",
        )

    frame["low_income_adults_19_64"] = frame[
        total_columns
    ].sum(axis=1, min_count=len(total_columns))

    frame["uninsured_low_income_adults_19_64"] = frame[
        uninsured_columns
    ].sum(axis=1, min_count=len(uninsured_columns))

    frame["uninsured_rate_low_income_adults_19_64"] = (
        frame["uninsured_low_income_adults_19_64"]
        / frame["low_income_adults_19_64"]
    )

    keep = [
        "year",
        "state",
        "NAME",
        "low_income_adults_19_64",
        "uninsured_low_income_adults_19_64",
        "uninsured_rate_low_income_adults_19_64",
    ]

    return frame[keep], mapping, api_url


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    frames = []
    provenance = {
        "dataset": "ACS 1-Year Detailed Tables",
        "group": GROUP,
        "years": YEARS,
        "excluded_years": {
            "2020": (
                "Census released experimental 2020 ACS 1-year estimates "
                "and advises against comparison with standard ACS years."
            )
        },
        "year_sources": {},
    }

    for year in YEARS:
        frame, mapping, api_url = fetch_year(year)
        frames.append(frame)
        provenance["year_sources"][str(year)] = {
            "api_url": api_url,
            "metadata_url": mapping["metadata_url"],
            "variables": mapping["groups"],
        }

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
