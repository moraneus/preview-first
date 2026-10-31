---
name: preview-first
description: This skill should be used before building or restyling any website or web app UI. It shows the developer three to five complete design directions in the browser first (colour palette with verified contrast, typography, buttons and components, motion, a drafted page, and how it looks on popular iPhone, Samsung, Pixel, iPad and laptop screens), lets them tweak and pick one, then writes a design contract (design/DESIGN.md and tokens) that all later UI work follows. Triggers include building a landing page, starting a frontend, choosing colours or fonts, redesigning a site, wanting to see the design before coding, device previews, design systems and design tokens.
license: MIT
metadata:
  author: moraneus
  version: "0.5.0"
  repository: https://github.com/moraneus/preview-first
---

# preview-first

Look before you build. This skill inserts a design stage before any application code is
written: the developer sees several complete, clearly different design directions in their
browser, picks one, and the choice becomes a written contract that every later session follows.

This is a design studio stage, not a website generator. The skill never writes the developer's
application code. It produces a decision and a contract. Scripts are deterministic and
standard-library Python; judgement (reading the brief, naming directions, writing copy) is yours.

## When to run it, when to offer it

Run the full stage when the developer is about to start, restart or restyle a web project:
"build me a landing page for X", "start the frontend", "I don't like how this looks", "pick
colours and fonts", or an explicit `/preview-first`.

Offer it in one line when a project already has UI code but no `design/DESIGN.md`: "Want to
see design directions first? I can show the current look next to alternatives." If accepted,
import the existing look as a direction (see Imports) so it is compared on equal terms.

Never trigger it for small edits to an already styled app ("add a button", "fix the padding").
When `design/DESIGN.md` exists, skip to After handoff.

## The flow

All scripts live in this skill's `scripts/` directory. Run them with `python3` (or
`uv run python3` where a project uses uv). Paths below are relative to the project root.

### 1. Read the project, then ask at most four questions

Read what exists before asking anything: package.json, Tailwind config, CSS custom properties,
a logo SVG, existing fonts, a README. Anything found is a constraint, not a question.

Ask only what the repo cannot answer, in plain language, one message:

1. What is the product and who is it for, in one sentence.
2. Three words for how it should feel, or a site they admire.
3. Anything fixed: a brand colour, a logo, a font, light or dark only.
4. Which kind of page matters most: marketing, app, content or store.

### 2. Write the brief

Normalise the answers into `.design-preview/brief.json`:

```json
{
  "product": "Ledgerline, an invoicing tool for freelance developers",
  "audience": "solo developers and small studios",
  "product_type": "product-type.saas",
  "moods": ["precise", "calm", "trustworthy"],
  "page_type": "marketing",
  "constraints": {"brand_colors": ["#154d8c"], "fonts": [], "scheme": "both"},
  "admired": ["https://linear.app"],
  "words": {"name": "Ledgerline", "tagline": "Invoices that match your git log"}
}
```

Map free text to node ids with `recommend.py --list product-types` and `--list moods`.
Unknown words are fine; the recommender falls back by alias and token overlap. Free text in
`product_type` is accepted too.

### 3. Open the preview within a minute: quick start

```bash
python3 <skill>/scripts/quick_start.py --brief .design-preview/brief.json --count 4 --open
```

One command recommends bundles, authors `directions.json` with the styles' names and honest copy
derived from the brief, builds the preview and starts the server. Give the developer the URL
immediately; do not make them wait for hand-written copy. Then, while they look, refine
`directions.json` (names, rationale, copy, layout) and rebuild; the page refreshes to the same
URL. Steps 3a and 4 describe what quick start does and what to refine.

The gallery has a **Surprise me** button: it asks the local server for a randomly composed
direction (an unused style, a fitting palette and pairing, a random draw of ideas and section
variants) and opens it. The developer can draw as often as they like and select any draw. The
same thing from the terminal: `random_direction.py --directions .design-preview/directions.json --build .design-preview`.

