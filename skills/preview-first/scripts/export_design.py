"""Export the selected direction as a design contract: design/DESIGN.md, tokens.json (W3C DTCG),
tokens.css, optional tailwind.css, a CLAUDE.md pointer and a .gitignore entry.

Usage: export_design.py --selection PATH --directions PATH [--project DIR]
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from build_preview import Prepared  # noqa: E402
from palette import RADIUS, ROLES, motion_tokens, scale_tokens  # noqa: E402

GEN_START = "<!-- preview-first:generated:start -->"
GEN_END = "<!-- preview-first:generated:end -->"
CLAUDE_LINE = ("UI work follows design/DESIGN.md. Read it before touching styles, and use design/tokens.css "
               "values rather than raw colours, sizes or durations.")
BREAKPOINTS = [360, 768, 1024, 1280, 1536]
GLOBAL_DONTS = [
    "No indigo-to-purple or blue-to-pink gradients, gradient headline text or coloured glows as decoration.",
    "No emoji as icons or bullets; use the icon set named above.",
    "No all-caps tracked eyebrow labels above headings unless this contract names them.",
    "No identical rounded cards in rows of three with the same grey shadow; vary section layouts.",
    "No arrows appended to link or button text; no em dashes in copy.",
    "No lorem ipsum, fake logos, invented statistics or truncated testimonial names.",
    "No scroll-reveal on every section, no marquees, typing cursors, pulsing dots or parallax.",
    "No raw hex, pixel or millisecond values in components; use the tokens.",
]
MOTION_FORBIDDEN = {0: "all animation", 1: "ambient motion, scroll-driven effects, springs with visible bounce, page-load sequences",
                    2: "ambient glow, card tilt, page-load mask reveals", 3: "motion that blocks input or runs longer than 800ms"}


# ---------------------------------------------------------------- helpers

def _apply_overrides(direction: dict, overrides: dict, idx: Dict[str, dict]) -> dict:
    d = copy.deepcopy(direction)
    b = d["bundle"]
    pal = overrides.get("palette")
    if pal and pal in idx:
        b["palette"] = pal
    pair = overrides.get("pairing")
    if pair and pair in idx:
        b["type_pairing"] = pair
    if overrides.get("radius") in RADIUS:
        b["radius_scale"] = overrides["radius"]
    if overrides.get("density") in ("airy", "regular", "compact"):
        b["density"] = overrides["density"]
    motion = overrides.get("motion")
    if motion is not None and str(motion).isdigit():
        b["motion_level"] = int(motion)
        # keep only patterns at or below the new level
    return d


def _detect_tailwind(project: Path) -> Optional[str]:
    """Return "v4", "v3" or None. v4 is recognised by `@import "tailwindcss"` or a tailwindcss ^4
    dependency; a config file alone (or a ^3 dependency) means v3."""
    version = None
    pkg = project / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            for key in ("dependencies", "devDependencies"):
                spec = (data.get(key) or {}).get("tailwindcss")
                if spec:
                    digits = re.search(r"(\d+)", str(spec))
                    version = "v4" if digits and int(digits.group(1)) >= 4 else "v3"
        except (OSError, ValueError):
            pass
    if version == "v4":
        return "v4"
    for css in list(project.glob("*.css")) + list(project.glob("*/*.css")) + list(project.glob("*/*/*.css")):
        if "node_modules" in css.parts:
            continue
        try:
            if '@import "tailwindcss"' in css.read_text(encoding="utf-8", errors="ignore"):
                return "v4"
        except OSError:
            continue
    if version == "v3":
        return "v3"
    for pattern in ("tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs", "tailwind.config.mjs"):
        if (project / pattern).exists():
            return "v3"
    return None


DEFAULT_NOTES = "## Project notes\n\nDecisions and constraints that are specific to this project. This section is never overwritten by preview-first.\n"


def _split_free_text(existing: Optional[str]):
    """Return (text before the start marker, text after the end marker). A file without markers
    is kept whole as free text after the generated block, so nothing hand-written is lost."""
    if not existing:
        return "", DEFAULT_NOTES
    if GEN_START in existing and GEN_END in existing:
        head = existing.split(GEN_START, 1)[0]
        tail = existing.split(GEN_END, 1)[1].lstrip("\n")
        return head, (tail if tail.strip() else DEFAULT_NOTES)
    return "", "## Project notes (previous DESIGN.md, kept verbatim)\n\n" + existing.strip() + "\n"


def _free_text(existing: Optional[str]) -> str:
    return _split_free_text(existing)[1]


def _fmt_hex_table(p: Prepared) -> str:
    rows = ["| Role | Light | Dark | OKLCH (light) | Use |", "|---|---|---|---|---|"]
    use = {
        "bg": "Page background", "surface": "Grouped areas, sidebars, table headers", "surface_raised": "Cards, inputs, menus",
        "text": "Body and headings", "text_muted": "Secondary text, captions, 3:1 minimum", "border": "Hairlines and dividers",
        "primary": "One primary action per view, links when the link style says so", "on_primary": "Text on primary",
        "accent": "Highlights, charts, selected states; never a second button colour", "on_accent": "Text on accent",
        "success": "Positive status with an icon or word", "warning": "Caution status with an icon or word",
        "danger": "Errors and destructive actions", "focus": "Focus rings, 2px, offset by the focus treatment",
    }
    for role in ROLES:
        rows.append("| %s | `%s` | `%s` | `%s` | %s |" % (role.replace("_", " "), p.resolved["light"][role]["hex"], p.resolved["dark"][role]["hex"],
                                                      p.resolved["light"][role]["oklch"], use[role]))
    return "\n".join(rows)


def _contrast_table(p: Prepared) -> str:
    rows = ["| Mode | Pair | Role | WCAG | APCA | Result |", "|---|---|---|---|---|---|"]
    for c in p.resolved["checks"]:
        rows.append("| %s | %s | %s | %.2f:1 | Lc %.0f | %s |" % (c["mode"], c["pair"], c["role"], c["wcag"], c["apca"], "pass" if c["ok"] else "fail"))
    return "\n".join(rows)


def _type_scale_rows(p: Prepared) -> str:
    ratio = float(p.pairing.get("scale_ratio", 1.25))
    steps = [("5xl", 5, "Display, hero only"), ("4xl", 4, "Page title"), ("3xl", 3, "Section title"), ("2xl", 2, "Card and subsection titles"),
             ("xl", 1, "Lead paragraph"), ("lg", 0.5, "Large body"), ("base", 0, "Body"), ("sm", -1, "Captions, labels"), ("xs", -2, "Footnotes, badges")]
    rows = ["| Token | Size | Role |", "|---|---|---|"]
    for name, power, role in steps:
        rows.append("| `--pf-text-%s` | %.3frem | %s |" % (name, ratio ** power, role))
    return "\n".join(rows)


def _components_md(p: Prepared) -> str:
    t = p.treatments
    parts = []
    parts.append("### Buttons\nShape **%s**, fill **%s**. Primary: `--pf-color-primary` on `--pf-color-on-primary`; one per view. Secondary: transparent with `--pf-color-border`. "
                 "States: hover darkens by 12 percent with `color-mix`, active scales to 0.97, focus uses the focus ring, disabled is 45 percent opacity, loading swaps the label for a spinner and holds the width. Minimum height 44px, 36px for the small size."
                 % (t.get("button_shape", "rounded"), t.get("button_fill", "solid")))
    parts.append("### Inputs\nEdge **%s**. Height 44px, `--pf-radius-sm`, label above the field in `--pf-text-sm` weight 500, helper and error text below in `--pf-text-xs`. Error state: border and message in `--pf-color-danger`. Focus: 2px ring in `--pf-color-focus`."
                 % t.get("input_edge", "hairline"))
    parts.append("### Cards\nEdge **%s**, radius `--pf-radius-lg`, padding `--pf-space-5`, background `--pf-color-surface-raised`. Do not wrap every section in a card; cards group repeatable items."
                 % t.get("card_edge", "border"))
    parts.append("### Navigation\n**%s**. Wordmark left, at most five links, one primary action. On mobile the links collapse into a menu button; the wordmark and primary action stay."
                 % t.get("nav", "airy"))
    parts.append("### Badges, alerts, tabs, switches\nBadges use tinted backgrounds (14 percent of the status colour) with the status colour as text. Alerts have a 3px left border in the status colour. Tabs show a 2px `--pf-color-primary` indicator under the selected tab. Switches are 40 by 24px with a spring on the thumb at motion level 2 and above.")
    parts.append("### Dividers and links\nDividers **%s**. Links **%s**." % (t.get("divider", "hairline"), t.get("link_style", "underline")))
    parts.append("### Elevation\n**%s**. Shadows, where allowed, stay under 6 percent total opacity and are layered (1px, 6px, 18px) rather than one blur." % t.get("elevation", "none"))
    return "\n\n".join(parts)


def _motion_md(p: Prepared) -> str:
    rows = ["| Pattern | Trigger | Duration | Easing | Communicates | Reduced motion |", "|---|---|---|---|---|---|"]
    for m in p.motion:
        rows.append("| %s | %s | %sms | `%s` | %s | %s |" % (m["name"], m.get("trigger"), m.get("duration_ms"), m.get("easing"), m.get("communicates"), m.get("reduced_motion")))
    tokens = "\n".join("- `%s`" % line.strip().rstrip(";") for line in motion_tokens(p.motion_level).splitlines() if line.strip().startswith("--"))
    return ("Motion level: **%d** (0 none, 1 subtle, 2 expressive, 3 showcase).\n\nTokens:\n%s\n\nAllowed patterns:\n\n%s\n\n"
            "Forbidden at this level: %s. Motion answers a person's action; one orchestrated moment per page at most. "
            "Animate only `transform` and `opacity`. Under `prefers-reduced-motion: reduce`, replace movement with fades and keep durations under 200ms."
            % (p.motion_level, tokens, "\n".join(rows), MOTION_FORBIDDEN.get(p.motion_level, "")))


def _ideas_md(p: Prepared) -> str:
    if not p.ideas:
        return "No ideas were attached to this direction; run `recommend.py` again to attach some."
    rows = []
    for i in p.ideas:
        where = "in the draft" if i.get("renders") else "for the build"
        seen = ", ".join(i.get("seen_on", [])[:3])
        rows.append("- **%s** (%s, %s). %s Build: %s%s%s" % (
            i["name"], i.get("category", ""), where, i.get("what", ""), i.get("implementation", ""),
            (" Pitfall: %s" % i["pitfalls"]) if i.get("pitfalls") else "",
            (" Seen on %s." % seen) if seen else ""))
    return "\n".join(rows)


def _devices_md(devices: List[dict]) -> str:
    rows = ["| Device | Viewport | DPR | Note |", "|---|---|---|---|"]
    for d in sorted([x for x in devices if x.get("default")], key=lambda x: x.get("share_rank", 99)):
        note = "safe area top %spx" % d["safe_area"]["top"] if d.get("safe_area", {}).get("top") else ""
        if d.get("fold"):
            note = "also check folded %sx%s" % (d["fold"]["folded"]["w"], d["fold"]["folded"]["h"])
        rows.append("| %s %s | %dx%d | %s | %s |" % (d["vendor"], d["model"], d["viewport"]["w"], d["viewport"]["h"], d.get("dpr"), note))
    return "\n".join(rows)


def render_design_md(p: Prepared, selection: dict, devices: List[dict], free_text: str) -> str:
    brief = p.brief
    name = (brief.get("words") or {}).get("name") or brief.get("product", "").split(",")[0]
    h, b = p.pairing["heading"], p.pairing["body"]
    mono = p.pairing.get("mono")
    css_url = p.pairing.get("css_url")
    loading = ("```html\n<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n<link rel=\"stylesheet\" href=\"%s\">\n```\nSelf-host for production: download the woff2 files and declare `@font-face` with `font-display: swap`." % css_url
               if css_url else "System or self-hosted faces; no network request for fonts.")
    radius_rows = "\n".join("- `--pf-radius-%s`: %s" % (k, v) for k, v in RADIUS[p.radius_scale].items())
    density_factor = {"airy": 1.25, "regular": 1.0, "compact": 0.75}[p.density]
    dont = list(p.style.get("tells_to_avoid", [])) + GLOBAL_DONTS
    gen = f"""{GEN_START}
