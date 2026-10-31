"""Shared building blocks for drafted pages, including the render hooks that design ideas switch on."""
from __future__ import annotations

import html
import re
from typing import List, Optional

E = html.escape

NAV_VARIANTS = ["bar", "split-meta", "menu-word", "pill", "rail"]
_NAV_HOOKS = (("nav-split-meta", "split-meta"), ("nav-menu-word", "menu-word"), ("nav-pill", "pill"), ("nav-rail", "rail"), ("nav-bar", "bar"))
VERSION_LINE = "v0.5.0"


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


# ---------------------------------------------------------------- topic components

def kit(p) -> dict:
    return dict(getattr(p, "kit", {}) or {})


def topic_block(p) -> str:
    """A component that belongs to this kind of product (a terminal, a balance, a schedule, a composer),
    placed after the first screen so the page reads as the product and not as a template."""
    from . import art  # local import to avoid a cycle
    k = kit(p).get("component") or "none"
    feats = features(p)
    name = E(brand(p))
    if k == "none" or explicit(p, "topic") == "none":
        return ""
    if k == "terminal":
        lines = "".join('<div><span class="pfd-term-prompt">$</span> %s</div>' % E(f["title"].lower().replace(" ", "-")) for f in feats[:4])
        inner = '<div class="pfd-term"><div class="pfd-term-bar"><span></span><span></span><span></span><span class="pfd-index">%s</span></div><pre class="pfd-term-body">%s<div><span class="pfd-term-prompt">$</span> <span class="pfd-cursor">█</span></div></pre></div>' % (name, lines)
    elif k == "composer":
        chips = "".join('<button class="pf-btn pf-btn-secondary pf-btn-sm" type="button">%s</button>' % E(f["title"]) for f in feats[:3])
        inner = ('<div class="pfd-composer"><div class="pfd-composer-box"><p class="pf-muted">%s</p><div class="pfd-composer-row"><span class="pfd-index">%s</span><button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button></div></div><div class="pf-row">%s</div></div>') % (
            E("Ask %s about %s" % (brand(p), feats[0]["title"].lower())), E("Sources shown with every answer"), E(p.copy.get("cta_primary", "Ask")), chips)
    elif k == "balance":
        rows = "".join('<li><span>%s</span><span class="pfd-num">%s</span></li>' % (E(f["title"]), ("+" if i % 2 else "-") + "%d.00" % (120 + i * 37)) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-balance"><span class="pfd-index">%s</span><span class="pfd-balance-figure">4,250.00</span><ul class="pfd-balance-list">%s</ul><p class="pf-small">Sample figures; the build shows real ones.</p></div>' % (E("Balance"), rows)
    elif k == "product-row":
        tiles = "".join('<a class="pfd-topic-tile" href="#">%s<span>%s</span><span class="pfd-price">%s</span></a>' % (art.render("object", seed="%s-tp%d" % (p.id, i)), E(f["title"]), ["48.00", "140.00", "32.00", "26.00"][i % 4]) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-topic-row">%s</div>' % tiles
    elif k == "work-list":
        rows = "".join('<a class="pfd-hover-row" href="#"><span class="pfd-hover-title">%s</span><span class="pfd-hover-meta">%s</span>%s</a>' % (E(f["title"]), E(brand(p)), index_label(p, i + 1, len(feats))) for i, f in enumerate(feats[:5]))
        inner = '<div class="pfd-hover-list">%s</div>' % rows
    elif k == "article-list":
        rows = "".join('<a class="pfd-archive-row" href="#"><span class="pfd-index">%s</span><span class="pfd-archive-title">%s</span><span class="pfd-archive-meta">%s</span></a>' % (E("2026.%02d" % (10 - i)), E(f["title"]), E("%d min" % (4 + i * 2))) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-archive">%s</div>' % rows
    elif k == "metrics":
        cells = "".join('<div class="pfd-metric"><span class="pfd-index">%s</span><span class="pfd-metric-figure" data-count="%s">%s</span>%s</div>' % (E(f["title"]), v, v, art.render("figure", seed="%s-mt%d" % (p.id, i + 11))) for i, (f, v) in enumerate(zip(feats[:4], ["1,284", "97.2", "312", "48"])))
        inner = '<div class="pfd-metrics">%s</div><p class="pf-small">Sample figures; the build shows real ones.</p>' % cells
    elif k == "rings":
        rings = "".join('<figure class="pfd-ring" style="--v:%d"><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="52" fill="none" stroke="var(--pf-color-border)" stroke-width="10"/><circle cx="60" cy="60" r="52" fill="none" stroke="var(--pf-color-primary)" stroke-width="10" stroke-linecap="round" pathLength="100" stroke-dasharray="var(--v) 100" transform="rotate(-90 60 60)"/></svg><figcaption><strong>%d%%</strong><span>%s</span></figcaption></figure>' % (v, v, E(f["title"])) for f, v in zip(feats[:3], (72, 48, 90)))
        inner = '<div class="pfd-rings">%s</div>' % rings
    elif k == "progress":
        steps = "".join('<li class="%s"><span class="pfd-index">%02d</span><span>%s</span></li>' % ("is-done" if i < 2 else "", i + 1, E(f["title"])) for i, f in enumerate(feats[:5]))
        inner = '<ol class="pfd-progress">%s</ol>' % steps
    elif k == "phone":
        inner = ('<div class="pfd-phone"><div class="pfd-phone-screen"><div class="pfd-phone-bar"><time data-live-time></time></div><h3>%s</h3><p>%s</p><button class="pf-btn pf-btn-primary" type="button">%s</button></div></div>') % (E(feats[0]["title"]), E(feats[0]["body"]), E(p.copy.get("cta_primary", "Open")))
    elif k == "toc":
        rows = "".join('<li><a href="#">%s</a><span class="pfd-index">%s</span></li>' % (E(f["title"]), E("%d.%d" % (1, i + 1))) for i, f in enumerate(feats[:5]))
        inner = '<div class="pfd-toc-block"><p class="pfd-index">Contents</p><ol>%s</ol></div>' % rows
    elif k == "feed":
        rows = "".join('<li class="pfd-feed-item"><span class="pfd-avatar" aria-hidden="true"></span><div><strong>%s</strong> <span class="pf-muted">%s</span></div><time class="pfd-index">%s</time></li>' % (E(brand(p)), E(f["title"].lower()), E("%dh" % (i + 1))) for i, f in enumerate(feats[:4]))
        inner = '<ol class="pfd-feed">%s</ol>' % rows
    elif k == "schedule":
        rows = "".join('<div class="pfd-sched-row"><time class="pfd-index">%02d:00</time><strong>%s</strong><span class="pf-muted">%s</span></div>' % (10 + i * 2, E(f["title"]), E(_short(f["body"]))) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-sched">%s</div>' % rows
    elif k == "hours":
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        rows = "".join('<div><span>%s</span><span class="pfd-num">%s</span></div>' % (d, "Closed" if i == 6 else "09:00 to 18:00") for i, d in enumerate(days))
        inner = '<div class="pfd-hours"><p class="pfd-index">Opening hours</p>%s<button class="pf-btn pf-btn-primary" type="button">%s</button></div>' % (rows, E(p.copy.get("cta_primary", "Book")))
    elif k == "spec-sheet":
        rows = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (E(f["title"]), E(_short(f["body"]))) for f in feats[:4])
        inner = '<dl class="pfd-spec-sheet">%s</dl>' % rows
    elif k == "itinerary":
        rows = "".join('<li><span class="pfd-index">Day %d</span><strong>%s</strong><span class="pf-muted">%s</span></li>' % (i + 1, E(f["title"]), E(_short(f["body"]))) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-itin">%s<ol>%s</ol></div>' % (art.render("globe", seed=p.id + "-it"), rows)
    else:  # product-window
        inner = art.render("ui_mock", seed=p.id + "-topic")
    return '<section class="pfd-topic pfd-topic-%s" data-section="topic" data-variant="%s">%s</section>' % (E(k), E(k), inner)


def _short(text: str) -> str:
    first = text.split(". ")[0]
    return first if len(first) <= 56 else first[:56].rsplit(" ", 1)[0]
