# Layout archetypes and generated artwork

The generic template is the strongest tell of generated design: navigation, a centred headline
with an eyebrow, two buttons, a screenshot, three identical icon cards, a logo bar, stats,
testimonials, a call-to-action band, a sitemap footer. preview-first never opens a direction
with it. Each style defaults to one of the archetypes below, observed on sites designers admire
(screenshots taken 2026-10-30; sources per archetype), and to artwork generated from the
direction's palette so no section shows a wireframe.

## Hero archetypes (`layout.hero`)

| Variant | What the first screen is | Seen on | Suits | Pitfalls |
|---|---|---|---|---|
| `statement` | A two-tone paragraph (headline strong, continuation muted) at display size, one inline link, then three captioned line figures with hairline column rules. No buttons above the fold. | https://linear.app | developer tools, infrastructure, AI products, anything with a strong idea | the paragraph must be one real sentence, not a tagline plus filler |
| `mark` | Giant left-aligned headline, one geometric mark in the centre, a three-line list on the right. Radical whitespace. | https://vercel.com | platforms, infrastructure, confident brands | needs a real mark; the list must be three true things |
| `wrap` | A framed stage: giant grotesque headline with alternating indents wrapping a single flat disc of accent colour; subhead and inline link below the frame. | https://rauno.me | portfolios, studios, launches, anything personal | keep one disc, flat colour, no gradient; square corners |
| `product-first` | A bordered stage: headline and two actions on the left, the real product window on the right bleeding past the frame edge. | https://cal.com | SaaS, tools with a visible UI | the window must be the product, not an illustration of one |
| `object` | Serif or display headline left with a small badge above, one large object right on a dark field. | https://resend.com | developer tools, premium products | the object carries the page; a weak object reads as decoration |
| `bleed` | Full-bleed artwork or photograph with a small centred text panel. | https://www.aesop.com | luxury, hospitality, fashion, wellness | text must sit on a quiet panel; the focal point stays off centre |
| `index` | A sticky left column with wordmark, one sentence and the page's table of contents; content and artwork on the right. | editorial sites, documentation, long product pages | content-heavy pages | the index must link to real sections |
| `poster` | Poster-scale headline as the image, subhead and actions beside, one mark at the side. | https://lusion.co, https://basement.studio | agencies, events, portfolios | headline under 12 words; tracking tight |
| `editorial` | Kicker, headline, lead, a side note with a figure. | publishing, knowledge tools | content-first products | avoid oversized italic serif |
| `split`, `centered` | The familiar layouts, kept for briefs that ask for them by name. | | | `centered` is the tell; never a default |

## Section archetypes

- Features `figures`: three captioned figures (Fig 1.1, 1.2, 1.3) with hairline rules, title and one sentence each. Captions in mono. Linear.
- Features `spec`: a specification list with a heavy rule above each row, term left, description centre, index number right. Technical and luxury products.
- Features `index`: a sticky figure on the left, large titles with one sentence each on the right.
- Features `bands`: full-bleed alternating surface bands, text left, artwork right. Consumer products.
- Proof `statement`: the proof line (or the headline) as a two-tone paragraph; use only sourced claims.
- Call to action `giant`: the lead, two actions, then the wordmark at poster size in 8 percent ink as a closing gesture.
- Footer `giant`: the wordmark at poster size, one true sentence, the real links.

## Generated artwork (`style.art`)

`drafts/art.py` renders deterministic SVG from the palette tokens, seeded by direction id so a
rebuild gives the same picture and a palette swap recolours it live.

| Kind | What it draws | Default for |
|---|---|---|
| `ui_mock` | A product window: title bar, sidebar, list rows, a line chart, a table with status pills | soft product, bento showcase |
| `terminal` | A terminal panel with prompt lines in token colours and a blinking cursor | dark console |
| `blueprint` | Fine grid, isometric outline, dimension lines, corner marks, a mono figure label | monochrome engineering |
| `isometric` | Stacked line-art slabs with one filled disc | lab figures |
| `swiss` | Circles, quarter arcs and bars in primary, accent and ink on a three-column grid | Swiss grid, playful geometric |
| `contours` | Topographic contour rings, every fourth in primary | paper editorial, warm organic |
| `halftone` | A dot field with an off-centre focal disc | quiet luxury, neo-brutalist sections |
| `orbit` | Concentric rings with markers and a filled core | luminous dark |
| `stickers` | Rotated badges with thick outlines and hard shadows | neo-brutalist |
| `sparklines` | A grid of numerals with sparklines | data dense |
| `mark` | One large geometric mark | poster type, studio wrap |
| `glass` | Translucent panels over a colour disc | glass layered |
| `figure` | A small captioned line figure (stack, grid, flow, rings, bars) | feature sections |

Artwork is a stand-in with real visual weight. The contract tells the builder to replace it
with product imagery or photography of equal weight, never stock photos or icon boxes.

## Choosing and overriding

Styles carry `layout_defaults`, `art` and `conventionality`. The recommender puts at least two
`distinct` styles in every set. Override per direction with `layout` and, for artwork, by
switching style; do not fall back to `centered` plus `columns` because it is safe.

## Craft details that recur on handmade sites

Hanging punctuation on display quotes; tabular numerals in data; captions on every figure;
hover underlines with offset; 1px rules in text colour at low alpha; sentence-case labels;
one orchestrated load, then stillness; section numbering only when the content is a sequence;
a giant footer; copy that names the product's real nouns.