# {name} design contract

Direction **{p.id} · {p.name}**, selected {selection.get("selected_at", _common.today())} with preview-first. Generated sections sit between the markers; write your own notes below the end marker and they survive re-export.

## Identity

{p.rationale or p.style.get("summary", "")}

- Style: **{p.style["name"]}** ({p.style["family"]}). {p.style.get("summary", "")}
- Traits: {", ".join(p.style.get("traits", []))}.
- Signals: {", ".join(p.style.get("signals", []))}.
- Brief: {brief.get("product", "")} Audience: {brief.get("audience", "not stated")}. Moods: {", ".join(m.split(".")[-1] for m in brief.get("moods", []))}. Page type: {brief.get("page_type", "marketing")}.

## Layout archetype

The first screen is not the generic template (centred headline, two buttons, screenshot, three cards). Keep this composition when building the real page.

- Hero: **{p.layout.get("hero", "see draft")}**. Sections: {", ".join("%s %s" % (k, v) for k, v in sorted(p.layout.items()) if k != "hero") or "per the draft"}.
- Artwork: **{(p.style.get("art") or {}).get("hero", "none")}** in the hero, **{(p.style.get("art") or {}).get("feature", "none")}** in sections; generated from the palette, replace with real product imagery or photography of equal weight, never stock.
- Inspired by: {", ".join(p.style.get("inspired_by", [])) or "the reference sites cited in the graph"}.

