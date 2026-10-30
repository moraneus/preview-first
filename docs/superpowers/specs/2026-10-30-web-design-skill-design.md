# Design: the "see it before you build it" web design skill

Date: 2026-10-30
Status: approved for planning (builder check answered 2026-10-30)
Name: preview-first (repo, plugin, marketplace and skill directory share the name; invoked as `/preview-first`)
Owner: moraneus

## 1. Intent

Developers who start a website with Claude Code today get design decisions
made for them silently, one component at a time, and only discover what the
site looks like after it is built. This skill inserts a design stage before any
application code is written. Claude produces several complete, distinct design
directions as real HTML pages, opens them in the developer's browser, shows each
one as a style tile, as a drafted page, and inside device frames for the most
popular phones, tablets and laptops. The developer picks one, tweaks it live if
they want, and the choice becomes a written design contract that every later
Claude session follows.

The skill is a design studio stage, not a website generator. It never writes the
developer's application code. It produces a decision and a contract.

Why now: AI-generated sites have a recognisable look that people mock (purple
gradients, identical rounded cards, Inter everywhere, emoji icons). A skill that
makes Claude show real options first, built from a curated knowledge graph of
what goes with what, and that refreshes that knowledge from live sources, is the
missing piece. The nearest existing skill (ui-ux-pro-max, a large CSV database
plus text recommendations) proves the demand but never shows anything in a
browser.

## 2. Goals, non-goals, anti-goals

Goals

- G1. Before a line of app code exists, the developer can open a browser and see
  three to five complete, clearly different design directions for their product.
- G2. Each direction is a real design system in miniature: palette with
  verified contrast, type pairing with a real scale, spacing and radius scale,
  buttons, inputs, cards, navigation, icon set, motion samples, a drafted
  landing or app page, and light and dark modes.
- G3. Each direction is shown inside device frames for the current most popular
  devices by vendor and model, at true CSS viewport sizes, with safe areas.
- G4. The developer can swap the palette, the type pairing, the radius scale,
  the density and the motion level of a direction live in the browser and the
  choice is captured.
- G5. Selecting a direction writes a design contract into the project
  (`design/DESIGN.md`, `design/tokens.json`, `design/tokens.css`) and wires it
  into the project's CLAUDE.md so later Claude work follows it without being
  asked.
- G6. Design decisions come from an explicit knowledge graph of styles,
  palettes, type pairings, component treatments, motion patterns, product types
  and audiences, with weighted "pairs with", "suits" and "avoid with" edges.
- G7. The knowledge refreshes from live, machine-readable sources (font
  popularity, baseline CSS support, library releases, design feeds) by a
  script and by a scheduled GitHub Action, and Claude can run the refresh at the
  start of a session.
- G8. Zero dependencies to install: Python 3 standard library only for scripts,
  plain HTML, CSS and JavaScript for the preview. Works offline after the
  knowledge is present.
- G9. Packaged as a Claude Code plugin and as a plain skill directory, with a
  README, demo recording and install instructions good enough to be shared
  widely.

Non-goals

- Not a component library, a CSS framework, or a site builder.
- Not a Figma replacement. No drag and drop editing.
- Not a hosted service. Everything runs locally.
- No guarantee of any star count. The repo is built to be shareable; adoption
  is not something the builder controls.

Anti-goals (what would make this a failure even if it technically works)

- Directions that all look like the same AI template with different colours.
- Directions that look good in the tile but fall apart on a real phone width.
- A contract that later Claude sessions ignore because it is too vague.
- A skill that pulls in npm or pip dependencies before it can show anything.
- Scraping fragile HTML from design galleries. Live refresh uses stable feeds
  and JSON only.

## 3. Who it is for

A developer, solo or on a small team, who is about to build a website or web
app with Claude Code and does not have a designer. They know what their product
is. They can say what they like when they see it. They cannot describe a design
system from scratch and do not want to learn to.

## 4. The experience, step by step

### 4.1 Trigger

The skill runs when the developer is about to start, restart or restyle a
web project: "build me a landing page for X", "start the frontend", "I don't
like how this looks, redesign it", or an explicit `/preview-first` invocation.

When a project already has UI code but no `design/DESIGN.md`, the stage is
offered in one line, not forced: "Want to see design directions first? I can
show the current look next to alternatives." If accepted, the existing look is
imported as a direction (section 4.7) so it is compared on equal terms. Small
edits to an already styled app ("add a button") never trigger the stage.

### 4.2 Brief