### 3a. Candidate bundles by hand

```bash
python3 <skill>/scripts/recommend.py --brief .design-preview/brief.json --count 4
```

Each bundle is a style, palette, type pairing, component treatments, motion patterns, icon
set and eight to twelve design ideas (`ideas`: sourced moves such as a split nav with live
time, a specimen hero, giant numerals, film grain, bracket buttons, a colophon footer), with
the graph edges that justified it and live alternatives for swapping. Diversity is
enforced: distinct style families, at most two palettes of one temperature, at most two
pairings of one type category, no palette or pairing used twice. Three to five bundles by default, up to eight when the developer asks to see more. Do not
drop below three; if the brief is narrow (dark only, one brand colour), say so and still show three.

### 4. Author directions.json

Turn bundles into `.design-preview/directions.json` (schema in `knowledge/schema.json`,
`files.directions`). For each direction supply what a script cannot:

- `name`: an idea, not a style ("Ledger", "Greenhouse", "Night shift"). Never "Modern" or "Clean".
- `rationale`: one paragraph that quotes the brief's own words and says why this direction
  answers them. Mention the one bold choice and what stays quiet.
- `copy`: real copy from the brief: headline, subhead, two calls to action, four nav labels,
  three to six features with a title and one sentence each, an honest proof line (or empty),
  a form title with field labels and submit text, a footer line. Sentence case, active voice,
  product nouns, no em dashes, no emoji, no arrows, no "Whether you are X or Y", no tricolons,
  no lorem ipsum, no invented numbers. Copy is the same across directions unless a direction's
  voice genuinely differs.
- `layout` (optional): override section variants; otherwise the direction's ideas and then the
  style's defaults choose them.
- `bundle.ideas` (keep or edit): the ideas the recommender attached. Drop one that does not fit
  the product, add one from `recommend.py --list ideas` when the brief or an admired site asks
  for it. Ideas with a render hook change the draft; the rest go to the contract.
- `copy.numbers` and `copy.stats` (optional): sourced figures `{value, label, source}`; the
  numbers hero and the stat wall render only when these exist, never with invented figures.
