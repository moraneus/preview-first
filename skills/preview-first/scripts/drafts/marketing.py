"""Marketing page draft: nav, hero, features, proof, call to action, footer."""
from __future__ import annotations

from ._shared import E, brand, buttons, features, footer, nav, pick, placeholder, section

VARIANTS = {
    "hero": ["split", "centered", "editorial", "product-shot", "poster"],
    "features": ["bento", "list", "alternating", "columns"],
    "proof": ["quote", "logos-text", "stats-sourced", "none"],
    "cta": ["band", "inline", "form"],
    "footer": ["columns", "minimal"],
}


def _hero(p, v: str) -> str:
    c = p.copy
    head = '<h1>%s</h1><p class="pf-lead">%s</p>%s' % (E(c["headline"]), E(c["subhead"]), buttons(p))
    if v == "split":
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, placeholder("Product screenshot", "4 / 3"))
    elif v == "centered":
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, placeholder("Product screenshot", "16 / 9", "pfd-media-wide"))
    elif v == "editorial":
        inner = ('<div class="pfd-hero-text"><p class="pf-kicker">%s</p>%s</div>'
                 '<aside class="pfd-hero-aside"><p class="pf-muted">%s</p></aside>') % (
            E(brand(p)), head, E(p.rationale or p.style.get("summary", "")))
    elif v == "product-shot":
        inner = '%s<div class="pfd-hero-text">%s</div>' % (placeholder("Product screenshot, full width", "21 / 9", "pfd-media-wide"), head)
    else:  # poster
        inner = ('<div class="pfd-hero-text"><h1 class="pfd-poster-title">%s</h1><div class="pfd-poster-row"><p class="pf-lead">%s</p>%s</div></div>') % (
            E(c["headline"]), E(c["subhead"]), buttons(p))
    return section("hero", v, inner)


def _features(p, v: str) -> str:
    feats = features(p)
    if v == "bento":
        cells = "".join('<article class="pf-card pfd-cell%s"><h3>%s</h3><p>%s</p>%s</article>' % (
            " pfd-cell-wide" if i == 0 else "", E(f["title"]), E(f["body"]), placeholder("Capability %d" % (i + 1), "3 / 2") if i < 2 else "")
            for i, f in enumerate(feats))
        inner = '<div class="pfd-bento">%s</div>' % cells
    elif v == "list":
        items = "".join('<li><h3>%s</h3><p>%s</p></li>' % (E(f["title"]), E(f["body"])) for f in feats)
        inner = '<div class="pfd-list-wrap"><h2>What you get</h2><ol class="pfd-list">%s</ol></div>' % items
    elif v == "alternating":
        rows = "".join('<div class="pfd-alt-row%s"><div><h3>%s</h3><p>%s</p></div>%s</div>' % (
            " is-flipped" if i % 2 else "", E(f["title"]), E(f["body"]), placeholder(f["title"], "4 / 3")) for i, f in enumerate(feats[:3]))
        inner = rows
    else:  # columns
        cols = "".join('<div class="pfd-col"><h3>%s</h3><p>%s</p></div>' % (E(f["title"]), E(f["body"])) for f in feats[:3])
        inner = '<div class="pfd-columns">%s</div>' % cols
    return section("features", v, inner)


def _proof(p, v: str) -> str:
    proof = p.copy.get("proof") or ""
    if v == "none":
        return section("proof", v, "")
    if v == "quote":
        inner = '<blockquote class="pfd-quote"><p>%s</p><footer class="pf-muted">%s</footer></blockquote>' % (
            E(proof or "A short, attributed quote from a real customer goes here. Nothing invented."), E("Name, role, company (real, with permission)"))
    elif v == "logos-text":
        inner = '<p class="pf-muted pfd-logos">%s</p>' % E(proof or "Used by teams you can name. Names only, no borrowed logos.")
    else:  # stats-sourced
        inner = ('<dl class="pfd-stats"><div><dt>%s</dt><dd>%s</dd></div></dl>') % (
            E("Sourced figure"), E(proof or "Every number on this page links to where it came from."))
    return section("proof", v, inner)


def _cta(p, v: str) -> str:
    c = p.copy
    if v == "band":
        inner = '<div class="pfd-band"><h2>%s</h2>%s</div>' % (E(c.get("form", {}).get("title") or c["headline"]), buttons(p))
    elif v == "inline":
        inner = '<div class="pfd-inline-cta"><p class="pf-lead">%s</p>%s</div>' % (E(c["subhead"]), buttons(p))
    else:  # form
        form = c.get("form") or {}
        fields = "".join('<label class="pf-field"><span>%s</span><input class="pf-input" type="text"></label>' % E(f) for f in form.get("fields", ["Email"]))
        inner = ('<form class="pfd-form" onsubmit="return false"><h2>%s</h2><div class="pfd-form-row">%s'
                 '<button class="pf-btn pf-btn-primary" type="submit">%s</button></div><p class="pf-small">No spam. Unsubscribe in one click.</p></form>') % (
            E(form.get("title", "Stay in touch")), fields, E(form.get("submit", "Subscribe")))
    return section("cta", v, inner)


def render(p) -> str:
    return "".join([
        nav(p),
        _hero(p, pick(p, "hero", VARIANTS["hero"])),
        _features(p, pick(p, "features", VARIANTS["features"])),
        _proof(p, pick(p, "proof", VARIANTS["proof"])),
        _cta(p, pick(p, "cta", VARIANTS["cta"])),
        footer(p, pick(p, "footer", VARIANTS["footer"])),
    ])
