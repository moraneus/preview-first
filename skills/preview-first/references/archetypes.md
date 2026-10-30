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
| `collage` | The wordmark at poster size with four to five images at hand-set, uneven positions and rotations; corner metadata (role, city, local time). | Framer "Caspia", https://rauno.me | designers, photographers, agencies, fashion | evenly spaced or mirrored images read as a grid again; respect reduced motion |
| `letter` | A narrow essay: date line, centred title, first-person paragraphs at 19 to 21px, a signature. No media, no cards. | https://arc.net (farewell letter), https://press.stripe.com | announcements, manifestos, founders' notes | the prose must be specific; no call-to-action band mid-letter |
| `ticker` | The brand name or a two-word claim at 20vw as a single-line marquee, one sentence and one link beneath. | https://basement.studio, https://lamalama.com | studios, launches, brutalist brands | one word, slow, paused on hover |
| `specimen` | The headline presented like a foundry specimen: mono metadata in the corners (face, size, year, time), hairlines above and below, numerals in a strip. | https://klim.co.nz, https://pangrampangram.com | engineering, type-led brands | the metadata must be true |
| `manifesto` | One paragraph of 60 to 120 words at 28 to 44px, left aligned, no headline, no buttons, one inline link. | https://arc.net, https://press.stripe.com | editorial, founders' notes, calm products | needs real prose |
| `numbers` | Three sourced figures at 96 to 160px with captions as the first screen; renders only when `copy.numbers` exists. | https://stripe.com/newsroom, https://posthog.com | data products, annual letters | invented numbers are the tell |
| `clip` | The name set larger than the viewport so the first and last letters bleed off; a small line in the exposed corner. | https://lusion.co, https://exo-ape.com | poster brands, agencies | needs a short name |
| `stacked` | Three or four words stacked one per line, alternating solid and outlined. | https://obys.agency, https://cuberto.com | studios, events, colour-blocked brands | keep to four lines |
| `poster` | Poster-scale headline as the image, subhead and actions beside, one mark at the side. | https://lusion.co, https://basement.studio | agencies, events, portfolios | headline under 12 words; tracking tight |
| `editorial` | Kicker, headline, lead, a side note with a figure. | publishing, knowledge tools | content-first products | avoid oversized italic serif |
| `split`, `centered` | The familiar layouts, kept for briefs that ask for them by name. | | | `centered` is the tell; never a default |

## Section archetypes

