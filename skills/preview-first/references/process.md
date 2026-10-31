# The stage in detail

This expands the flow in SKILL.md with the exact wording, decisions and edge cases.


## Copy before the first open

Write `.design-preview/copy.json` from the brief before running quick start: the navigation is the product's sections, the features are the things it does in its own nouns, the headline is a claim a user would repeat, the call to action is the verb of the first visit. Thirty seconds of writing is the difference between a product page and a template.

## Reading the project first

Look for, in this order, and record anything found as a constraint in `brief.json`:

| Signal | Where | Becomes |
|---|---|---|
| Framework | package.json dependencies | note for the contract (Tailwind v4 export, shadcn token names) |
| Brand colours | Tailwind config `theme.colors`, CSS custom properties, logo SVG fills | `constraints.brand_colors` (first is primary) |
| Fonts | `@font-face`, Google Fonts links, Tailwind `fontFamily` | `constraints.fonts` |
| Scheme | `color-scheme`, a dark-only app, existing `.dark` class | `constraints.scheme` |
| Product and audience | README, package description, landing copy | `product`, `audience` |
| Existing look | styles.css, tailwind config | an imported direction (see Imports) |

If a brand colour exists, pass it as `overrides.brand_primary` on every direction unless the
developer says the redesign may change it.

## The four questions

Send them in one message, numbered, with no examples hanging off them. Accept partial answers.
If the developer answers "just guess", choose and say what you chose.

1. What is the product and who is it for, in one sentence?
2. Three words for how it should feel, or a site you admire?
3. Anything fixed: a brand colour, a logo, a font, light or dark only?
4. Which kind of page matters most: marketing, app, content or store?

Translate the answers:

- Product sentence: keep it whole in `product`. Pull the name into `words.name` when obvious.
- Feel words: map to mood ids with `recommend.py --list moods`; keep the originals in the
  rationale. Unknown words are dropped by the recommender; do not invent moods.
- An admired site: put the URL in `admired`. If the network is available, read its CSS with
  `import_direction.py --url` and import it as a direction labelled "Reference" so the
  comparison is explicit; use its traits (dark or light, serif or sans, density) to choose moods.
- Fixed items: `constraints`. A fixed font goes into the rationale and, if it exists in the
  graph, pick pairings that include it; otherwise keep the developer's font as the body or
  heading face through an inline `type_pairing` with a proper fallback stack.
- Page type: `page_type`. When unsure, marketing for anything public, app for anything behind
  a login.

## Counting directions

- Default four. Three when the brief is tightly constrained (dark only plus a brand colour).
  Five when the developer says they have no idea what they want.
- Every direction must differ in style family. If the recommender returns fewer families than
  requested, say so rather than padding with a near duplicate.
- Order directions by recommender score, A first. Do not label any direction "recommended";
  the rationale carries your reasoning and the developer decides.

## Naming and rationale

Names are short nouns that evoke the idea: "Ledger", "Greenhouse", "Night shift", "Broadsheet",
"Workshop". Avoid adjectives (Modern, Clean, Bold) and style names (Brutalist, Glass).

A rationale is one paragraph, three to five sentences:

1. Quote the brief's words that this direction answers.
2. Name the one bold choice (the serif voice, the poster headline, the dark console).
3. Say what stays quiet so the bold choice reads.
4. Note the trade-off (who this might not suit) in one clause.

## Copy rules for the draft

The draft is read as if it were the product, so its words matter.

- Headline: the tagline if one exists; otherwise the product's promise in under ten words,
  specific to the product. Not "Build faster. Ship smarter."
- Subhead: one or two sentences, what it does and for whom, from the brief.
- Calls to action: say what happens ("Start free", "See a sample invoice"), never "Submit",
  "Learn more" alone, or "Get started" when something more specific exists.
- Features: three to six, each a concrete capability with one sentence of consequence.
- Proof: only something the developer stated. Otherwise leave it empty and the draft renders a
  labelled placeholder, which is honest.
- Nav: four real destinations for this product.
- Footer: one true sentence.
- Everywhere: sentence case, active voice, no em dashes, no emoji, no arrows, no "It's not
  just X, it's Y", no "Whether you're X or Y", no tricolons, no invented numbers or names.

## Message templates

After building:

> The preview is up at URL. Four directions:
> A Ledger: paper canvas, serif voice, one steady blue.
> B Console: near-black surfaces, Geist, cyan accent, dense.
> C Poster: huge grotesque headline, square corners, black and chalk.
> D Greenhouse: warm organic, rounded, sage and clay.
> Open a tile to swap palette, type, radius, density and motion; the Devices tab shows each
> on current phones, foldables, tablets and laptops. Select one there or tell me which.

Then stop.

After selection:

> Exported direction B with your overrides (palette Carbon signal, radius md). Written:
> design/DESIGN.md, design/tokens.json, design/tokens.css, and a pointer in CLAUDE.md.
> Commit design/ and CLAUDE.md. I will build to the contract from here.

## Edge cases

- No browser (SSH, container, CI): print the URL and the direction list; offer to describe
  any tile in words; accept the choice in chat.
- The developer wants to see it on their phone: the server binds 127.0.0.1 only. Suggest an
  SSH tunnel or the devices view; do not rebind to 0.0.0.0.
- Two projects at once: each project has its own `.design-preview/server.json` and port.
- Stale `server.json` from a crashed session: `serve_preview.py` detects a dead pid and starts
  fresh; `--stop` never kills a pid whose command line is not this server for this directory.
- Fonts blocked by the network: the tile shows the fallback notice; offer `--vendor-fonts` or
  proceed with system stacks and say so in the contract.
- Brand colour fails contrast: the tile and the contract list the failing pair. Offer the
  nearest passing step (adjust OKLCH lightness, keep hue and chroma) and record the original
  as `brand_source` in the rationale.
- The developer picks a direction and asks for a change that crosses families ("A but dark"):
  that is a new direction, not an override. Add it under a new id and rebuild.
- Re-running months later: run `refresh_knowledge.py` first; mention in the rationale if a
  platform feature a style relies on changed Baseline status.

## What the stage never does

- Write application code, components or pages in the developer's framework.
- Choose for the developer or declare a winner.
- Install dependencies.
- Send anything off the machine except font requests and the developer's own `?url=`.
- Edit anything outside `.design-preview/`, `design/`, the user cache, and one CLAUDE.md line.
