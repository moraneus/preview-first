# The handoff: DESIGN.md, tokens and the marker contract

`export_design.py` turns the selection into files the project keeps. This document describes
each file so later sessions, other agents and humans can rely on them.

## Files written

| File | Purpose | Regenerated |
|---|---|---|
| `design/DESIGN.md` | The contract, for humans and Claude | Generated block only |
| `design/tokens.json` | W3C Design Tokens Community Group format | Always |
| `design/tokens.css` | CSS custom properties, light and dark | Always |
| `design/tailwind.css` | `@theme` mapping, only when Tailwind v4 is detected | Always when detected |
| `design/history/<stamp>/` | Previous versions of the files above | Added on each re-export |
| `CLAUDE.md` | One pointer line | Added once |
| `.gitignore` | `.design-preview/` | Added once |

Commit `design/` and the CLAUDE.md line. `.design-preview/` is scratch and is ignored.

## The marker contract

```
<!-- preview-first:generated:start -->
... generated sections ...
<!-- preview-first:generated:end -->

## Project notes
... free text, never touched ...
```

Everything between the markers is replaced on re-export. Everything after the end marker is
copied through verbatim. Put project decisions, exceptions and rejected ideas in the free
section. If someone edits inside the generated block, their edit is lost on the next export
but is recoverable from `design/history/`.

## Generated sections, in order

1. Title and provenance: direction id and name, selection time.
2. Identity: rationale, style with family, traits, signals, and the brief in one line.
3. Palette: role table (light hex, dark hex, OKLCH, usage), rules, the contrast table from the
   checks that ran at export, and any warnings.
4. Typography: faces with category, weights and fallbacks, licence, scale ratio and measure,
   the scale table in rem, loading snippet, rules.
5. Spacing and radius: density factor, the radius scale with values, hierarchy rule.
6. Elevation: treatment and shadow policy.
7. Layout: breakpoints, container width, container queries, default section variants, touch
   targets and viewport rules.
8. Components: buttons, inputs, cards, navigation, badges and alerts, tabs and switches,
   dividers and links, elevation, each with treatment values and token names.
9. Motion: level, tokens, allowed patterns table, forbidden patterns, reduced motion rule.
10. Iconography: set, stroke, licence, usage rules.
11. Imagery: real imagery only, corner treatment, dimensions, alt text.
12. Writing style.
13. Accessibility floor.
14. Device checks: the default device table and the devices view URL pattern.
15. Do not: the style's own tells plus the global list.

## tokens.json

Top level groups: `color.light`, `color.dark` (14 roles each, `$type: color`, hex `$value`,
OKLCH in `$extensions.oklch`), `font` (heading, body, mono as `fontFamily` arrays with
fallbacks), `size` (xs to 5xl, `dimension` in rem), `radius` (xs to full), `space` (1 to 12),
`duration` (fast, base, slow, page), `easing` (out, in-out, in, spring). `$extensions.preview-first`
records the direction, style, palette, pairing, treatments, motion ids and icon set so a later
session can rebuild the preview.

Consumers: Style Dictionary, Tokens Studio, Cobalt and any DTCG reader. Use `color.light` and
`color.dark` as two sets, not as themes to diff.

## tokens.css

`:root` carries the light set and `color-scheme: light dark`. `[data-theme="dark"]` carries the
dark set, and `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` applies it
when no explicit theme is set. Then the radius, space, text, font, leading and measure tokens,
then motion tokens.

Names: `--pf-color-<role>`, `--pf-color-<role>-oklch`, `--pf-radius-<step>`, `--pf-space-<n>`,
`--pf-text-<step>`, `--pf-font-{heading,body,mono}`, `--pf-leading-{tight,normal,loose}`,
`--pf-measure`, `--pf-dur-{fast,base,slow,page}`, `--pf-ease-{out,in-out,in,spring}`.

Rename the prefix with a project-wide search if `pf` collides with something; keep the
structure.

## tailwind.css

Only when `tailwind.config.*` exists or a stylesheet imports `tailwindcss`. It maps the
`--pf-*` tokens into Tailwind v4 `@theme` names (`--color-*`, `--font-*`, `--radius-*`,
`--duration-*`) so utilities like `bg-primary`, `text-text-muted`, `font-heading`, `rounded-md`
resolve to the contract. Import it instead of a bare `@import "tailwindcss"`.

For shadcn projects, map `--pf-color-bg` to `--background`, `--pf-color-text` to
`--foreground`, `--pf-color-surface-raised` to `--card` and `--popover`, `--pf-color-primary` to
`--primary`, `--pf-color-on-primary` to `--primary-foreground`, `--pf-color-surface` to
`--secondary` and `--muted`, `--pf-color-text-muted` to `--muted-foreground`, `--pf-color-accent`
to `--accent`, `--pf-color-danger` to `--destructive`, `--pf-color-border` to `--border` and
`--input`, `--pf-color-focus` to `--ring`, and `--pf-radius-md` to `--radius`.

## Re-export and overrides

`selection.json` carries the overrides the developer ended on:

```json
{"direction": "B", "overrides": {"palette": "palette.harbor-grey", "pairing": "type-pairing.geist-geist",
 "radius": "md", "density": "regular", "motion": "1", "theme": "dark"}, "selected_at": "2026-10-30T10:00:00Z"}
```

The exporter applies palette and pairing ids (they must exist in the graph), radius, density and
motion level, then resolves and checks the palette again. `theme` is recorded but the contract
always ships both modes.

To change the contract later, edit `.design-preview/directions.json` or `selection.json` and
re-run the exporter; do not hand-edit the generated block.

## Reading the contract as a later session

Minimum: read Identity, Palette rules, Typography rules, Components for the component in hand,
Motion level and allowed patterns, and Do not. Use the token names, not the hex values printed
beside them. When something needed is missing (a chart palette, a data table density), add it
under Project notes with the values used, so the next session finds it.