- `copy.meta` (optional): `{"city": "Lisbon"}` for the split nav, colophon and overlay clock.
- The product type carries a topic kit (artwork kinds, a topic component such as a terminal, a
  balance, a schedule, a composer, a score board, and the product's nouns). The first screen and
  the section after it use it, so a scoreboard opens on a score and a shop on products. Set
  `layout.topic` to `none` to drop the topic component.
- `overrides` (optional): `{"brand_primary": "#hex", "brand_accent": "#hex"}` when the brief
  fixes a brand colour. The builder recomputes on-colours and reports any contrast failure.

Before building, run the anti-tell check in `references/anti-patterns.md` on every direction.
Refuse a tell unless the brief asked for it by name, and then say so in the rationale.

The first screen rule: no direction opens with the generic template (centred headline, two
buttons, a screenshot, then three identical cards). Each style defaults to a layout archetype
observed on admired sites (statement paragraph with captioned figures, type wrapping a flat
disc, product-first stage, display face beside an object, full-bleed art, sidebar index,
poster type) and to generated artwork drawn from the palette (blueprint, isometric figures,
terminal, Swiss composition, contours, halftone, orbit rings, stickers, sparklines, a single
mark). Keep those defaults unless the brief asks for the familiar look by name. At least two of
the directions come from styles marked `distinct`; the recommender enforces this, and it also
makes sure no two directions share a navigation device, a first-screen device or a texture.

### 5. Build and open the preview

```bash
python3 <skill>/scripts/build_preview.py --directions .design-preview/directions.json
python3 <skill>/scripts/serve_preview.py --dir .design-preview --open
```

`build_preview.py` writes `.design-preview/`: a gallery, and for each direction a style tile
(palette with contrast grades in both modes, type scale, spacing, radius, elevation, icons,
every component in every state, playable motion patterns), a drafted page for the brief's page
type, and a devices view that renders the draft inside CSS-drawn frames of the most popular
phones, foldables, tablets and laptops at true viewport sizes. Controls on every page swap
palette, type pairing, radius, density, motion level and theme live.

`serve_preview.py` starts a detached localhost server, writes `.design-preview/server.json`,
prints the URL and returns immediately. Add `--vendor-fonts` to the build for an offline
session; otherwise the tile shows a visible notice when a web font failed to load.

If the browser cannot open (SSH, container, CI), print the URL and the list of directions with
one line each, and continue in chat.

### 6. Tell the developer, then wait

Say what you built, give the URL, name the directions in one line each, and stop. Do not pick
for them, do not start coding, do not poll. The developer may spend a long time in the preview.
When they reply:

- If `.design-preview/selection.json` exists, read it. It holds the direction id and the live
  overrides (palette, pairing, radius, density, motion, theme) they ended on.
- Otherwise take the choice from their words ("B", "the dark one", "A but with D's type") and
  write `selection.json` yourself with the matching overrides.
- For a mutation ("B but warmer", "fewer rounded corners", "swap the headline font"), edit
  `directions.json` (or use an alternative from the bundle), rebuild, and point them back to
  the same URL. The server keeps running; ask them to refresh the page.
- For "show me more", run `recommend.py` again with `--count 5` or a changed brief, add the new
  directions under new ids, and rebuild.

`serve_preview.py --dir .design-preview --wait 1800` blocks until a selection exists, for
scripted use only. `--status` and `--stop` manage the server.

### 7. Export the contract

```bash
python3 <skill>/scripts/export_design.py --selection .design-preview/selection.json \
  --directions .design-preview/directions.json --project .
```

This writes `design/DESIGN.md` (the contract: identity, design ideas with sources and build
notes, palette with contrast table, typography,
spacing and radius, elevation, layout, every component with states and tokens, motion tokens and
allowed patterns, iconography, imagery, writing style, accessibility floor, device checks, and a
"do not" list), `design/tokens.json` (W3C Design Tokens format), `design/tokens.css`,
`design/tailwind.css` when Tailwind v4 is detected, a pointer line in CLAUDE.md, and a
`.gitignore` entry for `.design-preview/`. Re-export keeps the "Project notes" section and
copies the previous files to `design/history/`.

Confirm in one short message what was written and what the developer should commit (`design/`
and the CLAUDE.md line). Then build under the contract.

## After handoff

Whenever `design/DESIGN.md` exists:

- Read it before any UI change. Use `--pf-*` tokens from `design/tokens.css`, never raw hex,
  pixel or millisecond values in components.
- Keep to the allowed motion patterns and the motion level. Respect reduced motion.
- Run `contrast.py FG BG --role body|label|large|ui` on every new colour pair.
- Follow the "do not" list; when a request conflicts with the contract, say so and offer to
  re-run the stage rather than silently diverging.
- After a significant page is built, offer the device check: open
  `.design-preview/<id>/devices.html?url=http://localhost:PORT/path` to see the real page in the
  same frames. Pages that send frame-blocking headers cannot be shown; say so.
- Keep `design/DESIGN.md` free sections (below the end marker) for project decisions.

## Imports

To compare the project's current look, or a site the developer admires, as a direction:

```bash
python3 <skill>/scripts/import_direction.py --css src/styles.css --into .design-preview/directions.json --name "Today"
python3 <skill>/scripts/import_direction.py --tailwind tailwind.config.js --into .design-preview/directions.json
python3 <skill>/scripts/import_direction.py --tokens design-tokens.json --into .design-preview/directions.json
python3 <skill>/scripts/import_direction.py --url https://example.com --into .design-preview/directions.json --name "Reference"
```

The import derives a palette, pairing and nearest style, then rebuild. Imported palettes are
checked like any other; failures appear in the tile.

## Knowledge and refresh

Decisions come from `knowledge/graph.json`: styles, palettes (OKLCH, both modes), type pairings,
component treatments, motion patterns, product types, moods, icon sets, platform features,
reference sites, joined by weighted `pairs_with`, `suits`, `avoid_with`, `requires`,
`expresses` and `defaults_to` edges. `knowledge/devices.json` holds the device catalogue.
`validate_graph.py` checks schema, references and palette contrast; run it after any edit.

Live data (font popularity, Baseline status, library releases, design feeds) lives in
`knowledge/live/` (bundled snapshot, refreshed weekly by CI) and in the user cache. When
`refresh_knowledge.py --status` reports `stale: true` and the network is available, run
`refresh_knowledge.py` once at the start of the stage. When the developer asks what is current
right now, search the web for recent examples of their product type and bring back two or three
concrete observations (palette, type, layout) to inform the rationale; do not scrape galleries
into the graph.

## Quick reference

| Script | Purpose | Key flags |
|---|---|---|
| `recommend.py` | Brief to ranked, diverse bundles | `--brief`, `--count`, `--list` |
| `build_preview.py` | directions.json to `.design-preview/` | `--directions`, `--out`, `--vendor-fonts` |
| `serve_preview.py` | Local server, selection endpoint | `--open`, `--wait`, `--status`, `--stop` |
| `export_design.py` | Selection to `design/` contract and tokens | `--selection`, `--directions`, `--project` |
| `import_direction.py` | Existing look to a direction | `--css`, `--tailwind`, `--tokens`, `--url`, `--into` |
| `contrast.py` | Grade a colour pair | `FG BG --role` |
| `palette.py` | Library: palette resolution and token CSS (used by build and export) | imported, no CLI |
| `validate_graph.py` | Check the knowledge graph | `--strict` |
| `refresh_knowledge.py` | Pull live data | `--status`, `--bundled` |

## Common mistakes

- Showing one direction. The value is the comparison; always three to five.
- Directions that share a family or differ only in colour. Check the family, temperature,
  type category and hero archetype before building.
- Overriding a style's layout defaults back to "centered" plus "columns" because it is safe.
  That is the generated look the developer came here to avoid.
- Lorem ipsum or generic copy. The draft must read like the product.
- Starting to code before a selection exists, or picking for the developer.
- Forgetting the wait: after opening the preview, stop and let them look.
- Overwriting hand-written notes in DESIGN.md. Only the exporter touches the generated block.
- Treating a brand colour that fails contrast as fine. Show the warning and offer a darker step.
- Using a tell because it is fast: purple gradients, Inter by default, emoji icons, all-caps
  eyebrows, three identical cards, scroll-reveal everywhere, arrows on links.

## References

- `references/process.md`: the stage in detail, with the exact questions, message templates and edge cases.
- `references/anti-patterns.md`: the tells list, the refusal rule and the pre-show checklist.
- `references/archetypes.md`: the first-screen archetypes, section archetypes and generated artwork, with the sites they come from.
- `references/ideas.md`: the design ideas graph, how directions get their ideas, the render hooks and how to author an idea.
- `scripts/quick_start.py` and `scripts/random_direction.py`: the one-command open and the random draw described in step 3.
- `references/color.md`: OKLCH palettes, roles, contrast policy, dark mode, brand overrides.
- `references/typography.md`: pairing rules, scales, measures, loading, licences.
- `references/motion.md`: levels, durations, easings, springs, view transitions, reduced motion.
- `references/components.md`: the treatment vocabulary and component specifications.
- `references/layout.md`: breakpoints, grids, density, page types and layout variants.
- `references/devices.md`: the device catalogue, frames, defaults and how to add a device.
- `references/handoff.md`: the DESIGN.md sections, marker contract and token formats.
- `references/platform.md`: CSS features the skill relies on and their Baseline status.
