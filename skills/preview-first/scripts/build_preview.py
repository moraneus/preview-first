"""Build the browser preview (gallery, style tiles, drafts, device views) from directions.json.

Usage: build_preview.py --directions PATH [--out DIR] [--vendor-fonts] [--graph PATH]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from palette import RADIUS, ROLES, motion_tokens, resolve_palette, scale_tokens, tokens_css  # noqa: E402
from validate_graph import validate_file  # noqa: E402

PREVIEW_ASSETS = _common.ASSETS_DIR / "preview"
ICON_ASSETS = _common.ASSETS_DIR / "icons"
ICON_NAMES = ["search", "menu", "close", "arrow-right", "check", "plus", "settings", "user", "bell", "mail", "calendar", "download"]
ICON_LICENSES = {
    "icon-set.lucide": ("Lucide", "ISC"), "icon-set.phosphor": ("Phosphor", "MIT"), "icon-set.heroicons": ("Heroicons", "MIT"),
    "icon-set.tabler": ("Tabler Icons", "MIT"), "icon-set.radix": ("Radix Icons", "MIT"), "icon-set.material-symbols": ("Material Symbols", "Apache-2.0"),
}
VIEWS = [("tile", "Tile"), ("draft", "Draft"), ("devices", "Devices")]
DEMO_KIND = {
    "press-scale-97": "press", "hover-lift-2": "lift", "hover-tint": "tint", "underline-grow": "underline",
    "focus-ring-pulse-once": "focus", "enter-fade-up-8": "fade-up", "enter-scale-95": "scale-in", "exit-fade-fast": "fade-out",
    "button-loading-swap": "loading", "skeleton-shimmer": "shimmer", "toast-slide-in": "slide-in", "tab-indicator-slide": "tab",
    "switch-thumb-spring": "switch", "accordion-height": "accordion", "menu-stagger-30": "stagger", "page-crossfade-vt": "crossfade",
    "page-slide-vt": "slide-page", "scroll-reveal-once": "reveal", "scroll-progress-bar": "progress", "layout-flip": "flip",
    "spring-pop": "pop", "card-tilt-subtle": "tilt", "hero-mask-reveal": "mask", "ambient-glow-slow": "glow",
    "number-count-up": "count", "none": "none",
}

E = html.escape


# ---------------------------------------------------------------- helpers

def render_template(name: str, slots: Dict[str, str]) -> str:
    text = (PREVIEW_ASSETS / name).read_text(encoding="utf-8")
    missing = set(re.findall(r"{{(\w+)}}", text)) - set(slots)
    if missing:
        raise KeyError("template %s missing slots: %s" % (name, ", ".join(sorted(missing))))
    for key, value in slots.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def _resolve(ref, idx: Dict[str, dict], kind: str) -> dict:
    if isinstance(ref, dict):
        return ref
    node = idx.get(ref)
    if not node:
        raise KeyError("unknown %s id %r" % (kind, ref))
    return node


def _slug(text: str) -> str:
    return _common.slugify(text)


def _default_copy(brief: dict) -> dict:
    try:
        from drafts import default_copy  # type: ignore
        return default_copy(brief)
    except Exception:  # pragma: no cover - drafts module arrives in Task 10
        name = (brief.get("words") or {}).get("name") or brief.get("product", "Your product").split(",")[0]
        return {
            "headline": name,
            "subhead": brief.get("product", ""),
            "cta_primary": "Get started",
            "cta_secondary": "Learn more",
            "nav": ["Product", "Pricing", "About", "Sign in"],
            "features": [{"title": "Feature", "body": "What it does for the person using it."}] * 3,
            "proof": "",
            "form": {"title": "Stay in touch", "fields": ["Email"], "submit": "Subscribe"},
            "footer": name,
        }


# ---------------------------------------------------------------- direction preparation

class Prepared:
    """Everything the renderers need for one direction."""

    def __init__(self, direction: dict, brief: dict, idx: Dict[str, dict]):
        b = direction["bundle"]
        self.id = direction["id"]
        self.name = direction.get("name") or "Direction %s" % self.id
        self.rationale = direction.get("rationale", "")
        self.style = _resolve(b["style"], idx, "style")
        self.palette = _resolve(b["palette"], idx, "palette")
        self.pairing = _resolve(b["type_pairing"], idx, "type-pairing")
        self.treatments = b.get("treatments", {})
        self.motion = [_resolve(m, idx, "motion-pattern") for m in b.get("motion", [])]
        self.motion_level = int(b.get("motion_level", 1))
        self.icon_set = _resolve(b.get("icon_set", "icon-set.lucide"), idx, "icon-set")
        self.radius_scale = b.get("radius_scale", self.style.get("radius_scale", "md"))
        self.density = b.get("density", self.style.get("density", "regular"))
        alts = b.get("alternatives", {}) or {}
        self.alt_palettes = [idx[p] for p in alts.get("palettes", []) if p in idx]
        self.alt_pairings = [idx[p] for p in alts.get("type_pairings", []) if p in idx]
        self.overrides = direction.get("overrides", {}) or {}
        self.resolved = resolve_palette(self.palette, self.overrides)
        self.copy = dict(_default_copy(brief))
        self.copy.update(direction.get("copy", {}) or {})
        layout = dict((self.style.get("layout_defaults") or {}).get(brief.get("page_type", "marketing"), {}))
        layout.update(direction.get("layout", {}) or {})
        self.layout = layout
        self.brief = brief
        self.direction = direction

    # -- css ---------------------------------------------------------------
    def tokens_css(self) -> str:
        return (tokens_css(self.resolved) + scale_tokens(self.radius_scale, self.density, self.pairing)
                + motion_tokens(self.motion_level))

    def variants_css(self) -> str:
        parts: List[str] = []
        parts.append(tokens_css(self.resolved, selector='[data-palette="%s"]' % self.palette["id"]))
        for p in self.alt_palettes:
            parts.append(tokens_css(resolve_palette(p, self.overrides), selector='[data-palette="%s"]' % p["id"]))
        for p in [self.pairing] + self.alt_pairings:
            css = scale_tokens(self.radius_scale, self.density, p)
            parts.append(css.replace(":root {", '[data-pairing="%s"] {' % p["id"], 1))
        for scale in RADIUS:
            lines = ['[data-radius="%s"] {' % scale]
            lines += ["  --pf-radius-%s: %s;" % (k, v) for k, v in RADIUS[scale].items()]
            lines.append("}")
            parts.append("\n".join(lines))
        for density in ("airy", "regular", "compact"):
            css = scale_tokens(self.radius_scale, density, self.pairing)
            keep = [l for l in css.splitlines() if "--pf-space-" in l or "--pf-density" in l]
            parts.append('[data-density="%s"] {\n%s\n}' % (density, "\n".join(keep)))
        for level in range(4):
            parts.append(motion_tokens(level).replace(":root {", '[data-motion="%d"] {' % level, 1))
        return "\n".join(parts) + "\n"

    # -- misc --------------------------------------------------------------
    def font_links(self) -> List[str]:
        urls = []
        for p in [self.pairing] + self.alt_pairings:
            u = p.get("css_url")
            if u and u not in urls:
                urls.append(u)
        return urls

    def font_families(self) -> List[str]:
        fams = [self.pairing["heading"]["family"], self.pairing["body"]["family"]]
        if self.pairing.get("mono"):
            fams.append(self.pairing["mono"]["family"])
        return [f for f in fams if f and not f.startswith(("system-ui", "-apple-system", "ui-"))]

    def root_classes(self) -> str:
        classes = ["pf-root"] + ["pf-%s-%s" % (axis.replace("_", "-"), v) for axis, v in sorted(self.treatments.items())]
        return " ".join(classes)

    def icons(self) -> List[str]:
        folder = ICON_ASSETS / self.icon_set["id"].split(".", 1)[1]
        out = []
        for name in ICON_NAMES:
            f = folder / (name + ".svg")
            if f.exists():
                svg = f.read_text(encoding="utf-8")
                svg = re.sub(r"<\?xml[^>]*>", "", svg)
                svg = re.sub(r"\s(width|height)=\"[^\"]*\"", "", svg, count=2)
                svg = svg.replace("<svg", '<svg class="pf-icon" aria-hidden="true" focusable="false" data-icon="%s"' % name, 1)
                out.append(svg.strip())
        return out


# ---------------------------------------------------------------- chrome

def _chrome(p: Prepared, all_dirs: List[Prepared], view: str, depth: int = 1) -> str:
    up = "../" * depth
    dirs = "".join(
        '<a class="pfc-dir%s" href="%s%s/%s.html">%s <span>%s</span></a>'
        % (" is-current" if d.id == p.id else "", up, d.id, view, E(d.id), E(d.name)) for d in all_dirs
    )
    views = "".join(
        '<a class="pfc-view%s" href="%s%s/%s.html">%s</a>' % (" is-current" if v == view else "", up, p.id, v, label)
        for v, label in VIEWS
    )

    def select(name: str, label: str, options: List[tuple], current: str) -> str:
        opts = "".join('<option value="%s"%s>%s</option>' % (E(v), " selected" if v == current else "", E(t)) for v, t in options)
        return '<label class="pfc-ctl"><span>%s</span><select data-control="%s">%s</select></label>' % (label, name, opts)

    pal_opts = [(p.palette["id"], p.palette["name"])] + [(x["id"], x["name"]) for x in p.alt_palettes]
    pair_opts = [(p.pairing["id"], p.pairing["name"])] + [(x["id"], x["name"]) for x in p.alt_pairings]
    controls = "".join([
        select("palette", "Palette", pal_opts, p.palette["id"]),
        select("pairing", "Type", pair_opts, p.pairing["id"]),
        select("radius", "Radius", [(k, k) for k in RADIUS], p.radius_scale),
        select("density", "Density", [(k, k) for k in ("airy", "regular", "compact")], p.density),
        select("motion", "Motion", [("0", "0 none"), ("1", "1 subtle"), ("2", "2 expressive"), ("3", "3 showcase")], str(p.motion_level)),
        '<button class="pfc-theme" type="button" data-control="theme" aria-pressed="false" title="Toggle light and dark">Dark</button>',
    ])
    return (
        '<header class="pfc-bar" data-direction="%s">'
        '<a class="pfc-back" href="%sindex.html">All directions</a>'
        '<nav class="pfc-dirs" aria-label="Directions">%s</nav>'
        '<nav class="pfc-views" aria-label="Views">%s</nav>'
        '<div class="pfc-controls">%s</div>'
        '<button class="pfc-select" type="button" data-action="select" data-direction="%s">Select %s</button>'
        '</header>' % (E(p.id), up, dirs, views, controls, E(p.id), E(p.name))
    )


def _head(p: Prepared, title: str, depth: int = 1, extra_css: Sequence[str] = ()) -> str:
    up = "../" * depth
    links = "".join('<link rel="stylesheet" href="%s">' % E(u) for u in p.font_links())
    css = "".join('<link rel="stylesheet" href="%s">' % E(c) for c in extra_css)
    return (
        '<title>%s</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '%s<link rel="stylesheet" href="%sassets/preview.css"><link rel="stylesheet" href="tokens.css"><link rel="stylesheet" href="variants.css">%s'
        % (E(title), links, up, css)
    )


def _page(p: Prepared, all_dirs: List[Prepared], view: str, body: str, extra_css: Sequence[str] = (), depth: int = 1) -> str:
    notice = ('<p class="pf-font-notice" hidden>Fonts could not be loaded, so this preview shows the fallback stack. '
              'The real faces are <span data-fonts-missing></span>.</p>')
    main = '<main class="%s" data-direction="%s" data-fonts="%s">%s%s</main>' % (
        p.root_classes(), E(p.id), E("|".join(p.font_families())), notice, body)
    return render_template("shell.html", {
        "lang": "en",
        "title": "%s · %s · preview-first" % (p.name, view),
        "head": _head(p, "%s · %s" % (p.name, view.capitalize()), depth, extra_css),
        "html_attrs": ' data-direction="%s" data-palette="%s" data-pairing="%s" data-radius="%s" data-density="%s" data-motion="%d"%s' % (
            E(p.id), E(p.palette["id"]), E(p.pairing["id"]), E(p.radius_scale), E(p.density), p.motion_level,
            ' data-theme="dark"' if p.palette.get("scheme") == "dark" else ""),
        "chrome": _chrome(p, all_dirs, view, depth),
        "body": main,
        "scripts": '<script src="%sassets/preview.js" defer></script>' % ("../" * depth),
    })


# ---------------------------------------------------------------- tile

def _swatch(role: str, entry: dict, checks: List[dict], mode: str) -> str:
    related = [c for c in checks if c["mode"] == mode and (c["fg_role"] == role)]
    badge = ""
    if related:
        c = related[0]
        badge = '<span class="pf-contrast %s" title="%s">%s · %.1f:1 · Lc %.0f</span>' % (
            "is-ok" if c["ok"] else "is-fail", E(c["pair"]), "pass" if c["ok"] else "fail", c["wcag"], c["apca"])
    return (
        '<li class="pf-swatch" data-role="%s" data-mode="%s"><span class="pf-swatch-chip" style="background:%s"></span>'
        '<span class="pf-swatch-name">%s</span><code>%s</code><code>%s</code>%s</li>'
        % (E(role), mode, entry["hex"], E(role.replace("_", " ")), entry["hex"], E(entry["oklch"]), badge)
    )


def _section(key: str, title: str, intro: str, body: str) -> str:
    return '<section class="pf-tile-section" data-section="%s"><header><h2>%s</h2><p>%s</p></header>%s</section>' % (key, E(title), intro, body)


def _tile_body(p: Prepared) -> str:
    r = p.resolved
    pal = "".join(
        '<div class="pf-palette-mode" data-mode="%s"><h3>%s</h3><ul class="pf-swatches">%s</ul></div>' % (
            mode, mode.capitalize(), "".join(_swatch(role, r[mode][role], r["checks"], mode) for role in ROLES))
        for mode in ("light", "dark")
    )
    warn = "".join("<li>%s</li>" % E(w) for w in r["warnings"])
    if warn:
        pal += '<div class="pf-alert pf-alert-warning"><strong>Contrast warnings</strong><ul>%s</ul></div>' % warn
    palette_section = _section("palette", "Palette", "Every role, in both modes, with its contrast against the surface it sits on. "
                               "Body text is graded at WCAG 4.5:1 and APCA Lc 60; labels at Lc 45.", pal)

    h, b = p.pairing["heading"], p.pairing["body"]
    steps = [("5xl", "Display"), ("4xl", "Headline"), ("3xl", "Title"), ("2xl", "Section"), ("xl", "Lead"), ("lg", "Large body"), ("base", "Body"), ("sm", "Caption"), ("xs", "Footnote")]
    samples = "".join(
        '<div class="pf-type-sample" data-step="%s"><span class="pf-type-label">%s · var(--pf-text-%s)</span>'
        '<p class="pf-type-%s" style="font-size:var(--pf-text-%s)">%s</p></div>' % (
            s, label, s, "heading" if s in ("5xl", "4xl", "3xl", "2xl") else "body", s, E(p.copy.get("headline", p.name)))
        for s, label in steps
    )
    para = ('<p class="pf-measure-sample">%s %s</p>' % (E(p.copy.get("subhead", "")), E(
        "A paragraph set at body size on the measure this direction uses, so line length and leading can be judged before anything is built.")))
    mono = p.pairing.get("mono")
    type_meta = (
        '<dl class="pf-type-meta"><dt>Heading</dt><dd>%s (%s, %s)</dd><dt>Body</dt><dd>%s (%s, %s)</dd>%s'
        '<dt>Scale</dt><dd>%s</dd><dt>Measure</dt><dd>%sch</dd><dt>Licence</dt><dd>%s</dd><dt>Fallbacks</dt><dd><code>%s</code> · <code>%s</code></dd></dl>'
        % (E(h["family"]), E(h["category"]), E(", ".join(map(str, h.get("weights", [])))),
           E(b["family"]), E(b["category"]), E(", ".join(map(str, b.get("weights", [])))),
           ("<dt>Mono</dt><dd>%s</dd>" % E(mono["family"])) if mono else "",
           E(str(p.pairing.get("scale_ratio"))), E(str(p.pairing.get("measure_ch"))), E(str(p.pairing.get("license", ""))),
           E(p.pairing["fallback_heading"]), E(p.pairing["fallback_body"]))
    )
    type_section = _section("type", "Typography", "The pairing and its scale. %s" % E(p.pairing.get("notes", "")),
                            type_meta + samples + para)

    spaces = "".join('<li><span class="pf-space-bar" style="width:var(--pf-space-%d)"></span><code>space-%d</code></li>' % (n, n) for n in (1, 2, 3, 4, 6, 8, 12))
    spacing_section = _section("spacing", "Spacing", "A 4px base multiplied by the density factor (%s)." % E(p.density),
                               '<ul class="pf-space-scale">%s</ul>' % spaces)
    radii = "".join('<li><span class="pf-radius-chip" style="border-radius:var(--pf-radius-%s)"></span><code>radius-%s</code></li>' % (k, k) for k in ("xs", "sm", "md", "lg", "xl", "full"))
    radius_section = _section("radius", "Radius", "Scale <strong>%s</strong>. Hierarchy comes from using different steps, not one radius everywhere." % E(p.radius_scale),
                              '<ul class="pf-radius-scale">%s</ul>' % radii)
    elev = "".join('<li><div class="pf-elev pf-elev-%s"></div><code>%s</code></li>' % (k, k) for k in ("flat", "raised", "overlay"))
    elevation_section = _section("elevation", "Elevation", "Treatment <strong>%s</strong>; shadows are %s." % (E(p.treatments.get("elevation", "none")), E(p.style.get("shadow", "none"))),
                                 '<ul class="pf-elev-scale">%s</ul>' % elev)

    set_name, lic = ICON_LICENSES.get(p.icon_set["id"], (p.icon_set["name"], p.icon_set.get("license", "")))
    icons = "".join('<li>%s<code>%s</code></li>' % (svg, name) for svg, name in zip(p.icons(), ICON_NAMES))
    icons_section = _section("icons", "Iconography", "%s, stroke %s, %s licence. Never emoji." % (E(set_name), E(str(p.icon_set.get("stroke", ""))), E(lic)),
                             '<ul class="pf-icon-grid">%s</ul><p class="pf-small">Samples are the real %s glyphs, inlined. <a href="%s">%s</a></p>' % (
                                 icons, E(set_name), E(p.icon_set.get("url", "#")), E(p.icon_set.get("url", ""))))

    comp = []
    for state in ("default", "hover", "focus", "active", "disabled", "loading"):
        comp.append('<button class="pf-btn pf-btn-primary" type="button" data-state="%s"%s>%s</button>' % (
            state, " disabled" if state == "disabled" else "", "Working" if state == "loading" else E(p.copy.get("cta_primary", "Continue"))))
    buttons = '<div class="pf-row" data-component="button-primary">%s</div>' % "".join(comp)
    buttons += '<div class="pf-row" data-component="button-secondary">%s</div>' % "".join(
        '<button class="pf-btn pf-btn-secondary" type="button" data-state="%s">%s</button>' % (s, E(p.copy.get("cta_secondary", "Learn more"))) for s in ("default", "hover", "focus"))
    buttons += '<div class="pf-row" data-component="button-quiet"><button class="pf-btn pf-btn-quiet" type="button" data-state="default">Cancel</button><button class="pf-btn pf-btn-danger" type="button" data-state="default">Delete project</button></div>'
    inputs = "".join(
        '<label class="pf-field" data-state="%s"><span>%s</span><input class="pf-input" type="text" data-state="%s" value="%s"%s>%s</label>' % (
            s, "Work email" if s != "error" else "Work email", s, "ada@ledgerline.dev" if s != "default" else "", " disabled" if s == "disabled" else "",
            '<small class="pf-error">Use the address on the contract.</small>' if s == "error" else "")
        for s in ("default", "focus", "error", "disabled"))
    inputs = '<div class="pf-grid-2" data-component="input">%s</div>' % inputs
    select = ('<div class="pf-row" data-component="select"><label class="pf-field"><span>Currency</span><select class="pf-select"><option>EUR</option><option>USD</option><option>ILS</option></select></label>'
              '<label class="pf-check"><input type="checkbox" checked><span>Send a copy to me</span></label>'
              '<label class="pf-switch"><input type="checkbox" role="switch" checked><span class="pf-switch-track"></span><span>Automatic reminders</span></label></div>')
    card = ('<div class="pf-grid-2" data-component="card"><article class="pf-card"><h3>%s</h3><p>%s</p><a class="pf-link" href="#">Read the guide</a></article>'
            '<article class="pf-card"><span class="pf-badge">Draft</span><h3>Invoice 0142</h3><p class="pf-muted">Due 12 Nov · 3 line items</p>'
            '<div class="pf-row"><button class="pf-btn pf-btn-primary pf-btn-sm" type="button">Send</button><button class="pf-btn pf-btn-secondary pf-btn-sm" type="button">Edit</button></div></article></div>') % (
        E(p.copy["features"][0]["title"]) if p.copy.get("features") else "Card title", E(p.copy["features"][0]["body"]) if p.copy.get("features") else "Card body.")
    badges = ('<div class="pf-row" data-component="badge"><span class="pf-badge">Neutral</span><span class="pf-badge pf-badge-primary">Primary</span>'
              '<span class="pf-badge pf-badge-success">Paid</span><span class="pf-badge pf-badge-warning">Overdue</span><span class="pf-badge pf-badge-danger">Failed</span></div>')
    alerts = ('<div class="pf-stack" data-component="alert"><div class="pf-alert pf-alert-info"><strong>Saved.</strong> Changes apply to new invoices.</div>'
              '<div class="pf-alert pf-alert-danger"><strong>Payment failed.</strong> The card was declined; try another card or pay by transfer.</div></div>')
    tabs = ('<div class="pf-tabs" role="tablist" data-component="tabs"><button role="tab" aria-selected="true" class="pf-tab">Overview</button>'
            '<button role="tab" aria-selected="false" class="pf-tab">Line items</button><button role="tab" aria-selected="false" class="pf-tab">Activity</button><span class="pf-tab-indicator"></span></div>')
    nav_links = "".join('<a href="#">%s</a>' % E(x) for x in p.copy.get("nav", [])[:4])
    nav = ('<nav class="pf-nav" data-component="nav" aria-label="Sample navigation"><span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div>'
           '<button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button></nav>') % (
        E((p.brief.get("words") or {}).get("name") or p.name), nav_links, E(p.copy.get("cta_primary", "Start")))
    footer = ('<footer class="pf-footer" data-component="footer"><div><span class="pf-wordmark">%s</span><p class="pf-muted">%s</p></div>'
              '<div class="pf-footer-cols"><div><h4>Product</h4><a href="#">Pricing</a><a href="#">Changelog</a></div><div><h4>Company</h4><a href="#">About</a><a href="#">Contact</a></div></div></footer>') % (
        E((p.brief.get("words") or {}).get("name") or p.name), E(p.copy.get("footer", "")))
    components_section = _section("components", "Components",
                                  "Drawn with this direction's treatments: %s." % E(", ".join("%s %s" % (k.replace("_", " "), v) for k, v in sorted(p.treatments.items()))),
                                  "".join([buttons, inputs, select, card, badges, alerts, tabs, nav, footer]))

    demos = []
    for m in p.motion:
        slug = m["id"].split(".", 1)[1]
        kind = DEMO_KIND.get(slug, "fade-up")
        demos.append(
            '<figure class="pf-motion-demo" data-motion-id="%s" data-demo="%s" style="--demo-dur:%dms;--demo-ease:%s">'
            '<div class="pf-demo-stage"><div class="pf-demo-el"><span></span></div></div>'
            '<figcaption><strong>%s</strong><span class="pf-muted">%s · %dms · <code>%s</code> · %s</span><span class="pf-small">Reduced motion: %s</span>'
            '<button class="pf-btn pf-btn-secondary pf-btn-sm" type="button" data-action="play">Play</button></figcaption></figure>'
            % (E(m["id"]), kind, int(m.get("duration_ms", 0)), E(str(m.get("easing", "ease"))), E(m["name"]), E(m.get("trigger", "")),
               int(m.get("duration_ms", 0)), E(str(m.get("easing", "ease"))), E(m.get("communicates", "")), E(str(m.get("reduced_motion", ""))))
        )
    motion_section = _section("motion", "Motion", "Level %d. Each pattern plays on demand with its real duration and easing. "
                              '<label class="pf-check pf-inline"><input type="checkbox" data-control="reduced"><span>Simulate reduced motion</span></label>' % p.motion_level,
                              '<div class="pf-motion-grid">%s</div>' % "".join(demos))

    intro = (
        '<section class="pf-tile-intro"><p class="pf-kicker">Direction %s</p><h1>%s</h1><p class="pf-lead">%s</p>'
        '<dl class="pf-meta"><dt>Style</dt><dd>%s</dd><dt>Palette</dt><dd>%s</dd><dt>Type</dt><dd>%s</dd><dt>Icons</dt><dd>%s</dd></dl></section>'
        % (E(p.id), E(p.name), E(p.rationale or p.style.get("summary", "")), E(p.style["name"]), E(p.palette["name"]), E(p.pairing["name"]), E(p.icon_set["name"]))
    )
    return intro + "".join([palette_section, type_section, spacing_section, radius_section, elevation_section, icons_section, components_section, motion_section])


# ---------------------------------------------------------------- gallery

def _gallery(dirs: List[Prepared], brief: dict) -> str:
    name = (brief.get("words") or {}).get("name") or brief.get("product", "your product").split(",")[0]
    cards = []
    for p in dirs:
        r = p.resolved["dark" if p.palette.get("scheme") == "dark" else "light"]
        strip = "".join('<span style="background:%s" title="%s"></span>' % (r[k]["hex"], k) for k in ("bg", "surface", "text", "primary", "accent"))
        cards.append(
            '<article class="pfg-card" data-direction="%s">'
            '<link rel="stylesheet" href="%s/tokens.css">'
            '<div class="pfg-thumb"><iframe class="pfg-frame" loading="lazy" src="%s/draft.html?embed=1%s" title="%s draft" tabindex="-1"></iframe></div>'
            '<div class="pfg-body"><p class="pfc-kicker">Direction %s · %s</p><h2>%s</h2><p>%s</p>'
            '<div class="pfg-strip">%s</div>'
            '<p class="pfg-type"><span style="font-family:%s">%s</span> <span class="pfc-muted">with %s</span></p>'
            '<nav class="pfg-links"><a href="%s/tile.html">Tile</a><a href="%s/draft.html">Draft</a><a href="%s/devices.html">Devices</a></nav>'
            '<button class="pfc-select" type="button" data-action="select" data-direction="%s">Select %s</button></div></article>'
            % (E(p.id), E(p.id), E(p.id), "&theme=dark" if p.palette.get("scheme") == "dark" else "", E(p.name), E(p.id), E(p.style["name"]), E(p.name), E(p.rationale or p.style.get("summary", "")), strip,
               E("'%s', %s" % (p.pairing["heading"]["family"], p.pairing["fallback_heading"])), E(p.pairing["heading"]["family"]),
               E(p.pairing["body"]["family"]), E(p.id), E(p.id), E(p.id), E(p.id), E(p.name))
        )
    links = "".join('<link rel="stylesheet" href="%s">' % E(u) for p in dirs for u in p.font_links())
    body = (
        '<header class="pfg-head"><p class="pfc-kicker">preview-first</p><h1>Design directions for %s</h1>'
        '<p class="pfc-muted">%s</p><div class="pfc-controls"><button class="pfc-theme" type="button" data-control="theme" aria-pressed="false">Dark</button></div></header>'
        '<section class="pfg-grid">%s</section>'
        '<footer class="pfg-foot"><p>Pick a direction, or open a tile to swap palette, type, radius, density and motion live. '
        'Selecting writes <code>.design-preview/selection.json</code>; Claude then exports the design contract.</p></footer>'
        % (E(name), E(brief.get("product", "")), "".join(cards))
    )
    return render_template("shell.html", {
        "lang": "en", "title": "Design directions · preview-first",
        "head": '<title>Design directions · preview-first</title>%s<link rel="stylesheet" href="assets/preview.css">' % links,
        "html_attrs": ' data-gallery="1"', "chrome": "", "body": '<main class="pfg">%s</main>' % body,
        "scripts": '<script src="assets/preview.js" defer></script>',
    })


# ---------------------------------------------------------------- fonts (optional vendoring)

def _vendor_fonts(dirs: List[Prepared], out: Path, warnings: List[str]) -> None:
    fonts_dir = out / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
    seen = set()
    for p in dirs:
        for url in p.font_links():
            if url in seen:
                continue
            seen.add(url)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": ua})
                css = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")
                def repl(m):
                    furl = m.group(1)
                    fname = _slug(furl.rsplit("/", 1)[-1].split("?")[0]) + ".woff2"
                    target = fonts_dir / fname
                    if not target.exists():
                        target.write_bytes(urllib.request.urlopen(urllib.request.Request(furl, headers={"User-Agent": ua}), timeout=20).read())
                    return "url(%s)" % fname
                css = re.sub(r"url\((https://[^)]+\.woff2)\)", repl, css)
                (fonts_dir / (_slug(url) + ".css")).write_text(css, encoding="utf-8")
            except Exception as exc:  # network failures are reported, not fatal
                warnings.append("font vendoring failed for %s: %s" % (url, exc))


# ---------------------------------------------------------------- build

def build(directions: dict, out: Path, graph: dict, devices: List[dict], vendor_fonts: bool = False) -> dict:
    out = Path(out)
    problems = validate_file(directions, "directions", _common.load_schema())
    if problems:
        raise ValueError("directions.json invalid: " + "; ".join(problems[:5]))
    idx = _common.node_index(graph)
    brief = directions.get("brief", {})
    dirs = [Prepared(d, brief, idx) for d in directions["directions"]]
    warnings: List[str] = []
    pages: List[str] = []

    (out / "assets").mkdir(parents=True, exist_ok=True)
    for name in ("preview.css", "tile.css", "draft.css", "preview.js", "device-frames.css"):
        shutil.copyfile(PREVIEW_ASSETS / name, out / "assets" / name)
    if ICON_ASSETS.exists():
        shutil.copytree(ICON_ASSETS, out / "assets" / "icons", dirs_exist_ok=True)

    try:
        from drafts import render as render_draft  # type: ignore
    except Exception:  # pragma: no cover
        render_draft = None
    try:
        from drafts import render_devices  # type: ignore
    except Exception:  # pragma: no cover
        render_devices = None

    for p in dirs:
        d = out / p.id
        d.mkdir(parents=True, exist_ok=True)
        (d / "tokens.css").write_text(p.tokens_css(), encoding="utf-8")
        (d / "variants.css").write_text(p.variants_css(), encoding="utf-8")
        (d / "tile.html").write_text(_page(p, dirs, "tile", _tile_body(p), extra_css=("../assets/tile.css",)), encoding="utf-8")
        pages.append(str(d / "tile.html"))
        if render_draft:
            (d / "draft.html").write_text(
                _page(p, dirs, "draft", render_draft(brief.get("page_type", "marketing"), p), extra_css=("../assets/draft.css",)), encoding="utf-8")
            pages.append(str(d / "draft.html"))
        if render_devices:
            (d / "devices.html").write_text(
                _page(p, dirs, "devices", render_devices(p, devices), extra_css=("../assets/tile.css", "../assets/device-frames.css")), encoding="utf-8")
            pages.append(str(d / "devices.html"))
        warnings.extend("%s: %s" % (p.id, w) for w in p.resolved["warnings"])

    (out / "index.html").write_text(_gallery(dirs, brief), encoding="utf-8")
    pages.append(str(out / "index.html"))
    _common.dump_json(out / "data.json", {
        "brief": brief,
        "directions": [{
            "id": p.id, "name": p.name, "style": p.style["id"], "palette": p.palette["id"], "type_pairing": p.pairing["id"],
            "treatments": p.treatments, "motion": [m["id"] for m in p.motion], "motion_level": p.motion_level,
            "icon_set": p.icon_set["id"], "radius_scale": p.radius_scale, "density": p.density,
            "alternatives": {"palettes": [x["id"] for x in p.alt_palettes], "type_pairings": [x["id"] for x in p.alt_pairings]},
            "palette_resolved": p.resolved, "copy": p.copy, "layout": p.layout,
        } for p in dirs],
        "devices": devices,
        "built": _common.now_iso(),
    })
    if vendor_fonts:
        _vendor_fonts(dirs, out, warnings)
    return {"pages": pages, "warnings": warnings, "out": str(out)}


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build the preview-first browser preview.")
    ap.add_argument("--directions", required=True)
    ap.add_argument("--out", default=".design-preview")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ap.add_argument("--devices", default=str(_common.KNOWLEDGE_DIR / "devices.json"))
    ap.add_argument("--vendor-fonts", action="store_true")
    ns = ap.parse_args(list(argv))
    report = build(_common.load_json(ns.directions), Path(ns.out), _common.load_json(ns.graph),
                   _common.load_json(ns.devices)["devices"], ns.vendor_fonts)
    for w in report["warnings"]:
        print("warning:", w, file=sys.stderr)
    print(json.dumps({"out": report["out"], "pages": len(report["pages"]), "warnings": len(report["warnings"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
