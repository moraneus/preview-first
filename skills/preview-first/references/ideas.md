# Design ideas

The graph holds several hundred `idea` nodes: reusable moves observed on modern sites and
templates, each with a description, an implementation note, the sites it was seen on, a tell
risk, and edges to the styles, product types and moods it fits. They are the answer to "it
still looks like a generated site": a direction is no longer a palette plus a type pairing on a
fixed skeleton, it is a style plus eight to twelve specific ideas that change the navigation,
the first screen, the sections, the texture, the type details and the motion.

## Where ideas come from

A research sweep on 2026-10-30 across seven categories: developer tools and SaaS, studios and
award sites, fashion and hardware commerce, editorial and type foundries, templates and trend
reports, motion and interaction, typography and colour systems. Each idea cites the pages it
was taken from (`seen_on`, with `opened` marking pages that were actually fetched). Nothing is
copied; the idea is described generally enough to be rebuilt in the direction's own palette
and type. See `docs/research/2026-10-30-modern-design-ideas.md`.

## How a direction gets its ideas

`recommend.py` scores every idea for a style: the style's own `ideas` list first, then
`pairs_with` edges from the idea to the style, `suits` edges from the product type and
`expresses` edges from the moods. It then fills coverage slots (navigation, hero, type or
craft, section, imagery or colour or texture, motion, footer or component) and tops up to ten.
Rules:

- One idea per render hook inside a direction, and one hero, one nav, one footer, one proof
  and one call-to-action device.
- Across the set, no two directions share a nav, hero, texture, section, footer, proof or
  call-to-action device, so the gallery reads as five different sites.
- Ideas with `ai_tell_risk: high` are kept in the graph as warnings and are only chosen when a
  style names them in its own `ideas` list.
- Ideas with `page_types` only apply to those page types.

The chosen ids land in `bundle.ideas`; the author may edit the list in `directions.json`.

## Render hooks

An idea may carry `renders`, one of the closed hook names in `knowledge/schema.json`. The draft
engine turns hooks into markup, CSS and small scripts; everything else in the idea goes to the
contract for the builder. Hooks by group:

| Group | Hooks | What changes in the draft |
|---|---|---|
| Navigation | `nav-bar`, `nav-split-meta`, `nav-menu-word`, `nav-pill`, `nav-rail` | the nav variant: one line; wordmark, city and live time, "Menu"; wordmark and "Menu" with a full-screen overlay; floating pill; numbered side rail |
| Hero | `hero-ticker`, `hero-specimen`, `hero-manifesto`, `hero-numbers`, `hero-clip`, `hero-stacked` | the first screen, unless the author pinned `layout.hero`; `hero-numbers` falls back to the statement when the copy has no sourced `numbers` |
| Sections | `section-marquee`, `features-numerals`, `features-stack`, `features-strip`, `features-hover-list`, `features-cells`, `features-accordion`, `proof-giant-quote`, `proof-stat-wall`, `cta-ticket`, `footer-colophon` | a marquee of real nouns between hero and features; the features, proof, call to action and footer variants |
| Texture | `texture-grain`, `texture-grid`, `texture-crosses`, `texture-scanlines`, `texture-rules` | fixed grain layer, graph-paper grid behind the hero, plus marks at section corners, scanlines, ruled lines |
| Type | `type-outline`, `type-mixed-face`, `type-vertical-label`, `type-index-numbers`, `type-tight-display`, `type-hanging-punctuation`, `type-tabular` | one outlined word or one word in the mono, vertical section labels, "( 01 )" indices and figure captions, tight display tracking, hanging punctuation, tabular numerals |
| Buttons | `button-bracket`, `button-fill-up`, `button-circle-icon`, `button-underline` | `[ Get started ]` in mono, fill rising on hover, pill with a circled icon, plain underlined secondary |
| Motion | `motion-line-reveal`, `motion-cursor`, `motion-magnetic`, `motion-preloader`, `motion-count-up`, `motion-hover-swap`, `motion-scroll-progress`, `motion-view-transitions` | line mask reveal on the headline, custom cursor (fine pointers, never in embeds), magnetic primary buttons, counter preloader at level 3, count-up figures, hover image swap, a 1px progress hairline, cross-page transitions |
| Imagery | `image-duotone`, `image-dither`, `image-ascii`, `image-caption`, `image-sticker` | duotone filter on artwork, dithered or ASCII hero art, figure captions, rotated stickers with true words |
| Colour | `color-blocking`, `color-inverted-section`, `color-single-accent` | full-bleed blocks in bg, primary and ink; the last two sections inverted to ink; accent equals primary |
| Store, content, app | `store-lookbook`, `store-tiles`, `store-editorial-grid`, `store-sticky-buy`, `content-broadsheet`, `content-side-notes`, `content-archive`, `app-rail`, `app-ledger`, `app-inspector`, `app-command-palette` | the page-type variants of the same names |

Motion hooks respect `prefers-reduced-motion`, the motion level and the reduced-motion
simulation switch; the cursor and preloader never run inside gallery thumbnails or device
frames.

## Authoring ideas

Add an idea when you can name a real site that does it and describe it well enough to build.
Required: `category`, `what` (two or three sentences with values), `implementation` (one or two
lines, naming platform features), `ai_tell_risk` with `ai_tell_note`, `seen_on` (one to four
URLs). Give it `renders` only when the draft engine has a hook that shows exactly that idea;
otherwise leave it as a contract-only idea. Add `pairs_with` edges to the styles it fits and
list it in a style's `ideas` when it should always travel with that style. Run
`validate_graph.py`; unknown hooks and missing sources are errors.

## Tells kept as ideas

Some entries describe moves that now read as generated: the Instrument Serif italic accent
word, the Relume section library order, the bento grid of six equal cards, the purple gradient
hero, the glass card over a flat background. They carry `ai_tell_risk: high`, their
`ai_tell_note` says why, and the recommender never picks them unless a style asks. They stay
in the graph so the contract can name what to avoid with a reason.
