"""Marketing page draft: nav, hero, features, proof, call to action, footer.

Hero and section variants are layout archetypes observed on admired sites, not the generic
template (centred headline, two buttons, screenshot, three cards). Artwork is generated from
the palette by ``art.py`` so no section ever shows a wireframe placeholder.
"""
from __future__ import annotations

from . import art
from ._shared import E, brand, buttons, features, footer, nav, pick, section

VARIANTS = {
    "hero": ["statement", "mark", "wrap", "product-first", "object", "bleed", "index", "collage", "letter", "split", "editorial", "poster", "centered"],
    "features": ["figures", "spec", "index", "bands", "ledger", "list", "alternating", "bento", "columns"],
    "proof": ["statement", "quote", "logos-text", "stats-sourced", "none"],
    "cta": ["giant", "band", "inline", "form"],
    "footer": ["giant", "columns", "minimal"],
}


def _art(p, slot: str, label: str = "") -> str:
    kind = (p.style.get("art") or {}).get(slot) or ("ui_mock" if slot == "hero" else "figure")
    return art.render(kind, seed="%s-%s" % (p.id, slot), label=label)


def brief_line(p) -> str:
    text = (p.brief.get("audience") or p.brief.get("product", "")).split(",")[0]
    if len(text) <= 48:
        return text
    return text[:48].rsplit(" ", 1)[0]


def _two_tone(headline: str, subhead: str) -> str:
    """A statement paragraph: the headline strong, the continuation in muted text, one block."""
    return '<p class="pfd-statement"><strong>%s</strong> <em>%s</em></p>' % (E(headline), E(subhead))


