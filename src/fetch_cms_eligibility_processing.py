import json
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"

DATASET_ID = "5abea2e0-3f8e-4b49-a50d-d63d5fd9103c"
METASTORE_URL = (
    "https://data.medicaid.gov/api/1/metastore/schemas/dataset/items/"
    + DATASET_ID
)
FALLBACK_URL = (
    "https://download.medicaid.gov/data/"
    "renewal-dataset-september-2026-release.csv"
)


def discover_download_url():
    response = requests.get(METASTORE_URL, timeout=60)
    response.raise_for_status()
    payload = response.json()

    for distribution in payload.get("distribution", []):
        if str(distribution.get("format", "")).lower() == "csv":
            url = distribution.get("downloadURL")
            if url:
                return url

    return FALLBACK_URL


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    url = discover_download_url()
    output = RAW / "cms_eligibility_processing.csv"

    response = requests.get(url, timeout=120)
    response.raise_for_status()
    output.write_bytes(response.content)

    frame = pd.read_csv(output)

    provenance = {
        "dataset_id": DATASET_ID,
        "source_url": url,
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "states": int(frame["State Abbreviation"].nunique()),
        "min_reporting_period": int(frame["Reporting Period"].min()),
        "max_reporting_period": int(frame["Reporting Period"].max()),
    }

    (META / "cms_eligibility_processing_provenance.json").write_text(
        json.dumps(provenance, indent=2),
        encoding="utf-8",
    )

    print(
        "Downloaded CMS eligibility processing data: "
        f"{len(frame):,} rows from {url}"
    )


if __name__ == "__main__":
    main()
