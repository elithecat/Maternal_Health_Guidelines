"""Append the text of manually obtained PDFs (0_Data/manual_pdf/ref<ID>.pdf) to the paper files.

Use for full texts retrieved through library access (by the PI, a reviewer, or a browser session).
Idempotent: citations that already have full text are skipped.

Run: python3 -I 1_Scripts/08_ingest_manual_pdfs.py
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "0_Data"
spec = importlib.util.spec_from_file_location("oa", Path(__file__).with_name("07_fetch_open_access.py"))
oa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oa)


def main():
    cmap = json.loads((DATA / "citation_map.json").read_text())
    cits = {c["ref_id"]: c for c in cmap["citations"]}
    for pdf in sorted((DATA / "manual_pdf").glob("ref*.pdf")):
        rid = pdf.stem[3:]
        c = cits.get(rid)
        if c is None:
            print(f"{pdf.name}: no citation with ref_id {rid}")
            continue
        if c["full_text_available"]:
            print(f"{pdf.name}: already has full text, skipped")
            continue
        if not pdf.read_bytes()[:4] == b"%PDF":
            print(f"{pdf.name}: not a PDF, skipped")
            continue
        text = oa.pdf_text(pdf)
        n = len(text.split())
        if n < 300:
            print(f"{pdf.name}: only {n} words extractable (scanned?); needs OCR, skipped")
            continue
        paper = ROOT / c["paper_file"]
        md = paper.read_text().replace(
            "- **Full text in this file:** NO — abstract/metadata only",
            f"- **Full text in this file:** YES — PDF obtained via library access ({n:,} words; text extracted by pdfplumber, tables may be garbled)")
        paper.write_text(md + f"\n## Full text (PDF via library access)\n\n{text}\n")
        c.update({"full_text_available": True, "full_text_status": "Full text stored (PDF via library access)",
                  "full_text_source": "Manual PDF (library access)", "full_text_words": n, "manual_pdf": f"0_Data/manual_pdf/{pdf.name}"})
        print(f"{pdf.name}: added {n:,} words")
    (DATA / "citation_map.json").write_text(json.dumps(cmap, indent=1, ensure_ascii=False))
    print("full text now:", sum(c["full_text_available"] for c in cmap["citations"]), "/", len(cmap["citations"]))


if __name__ == "__main__":
    main()
