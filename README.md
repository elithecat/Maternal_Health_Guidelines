# Evidence behind ACOG CPG No. 5 (perinatal mental health treatment)

What kinds of studies support each recommendation in ACOG Clinical Practice Guideline No. 5 (*Treatment and Management of Mental Health Conditions During Pregnancy and Postpartum*, 2023): RCTs, sibling designs, or observational studies adjusted for observables with or without depression severity? And how large are they?

- **Start here:** `METHODS_AND_VERIFICATION.md` covers methods, preliminary results, limitations, and the human-verification plan.
- **Codebook:** `coding_protocol.md`
- **Results:** `2_Output/Compiled_evidence_coding.xlsx`. Per-rater and judge workbooks sit alongside it.
- **Papers:** not included here because they're copyrighted: the ACOG guideline PDF, its extracted text, and the article abstracts/full texts. `0_Data/citation_map.json` has every citation's PMID/PMCID/DOI. To rebuild `0_Data/papers/` from NCBI, put the guideline PDF in the project root and run `1_Scripts/02_fetch_papers.py`. `0_Data/missing_full_text.md` and `0_Data/fulltext_needed.md` link to the articles without open full text.
- **Pipeline:** `1_Scripts/`. Run in order with `python3 -I`; `05` needs `openpyxl`.

Status: AI-coded (3 raters + judge), **not yet human-verified**.
