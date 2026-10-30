# Components and the treatment vocabulary

Rules Claude applies when authoring `directions.json` bundles and when writing UI after handoff. The treatment vocabulary below is closed: every axis and every value here matches `knowledge/schema.json` (`node_kinds.treatment.axis_values`) and `validate_graph.py` rejects anything else. Each value is implemented in `assets/preview/preview.css` (and `draft.css` for page-level effects) as a class on the direction root: `pf-<axis>-<value>` with underscores in the axis turned into hyphens (`button_shape` plus `pill` gives `pf-button-shape-pill`). `build_preview.py` emits one class per axis from `bundle.treatments`, so a bundle must set all ten axes.

Defaults per style come from `defaults_to` edges in `knowledge/graph.json`; `recommend.py` copies them into the bundle. Change a value in the bundle when the brief justifies it and say why in the rationale.

## Choosing treatments

- Set all ten axes in every bundle. A missing axis falls back to the base CSS, which is the first value listed under each axis below, and the gallery will not say so.
- Keep the axes coherent: square buttons go with `image_corner` `none` and `focus_ring` `inset`; pill buttons go with `image_corner` `lg` and `nav` `floating` or `airy`.
- Treatments never carry colour. Colour comes from palette roles (`--pf-color-*`); treatments decide shape, edge, weight and layering.
- Two directions in one preview should differ on at least four axes. Same style, same treatments, new palette is one direction, not two (see anti-patterns.md).
- Prefer the quieter value when the brief is silent: `border` over `shadow`, `hairline` over `rule`, `none` over `layered`.

## button_shape

How much radius a button and a badge carry. Badges follow the button shape when it is `pill`.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `pill` | Consumer, soft, playful or luminous directions; buttons read as friendly objects | `pf-button-shape-pill` | soft-product, luminous-dark, playful-geometric, warm-organic |
| `rounded` | Product UI, tools, anything neutral; radius comes from `--pf-radius-md` so the style's radius scale decides the exact value (6 to 10px at `md`) | `pf-button-shape-rounded` | paper-editorial, mono-engineering, dark-console, glass-layered, bento-showcase |
| `square` | Editorial, Swiss, brutalist, luxury and data-dense directions; zero radius | `pf-button-shape-square` | swiss-grid, quiet-luxury, neo-brutalist, poster-type, data-dense |

`rounded` is the base rule (`.pf-btn { border-radius: var(--pf-radius-md) }`); `pill` sets `--pf-radius-full`; `square` sets 0.

## button_fill

How the primary button is filled. Secondary, quiet and danger buttons do not change with this axis.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `solid` | The default: primary fill with `on_primary` text; the one loud element on the view | `pf-button-fill-solid` | paper-editorial, swiss-grid, soft-product, luminous-dark, neo-brutalist, playful-geometric, glass-layered, bento-showcase |
| `outline` | Quiet and editorial directions; 1px border in text colour, transparent fill, inverts on hover | `pf-button-fill-outline` | mono-engineering, quiet-luxury, poster-type, data-dense |
| `ghost` | Toolbars and dense surfaces where a filled button would shout; no border, primary text, 12% tint on hover | `pf-button-fill-ghost` | none by default; opt in for app toolbars |
| `soft` | Dark and warm directions where a solid primary would glare; 18% tint of primary behind primary text, 30% border | `pf-button-fill-soft` | dark-console, warm-organic |

Rule: with `outline` or `ghost`, the primary button must still be the most visible control on the view. Achieve that with position and size, not by adding a second filled button.

## input_edge

How text inputs and selects are bounded.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `hairline` | The accessible default: 1px `border` colour, raised surface, 2px focus ring in `focus` colour | `pf-input-edge-hairline` | paper-editorial, mono-engineering, neo-brutalist, bento-showcase, data-dense |
| `filled` | Soft, dark and glass directions: `surface` fill, no border until focus | `pf-input-edge-filled` | soft-product, dark-console, luminous-dark, playful-geometric, warm-organic, glass-layered |
| `underline` | Editorial and luxury forms with one to three fields: bottom rule only, no left padding, focus thickens the rule to 2px | `pf-input-edge-underline` | swiss-grid, quiet-luxury, poster-type |

Rule: never use `underline` on a form with more than four fields or on any form with a table nearby; fields lose their boundaries.

## card_edge

