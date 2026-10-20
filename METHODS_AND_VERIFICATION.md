# Evidence behind ACOG CPG No. 5: methods and human-verification plan

**Guideline:** ACOG Clinical Practice Guideline No. 5, *Treatment and Management of Mental Health Conditions During Pregnancy and Postpartum*, Obstet Gynecol 2023;141:1262–88.
**Question:** For each recommendation, what kinds of studies does ACOG cite (RCTs, sibling designs, observational studies adjusted for observables with or without depression severity) and how large are they?
**Status:** AI-coded; not yet verified by a human. Prepared 2026-10-13.

## Where things are

| Path | Contents |
|---|---|
| `0_Data/citation_map.json` | 17 recommendations → 126 unique citations (137 rec–citation links), with PMID/PMCID/DOI and full-text status |
| `0_Data/papers/` | One markdown file per citation: ACOG citation as printed, PubMed metadata and abstract, and full text with tables when available |
| `0_Data/missing_full_text.md` | The 99 citations without stored full text, grouped by reason, with links |
| `0_Data/raw_xml/` | PubMed and PMC XML exactly as downloaded |
| `coding_protocol.md` | The codebook all raters and the judge followed (with Amendment 1) |
| `1_Scripts/` | Pipeline: parse references → map citations to recommendations → fetch papers → batch → find disagreements → build spreadsheets |
| `2_Output/Rater{1,2,3}_coding.xlsx` | Each rater's codes for all 126 citations |
| `2_Output/Judge_adjudication.xlsx` | Adjudicated disagreements, plus the judge's spot-check of unanimous comparative studies |
| `2_Output/Compiled_evidence_coding.xlsx` | Final codes, recommendation-level summary, rater comparison, and the human-verification worksheet |

---

## Methods

### 1. Project setup
The request was to start from the CLAUDE.md in the "setup" GitHub repo. No such file was reachable. The public `abilinski/claude-code-docker-setup` repo has only an example inside its README. The `elithecat` account has CLAUDE.md files in five project repos but no setup repo; a private one would return 404 (as `elithecat/setup` does), and this machine has no GitHub credentials. I followed the folder convention from `elithecat/SA_Prep_Power` (`0_Data/`, `1_Scripts/`, numbered outputs), which matches the requested `0_Data`. **Open item:** send the intended CLAUDE.md and I'll reconcile the project against it.

### 2. Recommendations and their citations
- I extracted the PDF text column by column (pdfplumber) because the two-column layout scrambles plain extraction. Output: `0_Data/acog_cpg5_text_by_column.txt`.
- I located 17 recommendation statements in "Clinical Recommendations and Evidence Summary": 14 graded and 3 Good Practice Points.
- A script (`rec_cites.py`) took every in-text citation number between one recommendation statement and the next. I then checked each list by hand against the text. One false positive was removed: "(3)" in the GPP1 section is a list marker, not reference 3.
- Two citation sources sit outside the numbered list:
  - Table 2, which the SSRI-for-depression recommendation (R7) cites. Its 9 footnote references were added to R7; 7 are new, and 2 duplicate refs 104 and 110.
  - The Lifeline for Moms toolkit, the source for Figures 1–2, which illustrate R3. Added to R3.
- Result: 126 unique citations and 137 rec–citation links. R7 (29 citations), R12 (27) and R11 (24) carry the most.

### 3. Matching citations to PubMed (PubMed MCP)
- **`convert_article_ids` (DOI → PMID/PMCID):** resolved 37 citations. This tool only returns PMIDs for articles deposited in PMC.
- **`lookup_article_by_citation` (author/journal/year/volume/first page):** resolved the rest. Before lookup I corrected errors in ACOG's reference list itself, all recorded in `citation_map.json → acog_citation_error`:
  - Ref 94 omits the journal (JAMA).
  - Refs 131 and 137 give an erratum's year and pages instead of the article's.
  - Refs 162 and 166 have the wrong year.
  - Ref 168 carries ref 169's DOI.
  - Refs 146 and 169 use ScienceDirect volume numbers.
