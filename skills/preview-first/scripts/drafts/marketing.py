"""Marketing page draft: nav, hero, features, proof, call to action, footer.

Hero and section variants are layout archetypes observed on admired sites, not the generic
template. Design ideas attached to a direction switch on render hooks (see `_shared.has`) that
change the navigation, add textures and marquees, choose section archetypes, decorate the
headline and pick artwork. Artwork is generated from the palette by ``art.py``.
"""
from __future__ import annotations

from . import art
from ._shared import (E, block_classes, brand, buttons, caption, explicit, features, footer, has, headline, index_label,
                      marquee, meta, nav, pick, section, stickers, vlabel, with_class)

VARIANTS = {
    "nav": ["bar", "split-meta", "menu-word", "pill", "rail"],
    "hero": ["statement", "mark", "wrap", "product-first", "object", "bleed", "index", "collage", "letter", "split", "editorial", "poster",
             "ticker", "specimen", "manifesto", "numbers", "clip", "stacked", "centered"],
    "features": ["figures", "spec", "index", "bands", "ledger", "numerals", "stack", "strip", "hover-list", "cells", "accordion", "list", "alternating", "bento", "columns"],
    "proof": ["statement", "quote", "giant-quote", "stat-wall", "logos-text", "stats-sourced", "none"],
    "cta": ["giant", "band", "inline", "form", "ticket"],
    "footer": ["giant", "columns", "minimal", "colophon"],
}
HERO_HOOKS = {"hero-ticker": "ticker", "hero-specimen": "specimen", "hero-manifesto": "manifesto", "hero-numbers": "numbers", "hero-clip": "clip", "hero-stacked": "stacked"}
FEATURE_HOOKS = {"features-numerals": "numerals", "features-stack": "stack", "features-strip": "strip", "features-hover-list": "hover-list",
                 "features-cells": "cells", "features-accordion": "accordion"}
PROOF_HOOKS = {"proof-giant-quote": "giant-quote", "proof-stat-wall": "stat-wall"}
CTA_HOOKS = {"cta-ticket": "ticket"}
FOOTER_HOOKS = {"footer-colophon": "colophon"}
ART_HOOKS = {"image-ascii": "ascii", "image-dither": "dither"}


def _art_kind(p, slot: str) -> str:
    for hook, kind in ART_HOOKS.items():
        if has(p, hook) and slot == "hero":
            return kind
    return (p.style.get("art") or {}).get(slot) or ("ui_mock" if slot == "hero" else "figure")


def _art(p, slot: str, label: str = "", n: int = 0) -> str:
    kind = _art_kind(p, slot)
    svg = art.render(kind, seed="%s-%s%s" % (p.id, slot, n or ""), label=label)
    if has(p, "image-duotone"):
        svg = svg.replace('<svg class="pfd-art ', '<svg class="pfd-art pfd-duotone ', 1)
    cap = caption(p, n, label) if label and n else ""
    return '<figure class="pfd-figure">%s%s</figure>' % (svg, cap) if cap else svg


def _feature_art(p, i: int, label: str = "") -> str:
    kind = (p.style.get("art") or {}).get("feature", "figure")
    return art.render(kind, seed="%s-f%d" % (p.id, i), label=label)


def _meta_line(text: str) -> str:
    """A short meta phrase for list rows: the first clause, cut at a word boundary, no dangling fragment."""
    first = text.split(". ")[0].split(", ")[0].split(";")[0].rstrip(".")
    if len(first) <= 44:
        return first
    return first[:44].rsplit(" ", 1)[0]


def brief_line(p) -> str:
    text = (p.brief.get("audience") or p.brief.get("product", "")).split(",")[0]
    if len(text) <= 48:
        return text
    return text[:48].rsplit(" ", 1)[0]


def _two_tone(headline_text: str, subhead: str) -> str:
    return '<p class="pfd-statement"><strong>%s</strong> <em>%s</em></p>' % (E(headline_text), E(subhead))


def _lead(p) -> str:
    return E(p.copy.get("lead") or p.copy["subhead"])


# ---------------------------------------------------------------- hero

