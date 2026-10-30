# Modern design ideas: the research sweep behind the ideas graph (2026-10-30)

Why this exists: after two rounds of layout archetypes the owner still judged the drafts "AI
default design". A diagnosis with screenshots (five directions for the same SaaS brief) found
one skeleton shared by every direction, the same five line figures repeated, the subhead
pasted three times per page, and the generated-site default faces (Geist, Inter, Plus Jakarta).
The fix was not another palette. It was to go and look at what handmade sites do in 2025 and
2026, store each move as a sourced node, and let the recommender compose a direction from them.

## Method

Seven researchers ran in parallel, each on one category, with WebSearch and WebFetch only
(no shared browser). Each wrote a JSON list of 45 to 85 ideas in a fixed shape (slug, name,
category, what, why, seen_on, opened, suits, pairs_with, avoid_with, pitfalls, tell risk and
note, implementation, renderable, year, confidence), a list of 15 to 27 reference sites, and a
notes file with values quoted from CSS and official design documents. Many 2026 sites are
rendered client-side or behind bot protection; the notes record which pages were actually
opened, which values come from third-party token extractions (lower confidence), and which
sites were unreachable. `tools/merge_ideas.py` normalised the files into `idea` and
`reference-site` nodes, inferred `pairs_with`, `suits` and `expresses` edges from the suits
and pairing words, and assigned render hooks conservatively (slug and name match only, never
for high-risk entries, with a hand-written override list). Fifty-two hook-bearing ideas were
hand-authored first so that every hook has a canonical, tested carrier.

Categories and starting lists:

| Category | Starting points | Notes file |
|---|---|---|
| Developer tools and SaaS | Linear, Vercel, Resend, Raycast, Warp, Clerk, Supabase, Neon, Cursor, Zed, Ghostty, Arc, PostHog, Railway, Fly, Tailscale, Liveblocks, Granola, Attio, Cal.com, Polar, Modal, Anthropic, Mistral, Perplexity, Notion, Sanity, Family, Craft | notes-devtools.md |
| Studios, agencies, portfolios, award sites | Locomotive, Basement, Lusion, Darkroom, Hello Monday, Unseen, Obys, Significa, Phantom, Immersive Garden, Build in Amsterdam, Lamalama, Mouthwash, Instrument, Collins, Pentagram, Koto, Cuberto, Exo Ape, Rauno, Paco, Emil Kowalski, Jhey, Awwwards SOTY and SOTM 2024 to 2026 | notes-studios.md |
| Fashion, luxury, hardware, commerce | Teenage Engineering, Nothing, Freitag, Bang & Olufsen, Arc'teryx, Rapha, Oura, Apple, Framework, Playdate, Acne, Byredo, Le Labo, Carhartt WIP, On, Sonos, Eight Sleep, Panic, Polestar, Analogue, Liquid Death, Our Legacy, Satisfy | notes-commerce.md |
| Editorial, publishing, docs, foundries | The Pudding, Stripe Press, Are.na, Works in Progress, Asterisk, Craig Mod, Every, Quanta, Noema, Aeon, LRB, n+1, Monocle, Kinfolk, Walker Art Center, Letterform Archive, Klim, Dinamo, Commercial Type, Pangram Pangram, Grilli, Displaay, Swiss Typefaces, Mintlify, Stripe docs, Starlight, Fumadocs | notes-editorial.md |
| Templates, galleries, trend reports, tells | Framer marketplace (Caspia, Soren, Neiden, Arpeggio, Mugen, Fabrica), siteinspire, minimal.gallery, curated.design, httpster, dark.design, recent.design, designspells, footer.design, slop catalogues (impeccable.style, adriankrebs, falia, 925 Studios), craft essays (Rauno, Emil Kowalski, Josh Comeau, Jim Nielsen, Max Böck, Robin Rendle) | notes-templates.md |
| Motion, interaction, 3D, generative | Codrops 2024 to 2026 (via reader proxy), GSAP, Lenis, animations.dev, motion.dev, Osmo, Vaul and Sonner, scroll-driven animations, view transitions, ASCII and dither renderers, ghost trails, square lens | notes-motion.md |
| Typography and colour systems | Fonts in Use, Typewolf, Google Fonts releases 2024 to 2026, Fontshare, free foundries, Radix Colors, Tailwind v4, Open Props, Evil Martians Harmony, the palettes of the sites above | notes-type.md |

## What the sweep found

Across categories the same handmade signals recur, and they are what the drafts now carry:

- **Zero radius, hairline, no shadow** is the luxury, hardware and studio default (Aesop,
  SSENSE, Bottega Veneta, Teenage Engineering, Liquid Death, Polestar, Nothing at 6 to 8px
  most). Separation is a 1px rule at 8 to 15 percent alpha or a flat surface change.
- **No brand colour, or one hot colour on under five percent of the page**: SSENSE, Nothing,
  Polestar and Analogue run grey-only interfaces; Teenage Engineering, Rapha, Arc, Mistral and
  Cursor use one saturated colour for prices, one band or one action.
- **Mono as the labelling voice**: captions, indices, dates, counts and metadata at 11 to 12px
  with light tracking on 17 of 47 sites in the earlier survey and most studio sites here;
  Warp's `[ fig. 1 ]` captions, Lamalama's `( 01 )` indices, Klim's "Site build" timestamp.