## Design ideas

Sourced moves this direction is built from. The draft shows the ones marked "in the draft"; carry all of them into the build, each with its implementation note. Do not add generic furniture (logo bar, three icon cards, testimonial carousel) around them.

{_ideas_md(p)}

## Palette

Palette **{p.palette["name"]}** ({p.palette.get("temperature")}, {p.palette.get("scheme")}). Authored in OKLCH, rendered to sRGB hex. Light and dark are two sets of the same roles; swap sets, never invert colours.

{_fmt_hex_table(p)}

Rules:
- One primary and one accent. The accent never becomes a second button colour.
- Status colours always travel with an icon or a word; colour alone carries no meaning.
- Dark mode is `[data-theme="dark"]` or the system preference when no theme is set; set `color-scheme` on the root so native controls follow.
- New colours must pass the contrast checker: `contrast.py FG BG --role body|label|large|ui`.

Contrast results at export:

{_contrast_table(p)}
{("Warnings: " + "; ".join(p.resolved["warnings"])) if p.resolved["warnings"] else ""}

## Typography

Pairing **{p.pairing["name"]}**. {p.pairing.get("notes", "")}

- Heading: **{h["family"]}** ({h["category"]}), weights {", ".join(map(str, h.get("weights", [])))}, fallback `{p.pairing["fallback_heading"]}`.
- Body: **{b["family"]}** ({b["category"]}), weights {", ".join(map(str, b.get("weights", [])))}, fallback `{p.pairing["fallback_body"]}`.
{("- Mono: **%s** for code, identifiers and tabular data only." % mono["family"]) if mono else "- Mono: `ui-monospace, SFMono-Regular, Menlo, monospace` for code and tabular data only."}
- Licence: {p.pairing.get("license", "")}.
- Scale ratio {p.pairing.get("scale_ratio")}, base 1rem (16px), measure {p.pairing.get("measure_ch")}ch, body line height {"1.6" if str(b.get("category", "")).startswith("serif") else "1.5"}, headings 1.15 with `text-wrap: balance`.

