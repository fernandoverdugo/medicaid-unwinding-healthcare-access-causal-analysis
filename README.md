# Medicaid Unwinding & Healthcare Access — Causal Program Evaluation

A reproducible public-policy evaluation examining whether states with greater Medicaid disenrollment during the post-pandemic unwinding experienced larger changes in health-insurance coverage and healthcare access.

## Core question

**Did greater exposure to Medicaid unwinding disenrollment lead to measurable deterioration in insurance coverage or healthcare access?**

The project is designed around causal inference rather than prediction. Its central task is to estimate a counterfactual: how outcomes in more heavily affected states might have changed if their unwinding exposure had been lower.

## Why this project matters

The Medicaid continuous-enrollment provision ended on March 31, 2023, after three years in which states generally could not disenroll beneficiaries. States then resumed eligibility redeterminations and implemented the unwinding differently, producing substantial variation in disenrollment and procedural-termination rates.

That variation creates an opportunity to study whether administrative implementation translated into measurable downstream changes in coverage and access to care.

## Planned causal design

The primary design will use a **difference-in-differences / event-study framework** with state-level variation in unwinding exposure.

The analysis will distinguish:

- **pre-unwinding outcomes:** years before redeterminations resumed;
- **post-unwinding outcomes:** years after unwinding began;
- **higher-exposure states:** states with larger finalized disenrollment intensity;
- **lower-exposure states:** states with lower disenrollment intensity.

The final specification will be selected only after the treatment definition, outcome coverage, and identifying assumptions are validated.

## Planned outcomes

Primary outcomes will focus on measures plausibly downstream of Medicaid coverage loss:

- uninsured rate;
- Medicaid coverage rate;
- delayed or forgone care because of cost, where suitable state-level survey data are available;
- selected subgroup outcomes for low-income nonelderly adults.

## Causal-inference components

The finished analysis is expected to include:

- transparent treatment construction;
- pre/post descriptive trends;
- difference-in-differences estimates;
- event-study coefficients;
- state and time fixed effects;
- clustered standard errors;
- parallel-trends diagnostics;
- placebo / falsification tests;
- alternative treatment definitions;
- sensitivity and robustness checks;
- subgroup heterogeneity;
- explicit causal assumptions and limitations.

## Data sources

Planned authoritative sources include:

- **CMS** Medicaid unwinding and enrollment data;
- **U.S. Census Bureau** ACS coverage outcomes;
- potentially **NHIS or other federal survey data** where geographic detail supports valid state-level inference;
- policy/context documentation from CMS and other primary government sources.

KFF may be used for cross-checking and contextual interpretation, but the analytical pipeline will prioritize original federal data where feasible.

## Repository status

**Phase 5 — final synthesis and presentation**

Treatment construction and the ACS state-year outcome panel are complete. The primary treatment was locked before outcome estimation.

The preliminary continuous-exposure DiD estimate for a **10 percentage-point higher disenrollment rate** is **−0.095 percentage points** in the low-income adult uninsured rate (95% CI **−1.139 to +0.948 pp**, p = **0.858**).

This is **not yet presented as a definitive causal null**. The joint pre-trend test has p = **0.096**, and the 2021 event-study lead is statistically nonzero relative to 2022. The project therefore proceeds to robustness analysis rather than treating parallel trends as proven.

See [Treatment Audit](docs/TREATMENT_AUDIT.md), [Outcome Construction](docs/OUTCOME_CONSTRUCTION.md), and [Primary Results](docs/PRIMARY_RESULTS.md).

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

## Project roadmap

1. ~~Validate authoritative unwinding and outcome data sources.~~
2. ~~Build and audit the state-level unwinding treatment panel.~~
3. ~~Build state-level outcome panels.~~
4. ~~Produce pre-treatment trend diagnostics.~~
5. ~~Estimate the primary difference-in-differences specification.~~
6. ~~Run robustness, placebo, and sensitivity analyses.~~
7. **Synthesize findings and finalize interpretation.**
8. Publish a concise policy-evaluation dashboard or report.

## Repository structure

```text
.
├── config/                  # Analysis assumptions and planned specifications
├── data/
│   ├── raw/                 # Source data retained in original form when practical
│   ├── processed/           # Reproducible state-level analytical panels
│   └── metadata/            # Provenance and validation summaries
├── docs/
│   ├── RESEARCH_DESIGN.md   # Causal framework and identifying assumptions
│   └── DATA_PLAN.md         # Source, treatment, and outcome plan
├── src/                     # Ingestion, cleaning, estimation, and diagnostics
├── tests/                   # Data-contract and analysis tests
├── LICENSE
├── requirements.txt
└── README.md
```

## Reproduce treatment construction

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python src/fetch_cms_eligibility_processing.py
python src/build_unwinding_exposure.py
python -m pytest -q
python src/validate_config.py
```

The CMS ingestion step discovers the current CSV distribution from the Data.Medicaid.gov dataset metadata, with a documented September 2026 release URL as a fallback.

## Responsible interpretation

This project will not label a coefficient as causal merely because it comes from a difference-in-differences regression. Causal interpretation will depend on the plausibility of the identifying assumptions, especially comparable pre-treatment trends and the absence of major differential contemporaneous shocks.

## License

This project is licensed under the [MIT License](LICENSE).
