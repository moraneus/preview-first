"""Drafted pages per page type, each section with several layout variants, plus the devices view.

``render(page_type, prepared)`` and ``render_devices(prepared, devices)`` return HTML fragments
that build_preview wraps in the preview shell. ``default_copy(brief)`` supplies honest neutral
copy derived from the brief when Claude has not written any.
"""
from __future__ import annotations

import html
import re
from typing import Dict, List

from . import app, content, marketing, store
from ._shared import E, section

PAGE_TYPES = ["marketing", "app", "content", "store"]
_MODULES = {"marketing": marketing, "app": app, "content": content, "store": store}
VARIANTS: Dict[str, Dict[str, List[str]]] = {name: mod.VARIANTS for name, mod in _MODULES.items()}


def _split_product(product: str):
    product = (product or "").strip().rstrip(".")
    m = re.match(r"^([^,:]{1,40}?)\s+is\s+(.+)$", product)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.match(r"^([^,:]{1,40}?),\s*(.+)$", product)
    if m and re.match(r"^(an?|the)\s", m.group(2), flags=re.I):
        return m.group(1).strip(), m.group(2).strip()
    return "", product


def _things(rest: str):
    """Pull the product's own nouns out of the description: the items after 'for', 'with', 'of' or a
    colon, split on commas and 'and'. 'keeps live scores for 501, Cricket and Around the Clock games'
    gives ['501', 'Cricket', 'Around the Clock games'] and the verb phrase 'keeps live scores for'."""
    m = re.search(r"\b(that|which|to)\s+([a-z][^,:]*?\b(?:for|with|of|across|between)\b)\s+(.+)$", rest, flags=re.I)
    m2 = re.search(r"\b(that|which)\s+(\w+)\s+(.+?)\s+for\s+(.+)$", rest, flags=re.I)
    verb, tail = "", None
    if m2 and ("," in m2.group(3) or " and " in m2.group(3)):
        verb, tail = m2.group(2) + " %s for " + m2.group(4), m2.group(3)  # 'makes %s for music labels'
    elif m:
        verb, tail = m.group(2).strip(), m.group(3)
    elif ":" in rest:
        tail = rest.split(":", 1)[1]
    if tail is None:
        return "", []
    parts = [x.strip(" .") for x in re.split(r",\s*|\s+and\s+|\s+or\s+", tail) if x.strip(" .")]
    parts = [x for x in parts if 1 <= len(x.split()) <= 5]
    return (verb, parts[:6]) if len(parts) >= 2 else ("", [])


def default_copy(brief: dict) -> dict:
    """Copy built only from the brief's own words: the product's nouns become the navigation and
    the sections, the description becomes the sentences. No lorem ipsum, no invented claims, no
    'what it does' furniture."""
    words = brief.get("words") or {}
    name, rest = _split_product(brief.get("product", ""))
    name = words.get("name") or name or "Your product"
    rest = re.sub(r"^(an?|the)\s+", "", rest, flags=re.I)
    audience = (brief.get("audience") or "").strip().rstrip(".")
    moods = [m.split(".")[-1].replace("-", " ") for m in (brief.get("moods") or [])]
    verb, things = _things(rest)
    headline = words.get("tagline") or (rest[:1].upper() + rest[1:] if rest else name)
    article = ("an " if rest[:1].lower() in "aeiou" else "a ") if rest else ""
    subhead = ("%s is %s%s." % (name, article, rest)) if rest else "%s, in one sentence." % name
    lead = ("Made for %s." % audience) if audience else subhead
    statement = subhead + ((" We built it for %s." % audience) if audience else "")
    if moods:
        statement += " It should feel %s." % (", ".join(moods[:-1]) + " and " + moods[-1] if len(moods) > 1 else moods[0])
    page_type = brief.get("page_type", "marketing")
    primary = words.get("cta") or {"marketing": "Get started", "app": "New", "content": "Start reading", "store": "Shop"}[page_type]
    secondary = {"marketing": "See it in use", "app": "Import", "content": "Browse the archive", "store": "View all"}[page_type]
    if things:
        features = []
        for t in things:
            title = t[:1].upper() + t[1:]
            if verb and "%s" in verb:
                body = "%s %s." % (name, verb % t)
            elif verb:
                body = "%s %s %s." % (name, verb, t)
            else:
                body = ("%s from %s." % (title, name)) if page_type == "store" else ("%s, part of %s." % (title, name))
            features.append({"title": title, "body": body})
        while len(features) < 3:
            features.append({"title": "Made for %s" % audience if audience else name, "body": lead})
        nav = [f["title"] for f in features[:3]] + ["About"]
    else:
        features = [
            {"title": name, "body": subhead},
            {"title": ("For %s" % audience) if audience else "Who it is for", "body": lead},
            {"title": "Start today", "body": "The first visit ends with a result on screen."},
        ]
        nav = {"marketing": ["Product", "Pricing", "About", "Sign in"], "app": ["Overview", "Items", "Reports", "Settings"],
               "content": ["Latest", "Topics", "About", "Subscribe"], "store": ["New", "Collections", "About", "Cart"]}[page_type]
    if page_type == "app" and things:
        nav = [f["title"] for f in features[:3]] + ["Settings"]
    return {
        "headline": headline,
        "subhead": subhead,
        "lead": lead,
        "statement": statement,
        "cta_primary": primary,
        "cta_secondary": secondary,
        "cta_line": "Start with %s today." % name,
        "nav": nav,
        "features": features,
        "proof": "",
        "meta": {"city": "", "year": "2026"},
        "form": {"title": "Stay in touch", "fields": ["Email"], "submit": "Subscribe"},
        "footer": "%s. Draft copy comes from the brief; replace it with your own." % name,
    }


