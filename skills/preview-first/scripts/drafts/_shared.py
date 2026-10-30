"""Shared building blocks for drafted pages, including the render hooks that design ideas switch on."""
from __future__ import annotations

import html
import re
from typing import List, Optional

E = html.escape

NAV_VARIANTS = ["bar", "split-meta", "menu-word", "pill", "rail"]
_NAV_HOOKS = (("nav-split-meta", "split-meta"), ("nav-menu-word", "menu-word"), ("nav-pill", "pill"), ("nav-rail", "rail"), ("nav-bar", "bar"))
VERSION_LINE = "v0.4.1"


def hooks(p) -> set:
    return set(getattr(p, "hooks", set()) or set())


def has(p, hook: str) -> bool:
    return hook in hooks(p)


def explicit(p, section_name: str) -> Optional[str]:
    """The variant the direction's author set by hand, if any (style defaults do not count)."""
    return (getattr(p, "layout_explicit", {}) or {}).get(section_name)


def section(name: str, variant: str, inner: str, extra_class: str = "") -> str:
    return '<section class="pfd-%s pfd-%s-%s %s" data-section="%s" data-variant="%s">%s</section>' % (
        E(name), E(name), E(variant), E(extra_class), E(name), E(variant), inner)


def pick(p, section_name: str, variants: List[str], hook_map: Optional[dict] = None) -> str:
    """Variant choice, in order: the author's explicit layout; a hook carried by one of the style's
    own default ideas; for the hero the style's layout default; any other hook from the direction's
    ideas; the style's layout default; the first variant."""
    v = explicit(p, section_name)
    if v in variants:
        return v
    own = set()
    for iid in (p.style.get("ideas") or []):
        for i in getattr(p, "ideas", []) or []:
            if i.get("id") == iid and i.get("renders"):
                own.add(i["renders"])
    for hook, variant in (hook_map or {}).items():
        if hook in own and variant in variants:
            return variant
    default = (p.layout or {}).get(section_name)
    if section_name == "hero" and default in variants:
        return default  # the first screen is the style's identity; borrowed hooks do not replace it
    for hook, variant in (hook_map or {}).items():
        if has(p, hook) and variant in variants:
            return variant
    return default if default in variants else variants[0]


def brand(p) -> str:
    return (p.brief.get("words") or {}).get("name") or p.copy.get("headline", p.name).split(" ")[0]


def meta(p) -> dict:
    m = dict(p.copy.get("meta") or {})
    m.setdefault("city", "")
    m.setdefault("year", "2026")
    return m


# ---------------------------------------------------------------- type decorations

def headline(p, text: str, cls: str = "") -> str:
    """The H1 with the direction's type hooks applied: one outlined word or one word in a
    contrasting face. Never both."""
    words = text.split()
    mark = None  # (index, css class) of the one decorated word
    if has(p, "type-outline") and len(words) > 1:
        mark = (len(words) - 1, "pfd-outline")
    elif has(p, "type-mixed-face") and len(words) > 2:
        mark = (max(range(len(words)), key=lambda k: len(words[k])), "pfd-alt")
    body = " ".join('<span class="%s">%s</span>' % (mark[1], E(w)) if mark and k == mark[0] else E(w) for k, w in enumerate(words))
    if has(p, "motion-line-reveal"):
        cls += " pfd-reveal"
    return '<h1 class="%s">%s</h1>' % (E(cls.strip()), body)


def index_label(p, n: int, total: Optional[int] = None, prefix: str = "") -> str:
    if has(p, "type-index-numbers"):
        txt = "( %02d )" % n if total is None else "%02d / %02d" % (n, total)
    else:
        txt = "%s%d" % (prefix, n) if prefix else "%02d" % n
    return '<span class="pfd-index">%s</span>' % E(txt)


def caption(p, n: int, text: str) -> str:
    if not (has(p, "image-caption") or has(p, "type-index-numbers")):
        return ""
    return '<figcaption class="pfd-caption">%s %s</figcaption>' % (index_label(p, n, prefix="Fig "), E(text))


def vlabel(p, text: str) -> str:
    return '<span class="pfd-vlabel" aria-hidden="true">%s</span>' % E(text) if has(p, "type-vertical-label") else ""


def stickers(p) -> str:
    if not has(p, "image-sticker"):
        return ""
    words = [meta(p)["year"], brand(p)]
    return "".join('<span class="pfd-sticker" style="--r:%ddeg;--x:%d%%;--y:%d%%" aria-hidden="true">%s</span>' % (r, x, y, E(w))
                   for w, (r, x, y) in zip(words, ((-8, 78, 8), (6, 6, 70))))


