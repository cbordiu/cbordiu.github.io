# Design documentation

Design decisions for **cbordiu.github.io**, the research CV website of Cristóbal Bordiú.
Agreed in a design session on 2026-09-24. Update these files whenever a decision changes,
so they stay the single source of truth for *why* the site is the way it is.

| File | Covers |
|---|---|
| [01-architecture.md](01-architecture.md) | Stack, repository, hosting, deployment, analytics |
| [02-content.md](02-content.md) | Site structure and every content section |
| [03-visual-design.md](03-visual-design.md) | Typography, colour, themes, and the three astro touches |
| [04-publications.md](04-publications.md) | Paper categories, filters, publication page layout |
| [05-data-pipeline.md](05-data-pipeline.md) | ADS / Google Scholar update script run by a local agent |

## Decisions at a glance

- **Astro** static site, built by a GitHub Action, served from GitHub Pages at `cbordiu.github.io`.
- **Hybrid structure**: a compact one-page home + a full `/publications` page.
- **Editorial serif** look, light and dark themes (auto + toggle), one muted amber accent.
- **Astro touches**: constellation timeline, faint real-sky starfield (Carina), per-section RA/Dec margin notes.
- **Papers from NASA ADS**, classified First author / Key contributor / Co-author, plus a Refereed-only filter.
- **Citations**: headline totals from Google Scholar (ADS fallback), per-paper counts from ADS.
- **Updates** by a Python script run by a local agent, pushing straight to the default branch.
- **English only.** No blog, no downloadable PDF CV (for now).