def _hero(p, v: str) -> str:
    c = p.copy
    name = brand(p)
    head = '%s<p class="pf-lead">%s</p>%s' % (headline(p, c["headline"]), _lead(p), buttons(p))
    feats = features(p)
    if v == "statement":
        figs = "".join('<figure>%s<figcaption>%s</figcaption></figure>' % (_feature_art(p, i), index_label(p, i, prefix="Fig 0.")) for i in (1, 2, 3))
        inner = ('<div class="pfd-hero-statement">%s<a class="pf-link pfd-inline-cta" href="#">%s</a></div>'
                 '<div class="pfd-hero-figures">%s</div>') % (_two_tone(c["headline"], c["subhead"]), E(c["cta_primary"]), figs)
    elif v == "mark":
        inner = ('<div class="pfd-hero-text">%s%s</div><div class="pfd-hero-mark">%s</div><ul class="pfd-hero-list">%s</ul>') % (
            headline(p, c["headline"], "pfd-h1-mark"), buttons(p), art.render("mark", seed=p.id), "".join("<li>%s</li>" % E(f["title"]) for f in feats[:3]))
    elif v == "wrap":
        words = c["headline"].split()
        half = max(1, len(words) // 2)
        inner = ('<div class="pfd-wrap-stage"><div class="pfd-wrap-disc" aria-hidden="true"></div>'
                 '<h1 class="pfd-wrap-title"><span>%s</span><span class="pfd-wrap-indent">%s</span><span>%s</span></h1></div>'
                 '<div class="pfd-wrap-foot"><p class="pf-lead">%s</p><a class="pf-link" href="#">%s</a></div>') % (
            E(" ".join(words[:half])), E(" ".join(words[half:])), E(name), _lead(p), E(c["cta_primary"]))
    elif v == "product-first":
        inner = ('<div class="pfd-stage"><div class="pfd-stage-text">%s<p class="pf-lead">%s</p>%s<p class="pf-small">%s</p></div>'
                 '<div class="pfd-stage-ui">%s</div></div>') % (headline(p, c["headline"]), _lead(p), buttons(p), E(c.get("note") or "No credit card needed."), _art(p, "hero"))
    elif v == "object":
        inner = ('<div class="pfd-hero-text"><span class="pf-badge pf-badge-primary">%s</span>%s<p class="pf-lead">%s</p>%s</div>'
                 '<div class="pfd-object">%s%s</div>') % (
            E(c.get("proof") or "%s \u00b7 %s" % (meta(p)["year"], name)), headline(p, c["headline"], "pfd-h1-display"), _lead(p), buttons(p), _art(p, "hero"), stickers(p))
    elif v == "bleed":
        inner = ('<div class="pfd-bleed">%s<div class="pfd-bleed-text"><p class="pf-kicker">%s</p>%s<p>%s</p>'
                 '<a class="pf-btn pf-btn-secondary" href="#">%s</a></div></div>') % (_art(p, "hero"), E(name), headline(p, c["headline"]), _lead(p), E(c["cta_primary"]))
    elif v == "index":
        toc = "".join('<li><a href="#f%d">%s</a>%s</li>' % (i + 1, E(f["title"]), index_label(p, i + 1)) for i, f in enumerate(feats))
        inner = ('<aside class="pfd-index-side"><span class="pf-wordmark">%s</span><p class="pf-small">%s</p><ol class="pfd-index-toc">%s</ol></aside>'
                 '<div class="pfd-index-main">%s<p class="pf-lead">%s</p>%s%s</div>') % (
            E(name), _lead(p), toc, headline(p, c["headline"]), E(feats[0]["body"]), buttons(p), _art(p, "hero"))
    elif v == "collage":
        kinds = ["figure", "mark", "contours", "halftone", "swiss", "stamp"]
        items = "".join('<div class="pfd-collage-item" style="--x:%d%%;--y:%d%%;--w:%dpx;--r:%ddeg">%s</div>' % (
            x, y, w_, r_, art.render(kinds[i % len(kinds)], seed="%s-col%d" % (p.id, i)))
            for i, (x, y, w_, r_) in enumerate([(4, 8, 180, -6), (72, 6, 220, 4), (82, 58, 160, -3), (10, 62, 200, 5), (46, 70, 150, -8)]))
        inner = ('<div class="pfd-collage">%s<div class="pfd-collage-center"><span class="pfd-collage-word">%s</span><p class="pf-lead">%s</p>'
                 '<a class="pf-link" href="#">%s</a></div></div>'
                 '<div class="pfd-corner pfd-corner-bl">%s</div><div class="pfd-corner pfd-corner-br"><time data-live-time>Local time</time></div>') % (
            items, E(name), _lead(p), E(c["cta_primary"]), E(brief_line(p)))
    elif v == "letter":
        paras = "".join("<p>%s %s</p>" % (E(f["title"]) + ".", E(f["body"])) for f in feats[:3])
        inner = ('<article class="pfd-letter"><p class="pf-kicker">%s</p>%s<p class="pfd-letter-lead">%s</p>%s'
                 '<p class="pfd-letter-sign">%s</p><a class="pf-link" href="#">%s</a></article>') % (
            E("30 October 2026"), headline(p, c["headline"]), E(c["subhead"]), paras, E("The %s team" % name), E(c["cta_primary"]))
    elif v == "ticker":
        inner = ('<div class="pfd-ticker" aria-label="%s"><div class="pfd-ticker-track"><span>%s</span><span>%s</span><span>%s</span><span>%s</span></div></div>'
                 '<div class="pfd-ticker-foot"><p class="pf-lead">%s</p><a class="pf-link" href="#">%s</a></div>') % (
            E(c["headline"]), E(name), E(name), E(name), E(name), E(c["headline"] + ". " + c["subhead"]), E(c["cta_primary"]))
    elif v == "specimen":
        face = p.pairing["heading"]["family"]
        inner = ('<div class="pfd-specimen"><div class="pfd-specimen-meta"><span>%s</span><span>Display</span><span>%s</span><time data-live-time></time></div>'
                 '%s<div class="pfd-specimen-row"><span class="pfd-specimen-nums">0123456789</span><p class="pf-lead">%s</p></div>'
                 '<div class="pfd-specimen-meta"><span>%s</span><span>%s</span><a class="pf-link" href="#">%s</a></div></div>') % (
            E(face), E(meta(p)["year"]), headline(p, c["headline"], "pfd-h1-specimen"), _lead(p), E(name), E(brief_line(p)), E(c["cta_primary"]))
    elif v == "manifesto":
        text = c.get("statement") or ("%s %s" % (c["headline"].rstrip(".") + ".", c["subhead"]))
        inner = ('<div class="pfd-manifesto"><p class="pf-kicker">%s</p><p class="pfd-manifesto-text%s">%s <a class="pf-link" href="#">%s</a></p></div>') % (
            E(name), " pfd-reveal" if has(p, "motion-line-reveal") else "", E(text), E(c["cta_primary"]))
    elif v == "numbers":
        nums = c.get("numbers") or []
        if len(nums) >= 3:
            cells = "".join('<div><span class="pfd-big-num" data-count="%s">%s</span><span class="pfd-caption">%s</span></div>' % (
                E(str(n.get("value", ""))), E(str(n.get("value", ""))), E(n.get("label", ""))) for n in nums[:3])
            inner = '<div class="pfd-numbers">%s</div><div class="pfd-numbers-foot">%s%s</div>' % (cells, headline(p, c["headline"], "pfd-h1-small"), buttons(p))
        else:  # no sourced figures in the copy: show the statement composition so nothing is invented
            return _hero(p, "statement").replace('data-variant="statement"', 'data-variant="numbers"', 1)
    elif v == "clip":
        inner = ('<div class="pfd-clip"><span class="pfd-clip-word" aria-hidden="true">%s</span></div>'
                 '<div class="pfd-clip-foot">%s<p class="pf-lead">%s</p>%s</div>') % (E(name), headline(p, c["headline"], "pfd-h1-small"), _lead(p), buttons(p))
    elif v == "stacked":
        words = c["headline"].split()
        lines = []
        step = max(1, (len(words) + 2) // 3)
        for i in range(0, len(words), step):
            lines.append(" ".join(words[i:i + step]))
        spans = "".join('<span class="%s">%s</span>' % ("pfd-outline" if i % 2 else "", E(l)) for i, l in enumerate(lines[:4]))
        inner = ('<h1 class="pfd-stacked%s">%s</h1><div class="pfd-stacked-foot"><p class="pf-lead">%s</p>%s</div>') % (
            " pfd-reveal" if has(p, "motion-line-reveal") else "", spans, _lead(p), buttons(p))
    elif v == "split":
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, _art(p, "hero"))
    elif v == "editorial":
        inner = ('<div class="pfd-hero-text"><p class="pf-kicker">%s</p>%s</div>'
                 '<aside class="pfd-hero-aside">%s<p class="pf-muted">%s</p></aside>') % (
            E(name), head, _feature_art(p, 0), E(p.rationale or p.style.get("summary", "")))
    elif v == "poster":
        inner = ('<div class="pfd-hero-text">%s<div class="pfd-poster-row"><p class="pf-lead">%s</p>%s</div></div>%s') % (
            headline(p, c["headline"], "pfd-poster-title"), _lead(p), buttons(p), _art(p, "hero"))
    else:  # centered, kept for briefs that ask for it
        inner = '<div class="pfd-hero-text">%s</div>%s' % (head, _art(p, "hero"))
    return section("hero", v, vlabel(p, "Introduction") + inner)


# ---------------------------------------------------------------- features

def _features(p, v: str) -> str:
    feats = features(p)
    n = len(feats)
    if v == "figures":
        cells = "".join('<figure class="pfd-fig" id="f%d">%s<figcaption><span class="pfd-fig-no">%s</span><h3>%s</h3><p>%s</p></figcaption></figure>' % (
            i + 1, _feature_art(p, i + 4), "Fig 1.%d" % (i + 1), E(f["title"]), E(f["body"])) for i, f in enumerate(feats[:3]))
        inner = '<div class="pfd-figures">%s</div>' % cells
    elif v == "spec":
        rows = "".join('<div class="pfd-spec-row" id="f%d"><dt>%s</dt><dd>%s</dd><span class="pfd-spec-no">%02d</span></div>' % (i + 1, E(f["title"]), E(f["body"]), i + 1) for i, f in enumerate(feats))
        inner = '<div class="pfd-spec"><h2>Specification</h2><dl class="pfd-spec-list">%s</dl></div>' % rows
    elif v == "index":
        items = "".join('<li id="f%d"><h3>%s</h3><p>%s</p></li>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-index-grid"><div class="pfd-index-art">%s</div><ol class="pfd-index-list">%s</ol></div>' % (_art(p, "feature"), items)
    elif v == "bands":
        inner = "".join('<div class="pfd-band-row%s" id="f%d"><div><h3>%s</h3><p>%s</p></div>%s</div>' % (
            " is-accent" if i % 2 else "", i + 1, E(f["title"]), E(f["body"]), _feature_art(p, i + 10)) for i, f in enumerate(feats[:3]))
    elif v == "ledger":
        rows = "".join('<a class="pfd-ledger-row" href="#f%d" id="f%d"><span class="pfd-ledger-title">%s</span><span class="pfd-ledger-thumbs">%s</span>'
                       '<span class="pfd-ledger-count">(%d)</span><span class="pfd-ledger-year">2026</span></a>' % (
            i + 1, i + 1, E(f["title"]), "".join(art.render("figure", seed="%s-led%d%d" % (p.id, i, j)) for j in range(1 + i % 3)), 3 + i * 4)
            for i, f in enumerate(feats))
        inner = '<div class="pfd-ledger"><h2>What you get <span class="pfd-ledger-count">(%d)</span></h2>%s</div>' % (n, rows)
    elif v == "numerals":
        rows = "".join('<div class="pfd-numeral-row" id="f%d"><span class="pfd-numeral" aria-hidden="true">%02d</span><div><h3>%s</h3><p>%s</p></div></div>' % (
            i + 1, i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-numerals">%s</div>' % rows
    elif v == "stack":
        cards = "".join('<article class="pfd-stack-card" id="f%d" style="--i:%d"><div class="pfd-stack-text">%s<h3>%s</h3><p>%s</p></div>%s</article>' % (
            i + 1, i, index_label(p, i + 1, n), E(f["title"]), E(f["body"]), _feature_art(p, i + 20)) for i, f in enumerate(feats[:4]))
        inner = '<div class="pfd-stack">%s</div>' % cards
    elif v == "strip":
        cards = "".join('<article class="pfd-strip-card" id="f%d">%s<h3>%s</h3><p>%s</p></article>' % (
            i + 1, _feature_art(p, i + 30), E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-strip-head"><h2>What you get</h2><span class="pfd-index">%02d / %02d</span></div><div class="pfd-strip" data-strip>%s</div>' % (1, n, cards)
    elif v == "hover-list":
        rows = "".join('<a class="pfd-hover-row" href="#f%d" id="f%d" data-hover-art="%d"><span class="pfd-hover-title">%s</span><span class="pfd-hover-meta">%s</span>%s</a>' % (
            i + 1, i + 1, i, E(f["title"]), E(_meta_line(f["body"])), index_label(p, i + 1, n)) for i, f in enumerate(feats))
        arts = "".join('<div class="pfd-hover-art" data-hover-art-id="%d" aria-hidden="true">%s</div>' % (i, _feature_art(p, i + 40)) for i in range(n))
        inner = '<div class="pfd-hover-list" data-hover-list>%s%s</div>' % (rows, arts)
    elif v == "cells":
        spans = ["pfd-cell-2", "", "", "pfd-cell-2", "", ""]
        cells = "".join('<div class="pfd-cell %s" id="f%d"><span class="pfd-index">%02d</span><h3>%s</h3><p>%s</p>%s</div>' % (
            spans[i % 6], i + 1, i + 1, E(f["title"]), E(f["body"]), _feature_art(p, i + 50) if spans[i % 6] else "") for i, f in enumerate(feats))
        inner = '<div class="pfd-cells">%s</div>' % cells
    elif v == "accordion":
        items = "".join('<details class="pfd-acc" name="pfd-acc"%s id="f%d"><summary><span>%s</span><span class="pfd-acc-no">%02d</span></summary><p>%s</p></details>' % (
            " open" if i == 0 else "", i + 1, E(f["title"]), i + 1, E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-acc-wrap"><h2>What you get</h2><div class="pfd-acc-list">%s</div></div>' % items
    elif v == "list":
        items = "".join('<li id="f%d"><h3>%s</h3><p>%s</p></li>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats))
        inner = '<div class="pfd-list-wrap"><h2>What you get</h2><ol class="pfd-list">%s</ol></div>' % items
    elif v == "alternating":
        inner = "".join('<div class="pfd-alt-row%s" id="f%d"><div><h3>%s</h3><p>%s</p></div>%s</div>' % (
            " is-flipped" if i % 2 else "", i + 1, E(f["title"]), E(f["body"]), _feature_art(p, i + 60)) for i, f in enumerate(feats[:3]))
    elif v == "bento":
        cells = "".join('<article class="pf-card pfd-cell%s" id="f%d"><h3>%s</h3><p>%s</p>%s</article>' % (
            " pfd-cell-wide" if i == 0 else "", i + 1, E(f["title"]), E(f["body"]), _feature_art(p, i + 70) if i < 2 else "") for i, f in enumerate(feats))
        inner = '<div class="pfd-bento">%s</div>' % cells
    else:  # columns
        cols = "".join('<div class="pfd-col" id="f%d"><h3>%s</h3><p>%s</p></div>' % (i + 1, E(f["title"]), E(f["body"])) for i, f in enumerate(feats[:3]))
        inner = '<div class="pfd-columns">%s</div>' % cols
    return section("features", v, vlabel(p, "What you get") + inner)


# ---------------------------------------------------------------- proof, cta

def _proof(p, v: str) -> str:
    proof = p.copy.get("proof") or ""
    stats = p.copy.get("stats") or []
    if v == "none":
        return section("proof", v, "")
    if v == "stat-wall" and len(stats) >= 2:
        cells = "".join('<div><span class="pfd-big-num" data-count="%s">%s</span><span class="pfd-caption">%s%s</span></div>' % (
            E(str(s.get("value", ""))), E(str(s.get("value", ""))), E(s.get("label", "")), (" <sup>%d</sup>" % (i + 1)) if s.get("source") else "") for i, s in enumerate(stats[:4]))
        inner = '<div class="pfd-stat-wall">%s</div>' % cells
    elif v in ("giant-quote", "quote") and (proof or v == "quote"):
        cls = "pfd-quote pfd-quote-giant" if v == "giant-quote" else "pfd-quote"
        inner = '<blockquote class="%s"><p>%s</p><footer class="pf-muted">%s</footer></blockquote>' % (
            cls, E(proof or "A short, attributed quote from a real customer goes here. Nothing invented."), E("Name, role, company (real, with permission)"))
    elif v == "statement" or (v in ("giant-quote", "stat-wall")):
        inner = _two_tone(proof or p.copy["headline"], "" if proof else (p.copy.get("lead") or p.copy["subhead"]))
    elif v == "logos-text":
        if not proof:
            return section("proof", v, "")
        inner = '<p class="pf-muted pfd-logos">%s</p>' % E(proof)
    else:  # stats-sourced
        inner = '<dl class="pfd-stats"><div><dt>%s</dt><dd>%s</dd></div></dl>' % (E("Sourced figure"), E(proof or "Every number on this page links to where it came from."))
    return section("proof", v, inner)


def _cta(p, v: str) -> str:
    c = p.copy
    line = c.get("cta_line") or c.get("form", {}).get("title") or c["headline"]
    if v == "giant":
        inner = ('<div class="pfd-giant"><p class="pf-lead">%s</p>%s<span class="pfd-giant-word" aria-hidden="true">%s</span></div>') % (E(line), buttons(p), E(brand(p)))
    elif v == "band":
        inner = '<div class="pfd-band"><h2>%s</h2>%s</div>' % (E(line), buttons(p))
    elif v == "inline":
        inner = '<div class="pfd-inline-cta"><p class="pf-lead">%s</p>%s</div>' % (E(line), buttons(p))
    elif v == "ticket":
        inner = ('<div class="pfd-ticket"><div class="pfd-ticket-main"><span class="pfd-index">%s · %s</span><h2>%s</h2><p class="pf-muted">%s</p></div>'
                 '<div class="pfd-ticket-stub">%s<span class="pfd-index">No. 001</span></div></div>') % (
            E(brand(p)), E(meta(p)["year"]), E(line), E(c.get("lead") or c["subhead"]), buttons(p))
    else:  # form
        form = c.get("form") or {}
        fields = "".join('<label class="pf-field"><span>%s</span><input class="pf-input" type="text"></label>' % E(f) for f in form.get("fields", ["Email"]))
        inner = ('<form class="pfd-form" onsubmit="return false"><h2>%s</h2><div class="pfd-form-row">%s'
                 '<button class="pf-btn pf-btn-primary" type="submit">%s</button></div><p class="pf-small">No spam. Unsubscribe in one click.</p></form>') % (
            E(form.get("title", "Stay in touch")), fields, E(form.get("submit", "Subscribe")))
    return section("cta", v, inner)


def render(p) -> str:
    order = ["hero", "features", "proof", "cta", "footer"]
    blocks = block_classes(p, order)
    hero_v = pick(p, "hero", VARIANTS["hero"], HERO_HOOKS)
    parts = [
        nav(p),
        with_class(_hero(p, hero_v), blocks["hero"]),
        marquee(p),
        with_class(_features(p, pick(p, "features", VARIANTS["features"], FEATURE_HOOKS)), blocks["features"]),
        with_class(_proof(p, pick(p, "proof", VARIANTS["proof"], PROOF_HOOKS)), blocks["proof"]),
        with_class(_cta(p, pick(p, "cta", VARIANTS["cta"], CTA_HOOKS)), blocks["cta"]),
        with_class(footer(p, pick(p, "footer", VARIANTS["footer"], FOOTER_HOOKS)), blocks["footer"]),
    ]
    return "".join(parts)
