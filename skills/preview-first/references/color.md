# Colour

Rules Claude applies when authoring, overriding or checking a palette for preview-first. Every palette in `knowledge/graph.json` is written in OKLCH, resolved to hex by `scripts/palette.py`, and graded by `scripts/contrast.py`. Tokens come out as `--pf-color-<role>` (hex) and `--pf-color-<role>-oklch`.

## Author in OKLCH

Write every colour as `oklch(L C H)`: L is lightness 0 to 1, C is chroma (0 is grey, 0.37 is the most saturated sRGB can hold at some hues), H is hue in degrees. Perceptual lightness means two colours with the same L look equally bright, so a palette stays coherent when hue changes. Source: https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl.

- Use three decimals for L and C and one for H, matching `format_oklch` in contrast.py: `oklch(0.975 0.010 80.0)`.
- Lightness is not contrast. A pair with L 0.21 on L 0.975 passes; a pair with L 0.55 on L 0.975 does not. Grade every pair, never eyeball it.
- `oklch_to_hex` clamps tiny gamut overshoot and otherwise reduces chroma by binary search until the colour fits sRGB, keeping L and H. Author within sRGB so the hex and oklch tokens agree; use `@media (color-gamut: p3)` only to raise chroma on accents, never to change hue or lightness.
- Build state variants with relative colour where supported, with a `color-mix()` fallback: `oklch(from var(--pf-color-primary) calc(l - 0.06) c h)` for hover, `color-mix(in oklab, var(--pf-color-primary) 90%, black)` for older engines. See references/platform.md.

### Lightness steps

Taken from `palette.paper-ink` and `derive_roles` in palette.py. Treat them as defaults, not laws; move a step when the grade demands it.

| Role | Light mode L | Dark mode L | Rule |
|---|---|---|---|
| bg | 0.97 to 0.985 | 0.16 to 0.18 | Never pure white or pure black |
| surface | bg minus 0.02 to 0.03 | bg plus 0.04 | Inset panels, sidebars, table stripes |
| surface_raised | bg or up to 0.99 | bg plus 0.08 | Cards, popovers, dialogs; in dark mode lighter means nearer |
| text | 0.20 to 0.22 | 0.93 to 0.95 | Warm or cool near-black, never `#000` |
| text_muted | text plus 35 percent of the gap to bg | same rule | Captions, help text, timestamps |
| border | bg minus 0.10 to 0.14 | bg plus 0.14 to 0.16 | Hairlines; pass the `ui` role against bg |
| primary | 0.26 to 0.52 | 0.72 to 0.88 | Dark enough for white text in light mode, light enough for dark text in dark mode |
| accent | 0.50 to 0.55 | 0.72 to 0.76 | One hue, used sparingly |
| success | 0.50 | 0.72 to 0.74 | Hue 150 |
| warning | 0.62 to 0.70 | 0.80 | Hue 75 to 80, always paired with dark text |
| danger | 0.52 | 0.70 to 0.72 | Hue 25 to 27 |
| focus | 0.50 | 0.76 | Must pass `ui` against bg in both modes |

### Chroma limits

- Tinted neutrals: 0.005 to 0.020 on bg, surface, surface_raised, border, text. Zero chroma reads as dead grey; above 0.02 the canvas starts to look coloured.
- Carry the same hue through all neutrals (paper-ink uses hue 80 for every neutral; slate palettes use 250 to 260). The tint is what makes a palette feel warm or cool.
- Text chroma 0.016 or less. Muted text keeps the same hue as text.
- Primary 0.02 (ink, charcoal) to 0.19 (ruby, poppy). Above 0.19 at mid lightness falls out of sRGB and gets clamped.
- Accent 0.12 to 0.17 in light mode, times 0.8 in dark mode.
- Status colours: success 0.13 to 0.14, warning 0.14 to 0.15, danger 0.19. Lower all three by 20 percent in dark mode.

## The 14 semantic roles

Defined in `ROLES` in palette.py and `palette_roles` in `knowledge/schema.json`. Every palette node must provide all 14 in both `light` and `dark`.

