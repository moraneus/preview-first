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
    if "," in product:
        name, rest = product.split(",", 1)
        return name.strip(), rest.strip()
    if " is " in product:
        name, rest = product.split(" is ", 1)
        return name.strip(), rest.strip()
    return "", product


def default_copy(brief: dict) -> dict:
    """Neutral copy built only from the brief's own words. No lorem ipsum, no filler claims."""
    words = brief.get("words") or {}
    name, rest = _split_product(brief.get("product", ""))
    name = words.get("name") or name or "Your product"
    rest = re.sub(r"^(an?|the)\s+", "", rest, flags=re.I)
    audience = (brief.get("audience") or "").strip().rstrip(".")
    headline = words.get("tagline") or (rest[:1].upper() + rest[1:] if rest else name)
    subhead = ("%s is %s%s." % (name, ("an " if rest[:1].lower() in "aeiou" else "a ") if rest else "", rest)) if rest else "%s, described in one honest sentence." % name
    if audience:
        subhead += " Made for %s." % audience
    page_type = brief.get("page_type", "marketing")
    primary = {"marketing": "Get started", "app": "New item", "content": "Start reading", "store": "Shop the collection"}[page_type]
    secondary = {"marketing": "See how it works", "app": "Import", "content": "Browse the archive", "store": "View all"}[page_type]
    features = [
        {"title": "What it does", "body": subhead.split(" Made for")[0]},
        {"title": "Who it is for", "body": ("Built for %s." % audience) if audience else "Built for the people named in the brief."},
        {"title": "How it works", "body": "Three steps from first visit to the result, each one visible on screen."},
    ]
    return {
        "headline": headline,
        "subhead": subhead,
        "cta_primary": primary,
        "cta_secondary": secondary,
        "nav": {"marketing": ["Product", "Pricing", "About", "Sign in"], "app": ["Overview", "Items", "Reports", "Settings"],
                "content": ["Latest", "Topics", "About", "Subscribe"], "store": ["New", "Collections", "About", "Cart"]}[page_type],
        "features": features,
        "proof": "",
        "form": {"title": "Stay in touch", "fields": ["Email"], "submit": "Subscribe"},
        "footer": "%s. Copy in this draft comes from the brief; replace it with your own." % name,
    }


def render(page_type: str, p) -> str:
    mod = _MODULES.get(page_type, marketing)
    return '<div class="pfd pfd-%s">%s</div>' % (E(page_type), mod.render(p))


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