def _hero(p, v: str) -> str:
    c = p.copy
    name = brand(p)
    head = '<h1>%s</h1><p class="pf-lead">%s</p>%s' % (E(c["headline"]), E(c["subhead"]), buttons(p))
    if v == "statement":
        inner = ('<div class="pfd-hero-statement">%s<a class="pf-link pfd-inline-cta" href="#">%s</a></div>'
                 '<div class="pfd-hero-figures">%s%s%s</div>') % (
            _two_tone(c["headline"], c["subhead"]), E(c["cta_primary"]),
            *('<figure>%s<figcaption>Fig 0.%d</figcaption></figure>' % (
                art.render((p.style.get("art") or {}).get("feature", "figure"), seed="%s-hero-%d" % (p.id, i)), i) for i in (1, 2, 3)))
    elif v == "mark":
        feats = features(p)[:3]
        inner = ('<div class="pfd-hero-text"><h1 class="pfd-h1-mark">%s</h1>%s</div>'
                 '<div class="pfd-hero-mark">%s</div>'
                 '<ul class="pfd-hero-list">%s</ul>') % (
            E(c["headline"]), buttons(p), art.render("mark", seed=p.id), "".join("<li>%s</li>" % E(f["title"]) for f in feats))
    elif v == "wrap":
        words = c["headline"].split()
        half = max(1, len(words) // 2)
        inner = ('<div class="pfd-wrap-stage"><div class="pfd-wrap-disc" aria-hidden="true"></div>'
                 '<h1 class="pfd-wrap-title"><span>%s</span><span class="pfd-wrap-indent">%s</span><span>%s</span></h1></div>'
                 '<div class="pfd-wrap-foot"><p class="pf-lead">%s</p><a class="pf-link" href="#">%s</a></div>') % (
            E(" ".join(words[:half])), E(" ".join(words[half:])), E(name), E(c["subhead"]), E(c["cta_primary"]))
    elif v == "product-first":
        inner = ('<div class="pfd-stage"><div class="pfd-stage-text"><h1>%s</h1><p class="pf-lead">%s</p>%s<p class="pf-small">No credit card needed.</p></div>'
                 '<div class="pfd-stage-ui">%s</div></div>') % (E(c["headline"]), E(c["subhead"]), buttons(p), _art(p, "hero"))
    elif v == "object":
        inner = ('<div class="pfd-hero-text"><span class="pf-badge pf-badge-primary">%s</span><h1 class="pfd-h1-display">%s</h1><p class="pf-lead">%s</p>%s</div>'
                 '<div class="pfd-object">%s</div>') % (E(c.get("proof") or "New: " + features(p)[0]["title"]), E(c["headline"]), E(c["subhead"]), buttons(p), _art(p, "hero"))
    elif v == "bleed":
        inner = ('<div class="pfd-bleed">%s<div class="pfd-bleed-text"><p class="pf-kicker">%s</p><h1>%s</h1><p>%s</p>'
                 '<a class="pf-btn pf-btn-secondary" href="#">%s</a></div></div>') % (_art(p, "hero"), E(name), E(c["headline"]), E(c["subhead"]), E(c["cta_primary"]))
    elif v == "index":
        feats = features(p)
        toc = "".join('<li><a href="#f%d">%s</a><span class="pf-muted">%02d</span></li>' % (i + 1, E(f["title"]), i + 1) for i, f in enumerate(feats))
        inner = ('<aside class="pfd-index-side"><span class="pf-wordmark">%s</span><p class="pf-small">%s</p><ol class="pfd-index-toc">%s</ol></aside>'
                 '<div class="pfd-index-main"><h1>%s</h1><p class="pf-lead">%s</p>%s%s</div>') % (
            E(name), E(c["subhead"]), toc, E(c["headline"]), E(features(p)[0]["body"]), buttons(p), _art(p, "hero"))
    elif v == "collage":
        feats = features(p)
        kinds = ["figure", "mark", "contours", "halftone", "swiss", "figure"]
        items = "".join('<div class="pfd-collage-item" style="--x:%d%%;--y:%d%%;--w:%dpx;--r:%ddeg">%s</div>' % (
            x, y, w_, r_, art.render(kinds[i % len(kinds)], seed="%s-col%d" % (p.id, i)))
            for i, (x, y, w_, r_) in enumerate([(4, 8, 180, -6), (72, 6, 220, 4), (82, 58, 160, -3), (10, 62, 200, 5), (46, 70, 150, -8)]))
        inner = ('<div class="pfd-collage">%s<div class="pfd-collage-center"><span class="pfd-collage-word">%s</span><p class="pf-lead">%s</p>'
                 '<a class="pf-link" href="#">%s</a></div></div>'
                 '<div class="pfd-corner pfd-corner-bl">%s</div><div class="pfd-corner pfd-corner-br">%s</div>') % (
            items, E(name), E(c["subhead"]), E(c["cta_primary"]), E(brief_line(p)), E("Local time 10:18"))
    elif v == "letter":
        feats = features(p)
        paras = "".join("<p>%s %s</p>" % (E(f["title"]) + ".", E(f["body"])) for f in feats[:3])
        inner = ('<article class="pfd-letter"><p class="pf-kicker">%s</p><h1>%s</h1><p class="pfd-letter-lead">%s</p>%s'
                 '<p class="pfd-letter-sign">%s</p><a class="pf-link" href="#">%s</a></article>') % (
            E("30 October 2026"), E(c["headline"]), E(c["subhead"]), paras, E("The %s team" % name), E(c["cta_primary"]))
    elif v == "split":
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, _art(p, "hero"))
    elif v == "editorial":
        inner = ('<div class="pfd-hero-text"><p class="pf-kicker">%s</p>%s</div>'
                 '<aside class="pfd-hero-aside">%s<p class="pf-muted">%s</p></aside>') % (
            E(name), head, _art(p, "feature"), E(p.rationale or p.style.get("summary", "")))
    elif v == "poster":
        inner = ('<div class="pfd-hero-text"><h1 class="pfd-poster-title">%s</h1><div class="pfd-poster-row"><p class="pf-lead">%s</p>%s</div></div>%s') % (
            E(c["headline"]), E(c["subhead"]), buttons(p), _art(p, "hero"))
    else:  # centered, kept for briefs that ask for it
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, _art(p, "hero"))
    return section("hero", v, inner)


