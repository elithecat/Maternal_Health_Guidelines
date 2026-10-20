"""Download open-access PDFs found by 06 and append their text to the paper files.

Only files that are genuine PDFs (start with %PDF) are kept. HTML landing pages, paywalls, and bot checks are
skipped and recorded. PMC website pages are not scraped (PMC disallows automated retrieval of non-OA-subset
articles); publisher or repository copies are used instead.

Inputs : 0_Data/oa_locations.json, 0_Data/citation_map.json
Outputs: 0_Data/oa_pdf/ref<ID>.pdf (untrusted downloads), updated 0_Data/papers/*.md and citation_map.json,
         0_Data/oa_fetch_log.json

Requires pdfplumber. Run: python3 -I 1_Scripts/07_fetch_open_access.py
"""
import json
import re
import time
import urllib.request
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "0_Data"
PDF_DIR = DATA / "oa_pdf"
SKIP_HOSTS = ("ncbi.nlm.nih.gov/pmc", "pmc.ncbi.nlm.nih.gov", "europepmc.org/articles", "scopus.com")
UA = "Mozilla/5.0 (Macintosh; research script for ACOG CPG 5 evidence review)"


def fetch_pdf(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read(30_000_000)
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
    if not data.startswith(b"%PDF"):
        return f"not a PDF ({len(data)} bytes)"
    dest.write_bytes(data)
    return "ok"


def pdf_text(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages, 1):
            w = p.width
            # most journal PDFs are two-column; extract left then right half so sentences stay in order
            left = p.crop((0, 0, w / 2, p.height)).extract_text(x_tolerance=1.5) or ""
            right = p.crop((w / 2, 0, w, p.height)).extract_text(x_tolerance=1.5) or ""
            full = p.extract_text(x_tolerance=1.5) or ""
            body = (left + "\n" + right) if len(left) > 200 and len(right) > 200 else full
            pages.append(f"[page {i}]\n{body}")
    return "\n\n".join(pages)


def main():
    PDF_DIR.mkdir(exist_ok=True)
    oa = json.loads((DATA / "oa_locations.json").read_text())
    cmap = json.loads((DATA / "citation_map.json").read_text())
    cits = {c["ref_id"]: c for c in cmap["citations"]}
    log = {}
    for rid, v in oa.items():
        if cits[rid]["full_text_available"]:
            continue  # already have full text (idempotent re-runs)
        urls =[u for u in v["candidates"] if not any(h in u for h in SKIP_HOSTS)]
        urls.sort(key=lambda u: 0 if re.search(r"pdf", u, re.I) else 1)
        tries = []
        for u in urls:
            dest = PDF_DIR / f"ref{rid}.pdf"
            status = fetch_pdf(u, dest)
            tries.append({"url": u, "status": status})
            time.sleep(1)
            if status != "ok":
                continue
            text = pdf_text(dest)
            nwords = len(text.split())
            if nwords < 300:
                tries[-1]["status"] = f"PDF has little extractable text ({nwords} words; likely a scan)"
                continue
            c = cits[rid]
            paper = ROOT / c["paper_file"]
            md = paper.read_text()
            md = md.replace("- **Full text in this file:** NO — abstract/metadata only",
                            f"- **Full text in this file:** YES — open-access PDF ({nwords:,} words; text extracted by pdfplumber, tables may be garbled)")
            md += f"\n## Full text (open-access PDF)\n\nSource: {u}\n\n{text}\n"
            paper.write_text(md)
            c.update({"full_text_available": True, "full_text_status": "Full text stored (open-access PDF)",
                      "full_text_source": f"Open-access PDF: {u}", "full_text_words": nwords, "oa_pdf": f"0_Data/oa_pdf/ref{rid}.pdf"})
            break
        log[rid] = tries
        print(rid, tries[-1]["status"] if tries else "no fetchable URL")
    (DATA / "oa_fetch_log.json").write_text(json.dumps(log, indent=1))
    (DATA / "citation_map.json").write_text(json.dumps(cmap, indent=1, ensure_ascii=False))
    print("full text now:", sum(c["full_text_available"] for c in cmap["citations"]), "/", len(cmap["citations"]))


if __name__ == "__main__":
    main()