How a card separates itself from the page.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `border` | Default: 1px `border` colour, no shadow; the border earns its place | `pf-card-edge-border` | paper-editorial, mono-engineering, dark-console, neo-brutalist, bento-showcase, data-dense |
| `shadow` | Soft and playful product UI: transparent border, two-layer shadow under 6% total opacity | `pf-card-edge-shadow` | soft-product, playful-geometric |
| `flat` | Grouping by spacing and a `surface` background only; editorial, Swiss, luxury, organic | `pf-card-edge-flat` | swiss-grid, quiet-luxury, warm-organic, poster-type |
| `inset` | Glass: 70% translucent raised surface, 16px blur, 1px inner highlight, one drop shadow. Only over colour or imagery | `pf-card-edge-inset` | luminous-dark, glass-layered |

Rule: `inset` requires something behind the card (a tinted hero, an image, a gradient the brief asked for). Glass over a flat background is a tell.

## nav

The top-level navigation pattern. The draft page renders `.pf-nav` for marketing, content and store pages; app pages render a shell (see layout.md) and `sidebar` describes it.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `airy` | Marketing and editorial: wordmark left, up to five links right, 72px tall, no bottom border | `pf-nav-airy` | paper-editorial, quiet-luxury, playful-geometric, warm-organic, poster-type |
| `compact` | Technical, Swiss, brutalist and showcase sites: 56px tall, hairline bottom border (2px text-colour rule when `divider` is `rule`) | `pf-nav-compact` | swiss-grid, mono-engineering, neo-brutalist, bento-showcase |
| `floating` | Soft and glass directions: detached pill 16px from the top, 80% raised surface with 12px blur, 56px tall | `pf-nav-floating` | soft-product, luminous-dark, glass-layered |
| `sidebar` | App shells and documentation: 240px vertical column; the tile's components section renders it as a column | `pf-nav-sidebar` | dark-console, data-dense |

Rule: links collapse below 860px in the draft (`.pf-nav-links { display: none }`); a real build must add a menu control, 44px tall, before shipping.

## divider

How sections are separated.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `hairline` | Default: 1px rule in `border` colour between sections, under nav and over footer | `pf-divider-hairline` | paper-editorial, mono-engineering, dark-console, bento-showcase, data-dense |
| `space` | Whitespace only; rhythm from `--pf-space-10` to `--pf-space-12`; soft, luminous, luxury, organic, glass | `pf-divider-space` | soft-product, luminous-dark, quiet-luxury, playful-geometric, warm-organic, glass-layered |
| `rule` | 2px to 4px rule in text colour; Swiss, brutalist, poster | `pf-divider-rule` | swiss-grid, neo-brutalist, poster-type |

`space` also clears the borders on `.pf-nav`, `.pf-footer`, `.pfd-list li` and tile sections; `rule` makes the footer rule 3px and list rules 2px.

## image_corner

Radius on imagery and media placeholders (`.pfd-media`).

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `none` | Square imagery; editorial, Swiss, luxury, brutalist, poster, data | `pf-image-corner-none` | swiss-grid, quiet-luxury, neo-brutalist, poster-type, data-dense |
| `sm` | Default: `--pf-radius-md`, matching cards | `pf-image-corner-sm` | paper-editorial, mono-engineering, dark-console, glass-layered, bento-showcase |
| `lg` | `--pf-radius-xl`; soft and playful directions | `pf-image-corner-lg` | soft-product, luminous-dark, playful-geometric, warm-organic |

Rule: image corners never exceed card corners. If `card_edge` is `flat` with `radius_scale` `none`, use `image_corner` `none`.

## focus_ring

How keyboard focus is shown. Every value meets WCAG 2.4.11 (focus appearance) when the palette's `focus` role passes the `focus on bg` check.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `offset` | Default and most visible: 2px solid ring in `focus` colour, 2px outside the element | `pf-focus-ring-offset` | paper-editorial, mono-engineering, playful-geometric, warm-organic, bento-showcase |
| `inset` | Square directions and dense tables where an outside ring would collide: ring 2px inside | `pf-focus-ring-inset` | swiss-grid, quiet-luxury, neo-brutalist, poster-type, data-dense |
| `glow` | Dark and soft directions: no outline, 4px box-shadow of `focus` at 40% alpha | `pf-focus-ring-glow` | soft-product, dark-console, luminous-dark, glass-layered |

Rule: never remove focus styles. `glow` is a replacement, not a removal; test it on the darkest surface of the palette.

## link_style

Inline links in body copy (`.pf-link`). Nav and footer links are muted text that underlines on hover regardless of this axis.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `underline` | Default and most accessible: text colour, 1px underline, 0.15em offset | `pf-link-style-underline` | paper-editorial, swiss-grid, quiet-luxury, warm-organic, poster-type |
| `colour` | `primary` colour, no underline until hover; only when `primary on bg` passes the `ui` contrast check | `pf-link-style-colour` | soft-product, dark-console, luminous-dark, playful-geometric, glass-layered, bento-showcase |
| `both` | `primary` colour and underline; technical and data directions where links must be found at a glance | `pf-link-style-both` | mono-engineering, neo-brutalist, data-dense |

