"""Application draft: shell, a primary view, a detail, then extras.

Views follow working products rather than the generic dashboard: a focus board with the one
number or object that matters at display size, cards, a kanban of columns, a feed, a ledger, a
table. Shells: sidebar, top bar, icon rail, bottom tabs (phone first), or none (full-bleed focus).
"""
from __future__ import annotations

import re

from . import art
from ._shared import E, brand, features, has, index_label, pick, section

VARIANTS = {
    "shell": ["sidebar", "topbar", "rail", "bottom-tabs", "none"],
    "view": ["table", "ledger", "board", "cards", "kanban", "feed"],
    "table": ["dense", "comfortable", "ledger"],  # density of the table view; "ledger" kept for older layouts
    "detail": ["panel", "drawer", "inspector", "none"],
    "extras": ["settings", "empty", "both", "none"],
}
SHELL_HOOKS = {"app-rail": "rail", "app-bottom-tabs": "bottom-tabs", "app-focus": "none"}
VIEW_HOOKS = {"app-board": "board", "app-cards": "cards", "app-kanban": "kanban", "app-feed": "feed", "app-ledger": "ledger"}
DETAIL_HOOKS = {"app-inspector": "inspector"}

STATUSES = [("Draft", "pf-badge"), ("Done", "pf-badge pf-badge-success"), ("Pending", "pf-badge pf-badge-warning"),
            ("Done", "pf-badge pf-badge-success"), ("Failed", "pf-badge pf-badge-danger")]
DATES = ["Updated today", "Updated 2 Nov", "Pending 9 days", "Updated 28 Oct", "Failed"]


def _rows(p):
    """Rows built from the brief's own feature titles; counts and dates are visibly sample data."""
    feats = features(p)
    rows = []
    for i in range(5):
        f = feats[i % len(feats)]
        rows.append(("%04d" % (142 - i), f["title"], DATES[i], "%d" % (120 * (i + 3)), STATUSES[i][0], STATUSES[i][1]))
    return rows


def _nav_links(p, current: int = 1) -> str:
    return "".join('<a href="#"%s>%s</a>' % (' aria-current="page"' if i == current else "", E(x)) for i, x in enumerate(p.copy.get("nav", [])[:5]))


def _figure(p) -> str:
    """The number the product is about, if the brief names one (501, 90 days, 3 steps); else the item count."""
    text = " ".join([p.copy.get("headline", "")] + [f["title"] for f in features(p)])
    m = re.search(r"\b(\d{2,4})\b", text)
    return m.group(1) if m else "%02d" % len(features(p))


def _shell_open(p, v: str) -> str:
    links = _nav_links(p)
    name = E(brand(p))
    if v == "sidebar":
        side = ('<aside class="pfd-sidebar"><span class="pf-wordmark">%s</span><nav class="pfd-sidenav">%s</nav>'
                '<div class="pfd-sidefoot"><span class="pfd-avatar" aria-hidden="true"></span><span class="pf-small">ada@%s.dev</span></div></aside>') % (name, links, E(brand(p).lower()))
        return '<div class="pfd-shell pfd-shell-sidebar">%s<div class="pfd-main">' % side
    if v == "rail":
        rail = "".join('<a href="#" title="%s"%s><span aria-hidden="true">%s</span></a>' % (E(x), ' aria-current="page"' if i == 1 else "", E(x[:1])) for i, x in enumerate(p.copy.get("nav", [])[:5]))
        side = ('<aside class="pfd-rail-shell"><span class="pf-wordmark pfd-rail-mark">%s</span><nav class="pfd-rail-nav" aria-label="Sections">%s</nav>'
                '<span class="pfd-avatar" aria-hidden="true"></span></aside>') % (E(brand(p)[:1]), rail)
        palette = ('<div class="pfd-palette" role="dialog" aria-label="Command palette"><div class="pfd-palette-input"><span class="pfd-index">&gt;</span><span>Search or run a command</span><kbd>K</kbd></div>'
                   '<ul class="pfd-palette-list">%s</ul></div>') % "".join('<li><span>%s</span><kbd>%s</kbd></li>' % (E(f["title"]), "G %d" % (i + 1)) for i, f in enumerate(features(p)[:4]))
        return '<div class="pfd-shell pfd-shell-rail">%s<div class="pfd-main">%s' % (side, palette if has(p, "app-command-palette") else "")
    if v == "bottom-tabs":
        tabs = "".join('<a href="#"%s><span class="pfd-tab-dot" aria-hidden="true"></span>%s</a>' % (' aria-current="page"' if i == 1 else "", E(x)) for i, x in enumerate(p.copy.get("nav", [])[:4]))
        top = '<header class="pfd-appbar"><span class="pf-wordmark">%s</span><time data-live-time></time><span class="pfd-avatar" aria-hidden="true"></span></header>' % name
        return '<div class="pfd-shell pfd-shell-bottom-tabs">%s<div class="pfd-main"><nav class="pfd-bottom-tabs" aria-label="Sections">%s</nav>' % (top, tabs)
    if v == "none":
        bar = '<header class="pfd-focusbar"><span class="pf-wordmark">%s</span><span class="pfd-index">%s</span><button class="pfd-menu-word" type="button">Menu</button></header>' % (name, E(p.copy.get("nav", ["Live"])[1] if len(p.copy.get("nav", [])) > 1 else "Live"))
        return '<div class="pfd-shell pfd-shell-none">%s<div class="pfd-main">' % bar
    top = ('<header class="pf-nav pfd-topbar"><span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div>'
           '<span class="pfd-avatar" aria-hidden="true"></span></header>') % (name, links)
    return '<div class="pfd-shell pfd-shell-topbar">%s<div class="pfd-main">' % top


