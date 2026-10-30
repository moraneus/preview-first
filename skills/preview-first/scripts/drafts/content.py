"""Content page draft: header, article, list of further reading, footer."""
from __future__ import annotations

from . import art
from ._shared import E, brand, features, footer, nav, pick, placeholder, section

VARIANTS = {
    "header": ["masthead", "minimal"],
    "article": ["single", "with-toc"],
    "list": ["cards", "lines"],
}


def _header(p, v: str) -> str:
    if v == "masthead":
        inner = ('<div class="pfd-masthead"><span class="pf-wordmark pfd-masthead-name">%s</span><p class="pf-muted">%s</p></div>%s') % (
            E(brand(p)), E(p.copy.get("subhead", "")), nav(p))
    else:
        inner = nav(p)
    return section("header", v, inner)


def _article(p, v: str) -> str:
    feats = features(p)
    paras = "".join("<h2 id=\"s%d\">%s</h2><p>%s</p><p>%s</p>" % (
        i, E(f["title"]), E(f["body"]), E("A second paragraph keeps the measure honest: around sixty-six characters per line, "
                                           "a line height that lets the eye return easily, and no decoration between paragraphs.")) for i, f in enumerate(feats[:3]))
    body = ('<article class="pfd-article"><header><p class="pf-kicker">%s · 6 min read</p><h1>%s</h1><p class="pf-lead">%s</p></header>%s%s</article>') % (
        E("30 October 2026"), E(p.copy["headline"]), E(p.copy["subhead"]), art.render((p.style.get("art") or {}).get("feature", "contours"), seed=p.id + "-" + str("Lead image with a real caption")), paras)
    if v == "with-toc":
        toc = '<nav class="pfd-toc" aria-label="On this page"><p class="pf-small">On this page</p>%s</nav>' % "".join(
            '<a href="#s%d">%s</a>' % (i, E(f["title"])) for i, f in enumerate(feats[:3]))
        return section("article", v, '<div class="pfd-article-grid">%s%s</div>' % (toc, body))
    return section("article", v, body)


def _list(p, v: str) -> str:
    feats = features(p)
    if v == "cards":
        items = "".join('<article class="pf-card"><p class="pf-kicker">%s</p><h3>%s</h3><p class="pf-muted">%s</p></article>' % (
            E("Topic"), E(f["title"]), E(f["body"])) for f in feats[:3])
        inner = '<h2>Further reading</h2><div class="pfd-cards">%s</div>' % items
    else:
        items = "".join('<li><a href="#">%s</a><span class="pf-muted">%s</span></li>' % (E(f["title"]), E("28 Oct 2026")) for f in feats[:5])
        inner = '<h2>Further reading</h2><ul class="pfd-lines">%s</ul>' % items
    return section("list", v, inner)


def render(p) -> str:
    return "".join([
        _header(p, pick(p, "header", VARIANTS["header"])),
        _article(p, pick(p, "article", VARIANTS["article"])),
        _list(p, pick(p, "list", VARIANTS["list"])),
        footer(p, "minimal"),
    ])
