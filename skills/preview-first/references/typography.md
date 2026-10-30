# Typography

Rules Claude applies when choosing, authoring and loading a type pairing for preview-first. Pairings live in `knowledge/graph.json` as `type-pairing.*` nodes; `scale_tokens` in `scripts/palette.py` turns one into `--pf-font-*`, `--pf-text-*`, `--pf-leading-*` and `--pf-measure` tokens.

## Pairing rules

- One or two families, never three. A mono face for code, paths, IDs and timestamps is the only permitted third (`mono` field).
- Body is a grotesque, neo-grotesque, humanist or geometric sans, or a system stack. Serif body is allowed only for long-form content pages and raises `--pf-leading-normal` to 1.6 automatically.
- Personality lives in the display face. The heading carries the idea (serif, mono, display, condensed grotesque); the body stays quiet and even. Source: https://www.gleamstudio.design/blog-post/font-trends-2026.
- The two faces must be clearly distinct in category or clearly siblings. Pair across categories (serif over sans, mono over sans) or inside one superfamily (`Geist` over `Geist`, `DM Serif Display` over `DM Sans`). Two unrelated sans faces that nearly match is the one pairing that always looks like a mistake.
- Match stress. Old-style and transitional serifs (broad-nib stress) sit well on humanist or grotesque sans. Didone serifs (vertical stress) need a geometric or neo-grotesque body; Didone plus humanist clashes. `type-pairing.playfair-display-dm-sans` and `type-pairing.gloock-manrope` show the rule; `type-pairing.eb-garamond-onest` shows the harmonious case.
- Match x-height. When the heading x-height is small (Cormorant, Garamond), let whitespace carry the page and keep the body a plain narrow grotesque.
- Single-weight display faces (Instrument Serif, Young Serif, Gloock, Anton, Archivo Black, Cal Sans) get one job: the H1 and perhaps the H2. Everything below is the body family.
- Upright roman for H1 by default. Italic display is a deliberate accent, never the whole headline.
- Decide on the heading first by mood, then pick the body for legibility at 14 to 16px, then check the pair at 1x on a phone frame before committing.

## Categories used in the graph

`face.category` enum from `knowledge/schema.json`:

| Category | Shape | Typical role | Examples in the graph |
|---|---|---|---|
| grotesque | Early sans, some irregularity, closed apertures | Heading or body | Work Sans, Hanken Grotesk, Instrument Sans, Archivo, Chivo, Host Grotesk, Bricolage Grotesque, Schibsted Grotesk, IBM Plex Sans |
| neo-grotesque | Smoothed, neutral, large x-height | Body, product UI | Inter, Inter Tight, Geist, Roboto Flex, Public Sans, Be Vietnam Pro |
| humanist | Calligraphic stress, open apertures | Body, long reading, accessibility | Source Sans 3, Nunito Sans, Onest, Lato, Atkinson Hyperlegible Next |
| geometric | Circles and straight lines | Body or friendly heading | Figtree, DM Sans, Manrope, Albert Sans, Plus Jakarta Sans, Outfit, Sora, Rethink Sans, Funnel Sans, Satoshi |
| serif-old-style | Diagonal stress, low contrast, bookish | Heading, editorial body | Fraunces, EB Garamond, Cormorant Garamond, Libre Caslon Text, Young Serif |
| serif-transitional | Upright stress, moderate contrast | Heading, long-form | Newsreader, Source Serif 4, Literata, Lora, Instrument Serif, DM Serif Display |
| serif-didone | Vertical stress, hairlines | Display only, large | Playfair Display, Gloock |
| serif-slab | Heavy square serifs | Heading, documentation | Roboto Slab, Zilla Slab, Bitter |
| mono | Fixed pitch | Code, data, developer headings | JetBrains Mono, IBM Plex Mono, Geist Mono, Martian Mono, Space Mono, Azeret Mono |
| display | Built for one size | H1 only | Syne, Unbounded, Archivo Black, Anton, Clash Display, Cal Sans |
| system | OS native | Zero-request shells | system-ui, ui-serif, ui-sans-serif, ui-monospace |

