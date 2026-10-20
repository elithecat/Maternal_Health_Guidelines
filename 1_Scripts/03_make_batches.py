"""Split citations into 3 size-balanced batches for the rater agents (snake assignment by file size)."""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
cm = json.loads((ROOT / "0_Data/citation_map.json").read_text())
cs = sorted(cm["citations"], key=lambda c: -os.path.getsize(ROOT / c["paper_file"]))
batches = [[], [], []]
for i, c in enumerate(cs):
    k = i % 6
    batches[k if k < 3 else 5 - k].append({"ref_id": c["ref_id"], "paper_file": c["paper_file"],
                                            "evidence_basis": "full_text" if c["full_text_available"] else ("abstract_only" if c.get("pmid") else "citation_only")})
for b, items in enumerate(batches, 1):
    items.sort(key=lambda x: (len(x["ref_id"]), x["ref_id"]))
    (ROOT / f"2_Output/agent_work/batch_{b}.json").write_text(json.dumps(items, indent=1))
    print(b, len(items), sum(os.path.getsize(ROOT / x["paper_file"]) for x in items), sum(x["evidence_basis"] == "full_text" for x in items))
