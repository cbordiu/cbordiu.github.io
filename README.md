# cbordiu.github.io

Research website of Cristóbal Bordiú — built with [Astro](https://astro.build), deployed to GitHub Pages.
Design decisions live in [`docs/`](docs/README.md).

## Develop

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static site in dist/
```

## Update content

| What | Where |
|---|---|
| Bio, trajectory, research lines, software, pinned papers, contact, sky coordinates | `src/data/profile.yaml` |
| Talks | `src/data/talks.yaml` |
| Press & outreach | `src/data/press.yaml` |
| Paper exceptions (category, hide, confirm/reject pending, manual works) | `src/data/overrides.yaml` |
| Figures | `public/figures/` |

## Update publications

```bash
python3 scripts/update_pubs.py            # fetch ADS + Scholar, commit & push if data changed
python3 scripts/update_pubs.py --dry-run  # show what would change
```

Needs `requests` and `pyyaml`, and an ADS token in `ADS_API_TOKEN` or `~/.ads/dev_key`.
Exit codes: `0` no change · `10` updated · `20` updated, new name-only matches in `src/data/pending.yaml` need review · `1` error.
See [docs/05-data-pipeline.md](docs/05-data-pipeline.md).

## Analytics

Set the repository variable `GOATCOUNTER_CODE` (Settings → Secrets and variables → Actions → Variables)
to your GoatCounter site code. Without it, no analytics script is included.
