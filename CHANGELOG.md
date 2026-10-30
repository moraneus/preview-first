# Changelog

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
