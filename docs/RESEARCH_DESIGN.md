# Research Design

## Evaluation question

Did greater state-level exposure to Medicaid disenrollment during the post-pandemic unwinding cause measurable deterioration in health-insurance coverage or healthcare access?

## Policy setting

The pandemic-era Medicaid continuous-enrollment requirement ended on March 31, 2023. States then resumed eligibility redeterminations and disenrollments. Implementation varied substantially across states in timing, renewal processes, ex parte renewal capacity, procedural disenrollment, and overall disenrollment intensity.

This variation is policy-relevant, but it is not automatically random. The design therefore treats identification as the central analytical problem rather than assuming that cross-state differences are causal.

## Unit of analysis

The preferred unit is a **state-year panel** for survey outcomes, supplemented by **state-month administrative data** for treatment construction and descriptive timing.

A state-month outcome panel may be used where an outcome is available at sufficient monthly frequency.

## Primary treatment concept

The preferred exposure measure is a finalized state-level unwinding intensity measure constructed from authoritative administrative data.

Candidate measures:

1. cumulative disenrollments divided by completed renewals;
2. procedural disenrollments divided by completed renewals;
3. net Medicaid/CHIP enrollment decline relative to the pre-unwinding baseline;
4. categorical high/medium/low exposure based on a pre-specified distributional rule.

The project will not select a treatment definition because it produces the strongest result. The primary measure will be chosen based on policy interpretation, completeness, and measurement quality before outcome estimation.

## Primary outcome concept

The preferred primary outcome is the **uninsured rate among low-income nonelderly adults**.

Secondary outcomes may include:

- Medicaid coverage rate;
- uninsured rate among children;
- cost-related delayed care;
- cost-related forgone care;
- healthcare access measures available consistently across states and time.

## Baseline difference-in-differences model

A first-pass binary exposure specification is:

```text
Y_st = α_s + λ_t + β(HighExposure_s × Post_t) + X_stγ + ε_st
```

where:

- `Y_st` is the outcome for state `s` in year `t`;
- `α_s` are state fixed effects;
- `λ_t` are year fixed effects;
- `HighExposure_s` identifies states above a pre-specified unwinding-intensity threshold;
- `Post_t` identifies the post-unwinding period;
- `X_st` contains a limited set of pre-specified time-varying covariates where justified;
- standard errors are clustered at the state level.

A continuous-exposure model may be estimated as a robustness specification.

## Event-study model

The event study will estimate year-specific treatment effects relative to a pre-treatment reference year.

Its primary purpose is diagnostic:

- assess pre-treatment coefficient behavior;
- visualize dynamic post-treatment effects;
- identify anticipation or divergence before unwinding.

The absence of individually significant pre-period coefficients will not by itself be treated as proof of parallel trends.

## Identification assumptions

A causal interpretation requires, at minimum:

### Parallel trends

In the absence of differential unwinding exposure, higher- and lower-exposure states would have experienced comparable changes in the outcome.

This will be assessed using multiple pre-period years and event-study coefficients.

### No differential contemporaneous shock

No other state-level policy or economic change should differentially affect higher-exposure states at the same time in a way that explains the estimated effect.

Potential confounders include:

- Medicaid expansion changes;
- state eligibility changes;
- ACA Marketplace policy differences;
- state economic conditions;
- major immigration or demographic changes;
- state-specific healthcare reforms.

### Stable treatment measurement

Administrative treatment measures must reflect comparable concepts across states. Differences in reporting practices will be documented and, where necessary, states with materially non-comparable data will be excluded in sensitivity analyses.

### No outcome-driven treatment construction

Treatment intensity will be defined without reference to downstream outcome estimates.

## Main diagnostics

The project will include:

- treatment-distribution audit;
- missingness audit;
- pre-period trend plots;
- event-study estimates;
- state-clustered uncertainty;
- alternative treatment thresholds;
- leave-one-state-out sensitivity;
- exclusion of states with major contemporaneous Medicaid expansion changes;
- placebo treatment dates;
- alternative outcome definitions where available;
- population-weighted and unweighted specifications.

## Heterogeneity

Subgroup analyses will be limited and pre-specified to reduce specification searching.

Priority subgroups:

- adults ages 19–64;
- low-income adults;
- children;
- Medicaid-expansion versus non-expansion states, if sample support is adequate.

## Interpretation standard

The project will distinguish among:

- **descriptive evidence**: observed changes and cross-state differences;
- **associational estimates**: adjusted relationships that do not satisfy a convincing causal design;
- **causal estimates**: effects supported by a defensible counterfactual design and robustness evidence.

If the parallel-trends or comparability evidence is weak, the final project will explicitly downgrade the causal interpretation rather than overstate the result.
