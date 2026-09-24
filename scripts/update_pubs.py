#!/usr/bin/env python3
"""Refresh the site's publication data from NASA ADS and Google Scholar.

Writes src/data/papers.json, src/data/metrics.json and src/data/pending.yaml,
then commits and pushes if (and only if) the data actually changed.
See docs/05-data-pipeline.md for the full contract.

Exit codes: 0 no change · 10 updated · 20 updated, pending items need review · 1 error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import requests
import yaml

ORCID = "0000-0002-7703-0692"
SURNAME = "bordiu"
SELF_NAME = "C. Bordiú"
SCHOLAR_ID = "W18yO88AAAAJ"

ADS_API = "https://api.adsabs.harvard.edu/v1"
ADS_FIELDS = (
    "bibcode,title,author,author_count,year,pubdate,pub,bibstem,volume,page,"
    "doi,identifier,property,doctype,citation_count"
)
# Doctypes that are never shown (data tables, errata, SKA science-book shells...).
SKIP_DOCTYPES = {"catalog", "dataset", "erratum", "misc", "proposal", "circular", "newsletter"}

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
PAPERS = DATA / "papers.json"
METRICS = DATA / "metrics.json"
PENDING = DATA / "pending.yaml"
OVERRIDES = DATA / "overrides.yaml"

EXIT_NOCHANGE, EXIT_UPDATED, EXIT_PENDING, EXIT_ERROR = 0, 10, 20, 1

JOURNALS = {
    "MNRAS": "MNRAS",
    "A&A": "A&A",
    "ApJL": "ApJL",
    "ApJ": "ApJ",
    "AJ": "AJ",
    "PASA": "PASA",
    "A&C": "Astronomy & Computing",
    "ExA": "Experimental Astronomy",
    "ITAI": "IEEE Trans. AI",
    "SerAJ": "Serbian Astron. J.",
    "Msngr": "The Messenger",
    "ASPC": "ASP Conf. Ser.",
    "SPIE": "Proc. SPIE",
    "EPJWC": "EPJ Web Conf.",
    "hsa": "Highlights of Spanish Astrophysics",
    "ASSP": "Astrophys. Space Sci. Proc.",
    "EAS": "EAS Annual Meeting",
    "eas": "EAS Annual Meeting",
    "hsax": "Highlights of Spanish Astrophysics X",
    "hypa": "ESO Hypatia Colloquium",
    "IAUGA": "IAU General Assembly",
    "ascl": "ASCL",
    "arXiv": "arXiv",
}


# ---------------------------------------------------------------- helpers

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def fold(s: str) -> str:
    """Lower-case and strip accents, for name matching."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def short_name(ads_name: str) -> str:
    """'Riggi, Simone' -> 'S. Riggi'; our own name -> 'C. Bordiú'."""
    if fold(ads_name).startswith(SURNAME):
        return SELF_NAME
    surname, _, given = ads_name.partition(",")
    initials = " ".join(f"{p[0]}." for p in re.split(r"[\s-]+", given.strip()) if p)
    return f"{initials} {surname.strip()}".strip()


def ads_token() -> str:
    tok = os.environ.get("ADS_API_TOKEN")
    if not tok:
        keyfile = Path.home() / ".ads" / "dev_key"
        if keyfile.exists():
            tok = keyfile.read_text().strip()
    if not tok:
        raise SystemExit("No ADS token: set ADS_API_TOKEN or create ~/.ads/dev_key")
    return tok


def ads_search(session: requests.Session, query: str) -> list[dict]:
    docs, start = [], 0
    while True:
        r = session.get(
            f"{ADS_API}/search/query",
            params={"q": query, "fl": ADS_FIELDS, "rows": 200, "start": start, "sort": "date desc"},
            timeout=60,
        )
        r.raise_for_status()
        resp = r.json()["response"]
        docs += resp["docs"]
        start += len(resp["docs"])
        if start >= resp["numFound"] or not resp["docs"]:
            return docs


def ads_metrics(session: requests.Session, bibcodes: list[str]) -> dict:
    r = session.post(f"{ADS_API}/metrics", json={"bibcodes": bibcodes, "types": ["indicators", "citations"]}, timeout=60)
    r.raise_for_status()
    m = r.json()
    return {
        "citations": m["citation stats"]["total number of citations"],
        "h_index": m["indicators"]["h"],
        "i10": m["indicators"]["i10"],
    }


class _ScholarTable(HTMLParser):
    """Collects the numbers of the 'Cited by' table (td.gsc_rsb_std)."""

    def __init__(self) -> None:
        super().__init__()
        self.values: list[int] = []
        self._grab = False

    def handle_starttag(self, tag, attrs):
        self._grab = tag == "td" and "gsc_rsb_std" in (dict(attrs).get("class") or "")

    def handle_data(self, data):
        if self._grab and data.strip().isdigit():
            self.values.append(int(data.strip()))
            self._grab = False