Rule: `colour` alone fails WCAG 1.4.1 (use of colour) when link and body colours are under 3:1 apart. Check it or use `both`.

## elevation

How many shadow levels exist.

| Value | Use when | Class | Style defaults |
|---|---|---|---|
| `none` | Nothing floats; layering by colour and border. Editorial, technical, Swiss, luxury, dark, brutalist | `pf-elevation-none` | paper-editorial, swiss-grid, mono-engineering, dark-console, quiet-luxury, neo-brutalist, warm-organic, poster-type, data-dense |
| `one` | A single soft level for raised surfaces (cards with `shadow`, menus, popovers) | `pf-elevation-one` | soft-product, playful-geometric, bento-showcase |
| `layered` | Two or three levels plus blur for glass; cards get a three-stop shadow | `pf-elevation-layered` | luminous-dark, glass-layered |

Rule: `layered` without `card_edge` `inset` or a translucent nav is decoration; drop to `one`.

## Tokens every component uses

Written by `palette.py` into `tokens.css`; use them, never raw values.

- Colour: `--pf-color-bg`, `surface`, `surface-raised`, `text`, `text-muted`, `border`, `primary`, `on-primary`, `accent`, `on-accent`, `success`, `warning`, `danger`, `focus` (each also as `-oklch`). Dark values switch under `[data-theme="dark"]` and the system preference.
- Radius: `--pf-radius-xs|sm|md|lg|xl|full` from the style's `radius_scale` (`none`, `sm`, `md`, `lg`, `pill`).
- Space: `--pf-space-1` to `--pf-space-12`, each `n × 0.25rem × density` (airy 1.25, regular 1, compact 0.75).
- Type: `--pf-text-xs|sm|base|lg|xl|2xl|3xl|4xl|5xl` from the pairing's `scale_ratio`; `--pf-font-heading|body|mono`; `--pf-leading-tight|normal|loose`; `--pf-measure`.
- Motion: `--pf-dur-fast|base|slow|page`, `--pf-ease-out|in-out|in|spring`; all durations are 0ms at motion level 0.

Derived states use `color-mix(in oklab, ...)` on these tokens, never a second hex value.

## Component specs

### Button `.pf-btn`

- Variants: `.pf-btn-primary` (one per view), `.pf-btn-secondary` (transparent, `border` colour, `surface` on hover), `.pf-btn-quiet` (muted text, no border), `.pf-btn-danger` (`danger` fill, white text; destructive confirmations only).
- Sizes: default `min-height: 44px`, padding `--pf-space-4` plus 2px, `--pf-text-base`; `.pf-btn-sm` 36px, `--pf-space-3`, `--pf-text-sm`. Small buttons only inside toolbars, table rows and nav; never as the page's primary action.
- Six states, each previewable with `data-state`: default; hover (primary mixes 12% text colour into primary; outline inverts); active (`scale(0.97)`, none at motion level 0); focus (per `focus_ring`); disabled (`opacity: 0.45`, `cursor: not-allowed`, no transform); loading (text transparent, 16px spinner in `on_primary`, or `primary` for outline, ghost and soft fills, `pointer-events: none`).
- Icon plus label gap is `--pf-space-2`; icons are 24px from the bundle's icon set, never emoji.
- Labels: sentence case, a verb, two to three words, no trailing arrow.

### Input `.pf-input` and field `.pf-field`

- Field is a `label` grid: caption span in `text` at 500 weight, control, optional `.pf-error` in `danger` at `--pf-text-xs`.
- Control: `min-height: 44px`, `--pf-space-3` horizontal padding, `--pf-radius-sm`, raised surface, `--pf-text-base` (16px minimum stops iOS zoom).
- Four states: default; focus (`focus` border plus 2px ring, or a 2px bottom rule for `underline`); error (`.pf-field[data-state="error"]`, `danger` border, error text present, never colour alone); disabled (`opacity: 0.5`).
- Placeholders are examples, not labels. Every input has a visible caption.

### Select `.pf-select`

Same box, states and tokens as the input; native element so the platform picker and keyboard behaviour stay intact. Do not restyle the options list in a preview.

### Checkbox `.pf-check`

Native input, 18px, `accent-color: var(--pf-color-primary)`, label gap `--pf-space-2`, `--pf-text-sm`. The whole label is the hit area (44px row height in forms).

### Switch `.pf-switch`

