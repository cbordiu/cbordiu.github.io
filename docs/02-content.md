# 02 — Content and structure

## Structure (hybrid)

- **`/`** is one compact, elegant page with the sections below, in this order.
- **`/publications`** is the full, filterable list (see [04](04-publications.md)).
- Each home section is a short version that links onward where relevant.

## Identity

- Name: **Cristóbal Bordiú**, with accents. In author lists the site matches the ADS form "Bordiu, C".
- Position: **Postdoctoral researcher, Instituto de Astrofísica de Andalucía (IAA-CSIC)**, Granada,
  since 05/2026. This is the **only** affiliation shown; INAF-OACt appears as a collaboration, not an affiliation.
  Context: CSIC4SKA project, Spanish SKA Regional Centre (espSRC) team.

## Hero

- A roles line above the name: **(Sub)mm & radio astronomer / Software engineer** (`roles` in `profile.yaml`).
- Name (surname in gold), then the position line "Postdoctoral researcher · IAA-CSIC, Granada", then the tagline:
  > I study how massive stars shape their surroundings, and build tools for the radio sky of the SKA era.
- **Portrait**: `public/portrait.webp`, a 480×480 square crop of the owner's photo, shown as a circle.
- The faint Carina starfield sits behind the hero (see [03](03-visual-design.md)).
- A quiet metrics line: refereed papers · h-index · citations (source noted; see [05](05-data-pipeline.md)).

## About

- Three paragraphs, set large at a light weight (300):
  1. The "engineer turned astrophysicist" story.
  2. Two research threads. Revised 2026-09-24 to name the focus: early-type evolved massive stars (LBVs, B[e] supergiants)
     and the lifecycle of dust and molecules in their outskirts. The second thread is the Galactic radio sky and the software for it, plus the current IAA role.
  3. Added 2026-09-24: deep learning for astronomical data analysis, and LLMs as tools for scientific research.
- **Accented phrases**: `*asterisks*` in `profile.yaml` mark key phrases, shown in the accent colour and revealed by the scroll effect too.
  Trailing punctuation stays in plain ink.
- The current role is described as "within the AMIGA group and the Spanish SKA Regional Centre", replacing the mention of CSIC4SKA
  (2026-09-24). The trajectory detail line was changed to match.
- **Scroll effect** (added 2026-09-24, inspired by iliatopuriaoficial.com): words start faint and turn bold and fully
  coloured as they cross a line at 66% of the viewport height. The bolding is a text stroke rather than a font-weight change, so the lines never reflow.
  Without JavaScript, or with reduced motion, the text is simply shown normally.

## Research trajectory (the constellation)

- **Decision**: the full path is shown, framed as the engineer → astrophysicist arc.
- **Why**: it is distinctive, and it explains the software/SKA side of the profile.
- The engineering years are drawn as dimmer stars, the astronomy years as brighter ones.
- **Institution logos** (added 2026-09-24) sit in their own column **between the star and the text**, centred on the role
  title like the stars. They are IAA-CSIC (the oval "IAA" mark only), INAF, UCM, VIU, Telefónica and Universidad de Oviedo (its coat of arms).
  Each is a single-colour alpha mask in `public/logos/*.png`, tinted with the theme's muted ink through CSS `mask`, and turns
  full ink on row hover. Sources: the IAA logo from iaa.csic.es (the IAA mark only); INAF, the UCM coat of arms, VIU and
  Telefónica and Oviedo from Wikimedia Commons. They are used only to identify affiliations.
- Each star is vertically centred on its role title (`--sy` in `Constellation.astro`), and they follow a gentle zig-zag
  (40–66 % of the star column). Tightened 2026-09-24.

| Period | Role | Where |
|---|---|---|
| 2008–2014 | Telecommunication Engineering | Universidad de Oviedo |
| 03/2014–03/2020 | Software Engineer | Eleven Paths (Telefónica) |
| 2014–2016 | MSc Astronomy & Astrophysics (TW Hya disk rotation with ALMA) | Universidad Internacional de Valencia |
| 10/2016–12/2021 | PhD in Astrophysics, cum laude (LBV mass loss, (sub)mm view) — advisor J. R. Rizzo | Universidad Complutense de Madrid / CAB (INTA-CSIC) |
| 03/2020–05/2026 | PhD student, then postdoctoral fellow (from 12/2021) — Radio Group | INAF – Osservatorio Astrofisico di Catania |
| 05/2026– | Postdoctoral researcher (CSIC4SKA, espSRC) | IAA-CSIC, Granada |

Source for this table: the owner's CV, ORCID, and the owner's own answers.

## Research lines (editorial list)

Revised 2026-09-24: the image cards were replaced with a text-only list, laid out **2×2** on wide screens and one column below 52rem.
Each line carries exactly **three keywords**. Each entry has a small line-drawn **symbol**
instead of a numeral (`symbol:` in `profile.yaml`, drawn in `LineSymbol.astro`), a large serif title, a mono keyword line,
2–3 sentences, and links to its key papers. There are no images and no coordinates.

| Line | Symbol |
|---|---|
| Evolved massive stars | four-point star |
| Galactic radio sky | clumpy (dashed) ring |
| Deep learning | small neural network |
| SKA simulation | radio dish |

1. **Evolved massive stars and their circumstellar medium**: LBVs, η Car, AG Car, HD 87643,
   and the ULISSES ALMA programme (80 h).
