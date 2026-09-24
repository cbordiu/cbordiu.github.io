# 03 — Visual design

## Direction: editorial serif, minimal

- The look is minimalist but elegant, close in feel to the typesetting of the owner's papers.
- **Typography**: a refined text serif (Newsreader or EB Garamond, self-hosted) for headings and body. A monospace
  font is used for small labels, dates, coordinates and metadata.
- There is plenty of white space and a narrow reading column. The alternatives, a modern sans or a dark-first
  "observatory" look, were rejected.

## Colour and themes

- **Themes**: light and dark. The system preference is followed by default, and a toggle overrides it (the choice is remembered
  per browser). The dark theme is a deep ink-blue, not pure black.
- **Accent**: a single **muted amber** ("starlight on ink"), used only for links, the active filter
  and the constellation stars. The owner may revisit this later.
- All colours are defined as CSS custom properties, so that retuning the palette means changing one file.

## Astro touches (all three, kept subtle)

1. **Constellation timeline**: the research trajectory is drawn as a constellation. Each position is a star,
   and faint lines join them in time order. The engineering years are dimmer, the astronomy years brighter. The current
   position is the brightest star. The drawing is an inline SVG, readable in both themes and on mobile, where it falls back to a
   vertical layout.
2. **Real-sky starfield**: bright stars from the actual sky around **Carina / η Car**, taken from a
   bright-star catalogue and projected, are drawn very faintly behind the hero with a slight parallax drift on scroll.
   It respects `prefers-reduced-motion`, and a static version is shown without JavaScript.
   Second revision (2026-09-24):
   - Stars are drawn as crisp cores. Bright ones (V < 3.8) get tapered four-point sparkles, so they read as stars rather than dust.
   - **Depth parallax on hover** (strengthened 2026-09-24): the stars sit in five layers by brightness, treated as
     distance, and drift with the pointer on hover devices with smoothing. The brightest stars are the foreground.
     The whole field also has a slight scroll parallax.

     | V (mag) | < 2 | 2–3 | 3–4 | 4–5 | ≥ 5 |
     |---|---|---|---|---|---|
     | Relative travel | 1.0 | 0.62 | 0.34 | 0.16 | 0.06 |

     Full travel is 48 px with the pointer at the hero's edge. η Car sits in the 0.62 layer.
   - **η Car is golden and slightly larger** (`--gold`): an 8-point sparkle with a slowly breathing gold glow. The ticks were removed.
   - The surname in the hero is set in `--gold`.
   - The margin coordinates showed **coordinates only, with no object names**, for mystery. This was superseded later that day:
     the section coordinates were removed entirely (see item 3).
   First revision (2026-09-24):
   - The stars were too faint, so they are now larger and brighter.
   - The brightest stars (V < 2.2) get a soft glow in dark mode only; in light mode it looked like smudges.
   - In dark mode, stars get a slight colour tint by B−V: bluish for B−V < 0, warm for B−V > 1.1.
   - About a third of the brighter stars twinkle slowly; this respects reduced-motion settings.
   - η Car is kept subtle: four faint amber ticks around the star, with no circle and no label. The coordinate line under the hero names it.
     The ticks are hidden on phones.
   η Car sits right of centre. Crux and α/β Cen spread to the
   east, on the left, with east on the left as on the sky. The field is 72° × 30°.
3. **Sky coordinates**: removed from all sections on 2026-09-24. Only the hero's "pointing" remains: the RA/Dec of
   η Car, without its name, linked to SIMBAD. The spectrum scroll-progress bar replaced them as the astro touch.

## Spectrum scroll-progress bar (added 2026-09-24)

- Chosen from a list of alternatives: spectral-line dividers, margin SEDs, frequency labels, beam ellipses.
- On the home page, the header's bottom edge is the baseline of a spectrum (`SpectrumBar.astro`).
  - As you scroll, the trace is revealed from left to right, and a small gold dot marks the scan position.
  - Each section adds one emission line at the scan position where that section reaches 40% of the viewport.
  - The lines are **unlabelled** (decided 2026-09-24): no identification is shown.
- The baseline is deterministic noise (`NOISE` = 3.2 px, light smoothing). The lines are narrow Gaussians (σ ≈ 1.1–2 px),
  and the Research line is double-peaked, like an expanding shell. Both were narrowed and made noisier on 2026-09-24.
- Each line's shape loosely follows a real transition, as an inside joke; the identifications are not shown anywhere:

  | Section | Line |
  |---|---|
  | About | CO J=2–1, 230.538 GHz |
  | Trajectory | ¹³CO J=2–1, 220.399 GHz |
  | Research | SiO v=0 J=5–4, 217.105 GHz |
  | Projects | HCN J=3–2, 265.886 GHz |
  | Software | H I, 1.420 GHz |
  | Selected papers | SO 6₅–5₄, 219.949 GHz |
  | Talks | CS J=5–4, 244.936 GHz |
  | Press | HCO⁺ J=3–2, 267.558 GHz |
  | Contact | N₂H⁺ J=3–2, 279.512 GHz |

- Without JavaScript there is no trace, just the plain header border. The header background went from 82% to 93% opacity so that content
  scrolling underneath doesn't compete with the trace.

## Dwell-to-reveal star names (added 2026-09-24)

- If you rest the pointer on a hero star for **1.5 s** (`DWELL` in `Starfield.astro`; shortened from 3 s), a thin gold ring draws around it,
  then a label fades in with the proper name (IAU, e.g. *Acrux*, *Hadar*), the designation (α¹ Cru), the spectral type and V.
  Stars without a proper name show only the designation or HR number. η Car shows "LBV, massive binary", in gold.
- The hit test takes the nearest star within 16 px, with bright stars favoured by 3 px per magnitude brighter than V = 4.
  Moving more than 30 px away hides the label. It only works on hover devices.
- Names come from `scripts/build_starfield.py`: BSC `Name` → Bayer/Flamsteed, and SIMBAD TAP `NAME` identifiers
  (by HR number), corrected with a small IAU/WGSN table. 15 of the 334 stars have proper names.

## Implementation notes

- **Greek glyphs**: Newsreader has no Greek, and a locally installed EB Garamond 08 drew Greek italic as blanks.
  The site therefore bundles `@fontsource/eb-garamond` Greek subsets (400, 400 italic), which the serif stack falls back to.
- The selected-paper posters no longer zoom the image on hover (changed 2026-09-24). Only the caption moves: the note
  slides in and the credit appears.

- Fonts are self-hosted through `@fontsource`: Newsreader Variable (optical sizes) and IBM Plex Mono 400/500.
- Paper figures on white backgrounds are slightly dimmed in the dark theme (`--figure-filter`).
- Measured contrast against the background: amber 4.8:1 (light) and 9.8:1 (dark); muted text 5.6:1 and 7.0:1.

## Principles

- Each astro touch must be noticeable to an astronomer and never distracting to anyone else.
- No heavy JavaScript libraries. The site must be fully readable with JavaScript disabled.
- It must be accessible: sufficient contrast in both themes, keyboard-usable filters, and visible focus states.