def render(page_type: str, p) -> str:
    mod = _MODULES.get(page_type, marketing)
    hooks = sorted(getattr(p, "hooks", set()) or [])
    classes = " ".join("pfd-hook-%s" % E(h) for h in hooks)
    extras = ""
    if "texture-grain" in hooks:
        extras += '<div class="pfd-grain" aria-hidden="true"></div>'
    if "texture-scanlines" in hooks:
        extras += '<div class="pfd-scanlines" aria-hidden="true"></div>'
    if "motion-scroll-progress" in hooks:
        extras += '<div class="pfd-progress" aria-hidden="true" data-progress></div>'
    if "motion-preloader" in hooks:
        extras += '<div class="pfd-preloader" data-preloader aria-hidden="true"><span class="pfd-preloader-count">0</span></div>'
    if "motion-cursor" in hooks:
        extras += '<div class="pfd-cursor-dot" data-cursor-dot aria-hidden="true"></div><div class="pfd-cursor-ring" data-cursor-ring aria-hidden="true"></div>'
    return '<div class="pfd pfd-%s %s" data-hooks="%s">%s%s</div>' % (E(page_type), classes, E(" ".join(hooks)), extras, mod.render(p))


# ---------------------------------------------------------------- devices view

def render_devices(p, devices: List[dict]) -> str:
    devices = sorted(devices, key=lambda d: (d.get("share_rank", 999), d["id"]))
    vendors: Dict[str, List[dict]] = {}
    for d in devices:
        vendors.setdefault(d["vendor"], []).append(d)
    checklist = "".join(
        '<fieldset class="pf-device-vendor"><legend>%s</legend>%s</fieldset>' % (
            E(vendor), "".join(
                '<label><input type="checkbox" data-device-id="%s"%s><span>%s</span></label>' % (
                    E(d["id"]), " checked" if d.get("default") else "", E(d["model"])) for d in items))
        for vendor, items in vendors.items()
    )
    figures = []
    for d in devices:
        vp = d["viewport"]
        sa = d.get("safe_area", {})
        fold = d.get("fold") or {}
        figures.append(
            '<figure class="pf-device" %sdata-device-id="%s" data-kind="%s" data-cutout="%s" data-w="%d" data-h="%d" data-crease="%s" data-rotated="0" '
            'style="--corner:%spx;--sa-top:%s;--sa-bottom:%s;--sa-left:%s;--sa-right:%s">'
            '<div class="pf-device-shell"><div class="pf-screen"><iframe title="%s %s"></iframe>'
            '<div class="pf-safe" aria-hidden="true"></div>%s</div>%s</div>'
            '<figcaption><strong>%s %s</strong><span><span data-viewport>%d × %d</span> · %s× · %s%s</span>'
            '<button class="pf-btn pf-btn-secondary pf-btn-sm" type="button" data-action="rotate">Rotate</button></figcaption></figure>'
            % ("" if d.get("default") else "hidden ", E(d["id"]), E(d["kind"]), E(d.get("cutout", "none")), vp["w"], vp["h"],
               "1" if fold.get("crease") else "0", d.get("corner_radius", 0), sa.get("top", 0), sa.get("bottom", 0), sa.get("left", 0), sa.get("right", 0),
               E(d["vendor"]), E(d["model"]), '<div class="pf-crease" aria-hidden="true"></div>' if fold.get("crease") else "",
               '<div class="pf-device-base" aria-hidden="true"></div>' if d["kind"] in ("laptop", "desktop") else "",
               E(d["vendor"]), E(d["model"]), vp["w"], vp["h"], E(str(d.get("dpr", 1))), E(d.get("year") and str(d["year"]) or "generic"),
               "" if d.get("verified") else " · viewport unverified")
        )
    toolbar = (
        '<div class="pf-device-toolbar">'
        '<form class="pf-device-urlform"><label class="pf-field"><span>Preview another page in these frames</span>'
        '<input class="pf-input" type="url" data-device-url placeholder="http://localhost:3000"></label>'
        '<button class="pf-btn pf-btn-secondary" type="submit">Load</button></form>'
        '<p class="pf-device-url-notice pf-alert pf-alert-warning" hidden>That page did not load inside a frame within five seconds. '
        'Sites that send X-Frame-Options or a frame-ancestors policy cannot be shown here.</p>'
        '<div class="pf-row"><label class="pf-check"><input type="checkbox" data-control="safe-area"><span>Show safe areas</span></label>'
        '<button class="pf-btn pf-btn-quiet pf-btn-sm" type="button" data-action="devices-all">Show all</button>'
        '<button class="pf-btn pf-btn-quiet pf-btn-sm" type="button" data-action="devices-none">Hide all</button></div>'
        '<details class="pf-device-picker"><summary>Choose devices (%d of %d shown)</summary><div class="pf-device-vendors">%s</div></details>'
        '</div>' % (sum(1 for d in devices if d.get("default")), len(devices), checklist)
    )
    intro = ('<section class="pf-tile-intro"><p class="pf-kicker">Direction %s</p><h1>%s on real screens</h1>'
             '<p class="pf-lead">The drafted page at each device\'s true CSS viewport, scaled to fit, with cutouts, home indicators and fold creases drawn to size. '
             'Ranked by current market share; uncheck or add devices below.</p></section>' % (E(p.id), E(p.name)))
    return intro + '<section class="pf-tile-section" data-section="devices">%s<div class="pf-devices">%s</div></section>' % (toolbar, "".join(figures))
