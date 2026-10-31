# Layout

Rules Claude applies when choosing layout variants in `directions.json`, when reviewing a draft in the preview, and when writing pages after handoff. The draft templates live in `scripts/drafts/*.py`; their CSS is `assets/preview/draft.css`. Tokens come from `tokens.css` (see components.md).

## Breakpoints

Design and test at these widths; they cover the catalogue in `knowledge/devices.json` and the StatCounter top resolutions (https://gs.statcounter.com/screen-resolution-stats).

| Width | What lands here | What must be true |
|---|---|---|
| 360 | Galaxy S25, Z Flip7, Z Fold7 cover, most Android mid-range (360x780, 360x800) | One column, full-width primary button, 16px side padding, nothing clipped |
| 768 | iPad portrait at 820 minus scrollbars, large phones in landscape, split-screen tablet | Two columns allowed for media plus text; nav still collapsed or a full menu |
| 1024 | iPad landscape (1180), small laptops, iPad Pro 13 portrait (1032), Z Fold7 open (984) | Full nav, sidebar shells, two-column article with table of contents |
| 1280 | Gallery thumbnails render the draft at 1280x800; MacBook Air exact 2x is 1280x832 | The reference width for every direction; what the developer compares |
| 1536 | Windows 1080p at 125% (9.99% of desktop traffic), Surface Laptop 7 | Container centred with visible margins, line length still under the measure |

Rules:

- Mobile first. Write the 360 layout without media queries, then add columns at `min-width` steps. Never start at 1280 and subtract.
- Breakpoints are where the content breaks, not where devices are. Use the five above as the test grid, and add a content-specific one only when a component breaks between them.
- The draft stylesheet collapses every multi-column grid at `max-width: 860px` and stacks buttons at 420px. That is the preview's simplification; shipped CSS uses the five steps.
- Test 1366x768 too (7.95% of desktop traffic): a hero taller than 700px pushes the first call to action below the fold there.

## Container and measure

- Page sections are centred with `max-width: 1200px` and side padding `--pf-space-8` (`--pf-space-5` under 860px). App shells and the device view are full-bleed.
- Prose measure is `--pf-measure` from the type pairing (`measure_ch`, 66ch by default; 60 to 68ch acceptable). Lead paragraphs under a hero cap at 48ch; centred heroes cap at 60ch.
- Headlines cap at 12 to 18ch (`.pfd-poster-title` 12ch, editorial hero 18ch). A headline wider than that is a paragraph.
- Above 1536px keep the container at 1200px and let the margins grow; do not scale the type up to fill.

## Density and spacing scale

Spacing tokens are `--pf-space-n = n × 0.25rem × density`, n from 1 to 12.

| Density | Factor | space-4 | space-8 | space-12 | Used by |
|---|---|---|---|---|---|
| airy | 1.25 | 1.25rem | 2.5rem | 3.75rem | paper-editorial, quiet-luxury, warm-organic, poster-type |
| regular | 1.0 | 1rem | 2rem | 3rem | swiss-grid, soft-product, luminous-dark, neo-brutalist, playful-geometric, glass-layered |
| compact | 0.75 | 0.75rem | 1.5rem | 2.25rem | mono-engineering, dark-console, bento-showcase, data-dense |

Rules:

- Section padding is `--pf-space-12` vertical; card padding `--pf-space-5`; control padding `--pf-space-3`; inline gaps `--pf-space-2`. Pick from the scale, never from a free number.
- Density is a bundle field (`bundle.density`) that defaults from the style. Override to `compact` for app pages when the brief says operators, analysts or dashboards; never go below `regular` on marketing or content.
- Density changes spacing only. Type size, control height (44px) and touch targets do not shrink with it.
- `--pf-density` is also exposed so component CSS can scale internal gaps once rather than per token.

## Grids

- Use CSS grid for page structure and flex for rows of controls. The draft uses `grid-template-columns: 1fr 1fr` for split heroes, `3fr 1fr` for editorial heroes, `1fr 2fr` for list wrappers, `repeat(3, 1fr)` for bento and columns, `240px 1fr` for the sidebar shell, `minmax(0, 1fr) 360px` for work areas, `200px minmax(0, 1fr)` for article with table of contents.
- Always `minmax(0, 1fr)` where a cell holds text or a table; plain `1fr` lets long words and tables blow out the column.
- Auto-fit grids for repeated items of unknown count: `repeat(auto-fit, minmax(240px, 1fr))` (`.pf-grid-2`) and `minmax(380px, 1fr)` for the gallery. Fixed counts (`repeat(3, 1fr)`) only when the count is fixed by content.
- Alignment: media next to text is `align-items: center`; headings next to asides are `align-items: end`; panels beside tables are `align-self: start`.
- Gap tokens: `--pf-space-4` inside bento, `--pf-space-8` between columns, `--pf-space-10` between a hero's halves.

## Container queries

Baseline widely available (Chrome 106, Firefox 110, Safari 16; 95.9% global, see `platform-feature.container-queries` in the graph and https://developer.mozilla.org/docs/Web/CSS/CSS_containment/Container_queries).

- After handoff, give reusable components `container-type: inline-size` on their wrapper and switch their internal layout with `@container (min-width: 480px)`; keep page-level breakpoints for the page grid only.
- A card, a product tile and a detail panel must each work at 280px, 360px and 560px container widths because the same component lands in a sidebar, a grid cell and a full column.
- Use container query units (`cqi`) for a poster headline inside a bounded box instead of `vw`, which ignores the sidebar.
- Do not use container queries in the preview drafts; they stay viewport based so the device frames show exactly what each viewport does.

## Page types and layout variants

`brief.page_type` picks the template. Each section has variants (`VARIANTS` in `scripts/drafts/<page>.py`); the section element carries `data-section` and `data-variant` so the preview and the tests can see what was chosen.

### Marketing (`marketing.py`): a programme of sections

`layout.programme` picks the set and order of sections: `classic` (hero, topic, marquee, features, band, proof, cta, footer), `showcase` (hero, band, topic, features, marquee, proof, footer), `editorial` (hero, manifesto, features, topic, proof, cta, footer), `launch` (hero, marquee, topic, proof, features, band, cta, footer), `index` (hero, features, topic, manifesto, footer), `bare` (hero, topic, features, footer). Topic, marquee, band and the pinned bar render only when the direction carries them. Every style sets a default programme; random draws pick one.

#### Sections: nav, hero, features, proof, cta, footer

Hero:

- `split`: text left, 4:3 product shot right. Works when there is a real screenshot and a two-line headline. Default for mono-engineering, playful-geometric, data-dense.
- `centered`: text centred over a 16:9 wide shot. Works for consumer products with one clear image; fails when the headline runs past 60ch or there is no image. Default for soft-product, luminous-dark, glass-layered.
- `editorial`: kicker, headline up to 18ch at `--pf-text-5xl`, side aside with a 1px left rule, aligned to the bottom. Works for publishing, studios, knowledge tools. Default for paper-editorial, warm-organic.
- `product-shot`: 21:9 full-width shot first, text under it. Works only when the screenshot carries the story. Default for dark-console, bento-showcase.
- `poster`: one headline at `clamp(3rem, 9vw, 8rem)`, 12ch, lead and buttons in a row beneath. Works for type-led brands with a short name or claim. Default for swiss-grid, quiet-luxury, neo-brutalist, poster-type.

Features:

- `bento`: three cells, first spans two columns, the first two carry 3:2 media. Works for feature overviews with real screenshots per cell; collapses to one column under 860px. Default for soft-product, luminous-dark, playful-geometric, glass-layered, bento-showcase.
- `list`: heading in a 1fr column, numbered list in 2fr, rules between items. Works for products with six or fewer precise claims and no imagery. Default for paper-editorial, mono-engineering, dark-console, poster-type, data-dense.
- `alternating`: three rows of text and 4:3 media, flipped on odd rows. Works when each feature has its own image. Default for quiet-luxury, warm-organic.
- `columns`: three text columns with a 2px top rule each. Works for Swiss and brutalist directions with short copy; the only variant with three equal columns, so the copy in each must differ in length and shape. Default for swiss-grid, neo-brutalist.

Proof:

- `quote`: one attributed quote at `--pf-text-2xl` in the heading face. Needs a real name; otherwise leave the placeholder text that says so.
- `logos-text`: a sentence naming customers. Names only, never borrowed logos.
- `stats-sourced`: one or two figures with their source. Never an invented number.
- `none`: section omitted (zero padding). Use for pre-launch products.

Call to action: `band` (surface panel, heading plus buttons; bordered when `card_edge` is `border`); `inline` (lead plus buttons over a top rule); `form` (one to two fields with the submit beside them, under 560px wide).

Footer: `columns` (wordmark plus three link columns) or `minimal` (wordmark plus three nav words).

### App (`app.py`): shell, view, detail, extras

Shell `sidebar`, `topbar`, `rail` (56px icon rail with an optional command palette), `bottom-tabs` (phone first, inside the safe area) or `none` (one slim bar, the view takes the viewport). View `table`, `ledger` (hairline rows, mono headers, lowercase status), `board` (the product's figure at display size with the next action and a live list), `cards`, `kanban` (three named columns) or `feed` (actor, verb, object, time). `table` keeps `dense` and `comfortable` as the table's density. Detail `panel`, `drawer`, `inspector` or `none`. Extras `settings`, `empty`, `both` or `none`. Every style sets all five in `layout_defaults.app`; the recommender keeps shells and views distinct across a set.


- Shell `sidebar` (240px column with wordmark, vertical nav, account row; turns into a top strip with a horizontally scrolling nav under 860px) or `topbar` (56px header with inline links). Sidebar when there are five or more destinations or the product is used all day; topbar for three to four destinations.
- Table `dense` (space-2 by space-3 cells) or `comfortable` (space-4). Dense for operators scanning many rows; comfortable for occasional admin screens.
- Detail `panel` (360px column beside the table, always visible) or `drawer` (slides over a scrim, 380px). Panel when the detail is consulted while scanning rows; drawer when the detail is an edit task.
- The empty state and the settings form render in every app draft so a direction is judged on its quiet screens as well as its busy one.

### Content (`content.py`): header, article, list, footer

- Header `masthead` (centred name at `--pf-text-4xl` plus a line, nav beneath) or `minimal` (nav only). Masthead for publications; minimal for documentation and blogs inside a product.
- Article `single` (one column at the measure) or `with-toc` (200px sticky table of contents plus article, static under 860px). Table of contents only when articles have three or more headings.
- List `cards` (three cards with kicker, title, summary) or `lines` (rows of title and date with rules). Lines for archives and documentation; cards only with distinct imagery or summaries per item.
- Footer is always `minimal`.

### Store (`store.py`): hero, grid, product, cart, footer

- Hero `product` (1:1 photo beside text with price and one button) or `collection` (text then a 21:9 band). Product when one item leads; collection for seasonal launches.
- Grid `two`, `three` or `four` columns of 4:5 product tiles. Two for luxury and few items; three as the general default; four only for catalogues with small, similar tiles. Under 860px, three and four become one; two becomes one at 420px.
- Product `gallery-left` (1.2fr gallery with thumbnails beside info) or `gallery-top` (gallery above info in a 720px column). Top when photos are landscape or the brand is editorial.
- Cart `drawer` (over a scrim) or `page`. Drawer for stores where people keep browsing; page for considered purchases.
- Footer is always `columns`.

### Variants added in 0.3.0

Marketing heroes `ticker`, `specimen`, `manifesto`, `numbers`, `clip`, `stacked`; features `numerals`, `stack`, `strip`, `hover-list`, `cells`, `accordion`; proof `giant-quote`, `stat-wall`; call to action `ticket`; footer `colophon`; nav `bar`, `split-meta`, `menu-word`, `pill`, `rail`. Store heroes `lookbook`, `tiles`, grid `editorial`, product `sticky-buy`. Content header `broadsheet`, article `side-notes`, list `archive`. App shell `rail`, table `ledger`, detail `inspector`. Each is described in `archetypes.md` and switched on by a render hook (see `ideas.md`) or by `layout` in directions.json.

## How a style's layout_defaults choose variants

- Each `style.*` node carries `layout_defaults` keyed by page type, for example `style.swiss-grid.layout_defaults.marketing = {hero: poster, features: columns, proof: stats-sourced, cta: band, footer: minimal}`.
- `build_preview.py` reads `layout_defaults[brief.page_type]`, then merges `direction.layout` on top; `pick()` in `_shared.py` uses the merged value when it is in the section's `VARIANTS`, otherwise the first variant.
- A style with no defaults for the brief's page type (for example neo-brutalist on a store) renders the first variant of every section. When `recommend.py` proposes such a style, set `layout` explicitly so the draft is a design decision, not an accident.
- Two directions in the same preview must not share the hero variant, and should share at most one other section variant. Defaults already differ per style; check after overriding.

Precedence: a variant the author set in `directions.json` `layout` wins; then a render hook carried by one of the style's own `ideas`; then (for the hero) the style's `layout_defaults`, since the first screen is the style's identity; then any other hook from the direction's ideas; then the style's `layout_defaults` for the remaining sections; otherwise the first variant in the module's `VARIANTS`.

## Overriding layout in directions.json

Add a `layout` object to the direction with section names as keys and variant names as values:

```json
{
  "id": "b",
  "name": "Ledger",
  "bundle": { "style": "style.data-dense", "...": "..." },
  "layout": { "hero": "poster", "features": "alternating", "proof": "none" }
}
```

- Keys are the section names for the brief's page type only; keys for other page types are ignored.
- Unknown variant names fall back silently to the first variant. Copy names exactly from the lists above.
- Record why in `rationale` when an override departs from the style's defaults, quoting the brief.
- Rebuild with `build_preview.py` after editing; the gallery thumbnail changes with the hero.

## Touch targets

- Interactive elements are at least 44 by 44 CSS px (Apple HIG and WCAG 2.5.8 enhanced; https://www.w3.org/TR/WCAG22/#target-size-enhanced). Buttons, inputs and selects are `min-height: 44px` in the base CSS; `.pf-btn-sm` (36px) and tabs (40px) are allowed only when the surrounding row gives 44px of hit area or 24px of spacing to the next target.
- Row actions in tables: the whole row is the target, or the action gets 44px with `--pf-space-2` between targets.
- Spacing between adjacent targets is at least `--pf-space-2` so a thumb does not hit two.
- On phones the primary button goes full width (`.pfd-actions .pf-btn { width: 100% }` under 420px) and sits in the lower half of the first screen where the thumb rests.

## Safe areas

- Set `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` and pad fixed and edge-touching elements with `env(safe-area-inset-top|right|bottom|left)` (https://developer.mozilla.org/docs/Web/CSS/env).
- Catalogue values (portrait, CSS px): iPhone 17 family 62 top and 34 bottom, iPhone 16 family 59/34, iPhone 16e 47/34, Android about 24/20, iPads 24/20, MacBook Pro notch sits inside the 37px menu bar. In landscape the iPhone side insets equal the portrait top and the bottom is 21.
- A sticky top bar: `padding-top: env(safe-area-inset-top)`; a bottom tab bar or sticky checkout button: `padding-bottom: max(var(--pf-space-3), env(safe-area-inset-bottom))`.
- Turn on "Show safe areas" in the devices view; nothing interactive may sit inside the red bands.

## Viewport units

- Use `100dvh` (or `min-height: 100dvh`) for full-height heroes and app shells so the browser toolbar collapsing on phones does not leave a gap or a jump; `svh` for anything that must fit with the toolbar shown (first-screen call to action), `lvh` for backgrounds only (https://web.dev/blog/viewport-units).
- The draft uses `min-height: 100vh` on `.pfd` and `.pfd-shell`; replace with `100dvh` after handoff.
- Never size type with `vh`; size poster headlines with `clamp()` on `vw` or `cqi` and cap the ch width.
- Horizontal `100vw` includes the scrollbar on desktop; use `100%` or `inline-size` instead.

## Layout tells to avoid

- Cards around everything. A card wraps one object with its own actions. Sections, tables, forms and articles sit on the page with spacing or a rule; `data-dense` lists "cards around every table" in its `tells_to_avoid` for this reason.
- Three identical columns of icon, title, two lines. Use `list`, `alternating` or `bento` with a wide first cell; if `columns` is chosen, vary the copy length and drop the icons.
- Six identical cards in a two-by-three grid. Cap repeated cards at three with different weights, or switch to a list.
- The centred hero with a pill label above the headline. Centre only with a real image and a headline under 60ch; the kicker is a short noun in muted text, never uppercase.
- Decorative step numbers (01, 02, 03) beside features that are not steps.
- The same section rhythm down the whole page: hero, three cards, band, three cards, band. Alternate dense and open sections; the proof section may be `none`.
- Sidebar shells on marketing pages, and marketing heroes on app pages.
- A page that only works at 1280. Check 360 and 1536 in the devices view before showing it.

Sources: Vercel design guide on earned borders and no cards around sections (https://vercel.com/design.md); Apple Human Interface Guidelines on layout and 44pt targets (https://developer.apple.com/design/human-interface-guidelines/layout); WCAG 2.2 target size (https://www.w3.org/TR/WCAG22/); viewport units (https://web.dev/blog/viewport-units); container queries baseline (https://web.dev/baseline); device shares and viewports in `docs/research/2026-10-30-devices.md`.


## Archetypes (0.2.0)

Marketing heroes now default to the archetypes in `archetypes.md` (statement, mark, wrap,
product-first, object, bleed, index, poster, editorial); features to figures, spec, index or
bands; proof may be a statement; the call to action and footer may be giant. `centered` plus
`columns` is never a default. Every style carries `art` and `conventionality`.