- **`search_articles`:** resolved the leftovers. One ambiguous match was settled by DOI. The AHRQ evidence report (ref 52) and NICE CG192 (ref 76) were matched to their NCBI Bookshelf PubMed records.
- **Check:** for every match, I compared the PubMed title words with the ACOG citation. This caught one false match: the lookup had paired ref 82 (Byatt 2012, *J Reprod Infant Psychol*) with a different Byatt 2012 paper. That journal's 2012 issues aren't in PubMed, so ref 82 is now citation-only. The raters who had its file were told mid-coding.
- **Final:** 113 of 126 citations are in PubMed. The other 13 are web pages, DSM-5-TR, FDA notices, a registry, professional position statements, or the ref 82 paper.

### 4. Retrieving papers
- **PubMed records:** for all 113, fetched from NCBI E-utilities (title, abstract, publication types, MeSH, PMCID).
- **Full text:** PMC JATS XML from NCBI E-utilities, with Europe PMC as a fallback. I didn't use the MCP's `get_full_text_article` for storage, for two reasons: its text drops every table (and tables hold covariate lists and analytic Ns), and it came back empty for the publisher-restricted and scanned records I tested.
- **Conversion:** each XML record became markdown with sections, tables, and figure captions.
- **What we have:**

| Status | n |
|---|---|
| Full text stored (PMC) | 27 |
| In PMC, but the publisher blocks machine download (readable on the PMC website) | 11 |
| PubMed record only (abstract; some letters have no abstract) | 73 |
| NCBI Bookshelf report (AHRQ ref 52, NICE ref 76) | 2 |
| Not indexed in PubMed | 13 |

Everything without full text is listed with links in `0_Data/missing_full_text.md`.

### 5. Coding
- **Protocol:** `coding_protocol.md` defines 15 mutually exclusive `study_type` codes, taken in a fixed decision order. The four the request asked about come first:
  - RCT
  - sibling/within-family
  - observational, adjusted for observables, **including** severity of the underlying condition
  - observational, adjusted for observables, **excluding** it

  The rest cover quasi-experimental, unadjusted/descriptive, systematic review, pharmacokinetic, case report, survey/qualitative, narrative review, guideline, protocol, resource, and other.
- **Severity:** counts as included when the analysis uses a symptom score or a claims or registry severity proxy (psychiatric hospitalization, visit counts, number of psychotropic classes, and so on). Adjusting or restricting on the diagnosis alone doesn't count. For non-depression indications, the analogous severity measure applies (e.g., seizure type for epilepsy).
- **Other fields:** whether any sibling analysis appears, comparison group, population, review component designs, number of studies, N (with unit and source), confidence, and rationale.
- **Raters:** three raters, Claude Opus 5.5 subagents, each coded all 126 citations. To keep each one's reading manageable, every rater ran as three instances with identical instructions over three size-balanced batches of 42, for nine runs in total. Raters worked only from the paper files: no web search, no recall of the paper from memory. They were told not to open other raters' outputs.
- **Amendment 1 (mid-coding):** the first finished batches showed the protocol didn't say what to do when the file doesn't show the covariates. Two default rules were added and sent to all nine runs, including the four already finished, which re-checked their codes:
  - (a) adjustment is stated but severity can't be seen → "adjusted, excl. severity" + severity `Unclear`;
  - (b) it isn't stated whether estimates are adjusted → "unadjusted/descriptive" + severity `Unclear` + Low confidence.

  The compiled sheet keeps these apart as "adjusted, severity unclear" and "adjustment unclear."