def _features(p, v: str) -> str:
    feats = features(p)
    if v == "figures":
        cells = "".join('<figure class="pfd-fig" id="f%d">%s<figcaption><span class="pfd-fig-no">Fig %d.%d</span><h3>%s</h3><p>%s</p></figcaption></figure>' % (
            i + 1, art.render((p.style.get("art") or {}).get("feature", "figure"), seed="%s-fig-%d" % (p.id, i + 4)), 1, i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats[:3]))
        inner = '<div class="pfd-figures">%s</div>' % cells
    elif v == "spec":
        rows = "".join('<div class="pfd-spec-row" id="f%d"><dt>%s</dt><dd>%s</dd><span class="pfd-spec-no">%02d</span></div>' % (i + 1, E(f["title"]), E(f["body"]), i + 1) for i, f in enumerate(feats))
        inner = '<div class="pfd-spec"><h2>Specification</h2><dl class="pfd-spec-list">%s</dl></div>' % rows
    elif v == "index":
        items = "".join('<li id="f%d"><h3>%s</h3><p>%s</p></li>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-index-grid"><div class="pfd-index-art">%s</div><ol class="pfd-index-list">%s</ol></div>' % (_art(p, "feature"), items)
    elif v == "bands":
        inner = "".join('<div class="pfd-band-row%s" id="f%d"><div><h3>%s</h3><p>%s</p></div>%s</div>' % (
            " is-accent" if i % 2 else "", i + 1, E(f["title"]), E(f["body"]), art.render((p.style.get("art") or {}).get("feature", "figure"), seed="%s-band%d" % (p.id, i))) for i, f in enumerate(feats[:3]))
    elif v == "ledger":
        rows = "".join('<a class="pfd-ledger-row" href="#f%d" id="f%d"><span class="pfd-ledger-title">%s</span><span class="pfd-ledger-thumbs">%s</span>'
                       '<span class="pfd-ledger-count">(%d)</span><span class="pfd-ledger-year">2026</span></a>' % (
            i + 1, i + 1, E(f["title"]), "".join(art.render("figure", seed="%s-led%d%d" % (p.id, i, j)) for j in range(1 + i % 3)), 3 + i * 4)
            for i, f in enumerate(feats))
        inner = '<div class="pfd-ledger"><h2>What you get <span class="pfd-ledger-count">(%d)</span></h2>%s</div>' % (len(feats), rows)
    elif v == "list":
        items = "".join('<li id="f%d"><h3>%s</h3><p>%s</p></li>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-list-wrap"><h2>What you get</h2><ol class="pfd-list">%s</ol></div>' % items
    elif v == "alternating":
        inner = "".join('<div class="pfd-alt-row%s" id="f%d"><div><h3>%s</h3><p>%s</p></div>%s</div>' % (
            " is-flipped" if i % 2 else "", i + 1, E(f["title"]), E(f["body"]), art.render((p.style.get("art") or {}).get("feature", "figure"), seed="%s-alt%d" % (p.id, i))) for i, f in enumerate(feats[:3]))
    elif v == "bento":
        cells = "".join('<article class="pf-card pfd-cell%s" id="f%d"><h3>%s</h3><p>%s</p>%s</article>' % (
            " pfd-cell-wide" if i == 0 else "", i + 1, E(f["title"]), E(f["body"]),
            art.render((p.style.get("art") or {}).get("feature", "figure"), seed="%s-cell%d" % (p.id, i)) if i < 2 else "") for i, f in enumerate(feats))
        inner = '<div class="pfd-bento">%s</div>' % cells
    else:  # columns
        cols = "".join('<div class="pfd-col" id="f%d"><h3>%s</h3><p>%s</p></div>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats[:3]))
        inner = '<div class="pfd-columns">%s</div>' % cols
    return section("features", v, inner)


def _proof(p, v: str) -> str:
    proof = p.copy.get("proof") or ""
    if v == "none":
        return section("proof", v, "")
    if v == "statement":
        inner = _two_tone(proof or p.copy["headline"], "" if proof else p.copy["subhead"])
    elif v == "quote":
        inner = '<blockquote class="pfd-quote"><p>%s</p><footer class="pf-muted">%s</footer></blockquote>' % (
            E(proof or "A short, attributed quote from a real customer goes here. Nothing invented."), E("Name, role, company (real, with permission)"))
    elif v == "logos-text":
        if not proof:
            return section("proof", v, "")
        inner = '<p class="pf-muted pfd-logos">%s</p>' % E(proof)
    else:  # stats-sourced
        inner = '<dl class="pfd-stats"><div><dt>%s</dt><dd>%s</dd></div></dl>' % (E("Sourced figure"), E(proof or "Every number on this page links to where it came from."))
    return section("proof", v, inner)


def _cta(p, v: str) -> str:
    c = p.copy
    if v == "giant":
        inner = ('<div class="pfd-giant"><p class="pf-lead">%s</p>%s<span class="pfd-giant-word" aria-hidden="true">%s</span></div>') % (
            E(c.get("form", {}).get("title") or c["headline"]), buttons(p), E(brand(p)))
    elif v == "band":
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
