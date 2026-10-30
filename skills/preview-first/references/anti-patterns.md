# Anti-patterns: the tells of generated design

The authoritative list. Claude applies it to every direction it authors, to every page it builds after handoff, and to the preview chrome itself. A tell is any choice that readers now recognise as the default output of a model rather than a decision made for this product.

## The refusal rule

Do not use a tell unless the brief asks for it by name. If it does, use it and note it in the direction's `rationale` ("brief asks for a purple gradient hero; kept to the hero only"). A mood word is not a request by name: "modern" does not ask for a gradient, "friendly" does not ask for emoji, "premium" does not ask for an italic serif. When unsure, treat the item as a tell and choose the instead rule.

Style nodes in `knowledge/graph.json` carry `tells_to_avoid`; read them for the chosen style before authoring and check the draft against them before showing it.

## Colour and effects

| Tell | Instead |
|---|---|
| Purple gradients, indigo to violet or blue to pink, on heroes, buttons or backgrounds (origin: Tailwind `indigo-500`) | One solid `primary` from a palette node; gradients only when the brief names them, and then one, on one surface |
| Gradient text in headlines | Headline in `text` colour; let the typeface carry the weight |
| Gradient buttons | Solid, outline, ghost or soft fills from the `button_fill` axis |
| Purple, blue or pink glow blobs behind content | A tinted `surface` band or nothing; `luminous-dark` earns its glow with a single accent and real product imagery |
| Glass without layering: `backdrop-filter` over a flat background | `card_edge` `inset` only over imagery or colour; otherwise `border` or `flat` |
| Dark mode by default with medium-grey body text on near-black | Dark only when the brief or product type asks; body text passes the `text on bg` body check in the palette (4.5:1 WCAG, APCA 60 or better) |
| Five or more gradient or blurred backgrounds on one page | Zero or one |
| Cream plus terracotta as the default warm palette | A warm palette chosen for the product: pick a different hue family from the graph, or a neutral with one named accent |
| Gold gradients and metallic effects for "premium" | Flat ink on paper, generous spacing, one restrained accent (`quiet-luxury`) |
| Neon accents on dark for anything not a developer tool | Cool or neutral palette with a mid-chroma accent that passes the `primary on bg` check |
| The same grey shadow under everything | `elevation` `none` or `one`; shadows under 6% total opacity, only on surfaces that float |
| Rounded corners plus soft shadow on every element | Pick a `radius_scale` and a `card_edge` and apply them consistently; most elements get no shadow |

## Typography

| Tell | Instead |
|---|---|
| Inter everywhere (also Geist, Space Grotesk, Plus Jakarta) with no decision behind it | A pairing node chosen for the product and a reason in the rationale; a system or grotesque body is fine when paired with a chosen display face |
| Oversized italic serif headline as the one idea | Serif display set roman at a measured size, or a grotesque; italic for emphasis inside a line only |
| All-caps tracked eyebrow label above the headline | Sentence case kicker in muted text (`.pf-kicker`), or no kicker |
| All-caps labels anywhere (table headers, buttons, badges, section labels) | Sentence case; weight and colour do the labelling |
| Centred hero copy in a generic sans | Left-aligned text, or centred only with a real image and a short headline |
| One word in a different colour inside the headline | Plain headline; emphasis by structure |
| Mono used for body copy or headings because it looks technical | Mono for code, ids, paths, timestamps and tabular data only |
| Headlines wider than 18ch, paragraphs past 70ch | Cap headlines at 12 to 18ch and prose at `--pf-measure` |
| Letter-spacing added to body or display text | Default tracking; slight negative tracking on large display sizes only (`-0.01em` to `-0.04em`) |
| Font sizes picked freely | The `--pf-text-*` scale from the pairing's ratio |

## Layout and components

