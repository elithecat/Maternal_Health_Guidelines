# Coding protocol: study design and sample size of citations supporting ACOG CPG No. 5

Source guideline: ACOG Clinical Practice Guideline No. 5, *Treatment and Management of Mental Health Conditions During Pregnancy and Postpartum* (Obstet Gynecol 2023;141:1262–88).

Each citation that ACOG uses in the evidence summary of a recommendation is coded **once, as a document**: classify what the cited paper *is* and what its *primary analysis* does, not how ACOG used it. Code only from the paper file in `0_Data/papers/` (metadata, abstract, and full text when present). Do not use web search or recall of the paper from memory. If the file does not let you determine a field, say so (`Unclear` / `null`) and lower your confidence.

## Fields

| Field | Allowed values | Notes |
|---|---|---|
| `ref_id` | as given | ACOG reference number; `T2x` = Table 2 footnote; `F1` = Figure 1/2 source |
| `evidence_basis` | `full_text`, `abstract_only`, `citation_only` | What the file contains |
| `study_type` | one code from the list below | Primary design of the paper's main analysis |
| `design_detail` | short text | e.g., "Retrospective cohort, US Medicaid claims, propensity-score stratification" |
| `severity_adjustment` | `Yes`, `No`, `Unclear`, `NA` | See definition below. `NA` for anything that is not a non-randomized comparison (RCTs, reviews, case reports, PK studies, guidelines) |
| `severity_measure` | short text or empty | What severity measure(s) entered the adjustment, or why `No`/`Unclear` |
| `sibling_analysis_any` | `Yes`, `No`, `Unclear` | Any sibling / within-mother / family-fixed-effects analysis, primary or sensitivity |
| `comparison_group` | short text | e.g., "Pregnant women with depression, unexposed"; "Placebo"; "None" |
| `population` | short text | e.g., "Pregnant women in US Medicaid, 2000–2010" |
| `perinatal_population` | `Yes`, `No`, `Mixed` | Pregnant/postpartum/lactating people or their offspring = `Yes` |
| `review_component_designs` | `RCTs only`, `Observational only`, `Mixed`, `Not stated`, `NA` | For systematic reviews/meta-analyses only |
| `n_studies` | integer or `null` | Systematic reviews/meta-analyses only: number of included studies |
| `sample_size_n` | integer or `null` | Total N in the primary analysis, in the paper's unit of analysis. For reviews: total pooled participants if reported, otherwise `null` |
| `sample_size_unit` | e.g., `women`, `pregnancies`, `infants`, `mother-infant pairs`, `participants`, `clinicians`, `cases` | Unit for `sample_size_n` |
| `sample_size_detail` | short text | Exposed/comparison counts, randomized vs analyzed, etc. |
| `sample_size_source` | `full_text`, `abstract`, `not_reported` | Where the N came from |
| `confidence` | `High`, `Medium`, `Low` | Your confidence in `study_type`, `severity_adjustment`, and `sample_size_n` together |
| `rationale` | 1–3 sentences | Key evidence for the classification; brief quotes (under 15 words) allowed |

## `study_type` codes

Pick exactly one. Work down the list and take the first code that fits the paper's **primary** analysis.

1. **`RCT`**: participants randomly assigned to intervention/comparator (individual, cluster, crossover, or pilot RCT). Secondary analyses that preserve the randomized comparison also count. A non-randomized secondary analysis of trial data is observational.
2. **`Sibling/within-family`**: the main estimate comes from a within-family contrast (exposure-discordant siblings, within-mother comparison across pregnancies, family fixed effects). If siblings are only a sensitivity analysis, code the main design and set `sibling_analysis_any = Yes`.
3. **`Observational – adjusted, incl. severity`**: a non-randomized comparison with adjustment for measured confounders (regression, propensity score, matching, stratification, weighting). The adjustment set includes a measure of severity of the underlying condition (see definition below).
4. **`Observational – adjusted, excl. severity`**: the same, but no severity measure. Adjustment, restriction, or matching on the diagnosis *alone* does **not** count as severity.
5. **`Observational – unadjusted/descriptive`**: cohort, case-control, cross-sectional, registry, or prevalence analyses with crude comparisons only, or purely descriptive.
6. **`Quasi-experimental (other)`**: designs that rely on plausibly exogenous variation: instrumental variables, regression discontinuity, difference-in-differences with a comparison group, interrupted time series. A pre/post comparison without a concurrent control is **not** quasi-experimental; code it 3, 4, or 5 depending on its adjustment.
7. **`Systematic review/meta-analysis`**: systematic review, meta-analysis, network meta-analysis, pooled/IPD analysis of multiple studies, Cochrane review, evidence report (for example AHRQ).
8. **`Pharmacokinetic/physiologic`**: drug concentrations, clearance, placental passage, breast-milk or infant serum levels, dose-requirement studies without a confounder-adjusted clinical outcome comparison.
9. **`Case report/case series`**: one or more exposed cases described without a comparison group.
10. **`Survey/qualitative/program evaluation`**: clinician or patient surveys, qualitative interviews or focus groups, program utilization or quality reports without a comparative effect estimate.
11. **`Narrative review/commentary`**: non-systematic review, clinical overview, editorial, commentary, "how I treat."
12. **`Guideline/consensus statement`**: clinical practice guideline, recommendation statement, practice bulletin, position statement, practice parameter.
13. **`Protocol/design paper`**: study protocol or rationale-and-design article with no results.
14. **`Not a study (resource)`**: website, registry homepage, training program, diagnostic manual, regulatory notice.
15. **`Other`**: anything else. Explain in `rationale`.