def _toolbar(p, title: str = None) -> str:
    title = title or (p.copy.get("nav", ["Items"])[1] if len(p.copy.get("nav", [])) > 1 else "Items")
    return ('<div class="pfd-toolbar"><h1>%s</h1><div class="pf-row"><label class="pf-field"><input class="pf-input" type="search" placeholder="Search" aria-label="Search"></label>'
            '<button class="pf-btn pf-btn-secondary pf-btn-sm" type="button">Filter</button><button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button></div></div>') % (
        E(title), E(p.copy.get("cta_primary", "New")))


def _view(p, v: str, density: str) -> str:
    feats = features(p)
    if v in ("table", "ledger"):
        if v == "ledger" or density == "ledger":
            rows = "".join('<tr><td class="pfd-index">%s</td><td>%s</td><td class="pf-muted">%s</td><td class="pfd-num">%s</td><td class="pfd-index">%s</td></tr>' % (
                E(a), E(b), E(c), E(d), E(st.lower())) for a, b, c, d, st, cls in _rows(p))
            table = '<table class="pfd-table pfd-table-ledger"><thead><tr><th>Id</th><th>Name</th><th>Updated</th><th class="pfd-num">Count</th><th>Status</th></tr></thead><tbody>%s</tbody></table>' % rows
            return section("view", "ledger", _toolbar(p) + table)
        rows = "".join('<tr><td><code>%s</code></td><td>%s</td><td class="pf-muted">%s</td><td class="pfd-num">%s</td><td><span class="%s">%s</span></td></tr>' % (
            E(a), E(b), E(c), E(d), cls, E(st)) for a, b, c, d, st, cls in _rows(p))
        table = '<table class="pfd-table pfd-table-%s"><thead><tr><th>Id</th><th>Name</th><th>Updated</th><th class="pfd-num">Count</th><th>Status</th></tr></thead><tbody>%s</tbody></table>' % (E(density if density != "ledger" else "dense"), rows)
        return section("view", "table", _toolbar(p) + table)
    if v == "board":
        fig = _figure(p)
        sides = "".join('<li><span>%s</span><span class="pfd-num pfd-board-small">%s</span></li>' % (E(f["title"]), "%d" % (60 - i * 19)) for i, f in enumerate(feats[:3]))
        inner = ('<div class="pfd-board"><div class="pfd-board-main"><span class="pfd-index">%s</span><span class="pfd-board-figure" data-count="%s">%s</span>'
                 '<span class="pfd-caption">%s</span><div class="pf-row"><button class="pf-btn pf-btn-primary" type="button">%s</button><button class="pf-btn pf-btn-secondary" type="button">Undo</button></div></div>'
                 '<ul class="pfd-board-side">%s</ul></div>') % (E(feats[0]["title"]), E(fig), E(fig), E(p.copy.get("lead") or p.copy.get("subhead", "")), E(p.copy.get("cta_primary", "Next")), sides)
        return section("view", v, inner)
    if v == "cards":
        cards = "".join('<article class="pfd-app-card">%s<div><span class="pfd-index">%s</span><h3>%s</h3><p>%s</p></div><span class="%s">%s</span></article>' % (
            art.render("figure", seed="%s-ac%d" % (p.id, i + 3)), index_label(p, i + 1), E(f["title"]), E(f["body"]), STATUSES[i % 5][1], E(STATUSES[i % 5][0])) for i, f in enumerate(feats[:6]))
        return section("view", v, _toolbar(p) + '<div class="pfd-app-cards">%s</div>' % cards)
    if v == "kanban":
        cols = ["Up next", "In play", "Done"]
        items = _rows(p)
        col_html = ""
        for ci, col in enumerate(cols):
            cards = "".join('<article class="pfd-kanban-card"><span class="pfd-index">%s</span><strong>%s</strong><span class="pf-small">%s</span></article>' % (E(a), E(b), E(c)) for a, b, c, d, st, cls in items[ci::3])
            col_html += '<div class="pfd-kanban-col"><h3>%s <span class="pfd-index">%d</span></h3>%s</div>' % (E(col), len(items[ci::3]), cards)
        return section("view", v, _toolbar(p) + '<div class="pfd-kanban">%s</div>' % col_html)
    if v == "feed":
        items = "".join('<li class="pfd-feed-item"><span class="pfd-avatar" aria-hidden="true"></span><div><strong>%s</strong> <span class="pf-muted">%s</span><p>%s</p></div><time class="pfd-index">%s</time></li>' % (
            E(brand(p)), E(f["title"].lower()), E(f["body"]), E(DATES[i % 5].replace("Updated ", ""))) for i, f in enumerate(feats[:5]))
        return section("view", v, _toolbar(p, p.copy.get("nav", ["Activity"])[0]) + '<ol class="pfd-feed">%s</ol>' % items)
    return section("view", v, _toolbar(p))


