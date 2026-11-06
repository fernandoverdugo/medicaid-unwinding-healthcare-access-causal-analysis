# Data Plan

## Objective

Build a reproducible state-level panel connecting Medicaid unwinding exposure to insurance-coverage and healthcare-access outcomes.

## Treatment data

### Preferred source: CMS

Use Centers for Medicare & Medicaid Services administrative data for state-level unwinding renewal outcomes and Medicaid/CHIP enrollment.

Target fields include:

- state;
- reporting month;
- renewals due;
- completed renewals;
- renewed coverage;
- total disenrollments;
- procedural disenrollments;
- ex parte renewals where available;
- Medicaid/CHIP enrollment.

The pipeline should retain source-period and revision information because monthly unwinding reports may have been updated after initial publication.

### Cross-check: KFF

KFF's archived Medicaid Enrollment and Unwinding Tracker may be used to:

- validate state totals;
- reconcile timing differences;
- understand state-specific reporting caveats;
- compare finalized cumulative metrics.

KFF-derived values should not silently replace federal source data.

## Outcome data

### Primary candidate: American Community Survey

The ACS is the preferred source for state-level insurance outcomes because it supports comparable state estimates and relevant demographic/economic subgroup definitions.

Planned measures:

- uninsured rate;
- Medicaid/public coverage rate;
- subgroup rates for nonelderly adults and low-income populations where feasible.

Potential years should provide multiple pre-period observations and at least one clean post-unwinding observation.

### Secondary healthcare-access outcomes

Healthcare-access outcomes such as delayed or forgone care because of cost will be added only if the chosen federal survey provides:

- sufficient state identifiers;
- consistent measures across the study period;
- adequate sample size;
- appropriate survey design information.

No outcome will be added solely to increase the number of analyses.

## Covariates

Candidate state-year covariates will be limited to variables with a clear confounding rationale, such as:

- unemployment rate;
- poverty rate;
- Medicaid expansion status;
- demographic composition;
- other major coverage-policy changes.

The preferred specification will avoid high-dimensional adjustment.

## Geographic scope

Target: 50 states plus the District of Columbia, subject to treatment-data comparability.

Exclusions must be rule-based and documented.

Potential exclusion reasons:

- non-comparable unwinding reporting;
- unresolved missing treatment values;
- major treatment-definition ambiguity;
- insufficient outcome data.

## Time scope

The final time window will be determined by outcome availability.

Desired structure:

- at least 3 pre-treatment years;
- unwinding transition period beginning in 2023;
- at least 1–2 post-treatment years where survey data permit.

## Derived treatment measures

Candidate derived fields:

```text
disenrollment_rate =
    disenrollments / completed_renewals

procedural_rate_completed =
    procedural_disenrollments / completed_renewals

procedural_share_disenrolled =
    procedural_disenrollments / disenrollments

net_enrollment_change =
    (post_enrollment - baseline_enrollment) / baseline_enrollment
```

Each denominator will be documented explicitly.

## Data validation

Automated checks should verify:

- unique state-period keys;
- valid state codes;
- expected date coverage;
- nonnegative counts;
- numerator <= relevant denominator;
- rates constrained to logical bounds;
- missingness by state and period;
- treatment source provenance;
- outcome-year completeness;
- no accidental duplicates after joins.

## Reproducibility

Raw downloads should be preserved where licensing and file size permit.

Every processed analytical file should be reproducible from source data through scripts under `src/`.

A metadata manifest should record:

- source URL;
- source agency;
- retrieval date;
- file name;
- period covered;
- checksum where practical;
- transformation script.
