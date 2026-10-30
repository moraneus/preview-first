"""Store draft: hero, product grid, product detail, cart, footer.

Variants follow commerce sites designers admire: a lookbook opening (one full-bleed image and a
line of type), an editorial grid with uneven tiles, a product page with a sticky buy column.
"""
from __future__ import annotations

from . import art
from ._shared import E, brand, features, footer, has, headline, index_label, marquee, nav, pick, section, vlabel

VARIANTS = {
    "hero": ["product", "collection", "lookbook", "tiles"],
    "grid": ["two", "three", "four", "editorial"],
    "product": ["gallery-left", "gallery-top", "sticky-buy"],
    "cart": ["drawer", "page"],
    "footer": ["columns", "minimal", "giant", "colophon"],
}
HERO_HOOKS = {"store-lookbook": "lookbook", "store-tiles": "tiles"}
GRID_HOOKS = {"store-editorial-grid": "editorial"}
PRODUCT_HOOKS = {"store-sticky-buy": "sticky-buy"}
FOOTER_HOOKS = {"footer-colophon": "colophon"}

PRICES = ["48.00", "140.00", "32.00", "26.00", "14.00", "58.00", "12.00", "44.00"]


def _products(p):
    """Product names come from the brief's feature titles; prices are placeholders."""
    feats = features(p)
    names = [f["title"] for f in feats]
    while len(names) < 8:
        names.append("%s %d" % (brand(p), len(names) + 1))
    return list(zip(names[:8], PRICES))


def _shot(p, seed: str, kind: str = None) -> str:
    kind = kind or (p.style.get("art") or {}).get("feature", "halftone")
    if kind == "figure":  # line figures explain features; a store needs things on a seamless
        kind = "object"
    svg = art.render(kind, seed=p.id + "-" + seed)
    if has(p, "image-duotone"):
        svg = svg.replace('<svg class="pfd-art ', '<svg class="pfd-art pfd-duotone ', 1)
    return svg


def _hero(p, v: str) -> str:
    c = p.copy
    if v == "product":
        inner = ('%s<div class="pfd-hero-text"><p class="pf-kicker">New this season</p>%s<p class="pf-lead">%s</p>'
                 '<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary" type="button">%s</button><span class="pfd-price">%s</span></div></div>') % (
            _shot(p, "Product photo"), headline(p, c["headline"]), E(c["subhead"]), E(c["cta_primary"]), PRICES[0])
    elif v == "lookbook":
        inner = ('<div class="pfd-lookbook">%s<div class="pfd-lookbook-line"><span class="pfd-index">%s · %s</span>%s'
                 '<a class="pf-link" href="#">%s</a></div></div>') % (
            _shot(p, "Lookbook", (p.style.get("art") or {}).get("hero", "grain_disc")), E(brand(p)), E((c.get("meta") or {}).get("year", "2026")),
            headline(p, c["headline"], "pfd-lookbook-title"), E(c["cta_secondary"]))
    elif v == "tiles":
        tiles = "".join('<a class="pfd-tile" href="#">%s<span>%s</span></a>' % (_shot(p, "tile %d" % i), E(name)) for i, (name, _) in enumerate(_products(p)[:6]))
        inner = '<div class="pfd-tiles">%s</div>' % tiles
    else:
        inner = ('<div class="pfd-hero-text">%s<p class="pf-lead">%s</p><a class="pf-btn pf-btn-secondary" href="#">%s</a></div>%s') % (
            headline(p, c["headline"]), E(c["subhead"]), E(c["cta_secondary"]), _shot(p, "Collection photo"))
    return section("hero", v, vlabel(p, "New") + inner)