{_type_scale_rows(p)}

Loading:

{loading}

Rules: headings in the heading face only; no all-caps tracked labels; tabular numerals (`font-variant-numeric: tabular-nums`) for prices, dates and counts; do not italicise whole headlines.

## Spacing and radius

Density **{p.density}** (factor {density_factor}): `--pf-space-N` is N × 4px × factor, N from 1 to 12. Section padding `--pf-space-12` vertical, `--pf-space-8` horizontal on desktop and `--pf-space-5` on phones.

Radius scale: **{p.radius_scale}**
{radius_rows}

Use different steps for different sizes of thing: controls take `sm` or `md`, cards `lg`, modals `xl`. One radius on everything is a tell.

## Elevation

Treatment **{p.treatments.get("elevation", "none")}**, style shadow **{p.style.get("shadow")}**. Flat surfaces use colour and borders; raised surfaces, where allowed, use layered shadows under 6 percent total opacity; overlays add a blur only when real content sits behind them.

## Layout

- Breakpoints: {", ".join("%dpx" % bp for bp in BREAKPOINTS)}. Mobile first; the {BREAKPOINTS[0]}px layout is designed, not derived.
- Container max width 1200px, page gutters from the spacing scale.
- Prefer container queries (`@container`) for components that appear in different widths.
- Default section layouts for this direction: {", ".join("%s %s" % (k, v) for k, v in sorted(p.layout.items())) or "see the drafted page"}.
- Touch targets at least 44 by 44px with 8px between them; viewport meta never disables zoom; use `min-height: 100dvh`.