def scholar_metrics() -> dict | None:
    """Headline totals from the public profile page; None if blocked or changed."""
    try:
        r = requests.get(
            "https://scholar.google.com/citations",
            params={"user": SCHOLAR_ID, "hl": "en"},
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"},
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        log(f"  scholar: request failed ({e})")
        return None
    p = _ScholarTable()
    p.feed(r.text)
    if len(p.values) < 6:  # captcha page or layout change
        log("  scholar: table not found (blocked?)")
        return None
    # [citations all, since, h all, since, i10 all, since]
    return {"citations": p.values[0], "h_index": p.values[2], "i10": p.values[4]}


# ---------------------------------------------------------------- normalise

def self_position(authors: list[str]) -> int | None:
    for i, a in enumerate(authors):
        if fold(a).startswith(SURNAME):
            return i + 1
    return None


def default_category(pos: int) -> str:
    return "first" if pos == 1 else "key" if pos <= 3 else "coauthor"


def kind_of(doc: dict) -> str:
    dt = doc.get("doctype", "")
    return {
        "article": "article",
        "inproceedings": "proceedings",
        "abstract": "abstract",
        "software": "software",
        "eprint": "preprint",
        "inbook": "chapter",
        "book": "chapter",
    }.get(dt, dt)


def arxiv_id(doc: dict) -> str | None:
    for ident in doc.get("identifier", []):
        m = re.match(r"^(?:arXiv:)?(\d{4}\.\d{4,5})$", ident)
        if m:
            return m.group(1)
    return None


def normalise(doc: dict, orcid_verified: bool) -> dict | None:
    authors = doc.get("author", [])
    pos = self_position(authors)
    if pos is None:
        return None
    n = doc.get("author_count", len(authors))
    head = [short_name(a) for a in authors[:3]]
    bibstem = (doc.get("bibstem") or [""])[0]
    arx = arxiv_id(doc)
    doi = (doc.get("doi") or [None])[0]
    return {
        "id": doc["bibcode"],
        "title": re.sub(r"<[^>]+>", "", (doc.get("title") or [""])[0]).strip(),
        "authors": head,
        "position": pos,
        "n_authors": n,
        "year": int(doc["year"]),
        "date": doc.get("pubdate", "")[:7].replace("-00", ""),
        "journal": JOURNALS.get(bibstem, doc.get("pub", "")),
        "volume": doc.get("volume"),
        "page": (doc.get("page") or [None])[0],
        "kind": kind_of(doc),
        "refereed": "REFEREED" in doc.get("property", []),
        "category": default_category(pos),
        "citations": doc.get("citation_count", 0),
        "links": {
            "ads": f"https://ui.adsabs.harvard.edu/abs/{doc['bibcode']}",
            "arxiv": f"https://arxiv.org/abs/{arx}" if arx else None,
            "doi": f"https://doi.org/{doi}" if doi else None,
        },
        "orcid": orcid_verified,
    }


def manual_entry(m: dict) -> dict:
    pos = m.get("position", 99)
    return {
        "id": m["id"],
        "title": m["title"],
        "authors": m.get("authors", []),
        "position": pos,
        "n_authors": m.get("n_authors", len(m.get("authors", []))),
        "year": int(m["year"]),
        "date": str(m.get("date", m["year"])),
        "journal": m.get("journal", ""),
        "volume": m.get("volume"),
        "page": m.get("page"),
        "kind": m.get("kind", "article"),
        "refereed": bool(m.get("refereed", False)),
        "category": m.get("category", default_category(pos)),
        "citations": m.get("citations", 0),
        "links": {"ads": None, "arxiv": m.get("arxiv"), "doi": f"https://doi.org/{m['doi']}" if m.get("doi") else None},
        "orcid": True,
        "manual": True,
    }


def dedupe(docs: list[dict]) -> list[dict]:
    """ADS sometimes keeps an eprint (or an ADASS preprint) apart from the published
    record. Keep one record per title, preferring refereed, then published, versions."""
    rank = {"article": 0, "inproceedings": 1, "inbook": 2, "abstract": 3, "software": 4, "eprint": 5}
    best: dict[str, tuple] = {}
    idents: dict[str, list] = {}
    for d in docs:
        key = re.sub(r"[^a-z0-9]", "", fold((d.get("title") or [""])[0]))[:80]
        idents.setdefault(key, []).extend(d.get("identifier", []))
        score = ("REFEREED" not in d.get("property", []), rank.get(d.get("doctype"), 9))
        if key not in best or score < best[key][0]:
            best[key] = (score, d)
    for key, (_, d) in best.items():  # keep e.g. the arXiv id of a dropped eprint
        d["identifier"] = sorted(set(idents[key]))
    keep = {id(v[1]) for v in best.values()}
    return [d for d in docs if id(d) in keep]


# ---------------------------------------------------------------- main

def load_yaml(path: Path) -> dict:
    return (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


def dump_json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def write_if_changed(path: Path, text: str, dry: bool) -> bool:
    if path.exists() and path.read_text() == text:
        return False
    if not dry:
        path.write_text(text)
    return True


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    ap.add_argument("--no-push", action="store_true", help="commit but do not push")
    ap.add_argument("--no-commit", action="store_true", help="write files but do not commit")
    ap.add_argument("--no-scholar", action="store_true", help="skip the Google Scholar scrape")
    args = ap.parse_args()

    old_ids = {p["id"] for p in json.loads(PAPERS.read_text())} if PAPERS.exists() else set()
    ov = load_yaml(OVERRIDES)
    confirmed, rejected = set(ov.get("confirmed") or []), set(ov.get("rejected") or [])
    hidden = set(ov.get("hide") or [])
    cat_over = ov.get("category") or {}

    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {ads_token()}"
    log("ADS: querying…")
    orcid_bibs = {d["bibcode"] for d in ads_search(s, f"orcid:{ORCID}")}
    docs = [d for d in ads_search(s, f'orcid:{ORCID} OR author:"Bordiu, C"')
            if d.get("doctype") not in SKIP_DOCTYPES]
    docs = dedupe(docs)

    papers, pending = [], []
    for d in docs:
        if d["bibcode"] in hidden or d["bibcode"] in rejected:
            continue
        verified = d["bibcode"] in orcid_bibs
        p = normalise(d, verified)
        if p is None:
            continue
        if not verified and d["bibcode"] not in confirmed:
            pending.append({"id": p["id"], "title": p["title"], "year": p["year"], "journal": p["journal"],
                            "position": p["position"], "link": p["links"]["ads"]})
            continue
        if p["id"] in cat_over:
            p["category"] = cat_over[p["id"]]
        papers.append(p)

    papers += [manual_entry(m) for m in ov.get("manual") or [] if m["id"] not in hidden]
    papers.sort(key=lambda p: (p["year"], p["date"], p["id"]), reverse=True)

    # ---- metrics
    refereed = [p for p in papers if p["refereed"] and p["kind"] == "article"]
    counts = {
        "refereed": len(refereed),
        "first_author": sum(p["category"] == "first" for p in refereed),
        "total": len(papers),
    }
    ads_m = ads_metrics(s, [p["id"] for p in papers if not p.get("manual")])
    prev = json.loads(METRICS.read_text()) if METRICS.exists() else {}
    # Scholar: newest of (fresh scrape, last good scrape/manual value, manual entry in overrides).
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prev_sch = prev.get("scholar") or None
    sch = None if args.no_scholar else scholar_metrics()
    candidates = []
    if prev_sch:
        candidates.append(prev_sch)
    if ov.get("scholar"):
        m = ov["scholar"]
        candidates.append({"citations": int(m["citations"]), "h_index": int(m["h_index"]), "i10": int(m["i10"]),
                           "fetched": str(m["date"]), "via": "manual"})
    if sch is not None:
        candidates.append({**sch, "fetched": today, "via": "scrape"})
    # Later candidates win ties, so a fresh scrape beats a manual entry dated today.
    scholar = max(reversed(candidates), key=lambda c: c["fetched"]) if candidates else None
    if scholar and prev_sch and {k: prev_sch.get(k) for k in ("citations", "h_index", "i10")} == \
            {k: scholar[k] for k in ("citations", "h_index", "i10")}:
        scholar = prev_sch  # same numbers: keep the old record so the date alone is not a change
    metrics = {
        "counts": counts,
        "ads": ads_m,
        "scholar": scholar,
        "headline": {**(scholar or ads_m), "source": "Google Scholar" if scholar else "NASA ADS"},
    }
    metrics["headline"].pop("fetched", None)
    metrics["headline"].pop("via", None)

    pending_text = yaml.safe_dump(
        {"note": "Name-only ADS matches (no ORCID). Move each id to 'confirmed' or 'rejected' in overrides.yaml.",
         "pending": pending},
        sort_keys=False, allow_unicode=True, width=120,
    )
    changed = [
        path.name
        for path, text in [(PAPERS, dump_json(papers)), (METRICS, dump_json(metrics)), (PENDING, pending_text)]
        if write_if_changed(path, text, args.dry_run)
    ]

    # ---- summary
    log(f"  papers: {len(papers)} shown · {counts['refereed']} refereed articles · {counts['first_author']} first-author")
    log(f"  metrics ({metrics['headline']['source']}): {metrics['headline']['citations']} citations, "
        f"h={metrics['headline']['h_index']}")
    if old_ids:
        for p in papers:
            if p["id"] not in old_ids:
                log(f"  NEW: {p['year']} {p['journal']} — {p['title'][:80]}")
    for p in pending:
        log(f"  PENDING: {p['id']} — {p['title'][:70]}")

    if not changed:
        log("No change.")
        return EXIT_NOCHANGE
    log(f"{'Would change' if args.dry_run else 'Changed'}: {', '.join(changed)}")
    if not (args.dry_run or args.no_commit):
        git("add", *(str(p.relative_to(ROOT)) for p in (PAPERS, METRICS, PENDING)))
        git("commit", "-m", f"data: refresh publications ({counts['total']} items, {len(pending)} pending)")
        if not args.no_push:
            git("push")
            log("Pushed.")
    return EXIT_PENDING if pending else EXIT_UPDATED


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — report and signal failure to the caller
        log(f"ERROR: {e}")
        sys.exit(EXIT_ERROR)
