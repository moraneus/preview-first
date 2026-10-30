# Contributing to preview-first

Thank you for helping. The most valuable contributions are knowledge: a palette that works, a
pairing you have shipped, a device that is missing, a reference site that proves an edge.

## Ground rules

- Python standard library only in `skills/preview-first/scripts/`. No new runtime dependencies.
- Every knowledge change runs through the validator and the tests:

```bash
python3 skills/preview-first/scripts/validate_graph.py
python3 -m pytest -q
```

- Evidence over opinion. A `pairs_with`, `suits` or `avoid_with` edge should cite at least one
  `reference-site` node in its `evidence` list. Confidence below 0.6 triggers a warning.
- Sources and dates on every node: `source`, `added`, `last_verified`.
- No AI tells in anything the skill shows: see `skills/preview-first/references/anti-patterns.md`.
- Commit messages use conventional prefixes: `feat(knowledge): ...`, `fix: ...`, `docs: ...`.

## Adding a palette

1. Author in OKLCH, both modes, all 14 roles (see `references/color.md`).
2. Check pairs while authoring: `python3 skills/preview-first/scripts/contrast.py "oklch(0.22 0.01 60)" "oklch(0.985 0.006 85)" --role body`.
3. Add the node to `knowledge/graph.json` with `temperature`, `scheme`, `hue_family`, `notes`.
4. Add `pairs_with` edges from the styles it suits (weights 0.6 to 0.95) and `avoid_with` edges where it clashes.
5. Run the validator. A failing contrast pair is an error, not a warning.

## Adding a type pairing

1. Check both families exist on Google Fonts (or use `source: "system"`, `"fontshare"`, `"self-hosted"`).
2. Fill `heading`, `body`, optional `mono`, real `fallback_heading` and `fallback_body` stacks, `scale_ratio`, `measure_ch`, `css_url`, `license`.
3. Add `pairs_with` edges from styles. Keep Inter as body in at most three pairings in total.

## Adding a style

A style is data: `family`, `summary`, `traits`, `signals`, `radius_scale`, `shadow`, `density`,
`layout_defaults`, `tells_to_avoid`, plus `defaults_to` edges to one treatment per axis and to
motion patterns at levels 1 and 2, a `pairs_with` edge to an icon set, and at least three
palettes and three pairings. If the style needs a treatment value that does not exist, add the
value to `schema.json`, implement it in `assets/preview/preview.css`, document it in
`references/components.md`, and add the treatment node.

## Adding or correcting a device

Edit `knowledge/devices.json`. Required: a source URL you checked (Apple or Samsung developer
docs, yesviz, Chrome's EmulatedDevices list, StatCounter), CSS viewport in portrait, DPR, safe
areas in CSS px, cutout type, corner radius (0 if unknown), `verified` true only when the numbers
come from a primary source. Keep exactly 12 defaults; argue for swaps in the pull request.

## Adding a reference site

A `reference-site` node records what you observed on a real site on a given date: style,
colours, fonts, button shape, card treatment, nav pattern, motion. Then attach its id to the
edges it supports. Do not copy site assets.

## Live sources

`knowledge/sources.json` lists machine-readable feeds only. Propose a new one with its URL,
format and what it would change in the graph. No HTML scraping.

## Preview and scripts

Tests live in `tests/`. Write the failing test first. The preview chrome must stay neutral grey
and must pass the anti-tell check itself. Run a manual look at the gallery, a tile, a draft and
the devices view before opening a pull request that touches `assets/preview/`.

## Releases

Bump `version` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` and the
SKILL.md frontmatter together, add a CHANGELOG entry, tag `vX.Y.Z`.

## Adding a design idea

Ideas are `idea` nodes in `knowledge/graph.json`. Add one when you can name a real site that does it and describe it well enough to build: `category`, `what` with concrete values, `implementation`, `ai_tell_risk` and `ai_tell_note`, `seen_on` URLs, and `renders` only when a hook in `knowledge/schema.json` shows exactly that move. Add `pairs_with` edges to the styles it fits, run `validate_graph.py`, and read `skills/preview-first/references/ideas.md` first.