### 6. Agreement and adjudication
- **What counts as a disagreement:** a citation is disputed if the raters differ on `study_type`, `severity_adjustment`, or `sibling_analysis_any`, or if their Ns are more than 10% apart (or one is missing). For reviews, the number of included studies is also compared.
- **Judge:** a separate Claude Opus 5.5 agent, not one of the raters, re-read each disputed paper and set the final value for every disputed field. It recorded which rater it sided with and why, and flagged items for human review.
- **Spot-check:** the judge also spot-checked every unanimously coded comparative study (RCT or adjusted observational, 19 citations). Here it could flag but not change codes.
- **Final values:** the unanimous value, or the judge's value on disputed fields. Where raters agreed on N within 10%, the final N is the median of the three.

**Inter-rater agreement (126 citations):**

| Field | % agreement | Fleiss' κ |
|---|---|---|
| Study type | 96.8 | 0.976 |
| Severity adjustment | 96.0 | 0.938 |
| Any sibling analysis | 93.7 | 0.614 |
| Sample size (±10%) | 99.2 | — |

16 citations had at least one disagreement. Sibling analysis had the lowest agreement (κ = 0.61). Every rater coded near-identical abstract-only register studies both `No` and `Unclear`.

**Adjudication:** the judge made 18 decisions on disputed fields across the 16 citations. It went with the rater majority 14 times and with a minority rater 4 times (refs 58, T2i and 148 on sibling; 141 on severity), and never chose a value no rater gave. It flagged all 16 for human review, mainly because 15 of them are abstract- or citation-only.

**Spot-check:** of the 19 unanimously coded comparative studies, the judge agreed with 16 and disputed 3, and flagged 9. As the protocol requires, the spot-check changed no codes; the disputes are flagged for a human:
- **T2a** (Huybrechts 2014): N should be the depression-restricted analytic sample (217,342) rather than the full cohort (949,504). That would match the convention the raters used for ref 110.
- **145, 150:** sibling analysis should be `Unclear`, not `No`, for abstract-only cohorts of births to mothers with epilepsy.

### 7. Flags for human review
A citation is flagged (yellow in the spreadsheets) when any of these holds:
- the judge flagged it, in adjudication or in the spot-check;
- the judge overrode a 2-rater majority;
- the raters split three ways on study type;
- the raters were unanimous but one reported Low confidence;
- it is a comparative study coded without full text;
- its PubMed title matches the ACOG citation poorly.

**34 of 126 citations are flagged.** Most are comparative or observational studies coded from abstracts.

### 8. Preliminary results (unverified)
Final codes for the 126 citations:

| Final code | n |
|---|---|
| RCT | 5 |
| Sibling/within-family | 0 |
| Observational, adjusted, **incl.** severity | 8 |
| Observational, adjusted, **excl.** severity | 3 |
| Observational, adjusted, severity unclear | 7 |
| Observational, adjustment unclear | 11 |
| Observational, unadjusted/descriptive | 7 |
| Systematic review/meta-analysis | 30 |
| Non-comparative (guidelines, narrative reviews, PK, case reports, surveys, resources, other) | 55 |

What stands out:
- **Very few RCTs.** Only 2 are perinatal: the postpartum sertraline trials under R7 (refs 115, 116). The other 3 test quetiapine/lithium in general-population bipolar depression (R11).
- **No sibling designs.** No citation uses a sibling or within-family design as its main analysis. None has a confirmed sibling sensitivity analysis either (11 are `Unclear`).
- **Severity adjustment is concentrated in R7.** Six of the 8 severity-adjusted studies support R7. Five are claims-based cohorts using severity proxies (refs 110, T2a, T2c, T2d, T2f). The sixth, ref 58, is abstract-only, and its severity code rests on the authors' claim. The other two are ref 95 (R5) and ref 142 (R11).
- **R12 rests on older observational data.** R12 (valproate, 27 citations) has no full text stored and no severity-adjusted study. Its support is case reports, descriptive cohorts, and epilepsy cohorts whose adjustment can't be verified from the abstracts.

Recommendation-level counts are in the `Rec_summary` sheet.

