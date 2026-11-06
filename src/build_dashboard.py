import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "metadata"
OUT = ROOT / "site"


def load_json(name):
    return json.loads((META / name).read_text(encoding="utf-8"))


def pct(value):
    return f"{value * 100:.3f}"


def main():
    primary = load_json("primary_did_result.json")
    robustness = load_json("robustness_results.json")
    pretrend = load_json("pretrend_diagnostic.json")
    outcomes = load_json("outcome_panel_summary.json")
    event_study = load_json("event_study_result.json")

    spec = primary["specification"]
    effect = spec["effect_per_10pp_higher_exposure"]
    low, high = spec["ci_95_per_10pp_higher_exposure"]

    annual = outcomes["uninsured_rate_by_year"]

    rows = [
        ("Primary DiD", effect, spec["p_value"]),
        (
            "Population weighted",
            robustness["population_weighted"]["effect_per_10pp"],
            robustness["population_weighted"]["p_value"],
        ),
        (
            "Procedural exposure",
            robustness["procedural_exposure"]["effect_per_10pp"],
            robustness["procedural_exposure"]["p_value"],
        ),
        (
            "Placebo timing",
            robustness["placebo_timing"]["effect_per_10pp"],
            robustness["placebo_timing"]["p_value"],
        ),
        (
            "5th–95th percentile trim",
            robustness["trimmed_exposure_5_95"]["effect_per_10pp"],
            robustness["trimmed_exposure_5_95"]["p_value"],
        ),
        (
            "Exclude 2021 pre-period",
            robustness["exclude_2021_preperiod"]["effect_per_10pp"],
            robustness["exclude_2021_preperiod"]["p_value"],
        ),
        (
            "Exclude NC & SD expansion",
            robustness["exclude_2023_expansion_states"]["effect_per_10pp"],
            robustness["exclude_2023_expansion_states"]["p_value"],
        ),
    ]

    table_rows = "".join(
        f"<tr><td>{name}</td><td>{pct(value)} pp</td><td>{p:.3f}</td></tr>"
        for name, value, p in rows
    )

    annual_rows = "".join(
        f"<tr><td>{year}</td><td>{float(rate) * 100:.1f}%</td></tr>"
        for year, rate in annual.items()
    )

    event_rows = "".join(
        (
            f"<tr><td>{row['year']}</td><td>Reference</td><td>—</td></tr>"
            if row["reference"]
            else
            f"<tr><td>{row['year']}</td>"
            f"<td>{row['effect_per_10pp_exposure'] * 100:.3f} pp</td>"
            f"<td>{row['p_value']:.3f}</td></tr>"
        )
        for row in event_study["estimates"]
    )

    joint = pretrend["joint_pretrend_test"]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Medicaid Unwinding & Healthcare Access</title>
<style>
body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin:0; background:#f6f7f9; color:#1f2937; }}
main {{ max-width:1100px; margin:auto; padding:42px 22px 64px; }}
h1 {{ font-size:2.3rem; margin-bottom:8px; }}
h2 {{ margin-top:36px; }}
.lead {{ font-size:1.1rem; color:#4b5563; max-width:850px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:16px; margin:26px 0; }}
.card {{ background:white; padding:20px; border-radius:14px; box-shadow:0 1px 4px rgba(0,0,0,.08); }}
.kpi {{ font-size:1.8rem; font-weight:700; }}
.label {{ color:#6b7280; font-size:.9rem; }}
table {{ width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; }}
th,td {{ text-align:left; padding:12px 14px; border-bottom:1px solid #e5e7eb; }}
th {{ background:#eef1f5; }}
.callout {{ background:white; border-left:5px solid #6b7280; padding:18px 20px; margin:20px 0; }}
.small {{ color:#6b7280; font-size:.9rem; }}
a {{ color:inherit; }}
</style>
</head>
<body>
<main>
<h1>Medicaid Unwinding & Healthcare Access</h1>
<p class="lead">A state-level causal program evaluation testing whether greater Medicaid disenrollment exposure during the post-pandemic unwinding was associated with larger increases in the uninsured rate among low-income adults.</p>

<div class="grid">
<div class="card"><div class="label">Primary effect per +10 pp exposure</div><div class="kpi">{pct(effect)} pp</div></div>
<div class="card"><div class="label">95% confidence interval</div><div class="kpi">{pct(low)} to {pct(high)} pp</div></div>
<div class="card"><div class="label">Primary p-value</div><div class="kpi">{spec["p_value"]:.3f}</div></div>
<div class="card"><div class="label">State-year observations</div><div class="kpi">{spec["n_state_years"]}</div></div>
</div>

<div class="callout"><strong>Bottom line:</strong> higher state-level Medicaid unwinding disenrollment exposure was not associated with a robustly larger increase in the annual uninsured rate among low-income adults in 2024–2025. This does not imply that the unwinding had no national, short-term, subgroup, or administrative effects.</div>

<h2>Robustness results</h2>
<table>
<thead><tr><th>Specification</th><th>Effect per +10 pp exposure</th><th>p-value</th></tr></thead>
<tbody>{table_rows}</tbody>
</table>

<h2>Pre-treatment diagnostics</h2>
<div class="grid">
<div class="card"><div class="label">Joint pre-trend test p-value</div><div class="kpi">{joint["p_value"]:.3f}</div></div>
<div class="card"><div class="label">Exposure × 2018–2022 outcome-change correlation</div><div class="kpi">{pretrend["correlation_exposure_with_2018_2022_change"]:.3f}</div></div>
</div>
<p class="small">The pre-trend evidence is not perfectly clean; the project therefore treats the causal interpretation as qualified rather than conclusive.</p>

<h2>Event study</h2>
<p class="small">Year-specific exposure interactions relative to 2022. Pre-period estimates are diagnostics; 2023 is the transition year.</p>
<table>
<thead><tr><th>Year</th><th>Effect per +10 pp exposure</th><th>p-value</th></tr></thead>
<tbody>{event_rows}</tbody>
</table>

<h2>Median state uninsured rate</h2>
<table>
<thead><tr><th>Year</th><th>Median rate</th></tr></thead>
<tbody>{annual_rows}</tbody>
</table>

<h2>Methodology</h2>
<p>Primary treatment: disenrollments divided by completed renewal outcomes during each state's initial 14-month unwinding window. Primary outcome: ACS uninsured rate among adults ages 19–64 below 138% of the federal poverty threshold. The primary model uses state and year fixed effects with state-clustered standard errors; 2023 is treated as a transition year.</p>

<p class="small">
<a href="https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis">Repository</a> ·
<a href="https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/blob/main/docs/FINAL_REPORT.md">Final report</a> ·
<a href="https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/blob/main/docs/RESEARCH_DESIGN.md">Research design</a> ·
<a href="https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/blob/main/docs/ROBUSTNESS_RESULTS.md">Robustness</a>
</p>
</main>
</body>
</html>
"""

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("Built site/index.html")


if __name__ == "__main__":
    main()
