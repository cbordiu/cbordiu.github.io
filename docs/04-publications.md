# 04 — Publications

## Categories (the main switch)

| Category | Default rule |
|---|---|
| **First author** | Author position 1 |
| **Key contributor** | Author position 2–3 |
| **Co-author** | Author position ≥ 4 |

- There is also a separate **"Refereed only"** checkbox, which acts across all categories. It keeps **refereed journal articles
  only**; refereed proceedings are excluded (changed 2026-09-24), so its count matches the headline "N refereed papers".
- Exceptions (promoting a paper to Key contributor, hiding errata or duplicates) go in `overrides.yaml`
  (see [05](05-data-pipeline.md)).
- **Counting convention**: the site uses the ADS numbers, deduplicated, with arXiv and VizieR duplicates removed.
  As of 2026-09-24 that is 39 refereed articles: 8 first-author, 4 key-contributor and 27 co-author.

## `/publications` page layout

- Papers are grouped by year, newest first.
- Each row shows:
  - Title
  - Authors, shortened: the first 3 authors, then `…, **C. Bordiú**, … (+N)` when he is further down. His name is always highlighted.
  - Journal, volume, page and year
  - Small links (ADS · arXiv · DOI) and a small citation count (from ADS)
- **Filters**: chips for First author / Key contributor / Co-author, each with a count, plus the "Refereed only" checkbox.
  - **"Refereed only" is on by default** (changed 2026-09-24). `?refereed=0` shows everything. The filter state is kept
    in the URL (e.g. `?cat=first`, `?cat=key&refereed=0`), so filtered views can be linked.
  - Without JavaScript the full list is shown, with category labels visible on each row.
- Non-refereed items (proceedings, abstracts, ASCL, eprints) are shown only when "Refereed only" is off.

## Home page

- Only the 4 pinned papers appear, with thumbnails (see [02](02-content.md)), plus a link to `/publications`.