## Components

{_components_md(p)}

## Motion

{_motion_md(p)}

## Iconography

Set **{p.icon_set["name"]}** (stroke {p.icon_set.get("stroke")}, {p.icon_set.get("license")}), {p.icon_set.get("url")}. One set across the product, 20 or 24px, `currentColor`. Icon-only buttons carry an `aria-label`. Never emoji.

## Imagery

Real product screenshots and real photographs only. Image corners **{p.treatments.get("image_corner", "sm")}**. Every image declares width and height or an aspect ratio. Decorative images have empty alt text; informative images describe what matters. No stock photos of people pointing at laptops, no fake logo walls, no gradient blobs.

## Writing style

Sentence case everywhere. Active voice; a button says what happens ("Save changes", not "Submit"). Name things by what people understand, not how the system is built. No em dashes, no filler openers, no "It's not just X, it's Y", no arrows in link text. Errors say what went wrong and what to do next; empty states invite the first action.

## Accessibility floor

WCAG 2.2 AA: 4.5:1 for text, 3:1 for large text and UI parts, visible focus on every interactive element, keyboard order matches visual order, headings in sequence, form labels visible, no information by colour alone, reduced motion respected, zoom to 200 percent without loss, content readable at 320px wide.

## Device checks

Check every significant page on these before calling it done (open `.design-preview/{p.id}/devices.html?url=http://localhost:PORT/page`):

{_devices_md(devices)}

## Do not

{chr(10).join("- " + x[:1].upper() + x[1:] + ("" if x.endswith(".") else ".") for x in dont)}
{GEN_END}

