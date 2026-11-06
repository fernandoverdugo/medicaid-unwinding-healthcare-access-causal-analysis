import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_analysis_config_preserves_pre_post_ordering():
    config = json.loads(
        (ROOT / "config" / "analysis.json").read_text(encoding="utf-8")
    )
    assert max(config["pre_period_target"]) < config["transition_year"]
    assert min(config["post_period_target"]) > config["transition_year"]


def test_source_registry_contains_primary_sources():
    registry = json.loads(
        (ROOT / "data" / "metadata" / "source_registry.json").read_text(
            encoding="utf-8"
        )
    )
    source_ids = {row["source_id"] for row in registry["sources"]}
    assert "cms_eligibility_processing" in source_ids
    assert "cms_monthly_enrollment" in source_ids
    assert "acs_health_insurance" in source_ids