- Features `figures`: three captioned figures (Fig 1.1, 1.2, 1.3) with hairline rules, title and one sentence each. Captions in mono. Linear.
- Features `spec`: a specification list with a heavy rule above each row, term left, description centre, index number right. Technical and luxury products.
- Features `index`: a sticky figure on the left, large titles with one sentence each on the right.
- Features `bands`: full-bleed alternating surface bands, text left, artwork right. Consumer products.
- Features `ledger`: full-width rows with a big title left, one to three small thumbnails, a count in parentheses and a year on the right, hairlines between rows. Studios, portfolios, archives, changelogs (https://locomotive.ca, https://lamalama.com).
- Features `numerals`: 01, 02, 03 at 120 to 200px in 12 percent ink beside a title and one sentence (https://locomotive.ca, https://significa.co).
- Features `stack`: sticky cards that pile with a 16px lip, each a shade darker (https://www.apple.com/iphone/).
- Features `strip`: a horizontal scroll-snap row with the last card cut by the viewport and a mono count (https://www.ssense.com).
- Features `hover-list`: plain rows, hovering reveals an image that follows the pointer (https://dennissnellenberg.com, https://locomotive.ca).
- Features `cells`: a bordered grid with plus marks at the intersections and uneven spans (https://vercel.com, https://linear.app/changelog).
- Features `accordion`: hairline rows with a rotating plus, one open at a time (https://www.aesop.com).
- Proof `giant-quote`: one attributed quote at 40 to 64px with hanging punctuation (https://linear.app/customers).
- Proof `stat-wall`: three or four sourced figures at 96px with footnote sources; renders only when `copy.stats` exists.
- Call to action `ticket`: a ticket with a perforated stub, mono meta and the single action (https://basement.studio).
- Footer `colophon`: one mono line with the brand, year, local time, the face in use, the version and the real links (https://rauno.me, https://paco.me).
- Store: `lookbook` and `tiles` openings, the `editorial` uneven grid, the `sticky-buy` product page. Content: the `broadsheet` masthead, `side-notes` reading layout, `archive` index. App: the icon `rail` shell, `ledger` table, `inspector` panel, command palette.
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
| `figure` | A small captioned line figure (stack, grid, flow, rings, bars, wave, dots, steps, cross, ladder, arc, target, beam; thirteen kinds chosen by seed) | feature sections |
| `ascii` | A field of mono characters whose density follows a wave and a disc, peaks in primary | phosphor terminal, dark console |
| `dither` | Bayer-ordered dithering of a radial light and a horizon band in two palette colours | acid lab, neo-brutalist |
| `flowfield` | Particles traced through a vector field, every ninth path in primary | technical and scientific products |
| `strands` | Horizontal wave strands bunching in the middle | night grain |
| `stamp` | A rotated circular stamp with text on a path | signal orange, collage heroes |
| `ruler` | Measurement ticks with one highlighted span | archive index, specification pages |
| `globe` | A wireframe globe with markers | infrastructure, travel |
| `specimen` | A type specimen block in the direction's own heading face | type-led heroes |
| `pixel` | A coarse symmetric pixel mark | retro and games |
| `scan` | An oscilloscope panel with scanlines and one waveform | hardware |
| `grain_disc` | One flat disc with film grain and a horizon line | clay canvas, lookbooks |
| `ticket` | A ticket with perforation, serial and barcode | events, launches |
| `object` | A flat vessel, box, cup, tube or disc on a seamless with one hard shadow | store product stand-ins |

Artwork is a stand-in with real visual weight. The contract tells the builder to replace it
with product imagery or photography of equal weight, never stock photos or icon boxes.

## Choosing and overriding

Styles carry `layout_defaults`, `art`, `conventionality` and `ideas`. The recommender puts at
least two `distinct` styles in every set and attaches eight to twelve ideas per direction; ideas
with render hooks pick the nav, hero and section variants unless the author pinned them in
`layout`. Override per direction with `layout` and `bundle.ideas`; do not fall back to
`centered` plus `columns` because it is safe. See `ideas.md`.

## Measured on 47 admired sites (2026-10-30)

From `docs/research/2026-10-30-layout-archetypes.md`, which loaded each site in headless Chromium and probed computed styles:

- Headline left-anchored on 19 of 35 real product and studio sites; zero hero buttons on 11; the "two buttons" pattern on 7. No admired site used three icon cards.
- 1px hairlines in `currentColor` at 8 to 15 percent alpha are the primary separator on product sites (Resend 107 instances, Linear 84, Warp 84, Raycast 68). The CSS uses `color-mix(in oklab, var(--pf-color-text) 12%, transparent)`.
- Mono is a labelling voice on 17 sites: captions, indices, dates, counts, 11 to 12px, tracking .04 to .08em, never the body (except the specification-sheet archetype).
- Display to body ratio runs 4 to 6 times on product sites and 13 to 30 times on poster and studio sites; the template's 2.5 to 3 times is itself a tell.
- Footers are bimodal: a one-line colophon under 70px, or a composition over 650px with a cropped giant wordmark, an address or a version number. Almost nobody ships the 350px four-column middle.
- `tabular-nums` on anything that counts; `text-wrap: balance` on headings and `pretty` on prose; hover underlines with `text-underline-offset: .2em`.

## Craft details that recur on handmade sites

Hanging punctuation on display quotes; tabular numerals in data; captions on every figure;
hover underlines with offset; 1px rules in text colour at low alpha; sentence-case labels;
one orchestrated load, then stillness; section numbering only when the content is a sequence;
a giant footer; copy that names the product's real nouns.
