# 05 — Data pipeline (ADS + Google Scholar, run by a local agent)

## Overview

- `scripts/update_pubs.py` (Python) is run **locally by a local scheduled agent**, not in CI.
- It fetches the publication data, writes the site's data files, and when something changed it commits and pushes to the
  default branch. The GitHub Action then rebuilds the site.
- **Decision**: it pushes straight to the default branch, with no pull request. The safeguard against wrong papers is the
  pending mechanism described below.

## Sources

| Data | Source | Notes |
|---|---|---|
| Paper list and metadata | NASA ADS API | Query: `orcid:0000-0002-7703-0692 OR author:"Bordiu, C"` |
| Per-paper citations | NASA ADS | Matched by bibcode/DOI |
| Headline totals (citations, h-index, i10) | Google Scholar profile page | Scraped with `requests` + the stdlib `html.parser`; falls back to ADS metrics |

- ADS token: the `ADS_API_TOKEN` environment variable, falling back to `~/.ads/dev_key`. It is never committed.
- If Scholar blocks the request, the script **keeps the last good Scholar numbers**. If there are none, it uses the ADS
  metrics. The site footnotes which source each number comes from.
- **Manual fallback** (decided 2026-09-24): `overrides.yaml` → `scholar:` holds citations, h-index, i10 and a `date`,
  copied by hand from the profile page. The pipeline uses the newest of a fresh scrape, the last stored value and the
  manual entry. A scrape wins a same-day tie. It was seeded on 2026-09-24 with 688 citations, h = 15 and i10 = 22.
- **Why**: Scholar blocks automated access by IP address. From this machine, plain requests, headless Chrome and an
  external fetch service all got the CAPTCHA page on 2026-09-24. SerpAPI (a paid service with a free tier) was
  considered and not adopted for now.
- The `scholarly` package was rejected as too heavy and brittle; `beautifulsoup4` was dropped because the stdlib parser is enough. Per-paper Scholar counts were rejected because matching by title is fragile.

## Cleaning ADS records

- VizieR `catalog`/`dataset` records, errata and other non-publication doctypes are skipped.
- Duplicates (an arXiv eprint or ADASS preprint kept apart from the published record) are merged by title.
  The refereed or published version is kept, and it inherits the arXiv id of the dropped eprint.
- Venue names come from the ADS `bibstem`, mapped to short journal names in the script (`JOURNALS`).
- Observed 2026-09-24: Google Scholar answered HTTP 429 (blocked) from this machine, so the ADS fallback is live.
  If Scholar never succeeds from the agent's host, the headline stays on ADS, which is expected and harmless.

## Keeping wrong papers out

- Papers that carry the owner's **ORCID** in ADS are **published automatically**.
- Papers matched **only by name** go to `pending.yaml` and are **hidden** until the owner moves them into
  `overrides.yaml` (confirm or reject). The agent should flag new pending items to the owner.
- ORCID tagging in ADS turned out to be patchy: 22 of his papers had no ORCID. At setup (2026-09-24) all of them were
  checked against the owner's CV and research topics and seeded into `confirmed`. Only matches that appear after that date are held back.

## Files

| File | Written by | Purpose |
|---|---|---|
| `src/data/papers.json` | script | Normalised paper list with category, refereed flag, links and citations |
| `src/data/metrics.json` | script | Headline totals, their source, and a timestamp |
| `src/data/overrides.yaml` | owner | Category overrides, hide list, confirmed pending items, and manual works not in ADS |
| `src/data/pending.yaml` | script | Name-only matches awaiting review |
| `src/data/talks.yaml`, `src/data/press.yaml` | owner | Talks and press, maintained by hand |

- Manual works to add via overrides: *Scientific Visualization on the Cloud: the NEANIAS Services towards EOSC
  Integration* (J. Grid Computing, 2022); *Towards Porting Astrophysics Visual Analytics Services…* (AISC, 2020);
  the 2026 book chapter *A Semi-supervised "Cluster-then-Label" Scheme for Photometric Classification of Evolved Stars*.

## Behaviour contract (for the agent)

- **Idempotent**: running it twice changes nothing the second time.
- **Commits only on real data changes.** A change to the `fetched_at` timestamp alone does not count as a change.
- **Exit codes**:

| Code | Meaning |
|---|---|
| 0 | No change |
| 10 | Updated and pushed |
| 20 | Updated, but new pending items need review |
| 1 | Error (nothing is written) |

Also `--no-commit`: write the files but don't commit.

- Flags:

| Flag | Effect |
|---|---|
| `--dry-run` | Show what would change, write nothing |
| `--no-push` | Write and commit, but don't push |
| `--no-scholar` | Skip the Google Scholar scrape |

- It prints a short human-readable summary: new papers, category counts, metrics delta, and pending items.

## Other build-time data

- `scripts/build_starfield.py` is a one-off: it builds `src/data/starfield.json` from the Yale Bright Star Catalogue
  (VizieR V/50, V < 5.8), with a gnomonic projection centred on η Car. Rerun it only to change the field.