Visually hidden input with `role="switch"` plus `.pf-switch-track`: 40 by 24px track in `border` colour, 18px white knob that translates 16px when checked, track turns `primary`, focus ring on the track. Use for settings that apply immediately; use a checkbox when a save button follows.

### Card `.pf-card`

Grid with `--pf-space-3` gap, `--pf-space-5` padding, raised surface, `--pf-radius-lg`, edge per `card_edge`, shadow per `elevation`. Heading inside is `h3` at `--pf-text-xl`. A card wraps one object with its own actions; it does not wrap a section, a table or a form (see layout.md).

### Badge `.pf-badge`

24px tall, `--pf-space-2` padding, `--pf-text-xs` at 500, `--pf-radius-sm` (full with `button_shape` `pill`). Tones: default (surface, muted text, border), `.pf-badge-primary`, `-success`, `-warning`, `-danger` as 14 to 18% tints with the role colour as text. A badge states a status word; it is not a button and never the only cue (pair with text in the row).

### Alert `.pf-alert`

`--pf-space-3` by `--pf-space-4` padding, `--pf-radius-md`, `surface` background, `--pf-text-sm`; `.pf-alert-info` (3px left rule in `primary`), `-warning`, `-danger`. Body may include a list. One alert per view; stacked alerts mean the layout needs a different pattern.

### Tabs `.pf-tabs`

Flex row with 1px bottom border; `.pf-tab` is a 40px button, muted text, `aria-selected="true"` turns text to `text` and draws a 2px `primary` underline. Two to six tabs, each a noun, no icons unless every tab has one.

### Nav `.pf-nav`

Wordmark `.pf-wordmark` (heading font, 600, `--pf-text-lg`), `.pf-nav-links` (muted, `--pf-text-sm`, gap `--pf-space-5`, underline on hover), one small primary button. Height, border and detachment per `nav`.

### Footer `.pf-footer`

Two-column grid: wordmark plus one honest sentence left, `.pf-footer-cols` right (three columns of `h4` in body font at 600 and muted links). `--pf-space-10` vertical padding, top rule per `divider`. Collapses to one column under 860px.

### Table `.pfd-table`

`border-collapse`, `--pf-text-sm`, raised surface, 1px outer border, `--pf-radius-md`; header cells 600 in muted text on `surface`; rows have 1px bottom rules and a 4% hover tint. Density variants: `dense` (`--pf-space-2` by `--pf-space-3`) and `comfortable` (`--pf-space-4` both ways). Numbers right-aligned with `tabular-nums` (`.pfd-num`); ids in mono; status as a badge with text. The third column hides under 860px, so put the least important column third.

### Empty state

A single `.pf-card`, centred, `--pf-space-10` padding: heading saying what is missing, one muted sentence saying when it appears or how to add it, one primary button. No illustration placeholder, no second button.

## One primary action per view

- Exactly one `.pf-btn-primary` is visible in a viewport at a time. Nav, hero and a call-to-action band at the foot of a long page count as separate viewports; a hero with two filled buttons does not.
- Everything else is secondary, quiet or a link. Destructive actions are `quiet` until confirmed, then `danger`.
- In tables and toolbars, the primary is the create action; row actions are quiet.
- In forms, the primary is submit; cancel is quiet and sits after it.

## Adding a new treatment value

1. Schema: add the value to `node_kinds.treatment.axis_values.<axis>` in `knowledge/schema.json`. New axes need a new key there and a new class prefix.
2. CSS: implement it in `assets/preview/preview.css` as `.pf-<axis>-<value> <selector>` using tokens only; add draft-level effects in `draft.css` and tile effects in `tile.css` where the existing values have them (`divider` and `image_corner` do). Cover every state the base component has.
3. Graph: add a `treatment.<axis>-<value>` node with `axis`, `value`, `css_class`, `description` and the common fields (`id`, `kind`, `name`, `source`, `added`, `last_verified`, `confidence`); add `defaults_to` edges from each style that should default to it, and remove that style's edge to the old value so each style has exactly one default per axis.
4. Document it in the matching table above with the styles that default to it, then run `uv run python3 skills/preview-first/scripts/validate_graph.py` and the test suite (`tests/test_skill_docs.py` checks this file against the schema).

Sources: Vercel design guide on earned borders and one-accent monochrome (https://vercel.com/design.md); Radix scale steps for tints and borders (https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale); shadcn token pairs (https://ui.shadcn.com/docs/theming); WCAG 2.2 focus appearance and target size (https://www.w3.org/TR/WCAG22/); Emil Kowalski on press scale and durations (https://emilkowal.ski/ui/great-animations).