{free_text}"""
    return gen


# ---------------------------------------------------------------- tokens

def _dtcg(p: Prepared) -> dict:
    out: dict = {"$schema": "https://design-tokens.github.io/community-group/format/", "color": {"light": {}, "dark": {}}, "font": {},
                 "size": {}, "radius": {}, "space": {}, "duration": {}, "easing": {}, "$extensions": {"preview-first": {
                     "direction": p.id, "name": p.name, "style": p.style["id"], "palette": p.palette["id"], "type_pairing": p.pairing["id"],
                     "treatments": p.treatments, "motion": [m["id"] for m in p.motion], "motion_level": p.motion_level, "icon_set": p.icon_set["id"]}}}
    for mode in ("light", "dark"):
        for role in ROLES:
            e = p.resolved[mode][role]
            out["color"][mode][role] = {"$type": "color", "$value": e["hex"], "$extensions": {"oklch": e["oklch"]}}
    out["font"]["heading"] = {"$type": "fontFamily", "$value": [p.pairing["heading"]["family"]] + [x.strip().strip("'\"") for x in p.pairing["fallback_heading"].split(",")]}
    out["font"]["body"] = {"$type": "fontFamily", "$value": [p.pairing["body"]["family"]] + [x.strip().strip("'\"") for x in p.pairing["fallback_body"].split(",")]}
    mono = p.pairing.get("mono")
    out["font"]["mono"] = {"$type": "fontFamily", "$value": ([mono["family"]] if mono else []) + ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"]}
    ratio = float(p.pairing.get("scale_ratio", 1.25))
    for name, power in [("xs", -2), ("sm", -1), ("base", 0), ("lg", 0.5), ("xl", 1), ("2xl", 2), ("3xl", 3), ("4xl", 4), ("5xl", 5)]:
        out["size"][name] = {"$type": "dimension", "$value": "%srem" % ("%.3f" % (ratio ** power)).rstrip("0").rstrip(".")}
    for k, v in RADIUS[p.radius_scale].items():
        out["radius"][k] = {"$type": "dimension", "$value": v if v != "0" else "0px"}
    factor = {"airy": 1.25, "regular": 1.0, "compact": 0.75}[p.density]
    for n in range(1, 13):
        out["space"][str(n)] = {"$type": "dimension", "$value": "%srem" % ("%.3f" % (n * 0.25 * factor)).rstrip("0").rstrip(".")}
    for line in motion_tokens(p.motion_level).splitlines():
        line = line.strip().rstrip(";")
        if line.startswith("--pf-dur-"):
            k, v = line[len("--pf-dur-"):].split(": ", 1)
            out["duration"][k] = {"$type": "duration", "$value": v}
        elif line.startswith("--pf-ease-"):
            k, v = line[len("--pf-ease-"):].split(": ", 1)
            out["easing"][k] = {"$type": "cubicBezier" if v.startswith("cubic-bezier") else "string", "$value": v}
    return out


def _tailwind_v3_note(p: Prepared) -> str:
    rows = "\n".join("        %s: 'var(--pf-color-%s)'," % (role.replace("_", "-"), role.replace("_", "-")) for role in ROLES)
    return ("# Tailwind v3 mapping\n\nThis project uses Tailwind v3, which has no `@theme`. Import `design/tokens.css` once, then "
            "extend the config so utilities resolve to the contract:\n\n```js\n// tailwind.config.js\nmodule.exports = {\n  theme: {\n    extend: {\n      colors: {\n%s\n      },\n"
            "      fontFamily: { heading: 'var(--pf-font-heading)', body: 'var(--pf-font-body)', mono: 'var(--pf-font-mono)' },\n"
            "      borderRadius: { sm: 'var(--pf-radius-sm)', md: 'var(--pf-radius-md)', lg: 'var(--pf-radius-lg)', xl: 'var(--pf-radius-xl)', full: 'var(--pf-radius-full)' },\n"
            "    },\n  },\n};\n```\n\nUpgrade to Tailwind v4 and re-run the export to get `design/tailwind.css` with an `@theme` block instead.\n") % rows


def _tailwind_css(p: Prepared) -> str:
    lines = ['@import "tailwindcss";', '@import "./tokens.css";', "", "/* preview-first design tokens for Tailwind v4. `inline` keeps the var() references live. */", "@theme inline {"]
    for role in ROLES:
        lines.append("  --color-%s: var(--pf-color-%s);" % (role.replace("_", "-"), role.replace("_", "-")))
    lines.append("  --font-heading: var(--pf-font-heading);")
    lines.append("  --font-body: var(--pf-font-body);")
    lines.append("  --font-mono: var(--pf-font-mono);")
    for k in RADIUS[p.radius_scale]:
        lines.append("  --radius-%s: var(--pf-radius-%s);" % (k, k))
    for k in ("fast", "base", "slow", "page"):
        lines.append("  --duration-%s: var(--pf-dur-%s);" % (k, k))
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- export

def export(selection: dict, directions: dict, project: Path, graph: dict, devices: List[dict]) -> dict:
    project = Path(project)
    idx = _common.node_index(graph)
    match = [d for d in directions["directions"] if d["id"] == selection.get("direction")]
    if not match:
        raise KeyError("direction %r is not in directions.json" % selection.get("direction"))
    overrides = selection.get("overrides") or {}
    direction = _apply_overrides(match[0], overrides, idx)
    p = Prepared(direction, directions.get("brief", {}), idx)
    if overrides.get("motion") is not None and str(overrides["motion"]).isdigit():
        level = int(overrides["motion"])
        p.motion = [m for m in p.motion if m.get("level", 0) <= level] or [idx["motion-pattern.none"]] if "motion-pattern.none" in idx else p.motion

    design = project / "design"
    history: Optional[Path] = None
    existing_md = None
    if (design / "DESIGN.md").exists():
        existing_md = (design / "DESIGN.md").read_text(encoding="utf-8")
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        history = design / "history" / stamp
        n = 1
        while history.exists():
            n += 1
            history = design / "history" / ("%s-%d" % (stamp, n))
        history.mkdir(parents=True, exist_ok=False)
        for f in design.iterdir():
            if f.is_file():
                shutil.copy2(f, history / f.name)
    design.mkdir(parents=True, exist_ok=True)

    written = []
    head_text, free_text = _split_free_text(existing_md)
    md = head_text + render_design_md(p, selection, devices, free_text)
    (design / "DESIGN.md").write_text(md, encoding="utf-8")
    written.append(str(design / "DESIGN.md"))
    _common.dump_json(design / "tokens.json", _dtcg(p))
    written.append(str(design / "tokens.json"))
    (design / "tokens.css").write_text("/* Generated by preview-first from direction %s. Edit DESIGN.md notes, not this file. */\n" % p.id + p.tokens_css(), encoding="utf-8")
    written.append(str(design / "tokens.css"))
    tw = _detect_tailwind(project)
    if tw == "v4":
        (design / "tailwind.css").write_text(_tailwind_css(p), encoding="utf-8")
        written.append(str(design / "tailwind.css"))
    elif tw == "v3":
        (design / "tailwind.md").write_text(_tailwind_v3_note(p), encoding="utf-8")
        written.append(str(design / "tailwind.md"))

    claude = project / "CLAUDE.md"
    updated = False
    text = claude.read_text(encoding="utf-8") if claude.exists() else ""
    if "design/DESIGN.md" not in text:
        text = (text.rstrip("\n") + "\n\n" if text.strip() else "# Project notes for Claude\n\n") + CLAUDE_LINE + "\n"
        claude.write_text(text, encoding="utf-8")
        updated = True

    gi = project / ".gitignore"
    gi_text = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if ".design-preview/" not in gi_text.splitlines() and ".design-preview" not in gi_text.splitlines():
        gi.write_text((gi_text.rstrip("\n") + "\n" if gi_text.strip() else "") + ".design-preview/\n", encoding="utf-8")

    return {"written": written, "history": str(history) if history else None, "claude_md_updated": updated, "warnings": p.resolved["warnings"]}


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Export the selected direction as a design contract.")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--directions", required=True)
    ap.add_argument("--project", default=".")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--devices", default=str(_common.KNOWLEDGE_DIR / "devices.json"))
    ns = ap.parse_args(list(argv))
    report = export(_common.load_json(ns.selection), _common.load_json(ns.directions), Path(ns.project),
                    _common.load_json(ns.graph), _common.load_json(ns.devices)["devices"])
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
