# Outcome Construction

## Primary outcome

The primary outcome is:

> **Uninsured rate among civilian noninstitutionalized adults ages 19–64 with family income below 138% of the federal poverty threshold.**

This population was selected because it is more directly relevant to Medicaid eligibility and redetermination than the overall uninsured rate.

## Source

U.S. Census Bureau American Community Survey, 1-Year Detailed Tables.

Primary table:

**C27016 — Health Insurance Coverage Status by Ratio of Income to Poverty Level in the Past 12 Months by Age**

The pipeline retrieves the state-level estimates directly from the Census Data API.

## Income definition

The outcome combines two C27016 poverty-ratio categories:

- under 1.00 of the poverty threshold;
- 1.00 to 1.37 of the poverty threshold.

Together, these represent income below 138% of poverty.

## Age definition

The analysis uses the table's **19 to 64 years** category.

## Outcome formula

```text
uninsured rate =
    uninsured adults ages 19–64 below 138% FPL
    -------------------------------------------
    all adults ages 19–64 below 138% FPL
```

Counts are summed across the two poverty-ratio categories before the rate is calculated.

## Analysis years

Primary panel:

- 2018
- 2019
- 2021
- 2022
- 2023
- 2024
- 2025

### Why 2020 is excluded

The Census Bureau did not release the standard 2020 ACS 1-year estimates. It released experimental 1-year estimates and explicitly advises users not to compare those experimental estimates with standard ACS 1-year products from other years.

Therefore, 2020 is omitted rather than treated as a normal pre-treatment observation.

## Treatment timing

- **Pre-treatment:** 2018, 2019, 2021, 2022
- **Transition:** 2023
- **Post-treatment:** 2024, 2025

2023 is not included in the primary post-treatment indicator because Medicaid unwinding began during the year and states started renewal cohorts at different times.

The 2023 estimate remains in the panel for descriptive and event-study interpretation.

## Validation

The outcome pipeline requires:

- one row per state-year;
- 51 jurisdictions in every included year;
- no missing primary outcome values;
- uninsured counts no larger than the relevant denominator;
- rates bounded between 0 and 1.

## Interpretation cautions

ACS health-insurance status is an annual survey measure, while Medicaid renewal activity occurred throughout the year.

The outcome therefore measures population-level insurance status, not a direct administrative count of people who lost Medicaid.

A change in the uninsured rate after unwinding can also reflect:

- transitions to employer coverage;
- ACA Marketplace enrollment;
- Medicaid re-enrollment;
- changes in income;
- migration;
- state policy changes;
- sampling variability.

For that reason, the causal design depends on comparative state trends, not on a simple before/after national change.