Diversity rule from the recommender: at most two pairings of one heading category across the directions shown.

## Scale

`scale_ratio` sets a modular scale from 1rem. `TYPE_STEPS` in palette.py emits:

`--pf-text-xs` (ratio to the minus 2), `--pf-text-sm` (minus 1), `--pf-text-base` (1rem), `--pf-text-lg` (power 0.5), `--pf-text-xl` (1), `--pf-text-2xl` (2), `--pf-text-3xl` (3), `--pf-text-4xl` (4), `--pf-text-5xl` (5).

| Ratio | Name | 5xl at 16px base | Use when |
|---|---|---|---|
| 1.2 | Minor third | 40px | Dense apps, dashboards, docs, tables, terminal-style headings. Many levels must fit in little space |
| 1.25 | Major third | 49px | The default for marketing and product pages; headings clearly bigger, body still dominant |
| 1.333 | Perfect fourth | 67px | Editorial and brand pages where the H1 is the image; serif or quirky display heading |
| 1.414 | Augmented fourth | 90px | Poster type, one headline per screen, display faces (Syne, Anton, Clash Display, Gloock) |

Rules:
- Set `font-size: clamp()` on the top two steps only: `clamp(2rem, 1.2rem + 3vw, var(--pf-text-5xl))`. Lower steps stay fixed so UI stays predictable.
- Minimum body size 16px on marketing and content pages, 14px in dense app tables (`--pf-text-sm`), 12px (`--pf-text-xs`) only for captions and badges.
- Every step in a direction comes from the token; no ad hoc 17px or 22px.
- Weight carries hierarchy before size. A 500 label next to a 400 value is a step without a size change.

## Measure and leading

Tokens: `--pf-measure` (from `measure_ch`, 60 to 68), `--pf-leading-tight` 1.15, `--pf-leading-normal` 1.5 (1.6 when the body category starts with `serif`), `--pf-leading-loose` 1.75.

