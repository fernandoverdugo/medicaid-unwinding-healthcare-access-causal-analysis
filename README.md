# Medicaid Unwinding & Healthcare Access — Causal Program Evaluation

A reproducible public-policy causal evaluation examining whether states with greater Medicaid disenrollment during the post-pandemic unwinding experienced larger changes in the uninsured rate among low-income adults.

[![Quality checks](https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/actions/workflows/quality-checks.yml)
[![Pages](https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/actions/workflows/pages.yml/badge.svg)](https://github.com/fernandoverdugo/medicaid-unwinding-healthcare-access-causal-analysis/actions/workflows/pages.yml)

**Live dashboard:** https://fernandoverdugo.github.io/medicaid-unwinding-healthcare-access-causal-analysis/

**Final report:** [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md)

## Core question

**Did greater exposure to Medicaid unwinding disenrollment lead to measurable deterioration in insurance coverage or healthcare access?**

The project is designed around causal inference rather than prediction. Its central task is to estimate a counterfactual: how outcomes in more heavily affected states might have changed if their unwinding exposure had been lower.

## Why this project matters

The Medicaid continuous-enrollment provision ended on March 31, 2023, after three years in which states generally could not disenroll beneficiaries. States then resumed eligibility redeterminations and implemented the unwinding differently, producing substantial variation in disenrollment and procedural-termination rates.

That variation creates an opportunity to study whether administrative implementation translated into measurable downstream changes in coverage and access to care.

## Study design

The final design is a **continuous-exposure difference-in-differences model** with a complementary event study.

- **Treatment:** state disenrollment rate among completed Medicaid renewal outcomes during each state's initial 14-month unwinding window
- **Primary outcome:** ACS uninsured rate among adults ages 19–64 below 138% of the federal poverty threshold
- **Pre-period:** 2018, 2019, 2021, 2022
- **Transition year:** 2023
- **Post-period:** 2024, 2025
- **Inference:** state and year fixed effects with standard errors clustered by state
- **Scope:** 50 states plus the District of Columbia

The treatment definition was audited and locked before outcome estimation. The primary specification uses continuous exposure rather than an arbitrary high/low cutoff.

## Key finding

For every **10 percentage-point higher Medicaid disenrollment exposure**, the estimated differential post-period change in the low-income adult uninsured rate was:

> **−0.095 percentage points**  
> 95% CI: **−1.139 to +0.948 pp**  
> p = **0.858**

The evidence does not show a robustly larger increase in annual uninsured rates in higher-exposure states. This is **not** evidence that the unwinding had no national, short-duration, subgroup, or administrative effects.

## Data sources

- **Centers for Medicare & Medicaid Services (CMS):** monthly Medicaid and CHIP eligibility-processing / renewal outcomes
- **U.S. Census Bureau ACS 1-Year Table-Based Summary Files:** table C27016 for insurance coverage by poverty ratio and age
- **Primary-source policy documentation:** used for timing and sensitivity decisions, including contemporaneous Medicaid expansion changes

## Methods demonstrated

Difference-in-differences, continuous treatment exposure, event-study diagnostics, state/year fixed effects, clustered inference, placebo timing, population-weighted estimation, alternative treatment definitions, exposure trimming, leave-one-state-out analysis, policy-confounding exclusions, reproducible data ingestion, automated validation, pytest, and GitHub Actions.

## Repository status

**Analysis complete.**

Treatment construction, outcome construction, pre-trend diagnostics, the primary DiD, event study, placebo tests, and robustness analyses are implemented and reproducible.

The result is intentionally described as a **qualified causal evaluation** rather than a definitive causal null because the pre-treatment evidence is not perfectly clean: the joint pre-trend test has p = **0.096**, and the 2021 event-study lead is statistically nonzero relative to 2022.

See [Research Design](docs/RESEARCH_DESIGN.md), [Treatment Audit](docs/TREATMENT_AUDIT.md), [Outcome Construction](docs/OUTCOME_CONSTRUCTION.md), [Primary Results](docs/PRIMARY_RESULTS.md), [Robustness Results](docs/ROBUSTNESS_RESULTS.md), and the [Final Report](docs/FINAL_REPORT.md).

## Robustness snapshot

The primary result remains small and statistically nonsignificant across the main sensitivity checks:

| Check | Effect per 10 pp higher exposure | p-value |
| --- | ---: | ---: |
| Primary DiD | −0.095 pp | 0.858 |
| Population weighted | −0.256 pp | 0.668 |
| Procedural disenrollment exposure | −0.012 pp | 0.984 |
| Placebo timing | −0.310 pp | 0.593 |
| 5th–95th percentile treatment trim | −0.491 pp | 0.440 |
| Excluding 2021 pre-period | −0.015 pp | 0.978 |
| Excluding NC & SD expansion states | −0.052 pp | 0.914 |
| High-vs-low median split | +0.069 pp | 0.944 |

Leave-one-state-out estimates range from **−0.298 to +0.147 pp**, indicating that no single state drives the result.

See [Robustness & Sensitivity Results](docs/ROBUSTNESS_RESULTS.md) for interpretation and remaining identification cautions.

## Repository structure

```text
.
├── config/                  # Analysis assumptions and planned specifications
├── data/
│   ├── raw/                 # Source data retained in original form when practical
│   ├── processed/           # Reproducible state-level analytical panels
│   └── metadata/            # Provenance and validation summaries
├── docs/                    # Research design, construction notes, results, final report
├── src/                     # Ingestion, cleaning, estimation, diagnostics, dashboard
├── tests/                   # Data-contract and estimation tests
├── LICENSE
├── requirements.txt
└── README.md
```

## Reproduce the full analysis

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python src/fetch_cms_eligibility_processing.py
python src/build_unwinding_exposure.py
python src/fetch_acs_outcomes.py
python src/build_outcome_panel.py
python src/pretrend_diagnostic.py
python src/estimate_primary_did.py
python src/event_study.py
python src/robustness_checks.py
python src/build_dashboard.py

python -m pytest -q
python src/validate_config.py
```

The pipeline retrieves current authoritative source files, reconstructs the analytical panels, reruns the causal models and robustness checks, and builds the policy-facing dashboard.

## Responsible interpretation

This project will not label a coefficient as causal merely because it comes from a difference-in-differences regression. Causal interpretation will depend on the plausibility of the identifying assumptions, especially comparable pre-treatment trends and the absence of major differential contemporaneous shocks.

## License

This project is licensed under the [MIT License](LICENSE).
