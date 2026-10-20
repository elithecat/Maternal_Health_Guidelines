"""Merge the three raters' codes, measure agreement, and write the judge's worklist.

Inputs : 2_Output/agent_work/rater{1,2,3}_batch{1,2,3}.json, 0_Data/citation_map.json
Outputs: 2_Output/agent_work/raters_merged.json   all rater codes keyed by ref_id
         2_Output/agent_work/disagreements.json   items + fields the judge must adjudicate
         2_Output/agent_work/agreement_stats.json percent agreement and Fleiss' kappa per field

Run: python3 -I 1_Scripts/04_find_disagreements.py
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "2_Output/agent_work"
RATERS = (1, 2, 3)
SIZE_TOL = 0.10  # sample sizes within 10% of each other count as agreement

STUDY_TYPES = [
    "RCT", "Sibling/within-family", "Observational – adjusted, incl. severity",
    "Observational – adjusted, excl. severity", "Observational – unadjusted/descriptive",
    "Quasi-experimental (other)", "Systematic review/meta-analysis", "Pharmacokinetic/physiologic",
    "Case report/case series", "Survey/qualitative/program evaluation", "Narrative review/commentary",
    "Guideline/consensus statement", "Protocol/design paper", "Not a study (resource)", "Other",
]


def canon_type(v):
    """Map minor spelling variants (dashes, case, numbering) onto the protocol's codes."""
    if not v:
        return None
    s = re.sub(r"^\s*\d+\.\s*", "", str(v)).strip().strip("`")
    key = lambda x: re.sub(r"[^a-z]", "", x.lower())
    for t in STUDY_TYPES:
        if key(s) == key(t):
            return t
    k = key(s)
    rules = [  # order matters: the three observational codes share a prefix
        (("unadjust", "descriptive"), 4), (("incl",), 2), (("excl",), 3), (("sibling", "withinfamily"), 1),
        (("quasi",), 5), (("systematic", "metaanal"), 6), (("pharmacokin", "physiolog"), 7),
        (("casereport", "caseseries"), 8), (("survey", "qualitat", "program"), 9),
        (("narrative", "commentary"), 10), (("guideline", "consensus"), 11), (("protocol",), 12),
        (("notastudy", "resource"), 13), (("rct", "random"), 0),
    ]
    for words, i in rules:
        if any(w in k for w in words):
            return STUDY_TYPES[i]
    return "Other"