# ---------------------------------------------------------------- navigation

def nav_variant(p) -> str:
    return pick(p, "nav", NAV_VARIANTS, dict(_NAV_HOOKS))


def _overlay(p, links: List[str]) -> str:
    items = "".join('<a href="#" style="--i:%d">%s</a>' % (i, E(x)) for i, x in enumerate(links[:6]))
    m = meta(p)
    return ('<div class="pfd-menu-overlay" data-menu-overlay hidden><div class="pfd-menu-top"><span class="pf-wordmark">%s</span>'
            '<button class="pfd-menu-word" type="button" data-action="menu" aria-expanded="true">Close</button></div>'
            '<nav class="pfd-menu-links" aria-label="Menu">%s</nav>'
            '<p class="pfd-menu-meta">%s<time data-live-time></time></p></div>') % (
        E(brand(p)), items, (E(m["city"]) + " · ") if m["city"] else "")


def nav(p, links: List[str] = None) -> str:
    links = links or p.copy.get("nav", [])
    v = nav_variant(p)
    name = E(brand(p))
    cta = E(p.copy.get("cta_primary", "Start"))
    items = "".join('<a href="#">%s</a>' % E(x) for x in links[:5])
    m = meta(p)
    if v == "split-meta":
        inner = ('<span class="pf-wordmark">%s</span><span class="pfd-nav-meta"><span>%s</span><time data-live-time>--:--</time></span>'
                 '<button class="pfd-menu-word" type="button" data-action="menu" aria-expanded="false">Menu</button>') % (
            name, E(m["city"] or m["year"]))
        html_ = '<nav class="pf-nav pfd-nav pfd-nav-split-meta" aria-label="Main" data-section="nav" data-variant="split-meta">%s</nav>%s' % (inner, _overlay(p, links))
    elif v == "menu-word":
        inner = '<span class="pf-wordmark">%s</span><button class="pfd-menu-word" type="button" data-action="menu" aria-expanded="false">Menu</button>' % name
        html_ = '<nav class="pf-nav pfd-nav pfd-nav-menu-word" aria-label="Main" data-section="nav" data-variant="menu-word">%s</nav>%s' % (inner, _overlay(p, links))
    elif v == "pill":
        inner = '<span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div><a class="pf-link pfd-nav-cta" href="#">%s</a>' % (name, items, cta)
        html_ = '<div class="pfd-nav-pill-wrap" data-section="nav" data-variant="pill"><nav class="pf-nav pfd-nav pfd-nav-pill" aria-label="Main">%s</nav></div>' % inner
    elif v == "rail":
        feats = p.copy.get("features") or []
        rail = "".join('<li><a href="#f%d" aria-label="%s">%02d</a></li>' % (i + 1, E(f.get("title", "")), i + 1) for i, f in enumerate(feats[:6]))
        inner = '<span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div><a class="pf-link pfd-nav-cta" href="#">%s</a>' % (name, items, cta)
        html_ = ('<nav class="pf-nav pfd-nav pfd-nav-rail" aria-label="Main" data-section="nav" data-variant="rail">%s</nav>'
                 '<ol class="pfd-rail" aria-label="Sections" data-rail>%s</ol>') % (inner, rail)
    else:
        inner = '<span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div><button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button>' % (name, items, cta)
        html_ = '<nav class="pf-nav pfd-nav pfd-nav-bar" aria-label="Main" data-section="nav" data-variant="bar">%s</nav>' % inner
    return html_


# ---------------------------------------------------------------- buttons, marquee, footer

def _icon(p, name: str) -> str:
    try:
        from build_preview import ICON_NAMES  # type: ignore
        svgs = p.icons()
        return svgs[ICON_NAMES.index(name)]
    except Exception:
        return ""


def buttons(p, size: str = "") -> str:
    primary = E(p.copy.get("cta_primary", "Get started"))
    secondary = E(p.copy.get("cta_secondary", "Learn more"))
    if has(p, "button-bracket"):
        return ('<div class="pf-row pfd-actions pfd-actions-bracket"><a class="pfd-bracket" href="#">%s</a><a class="pfd-bracket is-quiet" href="#">%s</a></div>') % (primary, secondary)
    if has(p, "button-circle-icon"):
        icon = _icon(p, "arrow-right") or '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
        return ('<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary pfd-btn-circle %s" type="button"><span>%s</span><span class="pfd-btn-icon" aria-hidden="true">%s</span></button>'
                '<a class="pf-link" href="#">%s</a></div>') % (size, primary, icon, secondary)
    if has(p, "button-fill-up"):
        return ('<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-secondary pfd-btn-fill %s" type="button"><span>%s</span></button>'
                '<a class="pf-link" href="#">%s</a></div>') % (size, primary, secondary)
    if has(p, "button-underline"):
        return ('<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary %s" type="button">%s</button>'
                '<a class="pf-link pfd-ulink" href="#">%s</a></div>') % (size, primary, secondary)
    return ('<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary %s" type="button">%s</button>'
            '<a class="pf-btn pf-btn-secondary %s" href="#">%s</a></div>') % (size, primary, size, secondary)