| Tell | Instead |
|---|---|
| Identical three cards with an icon, a title and two lines | `list`, `alternating`, or `bento` with one wide cell; vary copy length; no icons unless each shows the product |
| Six identical cards in a grid | At most three, with different weights, or a list with rules |
| Cards around everything (sections, forms, tables, articles) | Spacing or a rule; a card wraps one object with its own actions |
| Centred hero plus "Now in beta" pill | Hero variant chosen for the content; a kicker only if it says something true |
| Fake logo bars ("Trusted by" with invented or borrowed marks) | `proof` `logos-text` with names you are allowed to use, or `none` |
| Invented stats (10k users, 99.9% uptime, 4.9 stars) | `proof` `stats-sourced` with a figure and its source, or no stats |
| Testimonials with first names and initials, stock avatars or gradient initials | A real attributed quote with permission, or the placeholder that says one is needed |
| Decorative step numbers 01, 02, 03 | Numbers only for ordered steps, set in the body face |
| Arrows appended to links and buttons ("Learn more ->") | The label alone; underline or colour marks the link |
| Emoji icons (in lists, cards, headings, buttons) | Icons from the bundle's icon set at 24px, or no icon |
| Checkmark bullet lists of benefits | Prose, a numbered list, or a list with rules |
| Pill tag clouds of features | Short sentences |
| Rounded-corner screenshot mockups with a fake browser chrome and a gradient behind | The screenshot itself, cropped with intent, at `image_corner` |
| Two filled buttons side by side | One primary and one secondary or quiet (see components.md) |
| The same page rhythm repeated: cards, band, cards, band | Alternate dense and open sections; drop sections the product cannot fill |

## Copy

| Tell | Instead |
|---|---|
| Em dashes, in copy, in rationale, in code comments | Commas, colons, full stops, or two sentences |
| Lorem ipsum or "Your headline here" | Copy from the brief's own words (`default_copy()` builds it); when something is unknown, say so in plain words |
| "It's not just X, it's Y"; "Whether you're X or Y"; "Build faster. Ship smarter."; "Unlock", "Elevate", "Seamless", "Supercharge" | Say what the product does, for whom, in a sentence a user would say |
| Tricolons and rule-of-three everywhere | As many items as there are; two or four are fine |
| Buzzword features ("AI-powered insights") | The actual capability and its outcome |
| Title Case Headlines And Buttons | Sentence case |
| Exclamation marks, "Welcome to" | A statement |
| Invented names, companies and figures in testimonials, tables and footers | Names from the brief; otherwise neutral placeholders that are visibly placeholders ("Name, role, company") |
| Footer legal copy and addresses that are made up | The brand name and a sentence that says the copy is from the brief |

## Motion

| Tell | Instead |
|---|---|
| Scroll-reveal on every section | Stillness by default; at most one entrance pattern, once, on the hero, respecting `prefers-reduced-motion` |
| Marquees of logos or words | A static sentence |
| Typing cursors and typewriter text | The finished sentence |
| Pulsing dots, breathing glows, infinite ambient loops | A static status badge; ambient motion only at motion level 3 and when the brief asks |
| Parallax backgrounds | Fixed layout |
| Bounce easing on UI | `--pf-ease-out` for entrances, `--pf-ease-in-out` for moves, `ease` for colour; spring only for switches and drags |
| Hover zoom on imagery | Nothing, or a 1px border change |
| Transitions over 300ms on controls, page transitions over 400ms | Durations from `--pf-dur-*` (120 to 480ms depending on motion level) |
| Animating width, height, top or left | `transform` and `opacity` only |
| Motion that ignores reduced motion | Fades instead of movement under `prefers-reduced-motion: reduce`; nothing moves at motion level 0 |

## Imagery

| Tell | Instead |
|---|---|
| Fake photos, generated faces, stock handshake imagery | The product itself, or an honest labelled placeholder (`.pfd-media`) |
| Abstract 3D blobs, floating glass shapes, isometric illustrations | Product screenshots or nothing |
| Icons as the hero image | A screenshot, a photograph the team owns, or a type-led hero |
| Gradient-initial avatars | Neutral circle in `border` colour until a real avatar exists |
| Screenshots with fake data (Acme, John Doe, 1,234) in a shipped build | Real or representative data; the preview's draft table rows are placeholders and are labelled as such in the footer |
| Images without alt text or captions | Alt text that says what the image shows; captions on editorial lead images |
| Borrowed logos of real companies | Names in text, with permission |

