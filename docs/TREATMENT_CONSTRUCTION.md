# Medicaid Unwinding Treatment Construction

## Purpose

This document defines how the project converts CMS monthly renewal-processing data into state-level Medicaid unwinding exposure measures.

The treatment is constructed **before healthcare-access outcomes are estimated** so that treatment selection is not influenced by the eventual outcome results.

## Source

Primary source:

**Centers for Medicare & Medicaid Services — State Medicaid and CHIP Eligibility Processing Data**

The source reports monthly renewal outcomes for all states and the District of Columbia. CMS may publish both an original (`O`) and updated (`U`) record for a state-reporting-period.

## Canonical monthly record

For renewal outcomes, the pipeline gives priority to the updated record when one exists.

For each state and reporting month:

1. load original and updated reports separately;
2. use the updated value when present;
3. fall back to the original value when the updated report leaves a field blank;
4. retain one canonical state-month record.

This is necessary because CMS updated reports revise pending and completed renewal outcomes, while some fields are intentionally not repeated in updated submissions.

## Initial unwinding window

The primary exposure window is state-specific.

For each state:

1. identify the first reporting month containing a non-missing total disenrollment count and at least one completed renewal;
2. designate that month as the state's initial unwinding start;
3. include that month and the following 13 calendar months.

This produces a maximum 14-month initial window, reflecting the original federal unwinding framework under which states could initiate renewal cohorts at different times and were given up to 14 months to complete the initial renewal process.

Later renewal activity is retained in the canonical monthly file but is not included in the primary exposure measure.

## Primary denominator

The primary treatment denominator is:

```text
completed_renewals = renewed + disenrolled
```

rather than total renewals due.

This choice avoids mechanically classifying unresolved pending renewals as successful or unsuccessful renewal outcomes.

## Primary treatment candidate

```text
disenrollment_rate_completed =
    total disenrolled / completed renewals
```

Interpretation:

> Among renewals with a completed coverage outcome during the state's initial unwinding window, what share resulted in disenrollment?

## Secondary treatment measures

### Procedural disenrollment rate among completed renewals

```text
procedural_rate_completed =
    procedural disenrollments / completed renewals
```

This captures administrative loss of coverage when the state lacked sufficient information to complete an eligibility determination.

### Procedural share of disenrollments

```text
procedural_share_disenrolled =
    procedural disenrollments / total disenrollments
```

This distinguishes procedural terminations from determinations of substantive ineligibility.

### Pending share of renewals due

```text
pending_share_due =
    pending renewals / renewals due
```

This is treated as a process diagnostic rather than the primary treatment because pending renewals can reflect timing, mitigation strategies, processing backlogs, or reporting differences.

## Why counts are aggregated before rates

State-level exposure is constructed by summing the underlying beneficiary counts across the window and then calculating the rate.

The project does **not** average monthly percentages.

This gives months appropriate weight according to the number of completed renewals.

## Comparability cautions

CMS explicitly notes state-specific reporting differences and mitigation strategies that can affect comparisons.

Examples include:

- states delaying procedural terminations;
- differences in how ex parte renewals are classified;
- unusual pending-renewal patterns;
- state-specific reporting practices;
- revised outcome data.

These issues will be incorporated into the treatment audit and sensitivity analysis rather than ignored.

## Treatment selection rule

The current primary candidate is `disenrollment_rate_completed`.

It will become the final primary treatment only if the state-level audit shows:

- acceptable completeness;
- a meaningful cross-state distribution;
- interpretable variation;
- no small number of states dominating the measure;
- sufficient comparability for a program-evaluation design.

If these conditions fail, the project will change the design openly and document why rather than selecting a different exposure measure based on outcome significance.