def _grid(p, v: str) -> str:
    items = _products(p)
    if v == "editorial":
        sizes = ["pfd-ed-wide", "", "", "pfd-ed-tall", "", "pfd-ed-wide", "", ""]
        cards = "".join('<article class="pfd-product pfd-ed %s"><a href="#">%s</a><div class="pfd-ed-meta"><h3>%s</h3><span class="pfd-price">%s</span></div>%s</article>' % (
            sizes[i], _shot(p, name), E(name), E(price), index_label(p, i + 1, len(items))) for i, (name, price) in enumerate(items))
        return section("grid", v, '<div class="pfd-grid-head"><h2>Shop</h2><span class="pfd-index">%02d items</span></div><div class="pfd-ed-grid">%s</div>' % (len(items), cards))
    n = {"two": 2, "three": 3, "four": 4}[v]
    cards = "".join('<article class="pfd-product"><a href="#">%s</a><h3>%s</h3><p class="pfd-price">%s</p></article>' % (
        _shot(p, name), E(name), E(price)) for name, price in items[: n * 2])
    return section("grid", v, '<div class="pfd-grid-head"><h2>Shop</h2><span class="pf-muted">%d items</span></div><div class="pfd-products pfd-products-%d">%s</div>' % (len(items), n, cards))


def _product(p, v: str) -> str:
    f = features(p)[0]
    first_name = _products(p)[0][0]
    gallery = '<div class="pfd-gallery">%s<div class="pfd-thumbs">%s</div></div>' % (
        _shot(p, "Main product photo"), "".join(_shot(p, "Angle %d" % i) for i in range(1, 4)))
    if v == "sticky-buy":
        gallery = '<div class="pfd-gallery pfd-gallery-stack">%s</div>' % "".join(_shot(p, "Shot %d" % i) for i in range(1, 4))
    spec = ""
    if v == "sticky-buy":
        spec = ('<dl class="pfd-spec-sheet"><div><dt>Material</dt><dd>Stated in the brief</dd></div><div><dt>Made in</dt><dd>Stated in the brief</dd></div>'
                '<div><dt>Care</dt><dd>Stated in the brief</dd></div></dl>')
    info = ('<div class="pfd-product-info%s"><p class="pf-kicker">%s</p><h2>%s</h2><p class="pfd-price">%s</p><p>%s</p>'
            '<label class="pf-field"><span>Option</span><select class="pf-select"><option>Standard</option><option>Large</option></select></label>'
            '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="button">Add to cart</button><button class="pf-btn pf-btn-secondary" type="button">Save</button></div>'
            '<p class="pf-small">Free returns within 30 days. Ships in 2 days.</p>%s</div>') % (
        " pfd-sticky" if v == "sticky-buy" else "", E(brand(p)), E(first_name), PRICES[0], E(f["body"]), spec)
    return section("product", v, '<div class="pfd-product-layout%s">%s%s</div>' % (" pfd-product-sticky" if v == "sticky-buy" else "", gallery, info))


def _cart(p, v: str) -> str:
    lines = "".join('<li>%s<div><strong>%s</strong><span class="pf-muted">Qty 1</span></div><span class="pfd-price">%s</span></li>' % (
        _shot(p, name), E(name), E(price)) for name, price in _products(p)[:2])
    body = ('<h2>Your cart</h2><ul class="pfd-cart-lines">%s</ul><dl class="pfd-kv"><dt>Subtotal</dt><dd class="pfd-num">188.00</dd><dt>Shipping</dt><dd>Calculated at checkout</dd></dl>'
            '<button class="pf-btn pf-btn-primary pfd-wide" type="button">Checkout</button>') % lines
    if v == "drawer":
        return section("cart", v, '<div class="pfd-drawer-scrim"><aside class="pfd-drawer">%s</aside></div>' % body)
    return section("cart", v, '<div class="pfd-cart-page">%s</div>' % body)


def render(p) -> str:
    return "".join([
        nav(p),
        _hero(p, pick(p, "hero", VARIANTS["hero"], HERO_HOOKS)),
        marquee(p),
        _grid(p, pick(p, "grid", VARIANTS["grid"], GRID_HOOKS)),
        _product(p, pick(p, "product", VARIANTS["product"], PRODUCT_HOOKS)),
        _cart(p, pick(p, "cart", VARIANTS["cart"])),
        footer(p, pick(p, "footer", VARIANTS["footer"], FOOTER_HOOKS)),
    ])
