"""Find legal open-access copies for citations without stored full text (Amendment 2: code from full text).

Queries OpenAlex (open-access locations) and Europe PMC (full-text availability) for every PubMed-indexed
citation whose full text is not yet in 0_Data/papers/.

Output: 0_Data/oa_locations.json   {ref_id: {"openalex": {...}, "europepmc": {...}, "candidates": [urls]}}

Run: python3 -I 1_Scripts/06_find_open_access.py
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "0_Data"


def get_json(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "acog-cpg5-evidence-review (research script)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 + 2 * attempt)
    return {"_error": str(err)}


def main():
    cits = json.loads((DATA / "citation_map.json").read_text())["citations"]
    todo = [c for c in cits if c.get("pmid") and not c["full_text_available"]]
    out = {}
    for c in todo:
        rid, pm = c["ref_id"], c["pmid"]
        oa = get_json(f"https://api.openalex.org/works/pmid:{pm}")
        time.sleep(0.2)
        ep = get_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": f"EXT_ID:{pm} AND SRC:MED", "resultType": "core", "format": "json"}))
        time.sleep(0.2)
        cand = []
        oinfo = {}
        if "_error" not in oa:
            o = oa.get("open_access") or {}
            oinfo = {"is_oa": o.get("is_oa"), "oa_status": o.get("oa_status"), "oa_url": o.get("oa_url")}
            for loc in oa.get("locations") or []:
                for k in ("pdf_url", "landing_page_url"):
                    u = loc.get(k)
                    if u and loc.get("is_oa") and u not in cand:
                        cand.append(u)
        einfo = {}
        res = ((ep.get("resultList") or {}).get("result") or [{}]) if "_error" not in ep else [{}]
        if res:
            r = res[0]
            einfo = {"isOpenAccess": r.get("isOpenAccess"), "inEPMC": r.get("inEPMC"), "pmcid": r.get("pmcid"),
                     "hasPDF": r.get("hasPDF")}
            for ft in ((r.get("fullTextUrlList") or {}).get("fullTextUrl") or []):
                if ft.get("availabilityCode") in ("OA", "F") and ft.get("url") not in cand:
                    cand.append(ft["url"])
        out[rid] = {"pmid": pm, "doi": c.get("doi"), "full_text_status": c["full_text_status"],
                    "openalex": oinfo, "europepmc": einfo, "candidates": cand}
        print(rid, oinfo.get("oa_status"), len(cand))
    (DATA / "oa_locations.json").write_text(json.dumps(out, indent=1))
    n = sum(1 for v in out.values() if v["candidates"])
    print(f"{n}/{len(out)} have at least one open-access location")


if __name__ == "__main__":
    main()