def _detail(p, v: str) -> str:
    if v == "none":
        return section("detail", v, "", "pfd-shell-marker")
    f = features(p)[0]
    body = ('<header class="pfd-detail-head"><div><p class="pf-kicker">Item 0142</p><h2>%s</h2></div><span class="pf-badge">Draft</span></header>'
            '<p>%s</p><dl class="pfd-kv"><dt>Owner</dt><dd>%s</dd><dt>Updated</dt><dd>Today</dd><dt>Count</dt><dd class="pfd-num">360</dd></dl>'
            '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="button">%s</button><button class="pf-btn pf-btn-secondary" type="button">Edit</button>'
            '<button class="pf-btn pf-btn-quiet" type="button">Delete</button></div>') % (E(f["title"]), E(f["body"]), E(brand(p)), E(p.copy.get("cta_primary", "Save")))
    if v == "panel":
        return section("detail", v, '<aside class="pfd-panel">%s</aside>' % body)
    if v == "inspector":
        tabs = '<div class="pf-tabs" role="tablist"><button role="tab" aria-selected="true" class="pf-tab">Details</button><button role="tab" aria-selected="false" class="pf-tab">Activity</button><button role="tab" aria-selected="false" class="pf-tab">Notes</button></div>'
        return section("detail", v, '<aside class="pfd-inspector">%s%s</aside>' % (tabs, body))
    return section("detail", v, '<div class="pfd-drawer-scrim"><aside class="pfd-drawer">%s</aside></div>' % body)


def _extras(p, v: str) -> str:
    empty = ('<section class="pfd-empty" data-section="empty-state" data-variant="card"><div class="pf-card">'
             '<h3>Nothing here yet</h3><p class="pf-muted">%s</p><button class="pf-btn pf-btn-primary" type="button">%s</button></div></section>') % (
        E("The first %s appears here as soon as it exists. You can also add one by hand." % features(p)[0]["title"].lower()), E(p.copy.get("cta_primary", "Add")))
    settings = ('<section class="pfd-settings" data-section="settings" data-variant="form"><h2>Settings</h2><form class="pfd-settings-form" onsubmit="return false">'
                '<label class="pf-field"><span>Name</span><input class="pf-input" type="text" value="%s"></label>'
                '<label class="pf-field"><span>Default</span><select class="pf-select"><option>%s</option><option>%s</option></select></label>'
                '<label class="pf-switch"><input type="checkbox" role="switch" checked><span class="pf-switch-track"></span><span>Sounds and haptics</span></label>'
                '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="submit">Save changes</button><button class="pf-btn pf-btn-quiet" type="button">Cancel</button></div>'
                '</form></section>') % (E(brand(p)), E(features(p)[0]["title"]), E(features(p)[1]["title"]))
    return section("extras", v, "", "pfd-shell-marker") + {"settings": settings, "empty": empty, "both": empty + settings}.get(v, "")


def render(p) -> str:
    shell = pick(p, "shell", VARIANTS["shell"], SHELL_HOOKS)
    density = pick(p, "table", VARIANTS["table"])
    view = pick(p, "view", VARIANTS["view"], VIEW_HOOKS)
    if view == "table" and density == "ledger":
        view = "ledger"
    detail = pick(p, "detail", VARIANTS["detail"], DETAIL_HOOKS)
    if shell == "none" and detail == "panel":
        detail = "none"  # a focus screen has no side panel
    extras = pick(p, "extras", VARIANTS["extras"])
    return "".join([
        _shell_open(p, shell),
        section("shell", shell, "", "pfd-shell-marker"),
        section("table", density, "", "pfd-shell-marker"),  # density marker; the table itself is the view
        '<div class="pfd-work%s">' % ("" if detail != "none" else " pfd-work-single"),
        _view(p, view, density),
        _detail(p, detail),
        "</div>",
        _extras(p, extras),
        "</div></div>",
    ])