### Decisions for the PI before human verification
The judge raised three points of protocol interpretation. Settle them first, as Amendment 2:
1. **Sibling field when an abstract is silent.** The judge proposes `Unclear` unless the design rules out a within-family comparison (RCT, case report, cross-sectional, unrelated case-control, first pregnancies only). This would change several unanimous `No` codes, e.g., 127, 141, 145, 150, 151, 152, 166.
2. **N convention for restricted cohorts.** Should N be the full source cohort or the diagnosis-restricted sample behind the main adjusted estimate? Refs 110 and T2a currently disagree (739,114 restricted vs 949,504 full).
3. **Severity from an author's claim.** Ref 58 states it controlled for "maternal illness severity" without naming the measures. Under a strict reading of the protocol, it would be "adjusted, severity unclear."

## Limitations, in order of importance

1. **The raters are not independent the way human raters are.** All three are the same model reading the same file, so they make the same mistakes. On derived numbers (for example, an analytic N computed by subtracting an exclusion), all three often gave the identical figure. Read κ ≈ 0.98 as *consistency*, not as confirmation that the codes are right. A wrong code all three share produces no disagreement and never reaches the judge, which is why the judge spot-checks unanimous comparative studies and why the human audit below samples unflagged items too. A cheap improvement would be a fourth rater from a different model family.
2. **Most coding rests on abstracts.** Only 27 of 126 citations have stored full text. For abstract-only observational studies, the severity call, and sometimes even whether the estimates are adjusted, often can't be made; those are coded `Unclear` and flagged. The 11 PMC-restricted papers and most of the 73 abstract-only ones can be read through a university library.
3. **"Severity" for non-depression topics** (valproate in epilepsy, lithium, antipsychotics) was read as severity of that indication. That is a judgment call the user may want to revisit.
4. **The unit of analysis differs across studies** (pregnancies, women, infants, admissions, studies), so Ns aren't comparable across rows. The recommendation summary gives the median and maximum N among comparative studies only, and never sums them.
5. **Reviews are coded as reviews.** Systematic reviews and meta-analyses (30 citations) weren't unpacked into their component studies, so a recommendation backed mainly by meta-analyses of observational data shows few RCTs here even if a review contains some.
6. **The citation-to-recommendation mapping follows where ACOG put each citation in the text.** Some citations supply background (prevalence, risks of untreated illness) rather than evidence for the recommendation's claim. That distinction isn't coded.

---

## Plan for human verification

### Goal
Do three things at once:
- estimate how accurate the AI coding is;
- correct errors where they matter most (the comparative studies that drive the RCT / sibling / severity-adjusted counts);
- confirm the upstream steps (citation mapping, PMID matches) that everything else depends on.

### Who
Two people with training in epidemiology or biostatistics:
- **Reviewer A** is primary and reviews every item in the worksheet.
- **Reviewer B** independently double-codes a 30% random subset. That yields a human–human agreement benchmark against which to judge the AI–human agreement.

Both need university library access for the full texts that aren't stored here.

### What they work from
- The `Human_verification` sheet in `2_Output/Compiled_evidence_coding.xlsx`. Green columns are for reviewer input.
- `coding_protocol.md` and the paper files in `0_Data/papers/`.

### Step 0: calibration (≈1 hour, both reviewers)
- Both read `coding_protocol.md`.
- Each independently codes five practice citations, one per major type: one RCT, one adjusted cohort with severity proxies, one abstract-only cohort, one systematic review, and one case series.
- Discuss differences, and write down any rule clarifications as Amendment 2 before starting.

### Step 1: upstream checks (≈45 minutes, Reviewer A)
1. **Citation mapping.** For each of the 17 recommendations, read the ACOG evidence section (PDF pp. 1269–81) and confirm that the reference list in the `Rec_x_Citation` sheet is complete and correct, including the Table 2 footnotes under R7.
2. **PMID matches.** Open the PubMed link for every citation flagged with a title mismatch, plus a random 10% of the rest. Confirm that title, journal, and year match the ACOG citation.