Claude asks at most four questions, in plain language, and reads the project
first so it never asks what the repo already answers:

1. What is the product and who is it for (one sentence).
2. Three words for how it should feel, or a site they admire.
3. Anything fixed: a brand colour, a logo, a font, light or dark only.
4. Which kind of page matters most: marketing, app, content, store.

Existing colours, fonts and frameworks found in the repo (Tailwind config,
package.json, existing CSS variables, a logo SVG) are read and treated as
constraints.

### 4.3 Directions

The work splits between a deterministic script and Claude:

1. Claude normalises the brief into `.design-preview/brief.json`: product type
   id, mood ids, page type, constraints (brand colours, fonts, light or dark
   only), and the product's own words. `recommend.py --list product-types` and
   `--list moods` print the ids so Claude maps free text to nodes.
2. `recommend.py` walks the graph and emits ranked candidate bundles: style,
   palette, type pairing, component treatments, motion patterns, icon set,
   each with the edges and evidence that justified it. It returns three to five
   bundles with diversity enforced.
3. Claude authors what a script cannot: a name for each direction, a rationale
   paragraph that quotes the brief, and real draft copy (headline, subhead,
   feature names, calls to action, form labels) derived from the brief. Claude
   writes these into `.design-preview/directions.json`, whose schema is fixed
   in `knowledge/schema.json`. If copy is missing, the builder falls back to
   neutral copy generated from the brief's product sentence so the pipeline is
   testable without Claude.
4. Mutations ("B but warmer, with the type from D") are edits to
   `directions.json` followed by a rebuild.

Diversity is enforced by the recommender: no two directions may share
the same style family, and at most two may share a palette temperature or a
type category. Each direction is named for its idea, not its style ("Ledger",
"Greenhouse", "Night shift"), and has a one paragraph rationale that quotes the
brief.

Every direction passes the anti-tell check before it is shown. The check
refuses, unless the brief asked for them: the warm cream plus terracotta
combination, near-black plus one acid accent as a default, purple to pink
gradients, identical radius on every element, grey shadow under every card,
all-caps eyebrow labels, Inter or Roboto as the only face, emoji as icons,
arrows appended to every link, fade-up on every section.

### 4.4 Preview in the browser

Claude builds `.design-preview/` in the project with `build_preview.py`, starts
`serve_preview.py` detached in the background, and opens the browser.

Rendering is data driven through a closed vocabulary, not one CSS file per
style. `preview.css` implements every value of every component treatment axis
(button shape: pill, rounded, square; button fill: solid, outline, ghost, soft;
input edge: hairline, filled, underline; card edge: border, shadow, flat, inset;
nav density: airy, compact; and so on, the full vocabulary lives in
`references/components.md`). Each draft page template offers several layout
variants per section (hero: split, centered, editorial, product-shot, poster;
features: bento, list, alternating, columns; and so on), and a style's
`defaults_to` edges choose the variants. Adding a style is a data change.
Adding a new treatment value or layout variant is a CSS or template change.
This is what keeps two directions from being the same template in new colours.

Server lifecycle: `serve_preview.py` binds a free localhost port, writes
`.design-preview/server.json` with port and pid, serves the static files,
handles `POST /select`, and exits on `serve_preview.py --stop` or when the
project directory disappears. Claude never blocks on it. After opening the
browser Claude tells the developer the URL and waits for them in chat; when
they reply, Claude reads `selection.json` if it exists and otherwise takes the
choice from their words. A `--wait SECONDS` flag blocks until a selection
exists, for scripted use. The preview has four views,
switchable with a top bar, and a direction switcher.

Gallery view: all directions side by side as cards showing palette, type
sample, a button row and a thumbnail of the drafted page. Light and dark toggle.

Tile view (one direction): the style tile. Sections: palette (every role token
with hex and OKLCH, contrast ratio against its paired background, WCAG and APCA
grades), typography (faces, scale from display to caption, line length, weight
roles, sample paragraph at body size), spacing and radius scale, elevation,
icon set sample, components (buttons in default, hover, focus, active, disabled
and loading; text input in default, focus, error, disabled; select; checkbox and
switch; card; badge; alert; tabs; navigation bar; footer), motion (hover, press,
enter, exit, page transition and a scroll reveal, each playable with its
duration and easing printed, and a reduced-motion toggle).

Draft view (one direction): the drafted page for the chosen page type, built
with the direction's tokens and real copy derived from the brief, not lorem
ipsum. Resizable viewport with a width readout.