## Definition: severity of the underlying condition

This review focuses on depression severity. The construct is **severity of the indication for treatment**, because that is the confounder that separates treated from untreated people beyond the diagnosis itself. Count it as `severity_adjustment = Yes` when the analysis adjusts, matches, stratifies, or weights on any of the following:

- a symptom-severity score (e.g., EPDS, PHQ-9, HAM-D, BDI) or a clinician-rated severity;
- claims- or registry-based severity proxies, for example psychiatric hospitalization, ED visits for the condition, number of psychiatric outpatient visits, number of psychotropic drug classes, prior suicide attempt, duration or number of episodes, or a composite labeled as severity;
- for non-depression indications, the analogous severity measure for that condition (e.g., seizure type or frequency for epilepsy, illness course or prior episodes for bipolar disorder).

Code `No` when the analysis adjusts only for demographics, obstetric or medical factors, and/or the *presence* of a psychiatric diagnosis. Code `Unclear` when adjustment exists but the covariate list is not available (common with abstract-only files). If the analysis restricts to people with the diagnosis and also adjusts for severity proxies, code `Yes`.

## Sample size rules

- Report the N of the **primary analysis** (analytic sample), not the source population, unless only the latter is given (say so in `sample_size_detail`).
- RCTs: number randomized; give the number analyzed in `sample_size_detail` if it differs.
- Case reports: number of cases.
- Reviews: `n_studies` plus pooled participants in `sample_size_n` if reported.
- Guidelines, narrative reviews, protocols, resources: `null`.
- Write integers without commas (e.g., `3789330`).

## Output format

A JSON array with one object per assigned `ref_id`, using exactly the field names above. Use strings for categorical fields, integers or `null` for counts.

## Amendment 1 (issued during coding, applied to all raters)

- **Adjusted analysis, severity not determinable** (typically abstract-only files): code `study_type = Observational – adjusted, excl. severity` and `severity_adjustment = Unclear`. Severity counts as included only when the file shows it. The compiled spreadsheet reports these separately as "adjusted, severity unclear."
- **Adjustment status itself not determinable** (an abstract reports ORs/HRs but never says whether they are adjusted, controlled, or matched): code `study_type = Observational – unadjusted/descriptive`, `severity_adjustment = Unclear`, `confidence = Low`. Use `Observational – adjusted, excl. severity` only when the file explicitly reports adjustment, matching, or "controlling for" covariates. The compiled spreadsheet reports these as "adjustment unclear."
- **Ref 82** (Byatt 2012, J Reprod Infant Psychol) is not indexed in PubMed. An earlier version of its file held the wrong abstract; code it from the citation only (`evidence_basis = citation_only`).

## Amendment 2 (PI decisions, 2026-10-13, after first-round adjudication)

1. **Sibling analysis is determined from the full text.** Don't infer it from an abstract's silence. With full text, code `Yes` if any sibling/within-mother/family-fixed-effects analysis is reported, otherwise `No`. If the full text can't be obtained, code `Unclear` and flag the citation for library retrieval.
2. **Sample size = the N behind the main estimate:** the analytic sample of the paper's primary (fully adjusted, if adjusted) effect estimate. Not the source cohort, and not a broader descriptive sample. When the main estimate is restricted (e.g., to women with depression), use the restricted N. Give the source-cohort N in `sample_size_detail`.
3. **An author's explicit statement that the analysis controlled for illness severity counts as `severity_adjustment = Yes`**, even if the measures aren't itemized. Quote the statement in `severity_measure`.