### Step 2: code the worksheet blind, then compare
The worksheet holds three tiers:

| Tier | What | Why |
|---|---|---|
| 1 | Every flagged citation | Known uncertainty |
| 2 | Every unflagged comparative study (RCT, adjusted observational) | These determine the evidence-type counts the question is about |
| 3 | A seeded 20% random sample of the remaining unflagged citations, stratified by study type | Measures the error rate where the AI looked confident |

**Blind first, then reveal.** Hide the AI columns (study type through flag reasons), or work from a copy with them deleted. For each row:
- record the reviewer's own study type, severity, sibling, and N from the **full text** when it exists;
- unhide the AI codes and mark each one correct or incorrect;
- enter corrections and notes, and log the minutes spent.

**For abstract-only studies:** get the full text through the library before coding. If it can't be found, say so in `human_notes` and code from the abstract.

### Step 3: measure accuracy and decide
- **Per field** (study type, severity, sibling, N within 10%), report:
  - human vs. AI final percent agreement, with a 95% Wilson interval;
  - Cohen's κ for human vs. AI;
  - Cohen's κ for Reviewer A vs. Reviewer B on the overlap.
- **Decision rule for Tier 3:**
  - If study-type agreement is ≥ 95% with a lower 95% bound ≥ 85%, accept the unaudited, unflagged codes as they are.
  - Otherwise, extend human review to every citation in that study-type stratum.
- **Error patterns:** tabulate errors by evidence basis (full text vs abstract) and by study type to find systematic AI errors. One example would be the AI calling pooled analyses "systematic reviews"; another is the full-cohort vs. restricted-cohort N choice. Fix those classes everywhere, not just in the sampled rows.

### Step 4: finalize
- Human-corrected values replace AI values in a final column, keeping the AI value for the audit trail.
- Re-run `1_Scripts/05_build_spreadsheets.py`, or recompute the `Rec_summary` sheet, so the recommendation-level counts reflect the corrections.
- In any write-up, report: the AI agreement statistics, the human–AI accuracy, the human–human κ, and the number of items changed.

### Effort
Rough estimates:
- about 10–15 minutes for a comparative study that needs full-text retrieval;
- about 3–5 minutes for guidelines, reviews, and case reports.

| Reviewer | Work | Hours |
|---|---|---|
| A | Calibration (1 h) + upstream checks (0.75 h) + 61 worksheet rows (37 comparative/observational × ~12 min, 24 other × ~4 min) | ≈ 11 |
| B | Calibration (1 h) + 30% overlap (≈ 18 rows) | ≈ 4 |
| **Total** | | **≈ 15 person-hours** |

The worksheet has 61 rows: 34 flagged (Tier 1), 10 unflagged comparative studies (Tier 2), and 17 drawn for the random audit (Tier 3, seed 20261013).

### The request to send a reviewer

> **Subject:** Verification help: study designs behind ACOG's perinatal mental health guideline (~11 hours)
>
> Hi [name], I'm characterizing the evidence behind ACOG CPG No. 5 (perinatal mental health treatment): for each recommendation, what study designs it cites (RCT, sibling design, observational adjusted for observables with or without depression severity) and how large the studies are. Three AI raters coded all 126 citations and an AI judge resolved their disagreements. Before relying on any of it, I need a human check of the items most likely to be wrong and a random sample of the rest.
>
> **What I'd ask you to do:**
> 1. Read the 2-page coding protocol, then code 5 calibration papers. We'll compare notes for about 30 minutes.
> 2. Work through the `Human_verification` sheet (61 rows) with the AI columns hidden. Code each paper from the full text (library access needed for most), then unhide and mark the AI code right or wrong.
> 3. Spend 45 minutes confirming that the citation lists for the 17 recommendations match the guideline text.
>
> Everything is in one folder: protocol, paper files, links to full texts, and the spreadsheet. Estimated time is 11 hours; I'd like it back by [date]. You'll be acknowledged in any write-up. Could you do it?
