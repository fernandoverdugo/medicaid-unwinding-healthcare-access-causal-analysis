# Final Policy Evaluation Summary

## Question

Did states with greater Medicaid disenrollment during the post-pandemic unwinding experience larger increases in the uninsured rate among low-income adults?

## Design

This project uses a state-level continuous-exposure difference-in-differences design.

### Treatment

The primary treatment is the **disenrollment rate among completed renewal outcomes** during each state's initial 14-month unwinding window.

The treatment was constructed and audited before outcome estimation.

### Outcome

The primary outcome is the uninsured rate among civilian noninstitutionalized adults ages 19–64 with family income below 138% of the federal poverty threshold, derived from ACS table C27016.

### Time periods

- Pre-treatment: 2018, 2019, 2021, 2022
- Transition: 2023
- Post-treatment: 2024, 2025
- 2020 excluded because the standard ACS 1-year estimates were not released

## Main result

The primary estimate is:

> **−0.095 percentage points** in the low-income adult uninsured rate for every **10 percentage-point higher Medicaid disenrollment exposure**.

95% CI:

> **−1.139 to +0.948 percentage points**

p-value:

> **0.858**

The estimate is close to zero and statistically imprecise.

## What this means

The analysis does **not** find evidence that states with higher measured Medicaid unwinding disenrollment exposure experienced systematically larger post-unwinding increases in the annual uninsured rate among low-income adults.

That is not the same as concluding that the Medicaid unwinding caused no harm or had no effect.

The design is specifically testing **cross-state differential change**. A national effect shared broadly across states would not necessarily appear as a positive treatment coefficient.

## Descriptive context

Median state uninsured rates for the target population were:

- 2018: 18.8%
- 2019: 20.1%
- 2021: 18.1%
- 2022: 16.8%
- 2023: 16.6%
- 2024: 18.2%
- 2025: 20.0%

The descriptive rise after 2023 is real in the state medians, but it should not be confused with the causal estimate.

## Identification diagnostics

The pre-treatment evidence is reasonably stable but not perfect.

- Joint pre-trend test: p = 0.096
- Exposure correlation with 2018–2022 outcome change: −0.160
- 2021 event-study lead relative to 2022: statistically nonzero

Because of that 2021 lead, the project does not claim that the parallel-trends assumption is conclusively established.

## Robustness

The main result remains small and nonsignificant across multiple checks:

| Specification | Effect | p-value |
| --- | ---: | ---: |
| Primary DiD | −0.095 pp | 0.858 |
| Population weighted | −0.256 pp | 0.668 |
| Procedural disenrollment exposure | −0.012 pp | 0.984 |
| Placebo timing | −0.310 pp | 0.593 |
| 5th–95th percentile treatment trim | −0.491 pp | 0.440 |
| Excluding 2021 pre-period | −0.015 pp | 0.978 |
| Excluding NC & SD 2023 expansion states | −0.052 pp | 0.914 |
| High-vs-low median split | +0.069 pp | 0.944 |

Leave-one-state-out estimates range from −0.298 to +0.147 percentage points.

## Interpretation

The strongest defensible conclusion is:

> **Higher state-level Medicaid unwinding disenrollment exposure was not associated with a robustly larger increase in the annual uninsured rate among low-income adults in 2024–2025, relative to lower-exposure states.**

This conclusion is supported by consistent null-like estimates across weighting, alternative treatment definitions, placebo timing, exposure trimming, policy-confounding exclusions, and leave-one-state-out checks.

## Important limitations

This analysis cannot rule out:

- a national effect common to most states;
- short-duration coverage gaps between annual ACS measurements;
- effects on children or other subgroups;
- transitions from Medicaid to Marketplace or employer coverage;
- administrative burden not captured by annual uninsured status;
- heterogeneous effects within states;
- residual state-level confounding;
- pandemic-era disruptions to pre-treatment trends.

## Portfolio value

This project demonstrates:

- causal research design;
- treatment construction from administrative data;
- outcome construction from ACS micro-aggregates;
- difference-in-differences;
- event-study diagnostics;
- clustered inference;
- placebo testing;
- robustness analysis;
- policy-confounding sensitivity;
- reproducible data pipelines;
- CI-tested analytical workflows;
- disciplined interpretation of null and non-null evidence.
