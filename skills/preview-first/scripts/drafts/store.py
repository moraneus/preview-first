"""Store draft: hero, product grid, product detail, cart, footer."""
from __future__ import annotations

from ._shared import E, brand, features, footer, nav, pick, placeholder, section

VARIANTS = {
    "hero": ["product", "collection"],
    "grid": ["two", "three", "four"],
    "product": ["gallery-left", "gallery-top"],
    "cart": ["drawer", "page"],
}

PRICES = ["48.00", "140.00", "32.00", "26.00", "14.00", "58.00", "12.00", "44.00"]


def _products(p):
    """Product names come from the brief's feature titles; prices are placeholders."""
    feats = features(p)
    names = [f["title"] for f in feats]
    while len(names) < 8:
        names.append("%s %d" % (brand(p), len(names) + 1))
    return list(zip(names[:8], PRICES))


def _hero(p, v: str) -> str:
    c = p.copy
    if v == "product":
        inner = ('%s<div class="pfd-hero-text"><p class="pf-kicker">New this season</p><h1>%s</h1><p class="pf-lead">%s</p>'
                 '<div class="pf-row pfd-actions"><button class="pf-btn pf-btn-primary" type="button">%s</button><span class="pfd-price">%s</span></div></div>') % (
            placeholder("Product photo", "1 / 1"), E(c["headline"]), E(c["subhead"]), E(c["cta_primary"]), PRICES[0])
    else:
        inner = ('<div class="pfd-hero-text"><h1>%s</h1><p class="pf-lead">%s</p><a class="pf-btn pf-btn-secondary" href="#">%s</a></div>%s') % (
            E(c["headline"]), E(c["subhead"]), E(c["cta_secondary"]), placeholder("Collection photo", "21 / 9", "pfd-media-wide"))
    return section("hero", v, inner)


def _grid(p, v: str) -> str:
    n = {"two": 2, "three": 3, "four": 4}[v]
    cards = "".join('<article class="pfd-product"><a href="#">%s</a><h3>%s</h3><p class="pfd-price">%s</p></article>' % (
        placeholder(name, "4 / 5"), E(name), E(price)) for name, price in _products(p)[: n * 2])
    return section("grid", v, '<div class="pfd-grid-head"><h2>Shop</h2><span class="pf-muted">%d items</span></div><div class="pfd-products pfd-products-%d">%s</div>' % (len(_products(p)), n, cards))


def _product(p, v: str) -> str:
    f = features(p)[0]
    first_name = _products(p)[0][0]
    gallery = '<div class="pfd-gallery">%s<div class="pfd-thumbs">%s</div></div>' % (
        placeholder("Main product photo", "1 / 1"), "".join(placeholder("Angle %d" % i, "1 / 1", "pfd-thumb") for i in range(1, 4)))
    info = ('<div class="pfd-product-info"><p class="pf-kicker">%s</p><h2>%s</h2><p class="pfd-price">%s</p><p>%s</p>'
            '<label class="pf-field"><span>Option</span><select class="pf-select"><option>Standard</option><option>Large</option></select></label>'
            '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="button">Add to cart</button><button class="pf-btn pf-btn-secondary" type="button">Save</button></div>'
            '<p class="pf-small">Free returns within 30 days. Ships in 2 days.</p></div>') % (E(brand(p)), E(first_name), PRICES[0], E(f["body"]))
    return section("product", v, '<div class="pfd-product-layout">%s%s</div>' % (gallery, info))


def _cart(p, v: str) -> str:
    lines = "".join('<li>%s<div><strong>%s</strong><span class="pf-muted">Qty 1</span></div><span class="pfd-price">%s</span></li>' % (
        placeholder(name, "1 / 1", "pfd-thumb"), E(name), E(price)) for name, price in _products(p)[:2])
    body = ('<h2>Your cart</h2><ul class="pfd-cart-lines">%s</ul><dl class="pfd-kv"><dt>Subtotal</dt><dd class="pfd-num">188.00</dd><dt>Shipping</dt><dd>Calculated at checkout</dd></dl>'
            '<button class="pf-btn pf-btn-primary pfd-wide" type="button">Checkout</button>') % lines
    if v == "drawer":
        return section("cart", v, '<div class="pfd-drawer-scrim"><aside class="pfd-drawer">%s</aside></div>' % body)
    return section("cart", v, '<div class="pfd-cart-page">%s</div>' % body)


def render(p) -> str:
    return "".join([
        nav(p),
        _hero(p, pick(p, "hero", VARIANTS["hero"])),
        _grid(p, pick(p, "grid", VARIANTS["grid"])),
        _product(p, pick(p, "product", VARIANTS["product"])),
        _cart(p, pick(p, "cart", VARIANTS["cart"])),
        footer(p, "columns"),
    ])