## Pre-show checklist

Run on every direction before `serve_preview.py --open`, and once on the preview chrome. Fix, rebuild, then show.

Each direction:

1. No gradient anywhere unless the brief named it; no gradient text.
2. No purple, indigo or violet primary unless the brief's `brand_colors` contain it.
3. Heading face chosen for a reason stated in `rationale`; not Inter or Geist by default.
4. No all-caps text: kickers, table headers, buttons, badges, footer headings are sentence case.
5. No em dash in `name`, `rationale`, `copy` or the draft.
6. No emoji in copy or as icons; icons come from `bundle.icon_set`.
7. No lorem ipsum, no invented statistics, names, companies or logos; proof is `quote` with a real attribution, `logos-text` with names, `stats-sourced` with a source, or `none`.
8. No arrows appended to link or button labels.
9. Features section is not three identical cards unless the brief asked for columns; no six-card grid.
10. Cards only around objects; the table, form and article are not inside cards.
11. `card_edge` `inset` and `nav` `floating` only with something behind them.
12. Motion: at most one entrance pattern, no scroll-reveal on every section, no marquee, no pulsing; motion level matches the brief's `constraints.motion_level`.
13. Palette checks all pass in both schemes (`resolve_palette` warnings are empty), including `focus on bg` and `primary on bg`.
14. Every control is 44px tall; the primary button is single per view and full width at 360.
15. The draft reads at 360, 1280 and 1536 in the devices view; nothing clips, nothing is under a cutout or inside the safe-area band.
16. The style's own `tells_to_avoid` list is clear.
17. If the brief named a tell, the rationale says where it is used and why it is confined.

The preview chrome (`.pfc-*`, `.pfg-*`):

1. Neutral grey only; the chrome never carries a hue that competes with a direction.
2. System font, sentence case, no icons, no arrows, no emoji.
3. Labels are nouns: "Palette", "Type", "Density", "Motion", "Theme"; buttons are verbs: "Select", "Load", "Rotate".
4. No gradients, no shadows beyond the toast, no decorative dividers.
5. The gallery shows three to five directions, each thumbnail at the same 1280x800 scale, each with a different hero.

## Keeping directions different

Three to five directions in one preview must be separable at a glance in the gallery. Enforce all four:

- Family: no two directions share a `style.family` (`minimal`, `editorial`, `technical`, `soft`, `expressive`, `dark`, `bold`). Five directions means five families.
- Temperature: palettes differ in `temperature` across the set; at most two `neutral`, and never two `warm` unless the brief constrains hue. Mix `scheme` too: at least one light and, when the product type allows it, one dark or both.
- Type category: heading faces differ in `category` (`grotesque`, `humanist`, `geometric`, `neo-grotesque`, `serif-transitional`, `serif-old-style`, `serif-didone`, `serif-slab`, `mono`, `display`, `system`). Two serif directions must be different serif categories.
- Layout variants: no two directions share the hero variant; features variants differ in at least three of four directions; treatments differ on at least four axes between any pair (see layout.md and components.md).

Also vary density and radius scale across the set, and give each direction a name that is a noun from the product's world, not an adjective ("Ledger", "Darkroom", "Broadsheet"; not "Modern", "Clean", "Bold").

Sources: slop-detect checklist (https://github.com/ravidsrk/slop-detect); 925 Studios on AI design tells (https://www.925studios.co/blog/ai-slop-design-tells); Tenex on eight signs including the oversized italic serif and cream plus terracotta (https://tenex.studio/en/blog/ai-slop-8-signs/); why generated sites share Tailwind indigo-500 (https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p); Vercel design guide rejecting tracked eyebrows, marquees, typing cursors, pulsing indicators, parallax, scroll-reveal and cards around sections (https://vercel.com/design.md); the Linear effect on dark luminous sameness (https://rectangle.substack.com/p/the-linear-effect); Emil Kowalski on durations and easing (https://emilkowal.ski/ui/great-animations); reduced motion done right (https://www.joshwcomeau.com/react/prefers-reduced-motion/); section 4 of `docs/research/2026-10-30-design-directions-motion-platform.md`.
