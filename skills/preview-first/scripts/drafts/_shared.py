"""Shared building blocks for drafted pages."""
from __future__ import annotations

import html
from typing import List

E = html.escape


def section(name: str, variant: str, inner: str, extra_class: str = "") -> str:
    return '<section class="pfd-%s pfd-%s-%s %s" data-section="%s" data-variant="%s">%s</section>' % (
        E(name), E(name), E(variant), E(extra_class), E(name), E(variant), inner)


def pick(p, section_name: str, variants: List[str]) -> str:
    v = (p.layout or {}).get(section_name)
    return v if v in variants else variants[0]


def brand(p) -> str:
    return (p.brief.get("words") or {}).get("name") or p.copy.get("headline", p.name).split(" ")[0]


def nav(p, links: List[str] = None) -> str:
    links = links or p.copy.get("nav", [])
    items = "".join('<a href="#">%s</a>' % E(x) for x in links[:5])
    return ('<nav class="pf-nav pfd-nav" aria-label="Main"><span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div>'
            '<button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button></nav>') % (E(brand(p)), items, E(p.copy.get("cta_primary", "Start")))


def placeholder(label: str, ratio: str = "16 / 10", cls: str = "") -> str:
    """An honest image placeholder: a labelled surface, never a fake photo or logo."""
    return ('<div class="pfd-media %s" style="aspect-ratio:%s" role="img" aria-label="%s">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4zM4 15l5-5 4 4 3-3 4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>'
            '<span>%s</span></div>') % (E(cls), E(ratio), E(label), E(label))


def buttons(p, size: str = "") -> str:
    return ('<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary %s" type="button">%s</button>'
            '<a class="pf-btn pf-btn-secondary %s" href="#">%s</a></div>') % (
        size, E(p.copy.get("cta_primary", "Get started")), size, E(p.copy.get("cta_secondary", "Learn more")))


def footer(p, variant: str) -> str:
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