Devices view (one direction): the drafted page rendered inside device frames,
grouped by vendor. Default set: iPhone Pro Max, iPhone, iPhone e model, Samsung
Galaxy S Ultra, Galaxy S, Galaxy Z Fold (folded and unfolded), Galaxy Z Flip,
Galaxy A best seller, Pixel Pro and Pixel, iPad Pro, iPad Air, Galaxy Tab,
MacBook Air, MacBook Pro, a common Windows laptop and a 1440p desktop. Each
frame renders at the true CSS viewport, scaled to fit, with the device's safe
areas (Dynamic Island, punch hole, home indicator, fold crease) drawn. Each
frame is labelled with vendor, model, viewport and pixel ratio. A checklist lets
the developer show or hide devices, and a "rotate" control shows landscape.
Device data lives in `knowledge/devices.json` with a source and date per
entry, and the list is refreshed with the rest of the knowledge.

Controls present in tile, draft and devices views: palette variant, type
pairing variant, radius scale, density, motion level, light or dark. Each
control offers only variants the graph says pair with the direction's style.
Changes apply live through CSS custom properties and are remembered per
direction.

A "Select this direction" button on every view posts the direction and its
current overrides to the local server, which writes
`.design-preview/selection.json`. If the browser cannot be opened (SSH,
container), Claude prints the local URL and also accepts "I pick B" in chat.

### 4.5 Handoff

When a selection exists Claude runs the exporter, which writes:

- `design/DESIGN.md`: the design contract. Sections: identity and rationale,
  palette (semantic tokens with light and dark values, usage rules, contrast
  table), typography (faces, loading, scale, roles, measures), spacing, radius,
  elevation, layout grid and breakpoints, components (each with states and the
  exact tokens it uses), motion (tokens for durations and easings, which
  patterns are allowed and where, reduced-motion rule), iconography, imagery
  rules, writing style, accessibility floor, device checks to run, and an
  explicit "do not" list for this direction.
- `design/tokens.json`: W3C Design Tokens Community Group format, light and
  dark.
- `design/tokens.css`: CSS custom properties with `light-dark()` where
  supported and a class fallback, plus `@font-face` or font link snippets.
- `design/tailwind.css` (if Tailwind v4 is detected) with an `@theme` block,
  or a note on how to map tokens to the detected framework.
- A line in the project's CLAUDE.md: "UI work follows design/DESIGN.md. Read it
  before touching styles." Created if missing.

The preview directory is added to `.gitignore`. `design/` is committed.

Re-export is safe for hand edits. `DESIGN.md` is split into generated sections
wrapped in `<!-- preview-first:generated:start -->` and `:end` markers, and
free sections outside them that the exporter never touches. Before writing,
the exporter copies the previous `DESIGN.md` and tokens to
`design/history/<timestamp>/`. Token files are fully generated and are
overwritten.

### 4.6 Build with the contract

After handoff the skill's job is to make later work obey the contract. Its
SKILL.md instructs Claude, whenever `design/DESIGN.md` exists: read it before
any UI change, use tokens rather than raw values, keep to the allowed motion
patterns, run the contrast checker on any new colour, and offer the device
preview again after a significant page is built (rendering the real page, not
the draft, in the same device frames).

### 4.7 Replacing a template

