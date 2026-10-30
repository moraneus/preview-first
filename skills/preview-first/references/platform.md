# Platform

The CSS features preview-first relies on, their Baseline status, and how to use each without breaking older engines. Static values come from `platform-feature.*` nodes in `knowledge/graph.json` (caniuse, September 2026); live Baseline status comes from `knowledge/live/features.json` (web-features, fetched 2026-10-30). When the two disagree, the live file wins and the graph node is due a `last_verified` bump.

Baseline terms (https://web.dev/baseline): "widely" means available in all core browsers for at least 30 months; "newly" means available in all core browsers but not yet 30 months; "limited" means at least one core browser lacks it. Interop 2026 lists contrast-color(), attr(), shape(), scroll snap, container style queries, view transitions, scroll-driven animations and anchor positioning as focus areas, so expect the limited rows to move during the year.

## Feature table

| Node id | Baseline (live) | Chrome | Firefox | Safari | Global | Guard |
|---|---|---|---|---|---|---|
| `platform-feature.container-queries` | widely (high since 2025-08) | 105 | 110 | 16.0 | 95.9% | none needed; mobile-first fallback |
| `platform-feature.has` | widely (high since 2026-06) | 105 | 121 | 15.4 | 95.9% | `@supports selector(:has(a))` |
| `platform-feature.oklch` | widely (high since 2025-11) | 111 | 113 | 15.4 | 95.1% | hex declared first |
| `platform-feature.color-mix` | widely (high since 2025-11) | 111 | 113 | 16.2 | 94.8% | literal colour declared first |
| `platform-feature.relative-color` | newly (since 2024-09) | 125 | 128 | 18.0 | 93.5% | `color-mix()` fallback first |
| `platform-feature.light-dark` | newly (since 2024-05) | 123 | 120 | 17.5 | 91.3% | token pair fallback first |
| `platform-feature.property` | newly (since 2024-07) | 85 | 128 | 16.4 | 96.1% | works unregistered, just no interpolation |
| `platform-feature.starting-style` | newly (since 2024-08) | 117 | 129 | 17.5 | 93.1% | element simply appears |
| `platform-feature.popover` | newly (since 2025-01) | 114 | 125 | 17.0 | 93.6% | `@supports selector(:popover-open)` or polyfill |
| `platform-feature.text-wrap-balance` | newly (since 2024-05) | 114 | 121 | 17.5 | 94.0% | none needed; ignored when unsupported |
| `platform-feature.text-wrap-pretty` | limited | 117 | none | 26.0 | 87.6% | none needed; ignored when unsupported |
| `platform-feature.anchor-positioning` | limited | 125 (partial) | none | 27.0 | 87.4% | `@supports (anchor-name: --a)` plus JS fallback |
| `platform-feature.linear-easing` | widely (high since 2026-06) | 113 | 112 | 17.2 | 94.0% | keyword easing declared first |
| `platform-feature.view-transitions` | newly (since 2025-10) | 111 | 144 | 18.0 | 90.0% | feature-detect `startViewTransition` |
| `platform-feature.scroll-driven-animations` | limited | 115 | 159 (graph) / none (live) | 26.0 | 88.3% | `@supports (animation-timeline: scroll())` |
| `platform-feature.backdrop-filter` | widely in graph, newly in live (since 2024-09) | 76 | 103 | 18.0 | 96.0% | opaque surface fallback |

Chrome and Firefox columns show the live web-features numbers where present (the graph says Chrome 106 for container queries, Chrome 131 and Firefox 133 for relative colour, Chrome 116 for popover; the difference is partial versus full support). Sources: https://caniuse.com, https://web.dev/baseline/2025, https://github.com/web-platform-dx/web-features.

Policy: anything "widely" is used without a guard. Anything "newly" is used behind a declared fallback (the previous declaration in the same rule) or an `@supports` block. Anything "limited" is an enhancement only, never load-bearing.

## How to use each safely

### Container queries

Size queries are widely available. Put `container-type: inline-size` on the component's wrapper, not on the component, and name it when nesting.

```css
.card-grid { container: cards / inline-size; }
@container cards (inline-size > 40rem) { .card { grid-template-columns: 1fr 2fr; } }
```

Write the single-column layout unconditionally and add columns inside the query. Style queries (`@container style(--variant: compact)`) are an Interop 2026 item; do not rely on them yet. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries.

### :has()

Widely available. Use it for parent-state styling: `.field:has(:focus-visible) { border-color: var(--pf-color-focus); }`, `.form:has(:invalid) .submit { opacity: .6; }`, `body:has(dialog[open]) { overflow: hidden; }`. Keep selectors shallow; `:has()` inside a large subtree is re-evaluated on every mutation. Guard any rule whose absence changes layout: `@supports selector(:has(a)) { ... }`.

### oklch()

Widely available. `tokens_css` emits every role twice, `--pf-color-<role>` as hex and `--pf-color-<role>-oklch`, so components can use either. In custom CSS always declare hex first:

```css
.badge { background: #d9ecd9; background: oklch(0.92 0.05 150); }
```

Author in the sRGB gamut; raise chroma for P3 screens only inside `@media (color-gamut: p3)`. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch.

### color-mix()

Widely available. The skill's hover tints and status badges use it: `color-mix(in oklab, var(--pf-color-text) 6%, transparent)` for a hover wash, `color-mix(in oklab, var(--pf-color-success) 14%, transparent)` for a badge. Mix in `oklab` (Tailwind v4 does the same) so mid-tones stay clean. Put a literal fallback colour on the line before it.

### Relative colour syntax

Newly available. Derive state colours from a token while keeping its hue:

```css
.button-primary:hover {
  background: color-mix(in oklab, var(--pf-color-primary) 92%, black);
  background: oklch(from var(--pf-color-primary) calc(l - 0.05) c h);
}
```

Clamp lightness with `clamp(0, calc(l + 0.1), 1)` in dark mode. Chart series by hue rotation: `oklch(from var(--pf-color-primary) l c calc(h + 40))`. Source: https://developer.chrome.com/blog/css-relative-color-syntax.

### light-dark()

Newly available and dependent on `color-scheme` being set on an ancestor (`tokens_css` sets `color-scheme: light dark` on `:root`). Use it for one-off component colours not worth a token:

```css
.code { background: var(--pf-color-surface); background: light-dark(oklch(0.96 0.01 80), oklch(0.22 0.01 80)); }
```

Tokens remain the primary theme mechanism because `[data-theme]` forcing works everywhere; `light-dark()` follows `color-scheme`, so also set `color-scheme: dark` on `[data-theme="dark"]` when using it. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark.

### @property

Interpolation of custom properties (gradients, counters, angles). Unregistered properties still work as plain variables, so the fallback is "no animation".

```css
@property --n { syntax: "<integer>"; inherits: false; initial-value: 0; }
.stat { counter-reset: n var(--n); transition: --n 800ms var(--pf-ease-out); }
.stat::after { content: counter(n); }
```

Used by `motion-pattern.number-count-up` and by animated gradient angles at level 3. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/@property.

### @starting-style

Entry animation from `display: none`. Pair with `transition-behavior: allow-discrete` and keep the exit in the same rule.

```css
[popover], dialog {
  opacity: 1; translate: 0 0;
  transition: opacity var(--pf-dur-base) var(--pf-ease-out), translate var(--pf-dur-base) var(--pf-ease-out), display var(--pf-dur-base) allow-discrete, overlay var(--pf-dur-base) allow-discrete;
  @starting-style { opacity: 0; translate: 0 8px; }
}
[popover]:not(:popover-open), dialog:not([open]) { opacity: 0; translate: 0 8px; }
```

Without support the element appears instantly, which is acceptable. Used by `motion-pattern.enter-fade-up-8`, `motion-pattern.enter-scale-95` and the toast. Source: https://developer.chrome.com/blog/entry-exit-animations.

### Popover API

Newly available. Use `popover` on tooltips, menus and toasts with `popovertarget` on the trigger; it gives top layer, light dismiss and focus handling without JS. For dialogs use `<dialog>` with `showModal()`. Guard: `@supports selector(:popover-open)`; where unsupported, load the OddBird polyfill (https://github.com/oddbird/popover-polyfill) or fall back to a framework component. Anchor positioning is the natural partner but is still limited; position with JS (Floating UI) until it is newly available. Source: https://developer.mozilla.org/en-US/docs/Web/API/Popover_API.

### text-wrap: balance and pretty

`balance` on headings (up to four lines; the engines cap at six), `pretty` on paragraphs to avoid orphans. Both are ignored where unsupported and need no guard. Never set `balance` on body text; it is costly and changes measure. Source: https://developer.chrome.com/blog/css-text-wrap-balance, https://developer.chrome.com/blog/css-text-wrap-pretty.

### Anchor positioning

Limited (Chrome 125 partial, Safari 27, no Firefox). Treat it as an enhancement for tooltips and menus:

```css
@supports (anchor-name: --trigger) {
  .trigger { anchor-name: --trigger; }
  .menu { position: absolute; position-anchor: --trigger; top: anchor(bottom); left: anchor(left); position-try-fallbacks: flip-block; }
}
```

Keep the JS positioning path for everyone else. Do not ship anchor-only layouts. Source: https://developer.chrome.com/blog/anchor-positioning-api.

### linear() easing

Widely available. Carries the spring token `--pf-ease-spring`. Declare a keyword fallback first: `transition-timing-function: ease-out; transition-timing-function: var(--pf-ease-spring);`. Source: https://developer.chrome.com/docs/css-ui/css-linear-easing-function.

### View transitions

Newly available since October 2025 for same-document; cross-document needs Chrome 126 and Safari 18.2. Feature-detect `document.startViewTransition` in JS, keep the default crossfade to `--pf-dur-page`, and disable under reduced motion. Details and selectors in references/motion.md. Source: https://developer.chrome.com/docs/web-platform/view-transitions.

### Scroll-driven animations

Limited. Everything lives inside `@supports (animation-timeline: scroll())`, and the un-animated page must be complete. Only `motion-pattern.scroll-progress-bar` and `motion-pattern.scroll-reveal-once` use it. Source: https://developer.chrome.com/docs/css-ui/scroll-driven-animations.

### backdrop-filter

Widely usable (the live file marks it newly available because Firefox only unprefixed it in 103 and Safari in 18). Use it only where a real layer sits behind the surface (a sticky header over content, a sheet over a page); set an opaque `background` fallback and a semi-transparent one with `@supports (backdrop-filter: blur(1px))`. Check text contrast on the blurred surface against the darkest and lightest content that can scroll beneath it; grade the worst case with `contrast.py`. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter.

## Progressive enhancement patterns

- Two declarations, same property: the safe value first, the new value second. Engines that do not parse the second keep the first. This covers oklch, color-mix, relative colour, light-dark and linear().
- `@supports (property: value)` for features that change layout or behaviour: anchor positioning, scroll-driven animations, backdrop-filter, container queries in older code paths.
- `@supports selector(...)` for selector features: `:has()`, `:popover-open`.
- JS feature detection for APIs: `"startViewTransition" in document`, `HTMLElement.prototype.hasOwnProperty("popover")`, `CSS.supports("anchor-name: --a")`.
- Never gate content. Every guard hides motion or polish, not text, images or controls.
- Test the fallback path once per direction by disabling the feature in DevTools (Rendering panel for color-gamut and prefers-color-scheme; a user agent override for older Safari).
- Tailwind v4 already emits `color-mix(in oklab)` for opacity modifiers and `@supports` wrappers for some utilities; do not double-wrap.

## Live refresh of feature status

`scripts/refresh_knowledge.py` pulls https://cdn.jsdelivr.net/npm/web-features/data.json (listed under `features` in `knowledge/sources.json`, with the sixteen `ids` to extract) and writes `features.json`:

```json
{"fetched": "2026-10-30T06:21:41+00:00", "source": "web-features",
 "features": {"light-dark": {"name": "light-dark()", "baseline": "newly",
   "baseline_low_date": "2024-05-13", "baseline_high_date": null,
   "support": {"chrome": "123", "firefox": "120", "safari": "17.5", "safari_ios": "17.5"}}}}
```

- Default output is the user cache, `~/.cache/preview-first/live/` (or `$XDG_CACHE_HOME/preview-first/live/`). `--bundled` writes into `knowledge/live/` and is what the weekly CI job uses. `--status` prints the newest directory, its `fetched` time and `stale: true` once data is seven days old.
- `newest_live_dir()` picks whichever of the bundled snapshot and the cache has the later `fetched` stamp; `load_live()` reads `fonts`, `features`, `releases` and `feeds` from it.
- `annotate_graph()` matches each `platform-feature.*` node by `web_features_id` (falling back to the id slug) and attaches `live: {baseline, support, as_of}`. The graph file itself is not rewritten; the annotated copy feeds the recommender and the preview tile.
- Baseline strings map directly onto the schema enum (`widely`, `newly`, `limited`); `baseline_high_date` is set only for widely available features.
- When a feature moves from `limited` to `newly` in the live file, promote it in this document and in the graph node (`baseline`, `support`, `last_verified`) in the same change, then run `validate_graph.py --strict`.
- The refresh never scrapes HTML. One failing source does not abort the run; the report lists which files were written.

## Tailwind v4 token mapping

`export_design.py` writes `design/tailwind.css` when it finds a `tailwind.config.*` or a stylesheet with `@import "tailwindcss"`. The file maps preview-first tokens into Tailwind's `@theme` namespace so utilities pick them up (https://tailwindcss.com/docs/theme):

```css
@import "tailwindcss";
@theme {
  --color-bg: var(--pf-color-bg);            /* bg-bg, text-bg */
  --color-surface-raised: var(--pf-color-surface-raised);
  --color-primary: var(--pf-color-primary);  /* bg-primary, text-primary, border-primary */
  --color-on-primary: var(--pf-color-on-primary);
  --font-heading: var(--pf-font-heading);    /* font-heading */
  --font-body: var(--pf-font-body);
  --font-mono: var(--pf-font-mono);
  --radius-md: var(--pf-radius-md);          /* rounded-md */
  --duration-fast: var(--pf-dur-fast);       /* duration-fast */
}
@import "./tokens.css";
```

Rules:
- All fourteen roles map to `--color-<role>` with underscores turned into hyphens, every radius step maps to `--radius-<step>`, and the four durations map to `--duration-<step>`.
- Keep the default Tailwind palette available for one-off needs, but components use only the mapped names; `bg-indigo-500` in a component is a contract violation.
- Opacity modifiers (`bg-primary/10`) work because Tailwind v4 wraps the variable in `color-mix(in oklab, ...)`.
- Spacing stays on Tailwind's own scale; `--pf-space-*` (0.25rem steps times the density factor 0.75, 1 or 1.25) is for hand-written CSS and for `@theme { --spacing: calc(0.25rem * var(--pf-density)); }` when the developer wants density to drive utilities.
- Type scale: map `--text-xs` through `--text-5xl` to `--pf-text-*` only when the project opts in; Tailwind's defaults differ from the modular scale and mixing them is the usual source of stray sizes.
- Easings: add `--ease-out: var(--pf-ease-out); --ease-in-out: var(--pf-ease-in-out);` to `@theme` so `ease-out` utilities use the contract curves.
- Dark mode: the tokens switch under `[data-theme="dark"]` and the system query, so no `dark:` variants are needed for colours. Configure `@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));` only for non-colour dark overrides.

## shadcn token mapping

shadcn/ui themes with `x` and `x-foreground` pairs on `:root` and `.dark` (https://ui.shadcn.com/docs/theming). Map preview-first roles once in `globals.css` and leave the component files untouched:

| shadcn variable | preview-first token |
|---|---|
| `--background` | `--pf-color-bg` |
| `--foreground` | `--pf-color-text` |
| `--card`, `--popover` | `--pf-color-surface-raised` |
| `--card-foreground`, `--popover-foreground` | `--pf-color-text` |
| `--primary` | `--pf-color-primary` |
| `--primary-foreground` | `--pf-color-on-primary` |
| `--secondary`, `--muted` | `--pf-color-surface` |
| `--secondary-foreground` | `--pf-color-text` |
| `--muted-foreground` | `--pf-color-text-muted` |
| `--accent` | `--pf-color-surface` for hover washes, or `--pf-color-accent` only when the direction uses a strong accent on menu items |
| `--accent-foreground` | `--pf-color-text` or `--pf-color-on-accent`, matching the row above |
| `--destructive` | `--pf-color-danger` |
| `--border`, `--input` | `--pf-color-border` |
| `--ring` | `--pf-color-focus` |
| `--radius` | `--pf-radius-md` (shadcn's default is 0.625rem; the `md` radius scale gives 0.5rem, `lg` gives 0.75rem) |
| `--chart-1` to `--chart-5` | `--pf-color-primary`, `--pf-color-accent`, then relative-colour hue rotations |

Rules:
- Point the `.dark` block at the same `--pf-*` variables; they already switch under `[data-theme="dark"]`, so set `data-theme` instead of toggling `.dark`, or alias `.dark` to the same selector in `tokens.css`.
- shadcn's `--accent` is a hover surface, not a brand accent. Mapping `--pf-color-accent` to it paints every hovered menu item in the brand highlight; use `--pf-color-surface` unless the direction says otherwise.
- Status badges and alerts use the preview-first recipe (14 percent tint via `color-mix`, status colour text, 3px left border) rather than shadcn's defaults.
- Grade `--muted-foreground` on `--muted` and `--primary-foreground` on `--primary` with `contrast.py` after mapping; shadcn's own defaults pass, but a brand override may not.
- Radix colours (which shadcn once used) follow a 12-step scale where steps 1 and 2 are backgrounds, 3 to 5 interactive backgrounds, 6 to 8 borders, 9 and 10 solid fills, 11 and 12 text. The 14 roles collapse that scale: bg and surface are steps 1 to 2, surface_raised and hover tints steps 3 to 5, border steps 6 to 7, primary step 9, text_muted step 11, text step 12 (https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale).