def canon_cat(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    return {"yes": "Yes", "no": "No", "unclear": "Unclear", "na": "NA", "n/a": "NA", "partial/unclear": "Unclear"}.get(s, str(v).strip())


def to_int(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return int(v)
    m = re.sub(r"[,\s]", "", str(v))
    return int(m) if m.isdigit() else None


def sizes_agree(vals):
    if all(v is None for v in vals):
        return True
    if any(v is None for v in vals):
        return False
    lo, hi = min(vals), max(vals)
    return hi == lo or (lo > 0 and (hi - lo) / hi <= SIZE_TOL)


def fleiss_kappa(rows):
    """rows: list of category lists (one label per rater). Returns kappa or None."""
    rows = [r for r in rows if all(x is not None for x in r)]
    if not rows:
        return None
    n = len(rows[0])
    cats = sorted({x for r in rows for x in r})
    P = [(sum(c * c for c in Counter(r).values()) - n) / (n * (n - 1)) for r in rows]
    pj = {c: sum(r.count(c) for r in rows) / (len(rows) * n) for c in cats}
    Pbar, Pe = sum(P) / len(P), sum(p * p for p in pj.values())
    return None if Pe == 1 else round((Pbar - Pe) / (1 - Pe), 3)


def main():
    cmap = {c["ref_id"]: c for c in json.loads((ROOT / "0_Data/citation_map.json").read_text())["citations"]}
    merged = {rid: {} for rid in cmap}
    round2 = set()
    for r in RATERS:
        # round-1 batches first, then round-2 re-codes (Amendment 2), which replace round-1 codes
        for f in sorted(WORK.glob(f"rater{r}_batch*.json")) + sorted(WORK.glob(f"rater{r}_round2.json")):
            for row in json.loads(f.read_text()):
                rid = str(row.get("ref_id")).strip()
                if rid not in merged:
                    print(f"WARNING rater{r}: unknown ref_id {rid} in {f.name}")
                    continue
                row["study_type"] = canon_type(row.get("study_type"))
                for k in ("severity_adjustment", "sibling_analysis_any", "confidence"):
                    row[k] = canon_cat(row.get(k))
                row["sample_size_n"] = to_int(row.get("sample_size_n"))
                row["n_studies"] = to_int(row.get("n_studies"))
                row["coding_round"] = 2 if "round2" in f.name else 1
                if row["coding_round"] == 2:
                    round2.add(rid)
                merged[rid][f"rater{r}"] = row
    missing = {rid: [f"rater{r}" for r in RATERS if f"rater{r}" not in v] for rid, v in merged.items()}
    missing = {k: v for k, v in missing.items() if v}
    if missing:
        print("MISSING CODES:", missing)

    fields = ["study_type", "severity_adjustment", "sibling_analysis_any", "sample_size_n", "n_studies"]
    dis, stats_rows = [], {f: [] for f in fields}
    agree_ct = Counter()
    for rid, rv in merged.items():
        vals = {f: [rv.get(f"rater{r}", {}).get(f) for r in RATERS] for f in fields}
        disputed = []
        for f in ("study_type", "severity_adjustment", "sibling_analysis_any"):
            stats_rows[f].append(vals[f])
            if len(set(vals[f])) > 1:
                disputed.append(f)
            else:
                agree_ct[f] += 1
        if sizes_agree(vals["sample_size_n"]):
            agree_ct["sample_size_n"] += 1
        else:
            disputed.append("sample_size_n")
        types = Counter(vals["study_type"])
        if types.most_common(1)[0][0] == "Systematic review/meta-analysis" and not sizes_agree(vals["n_studies"]):
            disputed.append("n_studies")
        low_conf = [f"rater{r}" for r in RATERS if rv.get(f"rater{r}", {}).get("confidence") == "Low"]
        if disputed:
            dis.append({
                "ref_id": rid, "paper_file": cmap[rid]["paper_file"], "recs": cmap[rid]["recs"],
                "evidence_basis": rv.get("rater1", {}).get("evidence_basis"),
                "disputed_fields": disputed, "three_way_split_study_type": len(set(vals["study_type"])) == 3,
                "low_confidence_raters": low_conf,
                "rater_codes": {f"rater{r}": rv.get(f"rater{r}") for r in RATERS},
            })
    n = len(merged)
    stats = {
        "n_citations": n,
        "n_with_any_disagreement": len(dis),
        "percent_agreement": {f: round(100 * agree_ct[f] / n, 1) for f in ("study_type", "severity_adjustment", "sibling_analysis_any", "sample_size_n")},
        "fleiss_kappa": {f: fleiss_kappa(stats_rows[f]) for f in ("study_type", "severity_adjustment", "sibling_analysis_any")},
        "disputed_field_counts": dict(Counter(f for d in dis for f in d["disputed_fields"])),
        "sample_size_tolerance": SIZE_TOL,
    }
    (WORK / "raters_merged.json").write_text(json.dumps(merged, indent=1, ensure_ascii=False))
    (WORK / "disagreements.json").write_text(json.dumps(dis, indent=1, ensure_ascii=False))
    if round2:
        (WORK / "disagreements_round2.json").write_text(json.dumps([d for d in dis if d["ref_id"] in round2], indent=1, ensure_ascii=False))
        stats["round2_refs"] = sorted(round2)
        stats["round2_with_disagreement"] = sum(d["ref_id"] in round2 for d in dis)
    (WORK / "agreement_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
