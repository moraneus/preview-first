# Changelog

## 0.4.0 (2026-10-30)

More templates, bolder ones, and a page that shows them all.

- Five showcase heroes: split screen (two full-height panels, artwork on a solid primary panel), diagonal marquee bands, a mosaic of tiles with the text as one dark tile, kinetic type whose three lines slide at different speeds with scroll, and fanned cards. A mosaic feature grid (image-led masonry with captions) and a full-bleed poster band with the wordmark in difference blend. Scroll-driven motion hooks (parallax giant word, hero art scaling out, skewed marquee) and tilted framed images.
- Ten more artwork generators: mesh, torus, letter stack, blob, mosaic, bars, sun, lattice, rays, word cloud.
- Five bold styles: velodrome (lime on black, condensed display, kinetic type), festival poster (bone, signal red and mustard, diagonal bands, ticket), ultramarine (sand and deep blue, split screen, torus), pastel blocks (tinted section blocks, fanned cards, tilted frames), mosaic wall (image-led from the first pixel). Eight palettes from real sites and eight pairings (Big Shoulders with Mona Sans, Anton, Unbounded, Archivo Black, Syne, Bricolage Grotesque, Fraunces, Parkinsans over quiet bodies).
- `docs/templates.md` and `docs/assets/templates.png`: every style's first screen for one brief, built by `tools/build_showcase.py`.
- `recommend.py` accepts `--count` up to eight so a developer can see more directions at once.
- Variant precedence: the author's layout, then hooks from the style's own ideas, then the style's default hero, then other hooks, then the style's defaults for the other sections. Fixed outlined words that rendered invisible, the mosaic text tile, and mosaic captions on colour blocks.

## 0.3.0 (2026-10-30)

Non-generic by composition, not by colour.

- A research sweep across seven categories (developer tools and SaaS, studios and award sites, fashion and hardware commerce, editorial and type foundries, templates and trend reports, motion and interaction, typography and colour) produced 500 sourced design ideas, now `idea` nodes in the graph with descriptions, implementation notes, tell risk, the sites they were seen on and edges to styles, product types and moods. Report: `docs/research/2026-10-30-modern-design-ideas.md`; reference: `references/ideas.md`.
- The recommender attaches eight to twelve ideas to every direction with coverage rules (navigation, first screen, type craft, section, imagery or texture, motion, footer) and never lets two directions share a navigation, hero, texture, section, footer, proof or call-to-action device. High-risk ideas (the known tells) stay in the graph as warnings and are only chosen when a style asks.
- Sixty-five render hooks in the draft engine: five navigation devices (one-line bar, split nav with live local time, "Menu" word with a full-screen overlay, floating pill, numbered rail), six more heroes (ticker, specimen, manifesto, sourced numbers, clipped type, stacked words), six more feature archetypes (giant numerals, stacking cards, horizontal strip, hover list with image reveal, bordered cells with corner crosses, hairline accordion), giant quote and stat wall proofs, a ticket call to action, a colophon footer, five textures (grain, grid, crosses, scanlines, rules), type details (outlined word, one word in the mono, vertical labels, mono indices, tight display, hanging punctuation, tabular numerals), four button styles, eight motion behaviours (line mask reveal, custom cursor, magnetic buttons, preloader counter, count-up, hover swap, scroll progress, view transitions), imagery treatments (duotone, dither, ASCII, captions, stickers) and colour blocking. All respect reduced motion and the motion level; the cursor and preloader never run in thumbnails or device frames.
- Store, content and app drafts got the same treatment: lookbook and category-tile openings, an editorial grid and a sticky buy column; a broadsheet masthead, side notes and an archive index; an icon rail shell, a ledger table, an inspector panel and a command palette.
- Ten new styles built from the findings: acid lab, paper and signal, archive index, raw document, night grain, phosphor terminal, cobalt block, giant serif, signal orange, clay canvas. Twelve palettes anchored on hex values read from real sites and passed through the contrast checks. Seventeen pairings using Google Fonts families verified against the fonts snapshot (Bricolage Grotesque, Big Shoulders, Newsreader, Libre Caslon Display, Gloock, Familjen Grotesk, Martian Mono, Doto, Pixelify Sans, Funnel Display, Geologica, Mona Sans, Kode Mono, Parkinsans, Bodoni Moda, Italiana, Cormorant Garamond).
- Thirteen more artwork generators (ASCII field, dithered light, flow field, strands, stamp, ruler, globe, specimen, pixel mark, oscilloscope, grained disc, ticket, object stand-ins) and thirteen figure kinds chosen by seed, so the same figure no longer repeats across directions.
- Default copy no longer repeats the subhead three times; the numbers hero and the stat wall render only when the copy carries sourced figures.
- The contract gains a "Design ideas" section with each idea's description, build note and sources. `recommend.py --list ideas` lists the graph. Anti-patterns reconciled: a device named by an attached idea is a request by name; the pre-show checklist checks that the ideas are visible.
- 123 reference sites added from the sweep. Validator: unknown render hooks and ideas without sources are errors.

## 0.2.1 (2026-10-30)

- A 47-site layout survey with computed-style measurements (`docs/research/2026-10-30-layout-archetypes.md`) and its findings folded into `references/archetypes.md`.
- Three more archetypes from the survey: collage hero, letter hero, ledger feature rows. Hairlines, mono labels and giant words now follow the measured values.

## 0.2.0 (2026-10-30)

Non-generic by default.

- New layout archetypes for marketing pages, drawn from admired sites: statement (two-tone paragraph with captioned figures), mark (headline, one geometric mark, a three-line list), wrap (giant type with alternating indents over a flat disc), product-first (framed stage with the real UI), object (display face beside a single object), bleed (full-bleed artwork with small centred text), index (sticky side column). Feature sections: figures, specification list, index, colour bands. Proof as a statement, giant call to action and giant wordmark footer.
- Generated artwork replaces wireframe placeholders everywhere: thirteen palette-driven, deterministic SVG generators (product window, terminal, blueprint, isometric slabs, Swiss composition, contours, halftone, orbit rings, stickers, sparklines, single mark, glass panels, captioned figure).
- Two new styles: Studio wrap and Lab figures. Every style now carries `art`, `conventionality` and `inspired_by`; no style defaults to the centred hero.
- The recommender guarantees at least two `distinct` directions per set.
- The exported contract records the hero archetype, section variants and artwork kinds.
- Safe areas from the device catalogue are passed into embedded drafts.

## 0.1.0 (2026-10-30)

First release.

- Knowledge graph: 14 styles, 45 OKLCH palettes with light and dark sets, 43 type pairings, 33 component treatments, 26 motion patterns, 22 product types, 20 moods, 6 icon sets, 16 platform features, reference sites as evidence, and a 36-device catalogue.
- Scripts (standard library only): `recommend.py`, `build_preview.py`, `serve_preview.py`, `export_design.py`, `import_direction.py`, `contrast.py`, `validate_graph.py`, `refresh_knowledge.py`.
- Preview: gallery, style tile with contrast grades and playable motion, drafted pages for marketing, app, content and store with per-style layout variants, and a devices view with CSS-drawn frames, cutouts, fold creases and safe areas.
- Contract export: `design/DESIGN.md` with a marker contract for hand-written notes, W3C Design Tokens JSON, CSS custom properties, Tailwind v4 `@theme` mapping, CLAUDE.md pointer.
- Live refresh from Google Fonts, web-features, GitHub release feeds, npm and design feeds, with a weekly pull request workflow.
- Plugin and marketplace manifests for Claude Code; open skill layout for other agents.