def marquee(p) -> str:
    if not has(p, "section-marquee"):
        return ""
    words = [brand(p)] + [f.get("title", "") for f in (p.copy.get("features") or [])] + list(p.copy.get("nav", []))[:3] + [meta(p)["year"]]
    words = [w for w in words if w][:8]
    track = "".join('<span>%s</span><i aria-hidden="true"></i>' % E(w) for w in words)
    return ('<div class="pfd-marquee" aria-hidden="true" data-section="marquee" data-variant="line"><div class="pfd-marquee-track">%s%s</div></div>') % (track, track)


def placeholder(label: str, ratio: str = "16 / 10", cls: str = "") -> str:
    """An honest image placeholder: a labelled surface, never a fake photo or logo."""
    return ('<div class="pfd-media %s" style="aspect-ratio:%s" role="img" aria-label="%s">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4zM4 15l5-5 4 4 3-3 4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>'
            '<span>%s</span></div>') % (E(cls), E(ratio), E(label), E(label))


def footer(p, variant: str) -> str:
    links = "".join('<a href="#">%s</a>' % E(x) for x in p.copy.get("nav", [])[:5])
    m = meta(p)
    if variant == "colophon":
        face = p.pairing["heading"]["family"]
        parts = ['<span class="pf-wordmark">%s</span>' % E(brand(p)), "<span>%s</span>" % E(m["year"])]
        if m["city"]:
            parts.append("<span>%s</span>" % E(m["city"]))
        parts += ['<time data-live-time></time>', "<span>Set in %s</span>" % E(face), "<span>%s</span>" % VERSION_LINE,
                  '<nav class="pfd-footer-links">%s</nav>' % links]
        return section("footer", variant, '<footer class="pf-footer pfd-colophon">%s</footer>' % "".join(parts))
    if variant == "giant":
        inner = ('<div class="pfd-footer-giant"><span class="pfd-giant-word" aria-hidden="true">%s</span>'
                 '<div class="pfd-footer-giant-row"><p class="pf-muted">%s</p><nav class="pfd-footer-links">%s</nav></div></div>') % (
            E(brand(p)), E(p.copy.get("footer", "")), links)
        return section("footer", variant, '<footer class="pf-footer pf-footer-giant">%s</footer>' % inner)
    cols = ('<div class="pf-footer-cols"><div><h4>Product</h4><a href="#">Pricing</a><a href="#">Changelog</a><a href="#">Status</a></div>'
            '<div><h4>Company</h4><a href="#">About</a><a href="#">Contact</a></div>'
            '<div><h4>Legal</h4><a href="#">Privacy</a><a href="#">Terms</a></div></div>')
    inner = '<div><span class="pf-wordmark">%s</span><p class="pf-muted">%s</p></div>%s' % (
        E(brand(p)), E(p.copy.get("footer", "")), cols if variant == "columns" else '<p class="pf-muted">%s</p>' % E(" · ".join(p.copy.get("nav", [])[:3])))
    return section("footer", variant, '<footer class="pf-footer">%s</footer>' % inner)


def features(p) -> List[dict]:
    feats = list(p.copy.get("features") or [])
    while len(feats) < 3:
        feats.append({"title": "Feature %d" % (len(feats) + 1), "body": "What this does for the person using it."})
    return feats[:6]


def block_classes(p, order: List[str]) -> dict:
    """Section background classes for colour-blocked and inverted-ending pages."""
    out = {name: "" for name in order}
    if has(p, "color-blocking"):
        cycle = ["", "pfd-block-primary", "pfd-block-tint", "pfd-block-ink", "pfd-block-ink"]
        for i, name in enumerate(order):
            out[name] = cycle[i % len(cycle)]
    if has(p, "color-inverted-section"):
        for name in order[-2:]:
            out[name] = "pfd-block-ink"
    return out


def with_class(section_html: str, cls: str) -> str:
    if not cls:
        return section_html
    return re.sub(r'^(<section class="[^"]*)"', r'\1 %s"' % cls, section_html, count=1)
