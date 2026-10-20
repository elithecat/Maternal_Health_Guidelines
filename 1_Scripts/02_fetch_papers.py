"""Fetch PubMed records and PMC full text for every citation supporting an ACOG CPG 5 recommendation.

Inputs : 0_Data/citation_map.json  (built by 01_build_citation_map steps; PMIDs resolved with the PubMed MCP)
Outputs: 0_Data/raw_xml/            raw PubMed / PMC XML as downloaded (untrusted data, never executed)
         0_Data/papers/*.md         one markdown file per citation: metadata, abstract, full text (if available)
         0_Data/citation_map.json   updated with pmcid, title, publication types, full-text status
         0_Data/missing_full_text.md

Run from the project root:  python3 -I 1_Scripts/02_fetch_papers.py
"""
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "0_Data"
RAW = DATA / "raw_xml"
PAPERS = DATA / "papers"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"


def get(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest.read_bytes()
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            dest.write_bytes(data)
            time.sleep(0.4)  # NCBI: <= 3 requests/second without an API key
            return data
        except Exception as e:  # noqa: BLE001
            time.sleep(2 + 2 * attempt)
            err = e
    print(f"  FAILED {url}: {err}", file=sys.stderr)
    return b""


def text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""


# ---------- PubMed records ----------
def parse_pubmed(xml_bytes):
    out = {}
    root = ET.fromstring(xml_bytes)
    for art in root.iter("PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")
        a = art.find(".//Article")
        abst = []
        for t in a.findall(".//Abstract/AbstractText"):
            lab = t.get("Label")
            abst.append((f"**{lab.title()}:** " if lab else "") + text(t))
        authors = []
        for au in a.findall(".//AuthorList/Author"):
            if au.findtext("LastName"):
                authors.append(f"{au.findtext('LastName')} {au.findtext('Initials') or ''}".strip())
            elif au.findtext("CollectiveName"):
                authors.append(au.findtext("CollectiveName"))
        ids = {i.get("IdType"): i.text for i in art.findall(".//PubmedData/ArticleIdList/ArticleId")}
        year = a.findtext(".//Journal/JournalIssue/PubDate/Year") or (a.findtext(".//Journal/JournalIssue/PubDate/MedlineDate") or "")[:4]
        out[pmid] = {
            "title": text(a.find("ArticleTitle")),
            "journal": a.findtext(".//Journal/ISOAbbreviation") or a.findtext(".//Journal/Title"),
            "year": year,
            "authors": authors,
            "abstract": "\n\n".join(abst),
            "pub_types": [text(p) for p in a.findall(".//PublicationTypeList/PublicationType")],
            "mesh": [text(m.find("DescriptorName")) for m in art.findall(".//MeshHeadingList/MeshHeading")],
            "pmcid": ids.get("pmc"),
            "doi_pubmed": ids.get("doi"),
        }
    for book in root.iter("PubmedBookArticle"):
        pmid = book.findtext(".//BookDocument/PMID")
        abst = [text(t) for t in book.findall(".//Abstract/AbstractText")]
        out[pmid] = {
            "title": text(book.find(".//BookDocument/Book/BookTitle")) or text(book.find(".//ArticleTitle")),
            "journal": "NCBI Bookshelf " + (book.findtext(".//BookDocument/ArticleIdList/ArticleId[@IdType='bookaccession']") or ""),
            "year": book.findtext(".//BookDocument/Book/PubDate/Year") or "",
            "authors": [f"{au.findtext('LastName')} {au.findtext('Initials') or ''}".strip() for au in book.findall(".//AuthorList/Author") if au.findtext("LastName")],
            "abstract": "\n\n".join(abst),
            "pub_types": [text(p) for p in book.findall(".//PublicationType")] or ["Book/Report (NCBI Bookshelf)"],
            "mesh": [],
            "pmcid": None,
            "doi_pubmed": None,
            "bookaccession": book.findtext(".//BookDocument/ArticleIdList/ArticleId[@IdType='bookaccession']"),
        }
    return out


# ---------- JATS (PMC) -> markdown ----------
def inline(el):
    """Flatten inline JATS markup; render bibliographic cross-refs as [n]."""
    parts = [el.text or ""]
    for ch in el:
        tag = ch.tag.split("}")[-1]
        if tag == "xref" and ch.get("ref-type") == "bibr":
            parts.append(f"[{text(ch)}]")
        elif tag in ("table-wrap", "fig", "disp-formula"):
            pass  # rendered separately
        else:
            parts.append(inline(ch))
        parts.append(ch.tail or "")
    return re.sub(r"\s+", " ", "".join(parts))


def table_md(tw):
    lines = []
    label, cap = text(tw.find("label")), text(tw.find("caption"))
    lines.append(f"**{label}** {cap}".strip())
    tbl = tw.find(".//table")
    if tbl is None:
        lines.append("_(table provided as image only)_")
    else:
        rows = []
        for tr in tbl.iter("tr"):
            cells = [text(c).replace("|", "/") for c in tr if c.tag in ("td", "th")]
            rows.append(cells)
        if rows:
            w = max(len(r) for r in rows)
            rows = [r + [""] * (w - len(r)) for r in rows]
            lines.append("| " + " | ".join(rows[0]) + " |")
            lines.append("|" + "---|" * w)
            for r in rows[1:]:
                lines.append("| " + " | ".join(r) + " |")
    for fn in tw.findall(".//table-wrap-foot//p") + tw.findall(".//table-wrap-foot/fn"):
        t = text(fn)
        if t:
            lines.append(f"_{t}_")
    return "\n".join(lines)


def sec_md(sec, depth):
    out = []
    for ch in sec:
        tag = ch.tag.split("}")[-1]
        if tag == "title":
            out.append("#" * min(depth, 6) + " " + text(ch))
        elif tag == "p":
            out.append(inline(ch).strip())
            for tw in ch.iter("table-wrap"):
                out.append(table_md(tw))
            for fg in ch.iter("fig"):
                out.append(f"**{text(fg.find('label'))}** {text(fg.find('caption'))}".strip())
        elif tag == "sec":
            out.append(sec_md(ch, depth + 1))
        elif tag == "table-wrap":
            out.append(table_md(ch))
        elif tag == "fig":
            out.append(f"**{text(ch.find('label'))}** {text(ch.find('caption'))}".strip())
        elif tag == "list":
            out.extend("- " + text(li) for li in ch.findall("list-item"))
        elif tag in ("boxed-text", "disp-quote"):
            out.append(text(ch))
    return "\n\n".join(o for o in out if o)


def jats_body(xml_bytes):
    """Return (markdown_full_text, n_words) or ('', 0) if the record has no body text."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return "", 0
    body = root.find(".//article/body")
    if body is None:
        body = root.find(".//body")
    if body is None:
        return "", 0
    md = [sec_md(body, 2)]
    floats = root.find(".//floats-group")
    if floats is not None:
        for tw in floats.iter("table-wrap"):
            md.append(table_md(tw))
        for fg in floats.iter("fig"):
            md.append(f"**{text(fg.find('label'))}** {text(fg.find('caption'))}".strip())
    full = "\n\n".join(m for m in md if m).strip()
    n = len(full.split())
    return (full, n) if n > 150 else ("", n)  # scanned back-issues carry only a stub


def slug(s):
    s = re.sub(r"[^\w\-]+", "", (s or "Anon").split()[0].replace("’", "").replace("'", ""))
    return s[:25] or "Anon"


def write_missing(cits):
    miss = [c for c in cits if not c["full_text_available"]]
    groups = {}
    for c in miss:
        groups.setdefault(c["full_text_status"], []).append(c)
    order = ["In PMC, but publisher blocks full-text download (readable on PMC website)",
             "In PMC, but no machine-readable body text"]
    order += sorted(k for k in groups if k not in order)
    L = ["# Citations without full text in 0_Data/papers", "",
         f"{len(miss)} of {len(cits)} citations supporting ACOG CPG 5 recommendations have no full text stored. "
         "Each still has a file in `0_Data/papers/` with the ACOG citation and, where indexed, the PubMed abstract and metadata. "
         "Full text was sought from PubMed Central (NCBI efetch, then Europe PMC); the PubMed MCP `get_full_text_article` "
         "tool returns the same PMC content and was empty for the restricted records tested.", ""]
    for g in order:
        if g not in groups:
            continue
        L += [f"## {g} ({len(groups[g])})", "", "| ACOG ref | Rec(s) | First author, year | Title / citation | PMID | Link |", "|---|---|---|---|---|---|"]
        for c in sorted(groups[g], key=lambda c: (len(c["ref_id"]), c["ref_id"])):
            pm, pmc = c.get("pmid"), c.get("pmcid")
            link = (f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/" if pmc else
                    f"https://www.ncbi.nlm.nih.gov/books/{c['bookaccession']}/" if c.get("bookaccession") else
                    f"https://doi.org/{c['doi']}" if c.get("doi") else
                    (re.search(r"https?://\S+", c["citation"]).group(0) if re.search(r"https?://\S+", c["citation"]) else
                     f"https://pubmed.ncbi.nlm.nih.gov/{pm}/" if pm else "—"))
            au = (c.get("authors") or [c.get("first_author") or "—"])[0]
            title = (c.get("title") or c["citation"])[:140].replace("|", "/")
            L.append(f"| {c['ref_id']} | {c['recs_str']} | {au}, {c.get('pub_year') or '—'} | {title} | {pm or '—'} | {link} |")
        L.append("")
    (DATA / "missing_full_text.md").write_text("\n".join(L) + "\n")


def main():
    cmap = json.loads((DATA / "citation_map.json").read_text())
    cits = cmap["citations"]
    pmids = [c["pmid"] for c in cits if c.get("pmid")]
    print(f"{len(pmids)} PMIDs")
    recs = {}
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i + 100]
        xml = get(f"{EUTILS}?db=pubmed&id={','.join(batch)}&retmode=xml", RAW / f"pubmed_batch_{i // 100 + 1}.xml")
        recs.update(parse_pubmed(xml))

    for c in cits:
        rid = c["ref_id"]
        c["recs_str"] = ", ".join(c["recs"])
        pm = c.get("pmid")
        r = recs.get(pm, {}) if pm else {}
        c.update({k: r.get(k) for k in ("title", "journal", "authors", "pub_types", "mesh", "pmcid", "bookaccession")})
        c["pub_year"] = r.get("year") or c.get("year")
        full, nwords, ft_source = "", 0, None
        if c.get("pmcid"):
            pid = c["pmcid"].replace("PMC", "")
            xml = get(f"{EUTILS}?db=pmc&id={pid}&retmode=xml", RAW / f"PMC{pid}.xml")
            full, nwords = jats_body(xml)
            ft_source = "PMC (NCBI efetch JATS XML)" if full else None
            if not full:  # some publishers block XML at NCBI; Europe PMC mirrors PMC open-access text
                xml = get(EPMC.format(f"PMC{pid}"), RAW / f"EPMC_PMC{pid}.xml")
                full, nwords = jats_body(xml)
                ft_source = "Europe PMC (fullTextXML)" if full else None
        if full:
            status = "Full text stored"
        elif not pm:
            status = "Not indexed in PubMed"
        elif c.get("pmcid"):
            raw = (RAW / f"{c['pmcid']}.xml").read_text(errors="ignore")
            status = ("In PMC, but publisher blocks full-text download (readable on PMC website)"
                      if "does not allow downloading" in raw else "In PMC, but no machine-readable body text")
        elif c.get("bookaccession"):
            status = f"NCBI Bookshelf report ({c['bookaccession']}); not in PMC"
        else:
            status = "PubMed abstract only (no PMC full text)"
        c["full_text_status"] = status
        c["full_text_available"] = bool(full)
        c["full_text_source"] = ft_source
        c["full_text_words"] = nwords if full else 0

        first = (r.get("authors") or [c.get("first_author") or ""])[0] if r else (c.get("first_author") or c["citation"].split()[0])
        fname = f"ref{rid}_{slug(first)}_{c['pub_year'] or 'nd'}" + (f"_PMID{pm}" if pm else "") + ".md"
        c["paper_file"] = f"0_Data/papers/{fname}"
        head = [
            f"# [ACOG ref {rid}] {r.get('title') or c['citation']}",
            "",
            f"- **ACOG citation (as printed):** {c['citation']}",
            f"- **Supports recommendation(s):** {c['recs_str']}",
            f"- **PMID:** {pm or 'not indexed in PubMed'}" + (f"  (resolved via {c['pmid_source']})" if pm else ""),
            f"- **PMCID:** {c.get('pmcid') or '—'}",
            f"- **DOI:** {c.get('doi') or r.get('doi_pubmed') or '—'}",
            f"- **Journal / year:** {r.get('journal') or '—'} {c['pub_year'] or ''}",
            f"- **Authors:** {', '.join((r.get('authors') or [])[:8]) + (' et al.' if len(r.get('authors') or []) > 8 else '') or '—'}",
            f"- **PubMed publication types:** {'; '.join(r.get('pub_types') or []) or '—'}",
            f"- **Full text in this file:** {'YES — ' + ft_source + f' ({nwords:,} words)' if full else 'NO — abstract/metadata only'}",
            "",
            "## Abstract",
            "",
            r.get("abstract") or "_No abstract in PubMed._",
        ]
        if full:
            head += ["", "## Full text", "", full]
        (PAPERS / fname).write_text("\n".join(head) + "\n")

    write_missing(cits)
    cmap["citations"] = cits
    (DATA / "citation_map.json").write_text(json.dumps(cmap, indent=1, ensure_ascii=False))
    n_ft = sum(c["full_text_available"] for c in cits)
    print(f"full text: {n_ft}/{len(cits)}; PubMed-indexed: {len(pmids)}")


if __name__ == "__main__":
    main()