2. **The Galactic radio sky with MeerKAT**: the SMGPS Extended Source Catalogue, Kýklos, compact radio rings.
3. **Deep learning for radio astronomy** (added 2026-09-24): unsupervised SNR population, source detection,
   RADiff diffusion models, and semi-supervised classification of evolved stars. Key papers: Bufano+ 2024 A&A,
   Sortino+ 2024 IEEE TAI, Riggi+ 2024 PASA.
4. **Simulating the SKA**: skasim, CSIC4SKA / espSRC.

## Software (compact list, linked to GitHub)

- **skasim** (espsrc_ska_simulator), synthetic SKA observations.
- **mufasa**, Multiwavelength Fast SED Assembler.
- **caesar-rest / CIRASA**, source-finding services (ascl:2108.009).
- **NEANIAS** visual-analytics services (H2020).

The section ends with a link to the GitHub profile, https://github.com/cbordiu (`github:` in `profile.yaml`), with the GitHub mark in the accent colour.

Only software the owner leads is listed; collaborations on other people's projects are not.

## Pinned papers (home page)

- **Latest publication** (added 2026-09-24): a card above the posters shows the newest refereed article of any role,
  taken from `papers.json`, so it updates automatically with the ADS pipeline. It shows the month and year, title,
  short authors and venue, with a pulsing gold beacon; the animation is off with reduced motion.

Revised 2026-09-24: shown as four portrait "posters" in a 4×1 row. Each has a public outreach image of the object,
with the year, journal and title over a dark gradient; a one-line note and the credit appear on hover.
The layout is 2×2 on tablets and a horizontal swipe row on phones. The earlier figures from the papers are no longer used.

| Paper | Image | Credit / licence |
|---|---|---|
| Bordiú et al. 2026, ApJL 1005, L34 (HD 87643) | ESO eso0928a, reflection nebula around HD 87643 | ESO, CC BY 4.0 |
| Bordiú et al. 2025, A&A 695, A144 (SMGPS ESC) | MeerKAT Galactic Centre mosaic | I. Heywood, SARAO (press image, used with credit; no explicit licence) |
| Bordiú et al. 2024, A&A 690, A53 (Kýklos) | Cleaned-up MeerKAT L-band image of Kýklos, as published by IFLScience | C. Bordiú (INAF), the owner's own image |
| Bordiú et al. 2022, ApJL 939, L30 (η Car) | Hubble UV image of the Homunculus (heic1912a) | NASA, ESA, N. Smith, J. Morse; CC BY 4.0 |

The Kýklos slot first used the JWST WR 124 image as an illustrative stand-in. On 2026-09-24 it was replaced by the owner's
own MeerKAT image, cropped to 3:4 around the ring. The images are in `public/images/` as 720×960 WebP.

## Talks and conferences

- `src/data/talks.yaml` holds the complete list from the owner's CV (updated 2026-09-24): 23 contributions from 2018 to 2026.
  Fields: year, month, event, place, title and `kind`: oral (the default), invited, poster, or selected
  (the ESO Hypatia Colloquium, one of 40 talks chosen from over 200 applicants).
- The home page shows a summary line ("23 contributions · 2 invited") and the latest 6 talks. The rest sit behind a
  "Show all" disclosure, a native `<details>` element that needs no JavaScript. Invited and selected talks get an amber
  badge, and posters a grey one.

## Projects (added 2026-09-24)

- This is a new section, placed **after Software** (reordered 2026-09-24), split into **As principal investigator** and **As contributor**.
  Stored as `projects.pi` / `projects.contributor` in `profile.yaml`.
- Each row shows the period, title, funder (with the grant ID, and the PI for contributor projects) and a one-line role.
  PI projects get a gold ✦ and an amber period.
  - PI: two INAF Ricerca Fondamentale grants (2022–2024 evolved-star ML search; 2024–2026 MeerKAT radio shells).
  - Contributor: SKA precursors and MeerKAT+ (INAF, 2023–2026), Spanish VO, CAB–PRIMA, H2020 NEANIAS, CAB–SPICA.
- Section order: 01 About, 02 Trajectory, 03 Research, 04 Software, 05 Projects, 06 Selected papers (also the Publications page),
  07 Talks, 08 Press, 09 Contact.

## Outreach and press

- A hand-maintained YAML file. Seeded with coverage by CAB, MediaINAF, Phys.org and Space.com. The owner will complete it.

## Contact

- Links only: **ORCID**, **Google Scholar**, **NASA ADS**. No email, no GitHub, and no LinkedIn in the contact row.
  - ORCID: https://orcid.org/0000-0002-7703-0692
  - Scholar: https://scholar.google.es/citations?user=W18yO88AAAAJ
  - ADS: an author query on the ORCID.

## Open items for the owner

- Press: add links and any missing items.
- Manual works in `overrides.yaml`: verify the author positions of the two NEANIAS papers and the 2026 book chapter.

## Footer

- "© {year} Cristóbal Bordiú and Claude", with no institution because this is a personal site (changed 2026-09-24), followed by a small inline pixel-art **Clawd** (the Claude Code mascot) in Claude
  orange. Unicode has no Clawd emoji, so it is an SVG drawn in `Footer.astro`.

## Explicitly out of scope (for now)

- Blog / notes (blogs are what made the previous attempt stall).
- A downloadable PDF CV.
- Observing-time-as-PI section (can be added later; the data is known: 9 proposals, >200 h).