- **Metadata as design**: live local time in the nav or footer (Obys, Locomotive, How&How,
  Sterling), coordinates, version and commit hashes (jhey.dev), issue numbers instead of dates
  (Monocle), coarse dates (Walker, LRB), "Set in" colophons.
- **Dates are the biggest editorial differentiator**: coarse dates, issue numbers, status
  lines and collapsed ranges; nobody uses a calendar icon.
- **The first screen is rarely a centred headline**: single-word stacks (Locomotive, Immersive
  Garden, Significa), the work itself with no headline (Blond), a letter (Arc), a specimen
  (Klim, Sharp Type), a ticker (Basement, Lamalama), category tiles (Arket), sourced numbers.
- **Studio motion is one orchestrated load, then stillness**: line mask reveals at 0.8s with
  80ms stagger on the "osmo ease" `0.625, 0.05, 0, 1`, under 300ms for interface motion
  (Emil Kowalski, Liveblocks), preloader counters only on showcase sites, hover image reveals
  on project lists, magnetic buttons at 8px, custom cursors on studios only.
- **Texture is back**: film grain over flat colour (Resend's noise.png, Significa, Darkroom,
  Lusion), scanlines on hardware brands, dithering and ASCII as developer-brand imagery
  (Vercel Ship, Basement, Ghostty), paper tones such as #F4F1EA, #FAF9F5, #F7F7F2 instead of
  white, warm near-blacks such as #1C1917 and #2B2622 instead of #000.
- **Colour as structure**: full-bleed blocks in two or three solid colours with the nav
  inverting over each (Arc's single blue band, COS, Polestar), an inverted closing section
  (Locomotive, Aesop), cream and ink bands (Anthropic).
- **Lists, not cards**: hover lists for work, ledgers for archives, spec sheets for products,
  accordions with a plus for questions, archives with dates and counts.

### Hard values worth keeping

From official design documents and CSS read directly (see the notes for the full set):

- Resend design.md: display 96/96 at -0.96px, title 60/64 at -2.8px, body 16/24, mono 14/20;
  glass blur 25px; "never use Domaine in bold", "sentence case everywhere".
- Liveblocks design.md: durations 0, 150, 200, 300ms; easing `cubic-bezier(0.175, 0.885, 0.32,
  1.1)`; hit targets 24px on desktop and 44px on touch; tabular numerals; toasts never say
  "successfully".
- Vercel Geist colours: ten scales of ten steps with fixed roles (100 background to 1000 primary
  text), P3 where supported, "draw each border once"; radii 0, 5.6px or 9999px only.
- PostHog handbook: red #F54E00 is brand, not status; text at 90 percent, links at 95, hover
  100; no gradient backgrounds; stickers are a white border with a hard shadow.
- Linear redesign: 98 theme variables reduced to three (base, accent, contrast); Inter Display
  for headings since 2024.
- Lando Norris (SOTY 2025): lime #D2FF00 on #111112 and cream #EFEFE5; Brier Bold with Mona Sans.
- Vaul: 500ms `cubic-bezier(0.32, 0.72, 0, 1)`; Sonner: scale 1 minus 0.05 per index, 14px per
  index, 400ms enter, 4s lifetime.
- Codrops 2026 shape-aware ASCII: 6 by 10px cells, about 4,600 cells, a 95-glyph atlas, pause
  when off screen, reduced motion holds a frame.

## The tells, as the sweep recorded them

The 2025 kit that readers now recognise: a pill badge above a centred H1, two buttons, a grey
logo row; three identical cards with a rounded icon tile; indigo-to-purple or purple-to-cyan
gradients, gradient text and buttons, radial halos and mesh blobs; Inter for everything, then
Geist, Space Grotesk, Manrope, Plus Jakarta Sans, DM Sans, Satoshi, Outfit, Poppins; glass
panels over flat backgrounds; neon borders on dark; mid-grey body on near-black; the Instrument
Serif italic accent word; the Relume section library order; bento grids of equal cards; scroll
reveal on every section; invented statistics and testimonial carousels. These live in the graph
as `ai_tell_risk: high` ideas with notes, and in `references/anti-patterns.md`.

## What changed in the skill because of this

- `idea` nodes with render hooks, edges and sources; the recommender attaches eight to twelve
  per direction with coverage rules and no shared nav, hero or texture device across a set.
- Fifty-five hooks implemented in the draft engine, with CSS and plain JavaScript, across all
  four page types.
- Ten new styles built from the findings (acid lab, paper and signal, archive index, raw
  document, night grain, phosphor terminal, cobalt block, giant serif, signal orange, clay
  canvas), twelve palettes anchored on hex values read from real sites and checked for
  contrast, and seventeen pairings using Google Fonts families verified against the fonts
  snapshot (Bricolage Grotesque, Big Shoulders, Newsreader, Libre Caslon Display, Gloock,
  Familjen Grotesk, Martian Mono, Doto, Pixelify Sans, Funnel Display, Geologica, Mona Sans,
  Kode Mono, Parkinsans, Bodoni Moda, Italiana, Cormorant Garamond).
- Thirteen more artwork generators, including the object stand-ins that stores use instead of
  line figures.
- Default copy that no longer repeats the subhead, and heroes that refuse to invent numbers.

Counts after the merge are in the README's graph table and in `CHANGELOG.md` under 0.3.0.