- Prose and feature paragraphs: `max-inline-size: var(--pf-measure)`. 60 to 68 characters per line (Vercel: 60 to 68ch, https://vercel.com/design.md). Shorter measure (60 to 62) for large display faces and wide geometrics; longer (66 to 68) for reading serifs and humanist sans.
- Headings: `line-height: var(--pf-leading-tight)`, `letter-spacing` from 0 at 32px to minus 0.02em at 64px and above for grotesques; serifs and display faces keep 0 unless the face was drawn tight.
- Body: `--pf-leading-normal`. Longer measure gets taller leading.
- Captions and UI labels: 1.3 to 1.4.
- `text-wrap: balance` on headings up to four lines; `text-wrap: pretty` on paragraphs where supported (see references/platform.md). Balance costs layout time; never apply it to body text.
- Headings are sentence case. No letter-spaced uppercase eyebrows above the H1.

## Weights

- Load two or three weights per face, five files total at most. The graph lists the exact weights (for example Fraunces 500, 600, 700 over Figtree 400, 500, 600).
- Body 400, body emphasis 500 or 600, headings 600 or 700. Avoid 300 for anything under 24px on screen.
- Variable fonts (Fraunces, Inter, Roboto Flex, Literata, Newsreader, Bricolage Grotesque) ship one file: request a range `wght@400..700` on css2 and set `font-optical-sizing: auto` so the optical-size axis engages.
- Never synthesise bold or italic: declare `font-synthesis: none` when the loaded set lacks a style.

## Tabular numerals

- Any column of numbers, timer, price list, dashboard tile, table cell or counter: `font-variant-numeric: tabular-nums;`. Add `slashed-zero` for IDs and codes.
- Check the chosen face has tabular figures (Inter, Geist, Roboto Flex, Public Sans, Source Sans 3, IBM Plex, Manrope, JetBrains Mono do; many display serifs do not). When the heading face lacks them, set numerals in the body or mono face.
- Mono is for code, paths, IDs, hashes and timestamps, not for labels that happen to be technical (Vercel rule, https://vercel.com/design.md).

## Loading

Google Fonts (`face.source: "google"`), using the node's `css_url`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Figtree:wght@400;500;600&display=swap">
```

Rules: one `<link>` with every family in it, `display=swap` always, weights listed explicitly, in `<head>` before any stylesheet that uses the families. Source: https://developers.google.com/fonts/docs/css2.

Self-hosting (preferred for production, required for Fontshare faces):

```css
@font-face {
  font-family: "Satoshi";
  src: url("/fonts/Satoshi-Variable.woff2") format("woff2");
  font-weight: 300 900;
  font-style: normal;
  font-display: swap;
}
```

Add `<link rel="preload" as="font" type="font/woff2" href="/fonts/Satoshi-Variable.woff2" crossorigin>` for the body face only. Fontsource packages (`face.source: "fontsource"`) wrap the same approach: `npm i @fontsource-variable/figtree` then `import "@fontsource-variable/figtree";` (https://fontsource.org/docs/getting-started/install).

Fallback stacks: every pairing declares `fallback_heading` and `fallback_body`, and `scale_tokens` writes them into `--pf-font-heading` and `--pf-font-body`. Mono falls back to `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`. Pick a fallback with similar width (Georgia for transitional serifs, Arial or Helvetica for grotesques, Verdana for wide humanists) and add `size-adjust` and `ascent-override` on a named fallback `@font-face` when layout shift matters (https://developer.chrome.com/blog/font-fallbacks).

`build_preview.py --vendor-fonts` downloads the faces for an offline preview; otherwise the tile shows a visible notice when a web font failed to load.

Two system pairings (`type-pairing.system-ui-stack`, `type-pairing.system-serif-stack`) cost zero requests and are the honest choice for app shells, glass companions and anything that must paint instantly.

## Licences

Record the licence in the `license` field and check it before shipping, not after.

- OFL 1.1 (SIL Open Font License): free for commercial use, web embedding and bundling; may not be sold on its own; reserved font names apply when modified. Nearly all Google Fonts. https://openfontlicense.org
- Apache 2.0: Roboto, Roboto Flex, Roboto Slab and a few others. Free for any use with attribution in the notice file. https://www.apache.org/licenses/LICENSE-2.0
- Fontshare (ITF Free Font License): Clash Display, Satoshi, General Sans and the rest of the Indian Type Foundry free set. Free for personal and commercial use, web embedding included; no redistribution, no resale, no modification; download from fontshare.com and self-host. https://www.fontshare.com/licenses/itf-ffl
- System faces: no licence step; you are using what the OS provides.
- Commercial faces the research names (Söhne, Tiempos, Editorial New, GT America) need a paid web licence per domain or pageview tier; never list them in a pairing node without `source: "self-hosted"` and a note that the developer owns the licence.

## Typography tells to avoid

Sources: https://github.com/ravidsrk/slop-detect, https://tenex.studio/en/blog/ai-slop-8-signs/, https://www.925studios.co/blog/ai-slop-8-signs/.

- Inter everywhere. Inter, Geist or Space Grotesk as an unchosen default for heading and body with nothing else going on. `type-pairing.inter-tight-inter` and `type-pairing.geist-geist` are allowed when the direction earns them with a distinct accent and real product imagery; otherwise reach for `type-pairing.host-grotesk-funnel-sans` or `type-pairing.schibsted-grotesk-inter`.
- Oversized italic serif headline. The 80px italic Instrument Serif or Fraunces H1 over a grotesque body is the current editorial cliche. Keep display serifs upright, under 64px on desktop, and use italic for one word at most.
- Centered hero in a generic sans with a letter-spaced uppercase eyebrow.
- Three faces, or two sans faces that almost match.
- Mono for labels, nav and buttons on a page that is not a developer tool.
- Light (300) weights for body text; grey-on-grey captions under 12px.
- Space Grotesk alone (reserve `type-pairing.space-mono-space-grotesk` for brutalist pages).
- Script fonts on quiet-luxury directions.

## Adding a pairing node

Fields (schema.json, `node_kinds.type-pairing`):

- Common: `id` (`type-pairing.<heading>-<body>`), `kind: "type-pairing"`, `name`, `source`, `added`, `last_verified`, `confidence`.
- Required: `heading`, `body` (each a face object with `family`, `category`, `weights`, `source`), `fallback_heading`, `fallback_body` (CSS stacks without the family itself), `scale_ratio` (1.2, 1.25, 1.333 or 1.414), `measure_ch` (60 to 68), `license`.
- Optional: `mono` (face object), `css_url` (the full css2 link for Google faces; omit for Fontshare and system), `moods` (four or so words that match `mood.*` aliases), `notes` (one sentence saying why the two faces work together and any limit, such as a size cap), `live` (written by the refresh, do not author).

Procedure:

1. Confirm both families exist in `knowledge/live/fonts.json` when `source` is `google`; the refresh annotates `live.popularity_rank` and `live.trending` from it.
2. Set the exact weights the direction needs, not every weight the family offers.
3. Add `pairs_with` edges from one to three `style.*` nodes and `avoid_with` from styles it fights; attach `evidence` from a `reference-site.*` node where you have one.
4. Run `python3 <skill>/scripts/validate_graph.py --strict`. It checks the face objects, category and source enums, id shape and dates.
5. Build one preview and look at the H1, a paragraph and a table on the phone frame before merging.

## Pairing ids by heading category

Serif, old style: `type-pairing.fraunces-figtree`, `type-pairing.libre-caslon-text-work-sans`, `type-pairing.cormorant-garamond-hanken-grotesk`, `type-pairing.eb-garamond-onest`, `type-pairing.young-serif-rethink-sans`.

Serif, transitional: `type-pairing.instrument-serif-instrument-sans`, `type-pairing.newsreader-source-sans-3`, `type-pairing.source-serif-4-public-sans`, `type-pairing.literata-albert-sans`, `type-pairing.lora-nunito-sans`, `type-pairing.dm-serif-display-dm-sans`.

Serif, didone: `type-pairing.playfair-display-dm-sans`, `type-pairing.gloock-manrope`.

Serif, slab: `type-pairing.roboto-slab-roboto-flex`, `type-pairing.zilla-slab-lato`, `type-pairing.bitter-hanken-grotesk`.

Neo-grotesque: `type-pairing.inter-tight-inter`, `type-pairing.geist-geist`, `type-pairing.roboto-flex`.

Grotesque: `type-pairing.bricolage-grotesque-figtree`, `type-pairing.schibsted-grotesk-inter`, `type-pairing.host-grotesk-funnel-sans`, `type-pairing.chivo-be-vietnam-pro`, `type-pairing.archivo-archivo`.

Geometric: `type-pairing.plus-jakarta-sans`, `type-pairing.outfit-nunito-sans`, `type-pairing.sora-work-sans`, `type-pairing.manrope-ibm-plex-sans`.

Humanist: `type-pairing.atkinson-hyperlegible-next`.

Mono: `type-pairing.jetbrains-mono-inter`, `type-pairing.ibm-plex-mono-ibm-plex-sans`, `type-pairing.geist-mono-geist`, `type-pairing.space-mono-space-grotesk`, `type-pairing.martian-mono-public-sans`, `type-pairing.azeret-mono-albert-sans`.

Display: `type-pairing.syne-manrope`, `type-pairing.unbounded-onest`, `type-pairing.archivo-black-archivo`, `type-pairing.anton-work-sans`, `type-pairing.clash-display-satoshi` (Fontshare, self-host), `type-pairing.cal-sans-hanken-grotesk`.

System: `type-pairing.system-ui-stack`, `type-pairing.system-serif-stack`.

Scale ratios in use: 1.2 on the dense and reading pairings (Geist, Roboto Flex, Atkinson, Literata, Lora, Bitter, the mono-led set), 1.25 on most product and editorial pairings, 1.333 on the sharper editorial and bold grotesque pairings, 1.414 on the display and poster pairings.