The developer can ask for new directions at any time, ask to mutate one ("B but
warmer, with the type from D"), or import their own: a URL to a site they
admire (Claude reads its CSS variables and fonts where available), a Tailwind
config, an existing tokens.json, or a screenshot described in words. Imported
material becomes a direction with its own tile so it can be compared on equal
terms.

## 5. Knowledge

### 5.1 The graph

`knowledge/graph.json` holds nodes and edges. Node kinds:

- `style`: a visual direction family (editorial serif, Swiss grid, soft
  product, technical mono, luxury quiet, brutalist, playful geometric, warm
  organic, glass depth, dark console, and more). Fields: traits, era, what it
  signals, performance and accessibility notes, radius and shadow defaults.
- `palette`: a named semantic palette in OKLCH with hex renderings for light
  and dark, with roles: background, surface, surface raised, text, text muted,
  border, primary, on primary, accent, on accent, success, warning, danger,
  focus ring. Each carries computed contrast results and a temperature tag.
- `type-pairing`: heading and body faces, category, source (Google Fonts,
  Fontsource, system stack), loading snippet, suggested scale ratio, measure,
  weights, licence.
- `component-treatment`: how a component family is drawn in a style (button
  shape and fill, input border style, card edge, nav density, table style).
- `motion-pattern`: name, trigger, duration, easing, what it communicates,
  implementation note (CSS, View Transitions, scroll-driven, Motion or GSAP),
  reduced-motion behaviour.
- `product-type`: SaaS, developer tool, fintech, e-commerce, luxury commerce,
  portfolio, agency, editorial, dashboard, health, education, AI product,
  nonprofit, mobile app marketing, documentation, community, event, local
  business, and more.
- `mood`: adjectives used in briefs (calm, bold, trustworthy, playful, premium,
  technical, warm, minimal) mapped to style and palette affinities.
- `icon-set`: Lucide, Phosphor, Heroicons, Tabler, Radix Icons, Material
  Symbols, with stroke width and licence.
- `platform-feature`: CSS and web platform features a style depends on, with
  Baseline status (container queries, `:has`, `color-mix`, OKLCH,
  `light-dark()`, `@property`, text-wrap balance and pretty, anchor
  positioning, popover, scroll-driven animations, View Transitions).
- `device`: vendor, model, year, viewport, pixel ratio, safe areas, corner
  radius, share rank, source.
- `reference-site`: real sites used as evidence for an edge, with URL, date
  seen, and what was observed.

Edge kinds, each with a weight from 0 to 1 and an optional evidence list of
`reference-site` ids: `pairs_with`, `suits`, `avoid_with`, `requires`,
`expresses` (mood to style), `defaults_to` (style to component treatment and
motion pattern).

The schema is in `knowledge/schema.json` and validated in CI. Every node has
`source`, `added`, and `last_verified` dates.

### 5.2 Seeding

The initial graph is seeded from the research done for this project, saved as
reports under `docs/research/` (directions and motion, pairings survey, live
sources, device viewports, packaging): a survey of real sites across product types,
current design writing, platform feature status, and device share data. Target
at the first release: at least 14 styles, 40 palettes, 30 type pairings, 25
motion patterns, 20 product types, 25 devices and 60 reference sites, with
every edge that matters carrying at least one evidence reference. Nodes may
ship with an empty evidence list and a `confidence` field below 1.0; the
validator warns on them so contributors can fill them in.

### 5.3 Live refresh

`scripts/refresh_knowledge.py` (standard library only) pulls:

- Google Fonts popularity and trending (developer API with optional key, or
  the public metadata endpoint) to update type pairing availability and a
  "rising faces" list.
- web-features and Baseline JSON to update platform feature status.
- GitHub release Atom feeds and npm download counts for Motion, GSAP, shadcn,
  Radix, Tailwind, to keep implementation notes current.
- Design writing feeds (web.dev, Chrome for Developers, Smashing Magazine,
  CSS-Tricks, Josh Comeau, Rauno Freiberg, and others settled by the builder
  from the research) into `knowledge/live/feed.json`, titles and links only.
- Device share data where a stable JSON or CSV exists; otherwise the device
  list is maintained in the repo and dated.

Output goes to a user cache directory (`$XDG_CACHE_HOME/preview-first/live/`
or `~/.cache/preview-first/live/`), never into the installed skill, because a
plugin install location is overwritten on update. The repo also ships a
snapshot in `knowledge/live/`, updated by the weekly pull request, and scripts
read whichever of the two is newer. The graph proper is curated; live data annotates it (feature status, font availability, trend
flags) rather than rewriting it. A GitHub Action runs the refresh weekly and
opens a pull request with the diff. The skill tells Claude to run the refresh
when `knowledge/live/` is older than seven days and the network is available,
and to use web search for fresh inspiration for the specific product type when
the developer wants "what is current right now".

## 6. Repository layout

```
<repo>/
  README.md                      hero recording, one-line install, what you get
  LICENSE                        MIT
  CONTRIBUTING.md                how to add a style, palette, device, reference site
  .claude-plugin/plugin.json     plugin manifest
  .claude-plugin/marketplace.json
  skills/preview-first/
    SKILL.md                     the workflow, lean, progressive disclosure
    references/
      process.md                 brief, directions, preview, handoff, build rules
      color.md                   OKLCH palettes, contrast, dark mode strategy
      typography.md              pairing rules, scales, measures, loading
      motion.md                  patterns, durations, easings, reduced motion
      components.md              treatment rules per style
      layout.md                  grids, breakpoints, density, container queries
      anti-patterns.md           the AI tells list and the refusal rule
      devices.md                 how device preview works, how to add a device
      handoff.md                 DESIGN.md and tokens spec
      platform.md                CSS features and Baseline use
    knowledge/
      schema.json
      graph.json
      devices.json
      sources.json               live sources with URLs and parsers
      live/                      refreshed data, timestamped
    scripts/
      recommend.py               brief -> directions JSON
      build_preview.py           directions -> .design-preview/ (static files)
      serve_preview.py           local server, POST /select, opens browser
      export_design.py           selection -> design/ contract and tokens
      contrast.py                WCAG 2 and APCA, used by the others
      refresh_knowledge.py       live sources -> knowledge/live/
      validate_graph.py          schema and referential integrity
      import_direction.py        URL, tailwind config or tokens -> direction
    assets/
      preview/                   shell.html, tile.html, draft templates per
                                 page type, devices.html, preview.css,
                                 preview.js, device-frames.css
      icons/                     inline SVG samples per icon set (licensed)
  docs/
    superpowers/specs/           this document
    superpowers/plans/           implementation plan
    research/                    research reports that seeded the graph
  tests/                         pytest, standard library only under test
  .github/workflows/
    ci.yml                       validate graph, run tests, build preview smoke
    refresh.yml                  weekly refresh, opens PR
```

The skill directory is self-contained so it can be copied to
`~/.claude/skills/preview-first` or installed as a plugin. The same directory
works for other agents that read the open skill format; the README documents
Cursor, Codex and OpenCode paths.

## 7. Decisions already made

- Language: Python 3.9 or later standard library for scripts. No pip
  dependencies. Developer runs scripts through whatever Python they have; the
  skill calls them with `python3` and falls back to `uv run python3` if present.
- Preview: static HTML, CSS and JavaScript, no build step, no framework.
  Fonts load from Google Fonts or Fontsource at preview time when the network
  is available. Every type pairing carries a mandatory system fallback stack.
  When a face fails to load, the tile shows a visible notice naming the real
  face, so an offline preview is honest rather than silently wrong.
  `build_preview.py --vendor-fonts` downloads woff2 files into
  `.design-preview/fonts/` for a fully offline session. The tile always notes
  the licence and a self-hosting snippet.
- Colour: palettes are authored in OKLCH and rendered to hex. Contrast is
  reported in both WCAG 2 ratio and APCA Lc. A palette fails if body text is
  under 4.5:1 or under Lc 60 against its background.
- Devices: CSS-drawn frames, no bitmap mockups, so the repo stays small and
  licensing is clean. Viewports in CSS px from the device list, scaled with
  `transform: scale()` inside a fixed box.
- Selection transport: local HTTP server from the standard library on a free
  port, single endpoint, writes a JSON file. No websockets.
- Contract format: Markdown for humans and Claude, plus W3C design tokens JSON
  and CSS custom properties for tooling.
- Naming: `preview-first` everywhere (repository, plugin.json name,
  marketplace name and entry, `skills/preview-first/`), per the name research
  in `docs/research/2026-10-30-packaging-and-naming.md`. Tagline: "Look before
  you build."
- Script versus Claude: scripts are deterministic and testable (recommend,
  build, serve, export, contrast, refresh, validate). Claude supplies
  judgement (brief normalisation, names, rationale, copy, mutations) through
  JSON files with fixed schemas. No script calls a model.
- Testing: test-driven for the Python scripts. The preview HTML is smoke
  tested by building it in CI and checking the files and key selectors exist;
  visual review is done by hand with screenshots during development.
- Licence: MIT.

## 8. Constraints

- Everything must work from a fresh clone with only Python 3 and a browser.
- No network needed for the preview after the knowledge is present.
- Git identity for all commits is the repo owner. No co-author trailers.
- Scripts write only inside `.design-preview/`, `design/`, the user cache
  directory, and the one CLAUDE.md pointer line. The preview page makes no
  network requests except font loading and the developer-supplied `?url=`.
- Keep SKILL.md under about 3,000 words; detail lives in references.

## 9. Left to the builder

- Exact node counts and the specific entries in the graph, within the seeding
  targets.
- The visual design of the preview chrome itself. It must be neutral so it
  does not colour the directions, and it must itself pass the anti-tell check.
- The list of feeds in `sources.json`, from the research.
- The exact set of draft page templates per page type (marketing, app,
  content, store) and how many sections each has.
- How the recommender scores diversity and how ties are broken.
- The CLAUDE.md wording for the contract pointer.
- GitHub topics.

## 10. Open questions for the owner

None blocking. Assumptions taken in their place:

- Public repository under the owner's GitHub account, MIT licence.
- English copy in the preview and contract.
- The first release targets Claude Code first; other agents are documented
  but not tested.
