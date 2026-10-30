"""Content page draft: header, article, list of further reading, footer.

Variants: a broadsheet masthead with a date line and rules, a two-column reading layout with a
side note, an archive index with dates and counts.
"""
from __future__ import annotations

from . import art
from ._shared import E, brand, features, footer, has, headline, index_label, nav, pick, section

VARIANTS = {
    "header": ["masthead", "minimal", "broadsheet"],
    "article": ["single", "with-toc", "side-notes"],
    "list": ["cards", "lines", "archive"],
    "footer": ["minimal", "columns", "giant", "colophon"],
}
HEADER_HOOKS = {"content-broadsheet": "broadsheet"}
ARTICLE_HOOKS = {"content-side-notes": "side-notes"}
LIST_HOOKS = {"content-archive": "archive"}
FOOTER_HOOKS = {"footer-colophon": "colophon"}
SECOND = ("A second paragraph keeps the measure honest: around sixty-six characters per line, "
          "a line height that lets the eye return easily, and no decoration between paragraphs.")


def _header(p, v: str) -> str:
    if v == "masthead":
        inner = ('<div class="pfd-masthead"><span class="pf-wordmark pfd-masthead-name">%s</span><p class="pf-muted">%s</p></div>%s') % (
            E(brand(p)), E(p.copy.get("subhead", "")), nav(p))
    elif v == "broadsheet":
        links = "".join('<a href="#">%s</a>' % E(x) for x in p.copy.get("nav", [])[:5])
        inner = ('<div class="pfd-broadsheet"><div class="pfd-broadsheet-line"><span>%s</span><time data-live-time></time><span>No. 001</span></div>'
                 '<span class="pfd-broadsheet-name">%s</span><div class="pfd-broadsheet-line"><span>%s</span><nav class="pfd-broadsheet-nav" aria-label="Main">%s</nav></div></div>') % (
            E("Thursday 30 October 2026"), E(brand(p)), E(p.copy.get("subhead", "")[:70]), links)
    else:
        inner = nav(p)
    return section("header", v, inner)


def _lead_art(p) -> str:
    return art.render((p.style.get("art") or {}).get("feature", "contours"), seed=p.id + "-lead")


def _article(p, v: str) -> str:
    feats = features(p)
    paras = "".join("<h2 id=\"s%d\">%s</h2><p>%s</p><p>%s</p>" % (i, E(f["title"]), E(f["body"]), E(SECOND)) for i, f in enumerate(feats[:3]))
    cap = '<figcaption class="pfd-caption">%s %s</figcaption>' % (index_label(p, 1, prefix="Fig "), E("Lead figure; replace with a real photograph and a true caption.")) if (has(p, "image-caption") or v == "side-notes") else ""
    body = ('<article class="pfd-article"><header><p class="pf-kicker">%s · 6 min read</p>%s<p class="pf-lead">%s</p></header><figure class="pfd-figure">%s%s</figure>%s</article>') % (
        E("30 October 2026"), headline(p, p.copy["headline"]), E(p.copy["subhead"]), _lead_art(p), cap, paras)
    if v == "with-toc":
        toc = '<nav class="pfd-toc" aria-label="On this page"><p class="pf-small">On this page</p>%s</nav>' % "".join(
            '<a href="#s%d">%s</a>' % (i, E(f["title"])) for i, f in enumerate(feats[:3]))
        return section("article", v, '<div class="pfd-article-grid">%s%s</div>' % (toc, body))
    if v == "side-notes":
        notes = "".join('<aside class="pfd-side-note"><span class="pfd-index">%d</span>%s</aside>' % (i + 1, E(f["body"])) for i, f in enumerate(feats[:3]))
        return section("article", v, '<div class="pfd-article-notes">%s<div class="pfd-notes-col">%s</div></div>' % (body, notes))
    return section("article", v, body)


def _list(p, v: str) -> str:
    feats = features(p)
    if v == "cards":
        items = "".join('<article class="pf-card"><p class="pf-kicker">%s</p><h3>%s</h3><p class="pf-muted">%s</p></article>' % (
            E("Topic"), E(f["title"]), E(f["body"])) for f in feats[:3])
        inner = '<h2>Further reading</h2><div class="pfd-cards">%s</div>' % items
    elif v == "archive":
        rows = "".join('<a class="pfd-archive-row" href="#"><span class="pfd-index">%s</span><span class="pfd-archive-title">%s</span><span class="pfd-archive-meta">%s</span></a>' % (
            E("2026.%02d" % (10 - i)), E(f["title"]), E("%d min" % (4 + i * 2))) for i, f in enumerate(feats[:6]))
        inner = '<div class="pfd-archive-head"><h2>Archive</h2><span class="pfd-index">%02d entries</span></div><div class="pfd-archive">%s</div>' % (len(feats), rows)
    else:
        items = "".join('<li><a href="#">%s</a><span class="pf-muted">%s</span></li>' % (E(f["title"]), E("28 Oct 2026")) for f in feats[:5])
        inner = '<h2>Further reading</h2><ul class="pfd-lines">%s</ul>' % items
    return section("list", v, inner)


def render(p) -> str:
    return "".join([
        _header(p, pick(p, "header", VARIANTS["header"], HEADER_HOOKS)),
        _article(p, pick(p, "article", VARIANTS["article"], ARTICLE_HOOKS)),
        _list(p, pick(p, "list", VARIANTS["list"], LIST_HOOKS)),
        footer(p, pick(p, "footer", VARIANTS["footer"], FOOTER_HOOKS)),
    ])
