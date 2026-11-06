# Treatment Exposure Audit

## Decision

**Primary treatment locked:** `disenrollment_rate_completed`

The treatment is defined as:

```text
total disenrollments during the state's initial unwinding window
----------------------------------------------------------------
renewed coverage + total disenrollments during the same window
```

The denominator therefore includes completed renewal outcomes only. Pending renewals are excluded from the primary treatment measure.

## Data audited

The live CMS pipeline retrieved the October 2026 release of the State Medicaid and CHIP Eligibility Processing Data.

The treatment build produced a complete state-level exposure panel for:

- 50 states;
- District of Columbia;
- 51 total jurisdictions.

Every jurisdiction had the full 14-month initial unwinding window required by the treatment definition.

## Exposure distribution

Across 51 states/DC:

| Percentile | Disenrollment rate among completed renewals |
| --- | ---: |
| 5th | 13.9% |
| 25th | 24.6% |
| Median | 30.7% |
| 75th | 38.6% |
| 95th | 52.5% |

The interquartile range is approximately 14 percentage points, providing meaningful cross-state variation without requiring an extreme-value design.

## Highest-exposure states

| State | Exposure |
| --- | ---: |
| Utah | 53.9% |
| Montana | 53.3% |
| Oklahoma | 52.6% |
| Texas | 52.5% |
| Idaho | 51.6% |

All five states had the full 14-month observation window.

## Lowest-exposure states

| State | Exposure |
| --- | ---: |
| Maine | 8.1% |
| North Carolina | 12.7% |
| Virginia | 13.2% |
| Oregon | 14.5% |
| California | 17.6% |

All five states had the full 14-month observation window.

## Completeness

**States with fewer than 14 observed months: 0**

This removes one major comparability concern: the exposure ranking is not being driven by states observed for systematically shorter treatment windows.

## Why the treatment survives the audit

The primary treatment candidate was retained because it meets the pre-specified criteria:

- complete coverage across all 51 jurisdictions;
- meaningful cross-state variation;
- no dependence on incomplete state windows;
- interpretable policy meaning;
- denominator based on completed renewal outcomes rather than unresolved cases;
- variation is not concentrated in a single state or tiny cluster.

## Remaining cautions

The treatment is still not randomly assigned.

States with high disenrollment rates may systematically differ from low-disrollment states in:

- Medicaid expansion history;
- renewal automation;
- procedural safeguards;
- state administrative capacity;
- labor-market conditions;
- demographics;
- other contemporaneous coverage policies.

These differences are identification risks, not reasons to discard the treatment measure.

The outcome analysis must therefore include:

- pre-treatment trend diagnostics;
- event-study estimates;
- state and time fixed effects;
- clustered standard errors;
- sensitivity to alternative exposure definitions;
- exclusion/sensitivity checks for states with major contemporaneous coverage-policy changes;
- population-weighted and unweighted specifications.

## Treatment-classification strategy

The preferred primary specification will use the **continuous exposure rate** rather than converting states into arbitrary treatment/control groups.

A high-versus-low treatment split may be used as a secondary specification for interpretability, but the threshold will not replace the continuous primary design.

This choice preserves more information and avoids making the result depend on a single categorical cutoff.

## Audit conclusion

The state-level Medicaid unwinding exposure measure is sufficiently complete, variable, and interpretable to proceed to outcome-panel construction.

The treatment definition is now considered **pre-outcome locked**. Changes to the primary treatment after outcome estimation begins must be documented as sensitivity or alternative specifications rather than silently replacing the primary measure.
