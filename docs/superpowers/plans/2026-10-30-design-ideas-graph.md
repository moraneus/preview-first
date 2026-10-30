# Design ideas graph and non-generic drafts (0.3.0) Implementation Plan

> Inline execution by the session. Spec: the owner's instruction of 2026-10-30: "It still looks like an AI default design. Suggest more a non-like AI design. Get inspiration from the most modern websites and templates. Do not copy the exact design, but get inspired by them. Store at least 250 modern design ideas in your DB graph. Make sure you updated all repo and document then."

**Goal:** Drafts that no longer share one skeleton, with at least 250 sourced design ideas in the graph that the recommender assigns per direction, the drafts render where possible, and the contract hands to the builder.

**Architecture:** A new `idea` node kind (category, what, implementation, render hook, tell risk, sources) with edges to styles, product types and moods. The recommender picks 8 to 12 ideas per direction with category coverage and no reuse across the set. `Prepared` exposes `ideas` and a `hooks` set; the draft engine turns hooks into navigation variants, textures, type treatments, button styles, sections, artwork and motion. Export writes a "Design ideas" section. New styles, palettes and pairings come from the research sweep.

**Tech stack:** Python 3.9 standard library, static HTML/CSS/JS, pytest.

## Diagnosis (screenshots 2026-10-30, SaaS brief, five directions)

- One skeleton: wordmark nav with four links and a button, headline, three features, quote, call to action, footer, in every direction.
- The same five line figures (stacked diamonds, bell curve, rounded-square grid, rings, bars) repeat across directions.
- The subhead is repeated three times per page by default copy.
- Faces are the generated-site defaults: Geist, Inter, Plus Jakarta.
- No texture, no live metadata, no marquee, no giant numerals, no colour blocking, no cursor or reveal motion; whitespace with small content.

## Tasks

1. Schema and validator: `idea` kind, `render_hooks` closed list, style `ideas` field, bundle `ideas` field. Tests in test_validate_graph, test_graph_content.
2. Recommender: `_ideas_for` with coverage and uniqueness; `ideas` in bundle output. Tests in test_recommend.
3. Prepared, build data.json, export "Design ideas" section. Tests in test_build_preview, test_export.
4. Research sweep (seven agents) normalised by `scripts/dev/merge_ideas.py` (dev-only, not shipped) into graph ideas, reference sites, edges. Target 250+.
5. New styles (8), palettes (12+), pairings (14+) from the research, validated against the Google Fonts snapshot.
6. Draft hooks: nav variants (split-meta, menu-word with overlay, pill, index rail), textures (grain, grid, crosses, scanlines, rules), type (outline giant, mixed face, vertical label, index numbers, tight display), buttons (arrow slide, bracket, fill up, circle icon), sections (marquee, numerals, stack, strip, hover list, grid cells, accordion, giant quote, stat wall, colophon footer, colour blocking), motion (line reveal, custom cursor, magnetic, preloader count, count up).
7. Art: ascii, dither, flowfield, strands, stamp, ruler, globe, specimen, pixel, scan, grain disc, ticket.
8. Default copy without repetition; app, content and store page types get hook support and two new variants each.
9. Docs: references/ideas.md, archetypes.md, anti-patterns.md reconciled, SKILL.md, README, CHANGELOG, research report, memory.
10. Visual pass with screenshots at 1280 and 390; tests on 3.9 and 3.11; release 0.3.0.
