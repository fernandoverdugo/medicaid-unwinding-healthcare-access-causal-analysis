# Robustness & Sensitivity Results

## Summary

The primary continuous-exposure difference-in-differences estimate is small, statistically imprecise, and remains qualitatively similar across multiple sensitivity checks.

Primary estimate:

- **−0.095 percentage points** in the low-income adult uninsured rate per 10 percentage-point higher unwinding disenrollment exposure;
- 95% CI: **−1.139 to +0.948 pp**;
- p = **0.858**.

The robustness results do not reveal a hidden large positive effect that is being masked by the primary specification.

## Completed checks

| Specification | Effect per 10 pp higher exposure | p-value |
| --- | ---: | ---: |
| Primary unweighted DiD | **−0.095 pp** | 0.858 |
| Population-weighted DiD | **−0.256 pp** | 0.668 |
| Procedural disenrollment exposure | **−0.012 pp** | 0.984 |
| Placebo 2021–2022 treatment timing | **−0.310 pp** | 0.593 |
| 5th–95th percentile exposure trim | **−0.491 pp** | 0.440 |

None of these specifications produces a statistically distinguishable treatment effect.

## Population weighting

The population-weighted model gives:

> **−0.256 pp** per 10 percentage-point higher disenrollment exposure, p = **0.668**.

Giving greater weight to states with larger low-income adult populations does not materially change the conclusion.

## Alternative treatment: procedural disenrollment

Replacing total disenrollment exposure with the procedural disenrollment rate among completed renewals gives:

> **−0.012 pp**, p = **0.984**.

This is particularly informative because procedural terminations are more directly tied to administrative renewal processes than substantive ineligibility determinations.

The result remains essentially zero.

## Placebo timing

A false post period was assigned to 2021–2022 within the pre-treatment years.

Placebo estimate:

> **−0.310 pp**, p = **0.593**.

The placebo does not produce a statistically significant treatment effect.

This is reassuring, although it does not eliminate the pre-trend concerns identified in the event study.

## Exposure trimming

States outside the 5th–95th percentile of the treatment distribution were excluded.

Trimmed estimate:

> **−0.491 pp**, p = **0.440**.

Removing the most extreme treatment-exposure states does not reverse the result or generate a statistically significant effect.

## Leave-one-state-out sensitivity

The primary model was re-estimated 51 times, excluding one jurisdiction at a time.

The estimated effect per 10 percentage-point higher exposure ranged from:

> **−0.298 pp to +0.147 pp**

Most negative estimate:

- excluding **North Carolina**: −0.298 pp

Most positive estimate:

- excluding **South Dakota**: +0.147 pp

No single state is responsible for the primary near-zero estimate.

## Contemporaneous Medicaid expansion sensitivity

North Carolina and South Dakota are treated as important policy-confounding cases because both implemented ACA Medicaid expansion during 2023:

- South Dakota expansion effective **July 1, 2023**;
- North Carolina expansion effective **December 1, 2023**.

Because those expansions directly affect insurance coverage among low-income adults, a specification excluding both states is included in the robustness pipeline.

This exclusion is policy-driven and was not selected based on whether it strengthens the treatment estimate.

## Binary exposure sensitivity

The robustness pipeline also includes a secondary high-versus-low exposure specification based on the median treatment rate.

The continuous treatment specification remains primary because it preserves more information and avoids making the result depend on a single cutoff.

The binary model is included only as an interpretability check.

## What the robustness results support

The completed checks support the following statement:

> Across weighting choices, alternative treatment definitions, placebo timing, exposure trimming, and leave-one-state-out analyses, there is no evidence of a robust positive relationship between greater state Medicaid unwinding disenrollment exposure and larger post-unwinding increases in the uninsured rate among low-income adults.

That is narrower than saying the unwinding had no effect.

The design estimates whether **states with greater measured disenrollment exposure experienced larger changes than states with lower exposure**. It cannot rule out:

- a national effect shared across states;
- effects on populations not captured by the ACS outcome;
- short-duration coverage disruptions between annual ACS measurements;
- effects offset by Marketplace or employer coverage transitions;
- heterogeneous effects within states;
- administrative harms not expressed as annual uninsured status.

## Remaining identification caution

The pre-treatment evidence is not perfectly clean.

The joint pre-trend test has p = **0.096**, and the 2021 event-study coefficient is statistically nonzero relative to 2022.

For that reason, the final project should describe the evidence as a **carefully qualified causal evaluation** rather than claiming that the parallel-trends assumption has been conclusively established.

## Next checks

Remaining high-value analyses are:

1. final policy-confounding exclusion for 2023 expansion states;
2. median high-versus-low exposure sensitivity;
3. alternative pre-period specifications;
4. alternative outcome definitions where available;
5. a final results visualization and policy-facing summary.
