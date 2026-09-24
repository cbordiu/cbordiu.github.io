# 01 — Architecture, hosting, deployment

## Stack: Astro

- **Decision**: [Astro](https://astro.build) static site generator, with content kept as data files
  (JSON/YAML) and rendered to plain static HTML. JavaScript is used only where it adds value:
  the theme toggle, the publication filters, and the starfield.
- **Why**: adding a paper, talk or press item means editing a data file, not HTML. The output is
  static and fast, and it works on GitHub Pages. The name is also a small pun on the astro theme.
- **Rejected**: hand-written HTML (too much upkeep); Jekyll/Hugo (the previous minimal-mistakes fork
  never got finished, and a heavy theme is what made it stall).
- **Toolchain**: Node 22 (available locally), npm. Python 3 for the data pipeline (see 05).

## Repository

- Repo: `cbordiu/cbordiu.github.io` (existing). The old minimal-mistakes fork has no real content.
- **Decision**: replace it with a fresh history. The new site is developed on a local orphan branch
  `new-site`. The existing `master` branch is left untouched until go-live.
- **Go-live** (irreversible, needs explicit approval of a local preview first):
  1. Force-push the new history to the default branch (currently `master`; the workflow also accepts `main`).
  2. The owner switches **Settings → Pages → Source** to *GitHub Actions* (a manual step).
  3. Delete the stale remote branches `gh-pages-2.2.1` and `gh-pages-3.1.6` (optional, after confirmation).
- A custom domain can be added later with a `CNAME` file. It is not needed now.

## Deployment

- A GitHub Action (the official `withastro/action` + `actions/deploy-pages`) builds and deploys on every push
  to the default branch.
- The data pipeline runs **locally**, not in CI, because Google Scholar scraping would be blocked
  from GitHub runners. CI only builds whatever data is committed.

## Analytics

- **Decision**: [GoatCounter](https://www.goatcounter.com): free, privacy-friendly, no cookies, no consent banner.
- The site code is the repository variable `GOATCOUNTER_CODE`, which the workflow passes to the build as
  `PUBLIC_GOATCOUNTER_CODE`. If it is unset, no script is injected.

## Language

- English only. A Spanish version was rejected because it doubles the upkeep for little gain with the target audience.
