import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "analysis.json"
SOURCES = ROOT / "data" / "metadata" / "source_registry.json"


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    required_config = {
        "project",
        "analysis_level",
        "pre_period_target",
        "transition_year",
        "post_period_target",
        "primary_treatment_candidate",
        "primary_outcome_candidate",
        "cluster_level",
        "primary_design",
        "secondary_design",
        "causal_label_requires_diagnostics",
    }

    missing = required_config - set(config)
    if missing:
        raise RuntimeError(
            "Missing required analysis configuration fields: "
            + ", ".join(sorted(missing))
        )

    if config["analysis_level"] not in {"state_year", "state_month"}:
        raise RuntimeError("Unsupported analysis level.")

    if config["primary_design"] != "difference_in_differences":
        raise RuntimeError("Primary design must remain difference-in-differences.")

    if config["secondary_design"] != "event_study":
        raise RuntimeError("Secondary design must remain event-study.")

    if not config["causal_label_requires_diagnostics"]:
        raise RuntimeError(
            "Causal interpretation must remain conditional on diagnostics."
        )

    if max(config["pre_period_target"]) >= config["transition_year"]:
        raise RuntimeError("Pre-period years overlap the transition year.")

    if min(config["post_period_target"]) <= config["transition_year"]:
        raise RuntimeError("Post-period years must follow the transition year.")

    source_rows = sources.get("sources", [])
    source_ids = {row["source_id"] for row in source_rows}

    required_sources = {
        "cms_eligibility_processing",
        "cms_monthly_enrollment",
        "acs_health_insurance",
    }

    if not required_sources.issubset(source_ids):
        raise RuntimeError("Authoritative source registry is incomplete.")

    for row in source_rows:
        for key in ["source_id", "agency", "name", "url", "role", "notes"]:
            if not row.get(key):
                raise RuntimeError(
                    f"Source {row.get('source_id', '<unknown>')} is missing {key}."
                )

    print("Causal analysis configuration validation passed.")


if __name__ == "__main__":
    main()
