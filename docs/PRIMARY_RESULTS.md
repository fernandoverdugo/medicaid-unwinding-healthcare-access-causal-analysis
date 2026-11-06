# Primary Difference-in-Differences Results

## Status

**Primary estimate finalized; interpretation remains qualified by pre-trend diagnostics.**

The primary continuous-exposure difference-in-differences model uses treatment and outcome definitions that were locked before outcome estimation. The estimate has since been stress-tested with weighting, placebo timing, alternative exposure measures, exposure trimming, policy-confounding exclusions, binary exposure, exclusion of the 2021 pre-period observation, and leave-one-state-out analysis.

See [Robustness & Sensitivity Results](ROBUSTNESS_RESULTS.md) for the completed checks.

## Primary specification

Outcome:

> Uninsured rate among civilian noninstitutionalized adults ages 19–64 with family income below 138% of the federal poverty threshold.

Treatment:

> State Medicaid unwinding disenrollment rate among completed renewal outcomes during the state's initial 14-month unwinding window.

Primary panel:

- pre-period: 2018, 2019, 2021, 2022;
- transition year: 2023, excluded from the primary pre/post interaction;
- post-period: 2024, 2025;
- 51 states/DC;
- 306 state-year observations in the primary DiD model.

Specification:

```text
outcome_st =
    state fixed effects
  + year fixed effects
  + β(unwinding exposure_s × post_t)
  + error_st
```

Standard errors are clustered by state.

## Primary estimate

For a **10 percentage-point higher Medicaid disenrollment exposure**:

| Estimate | Result |
| --- | ---: |
| Differential post-period change | **−0.095 percentage points** |
| 95% CI | **−1.139 to +0.948 pp** |
| p-value | **0.858** |

The estimate is close to zero and statistically imprecise.

Under the identifying assumptions, this model does not provide evidence that states with greater unwinding disenrollment exposure experienced systematically larger increases in the low-income adult uninsured rate during 2024–2025.

That statement should not be interpreted as proof of no effect.

## Pre-treatment diagnostics

Using 2018 as the reference year, the exposure-by-year pre-period estimates were:

| Year | Coefficient per unit exposure | SE | p-value |
| --- | ---: | ---: | ---: |
| 2018 | Reference | — | — |
| 2019 | 0.0306 | 0.0255 | 0.230 |
| 2021 | 0.0239 | 0.0598 | 0.689 |
| 2022 | −0.0552 | 0.0727 | 0.448 |

Joint test that all three pre-treatment exposure interactions equal zero:

- statistic: **6.338**
- p-value: **0.096**

Correlation between unwinding exposure and the state's 2018–2022 outcome change:

- **−0.160**

These diagnostics do not show a strong monotonic pre-trend, but the joint test is close enough to conventional thresholds that the parallel-trends assumption should not be treated as established.

## Event study

The event study uses 2022 as the reference year and reports the estimated difference associated with a 10 percentage-point higher unwinding exposure.

| Year | Effect | 95% CI | p-value |
| --- | ---: | ---: | ---: |
| 2018 | +0.552 pp | −0.783 to +1.887 | 0.417 |
| 2019 | +0.858 pp | −0.329 to +2.046 | 0.156 |
| 2021 | **+0.791 pp** | **+0.084 to +1.498** | **0.028** |
| 2022 | Reference | — | — |
| 2023 | +0.062 pp | −0.305 to +0.429 | 0.742 |
| 2024 | +0.534 pp | −0.167 to +1.235 | 0.135 |
| 2025 | +0.376 pp | −0.439 to +1.191 | 0.366 |

The statistically nonzero 2021 lead is a reason for caution. A single significant pre-period coefficient does not automatically invalidate a design, particularly with multiple comparisons and a disrupted pandemic-era time series, but it does weaken a simple claim that higher- and lower-exposure states followed perfectly parallel pre-treatment paths.

## National descriptive pattern

The median state uninsured rate for the target low-income adult population was:

| Year | Median state rate |
| --- | ---: |
| 2018 | 18.8% |
| 2019 | 20.1% |
| 2021 | 18.1% |
| 2022 | 16.8% |
| 2023 | 16.6% |
| 2024 | 18.2% |
| 2025 | 20.0% |

The national descriptive increase after 2023 should not be confused with the DiD estimate. The causal design asks whether states with **greater unwinding exposure changed more than states with lower exposure**, not whether uninsured rates rose nationally.

## Current interpretation

The current evidence supports a restrained conclusion:

> Low-income adult uninsured rates increased nationally after the unwinding transition, but the primary state-level continuous-exposure model does not show that states with higher Medicaid disenrollment exposure experienced a reliably larger post-period increase. Because pre-treatment diagnostics are not perfectly clean, robustness analysis is required before interpreting the near-zero DiD coefficient causally.

## Robustness status

The planned robustness work is complete. Across all major sensitivity checks, estimates remain small and statistically nonsignificant. The final interpretation is documented in [FINAL_REPORT.md](FINAL_REPORT.md).