| Role | Token | Use it for | Never for |
|---|---|---|---|
| bg | `--pf-color-bg` | Page canvas, `<body>` | Cards |
| surface | `--pf-color-surface` | Sidebars, inset panels, zebra rows, code blocks, input fills | Text |
| surface_raised | `--pf-color-surface-raised` | Cards, popovers, dialogs, dropdowns, toasts | Page canvas |
| text | `--pf-color-text` | Body copy, headings, labels, icons at rest | Decorative fills |
| text_muted | `--pf-color-text-muted` | Captions, helper text, placeholders, secondary metadata | Anything a person must read to act |
| border | `--pf-color-border` | Hairlines, dividers, input edges, table rules | Text, icons |
| primary | `--pf-color-primary` | Primary button fill, links, selected tab indicator, active nav, chart series one | Large background washes |
| on_primary | `--pf-color-on-primary` | Text and icons sitting on primary | Anything else |
| accent | `--pf-color-accent` | The one highlight per view: a badge, a marked word, an illustrative stroke | Buttons (that is primary's job), body text |
| on_accent | `--pf-color-on-accent` | Text and icons sitting on accent | Anything else |
| success | `--pf-color-success` | Positive status: saved, paid, online. Pair with an icon or word | Branding |
| warning | `--pf-color-warning` | Caution status: expiring, degraded. Always dark text on it | Decorative |
| danger | `--pf-color-danger` | Destructive actions, errors, failed states | Emphasis in prose |
| focus | `--pf-color-focus` | `:focus-visible` ring, 2px solid, offset 2px | Hover |

Rules:
- Status colours carry meaning only with a second cue (icon, label, position). Colour alone fails WCAG 1.4.1.
- Tinted status badges: `color-mix(in oklab, var(--pf-color-success) 14%, transparent)` as background, status colour as text (see export_design.py component spec).
- Charts: primary first, then accent, then derive hues with relative colour by rotating `h` in 40 degree steps; never a rainbow.
- One accent per view. If two things need emphasis, one of them does not.

## Light and dark strategy

The same palette node carries both modes. Author light first, derive dark, then adjust by grading.

1. Same hue. Every role keeps its H in dark mode (`derive_roles` copies hue through).
2. Inverted lightness. bg 0.975 becomes 0.16 to 0.17; text 0.21 becomes 0.93 to 0.95; primary moves to at least 0.72, accent to at least 0.74.
3. Chroma times 0.8 on primary, accent and status colours. Saturated colour on near-black glows and vibrates; the same chroma that looks confident on paper looks neon on carbon. Neutral chroma caps at 0.02 (bg) and 0.02 (text).
4. Elevation by lightness. In light mode shadows show depth; in dark mode shadows vanish, so surface_raised must be visibly lighter than surface, which is lighter than bg.
5. `color-scheme: light dark;` on `:root`. `tokens_css` emits it so form controls, scrollbars and the UA default canvas follow the theme. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme.
6. Theme switching. `tokens_css` writes light under `:root`, dark under `[data-theme="dark"]`, and dark again under `@media (prefers-color-scheme: dark)` for `:root:not([data-theme="light"])`. Set `data-theme` on `<html>` to force a mode; leave it off to follow the system.
7. `light-dark()` for one-off values outside the token file: `color: light-dark(oklch(0.21 0.016 80), oklch(0.93 0.005 80));`. It needs `color-scheme` set on an ancestor and is Baseline newly available (Chrome 123, Firefox 120, Safari 17.5), so keep tokens as the primary mechanism and use `light-dark()` only inside components with a sensible single-colour fallback declared first.

Dark-mode failures to check by hand: medium grey body text on black (text L below 0.85), a brand primary left at light-mode lightness (unreadable as a link), warning yellow with white text, shadows used for elevation.

## Contrast policy

Two systems, one floor.

- WCAG 2.2 AA is the legal floor (the European Accessibility Act has applied since 28 June 2025). Nothing ships below it. Source: https://www.w3.org/TR/WCAG22/#contrast-minimum.
- APCA (Lc, 0.1.9) is the design check. It predicts legibility better, especially for dark mode and thin type, but it is not yet law. Source: https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html and https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.

`contrast.py` grades a pair under four roles. A pair is `ok` only when both systems pass.

| Role | Covers | WCAG minimum | APCA minimum (abs Lc) |
|---|---|---|---|
| body | Running text, paragraphs, table cells, inputs | 4.5 | 60 |
| label | Button and form labels, 14px or larger at medium weight | 4.5 | 45 |
| large | 24px or larger, or 19px bold; headings, display numerals | 3.0 | 45 |
| ui | Non-text: borders, focus rings, icons, chart strokes | 3.0 | 30 |

Pick the role by the smallest, lightest text that will sit on the pair. Muted captions are `body`, not `large`, when they run to a sentence.

The nine default checks (`palette_checks` in schema.json) run on every palette in both modes:
text on bg, text on surface, text on surface_raised (body); on_primary on primary, on_accent on accent (label); text_muted on bg (large); focus on bg, danger on bg, primary on bg (ui).

Run it:

```bash
python3 <skill>/scripts/contrast.py "#31302e" "#f6f5f4" --role body
python3 <skill>/scripts/contrast.py "oklch(0.985 0.008 80)" "oklch(0.26 0.025 260)" --role label
```

Output is JSON with `wcag`, `apca`, `wcag_pass`, `apca_pass`, `ok`, `wcag_level`. Grade every new pair a component introduces, not only the palette's defaults, and quote the numbers in DESIGN.md.

Extra pairs to grade by hand: text_muted on surface and surface_raised (body if it is a sentence), border on bg (ui), link primary on surface_raised (body), status text on its tinted badge (label), placeholder on input fill (body).

## Brand colour overrides

A brand colour arrives through the brief (`constraints.brand_colors`) and is applied as `overrides: {"brand_primary": "#hex", "brand_accent": "#hex"}` on a direction. `resolve_palette(palette, overrides)` in palette.py then:

1. Replaces `primary` (or `accent`) in both modes with the brand value, unchanged.
2. Recomputes `on_primary` (or `on_accent`) with `best_on_colour`, which picks whichever of `#ffffff` and `#111111` has the higher WCAG ratio against the fill.
3. Reruns all nine checks and appends a warning string for each failure, for example `light: on_primary on primary fails label contrast (WCAG 3.10, APCA 41)`.

The same hex is used in light and dark mode, so a brand colour tuned for white will usually fail `primary on bg` (ui) in dark mode or `on_primary on primary` (label) in light mode. Handle it like this:

- Fail on the fill (`on_primary on primary` below 4.5): keep the brand hue, darken the fill for buttons. Author a step with `oklch(from <brand> calc(l - 0.08) c h)` until it passes, and keep the original brand value for large fills and illustration where white text does not sit on it.
- Fail as text or stroke (`primary on bg` below 3.0): derive a text variant of the brand colour with lower L for light mode and higher L for dark mode; keep the exact brand colour for logos and large blocks only.
- Fail in dark mode only: lighten to L 0.72 or above and multiply chroma by 0.8, keep hue. Say so in the rationale.
- Yellow, lime, mint, sky, amber brand colours: `best_on_colour` will choose `#111111`. Design the button with dark text; do not fight it with white text and a shadow.
- Never ship with a warning left in `checks`. Show the developer the warning and the adjusted step, and ask which contexts keep the untouched brand value.

Radix's scale rule applies: step 9 solid colours in Sky, Mint, Lime, Yellow and Amber need dark text. Source: https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale.

## Adding a palette node

Fields (schema.json, `node_kinds.palette`):

- Common: `id` (`palette.<slug>`, lower-case and hyphens), `kind: "palette"`, `name`, `source` (URL or repo path), `added`, `last_verified` (ISO dates), `confidence` 0 to 1 (below 0.6 warns).
- Required: `temperature` (`warm`, `cool`, `neutral`), `scheme` (`light`, `dark`, `both`, meaning which mode the palette was designed around), `light` and `dark`, each a table of all 14 roles as `oklch(...)` or `#hex` strings.
- Optional: `hue_family` (one word: `blue`, `green`, `clay`), `notes` (one sentence on where it suits and any tell it flirts with).

Procedure:

1. Start from the closest existing node and change hue first, lightness second.
2. Author light, derive dark by the strategy above.
3. Add `pairs_with` edges from one to three `style.*` nodes (weight 0 to 1) and `avoid_with` edges from styles it would ruin; `pairs_with` and `avoid_with` edges expect `evidence` pointing at a `reference-site.*` node, otherwise the validator warns.
4. Run `python3 <skill>/scripts/validate_graph.py --strict`. It parses every colour, runs the nine checks in both modes, and errors on any failure, missing role, bad id or dangling edge.
5. Name it as two materials or a material and a signal (`Slate & Signal`), never as a mood.

## Palette ids by temperature and scheme

Warm, light: `palette.paper-ink`, `palette.moss-cream`, `palette.clay-bone`, `palette.olive-ivory`, `palette.cocoa-peach`, `palette.espresso-cream`, `palette.sage-linen`, `palette.brick-parchment`, `palette.sand-indigo`, `palette.poppy-cream`.

Warm, dark: `palette.obsidian-copper`, `palette.bronze-night`.

Warm, both: `palette.plum-linen`, `palette.forest-brass`, `palette.cherry-paper`, `palette.mustard-ink`, `palette.tangerine-slate`, `palette.butter-cobalt`, `palette.hazard-yellow`.

Cool, light: `palette.arctic-teal`, `palette.nordic-ice`, `palette.harbor-grey`.

Cool, dark: `palette.midnight-lime`, `palette.steel-cyan`, `palette.terminal-green`, `palette.lime-graphite`, `palette.mint-charcoal`.

Cool, both: `palette.slate-signal`, `palette.ocean-sand`, `palette.lavender-stone`, `palette.cobalt-paper`, `palette.navy-gold`, `palette.pine-chalk`, `palette.iris-fog`, `palette.marine-bone`, `palette.sky-tomato`.

Neutral, light: `palette.denim-wheat`, `palette.teal-sand`.

Neutral, dark: `palette.graphite-amber`, `palette.carbon-signal`.

Neutral, both: `palette.ink-coral`, `palette.ruby-chalk`, `palette.charcoal-saffron`, `palette.violet-ash`, `palette.rose-granite`.

Diversity rule from the recommender: at most two palettes of one temperature across the directions shown, and no palette used twice.

## Colour tells to avoid

Each is a known signature of unchosen, generated design. Sources: https://github.com/ravidsrk/slop-detect, https://www.925studios.co/blog/ai-slop-design-tells, https://tenex.studio/en/blog/ai-slop-8-signs/, https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p.

- Indigo to purple or blue to violet gradients, anywhere. Tailwind `indigo-500` as an unchosen primary.
- Gradient text in headlines. Gradient fills on buttons.
- Purple, blue or pink glow blobs behind a hero. Radial glows on dark canvases without a product image in front of them.
- Glass (`backdrop-filter`) with nothing layered behind it.
- Permanent dark mode with medium grey body text (text L under 0.85 on bg L under 0.2).
- Five or more gradient backgrounds on one page. Gold gradients on quiet-luxury directions.
- Cream canvas plus terracotta accent as a default (`palette.clay-bone` is allowed only when the brief asks for ceramics or craft by name, and the rationale says so).
- Gradient-initial avatars. Rainbow chart series.
- One word of the headline in a different colour as the only idea.
- The same grey shadow under every card; shadows used for elevation in dark mode.
- Pure `#000` on pure `#fff`, or any neutral with zero chroma next to tinted ones.

When a brief asks for one of these by name, use it once, deliberately, and write the reason into the direction's rationale.
