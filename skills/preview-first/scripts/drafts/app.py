"""Application draft: shell, data table, detail, empty state and settings form."""
from __future__ import annotations

from . import art
from ._shared import E, brand, features, pick, section

VARIANTS = {
    "shell": ["sidebar", "topbar"],
    "table": ["dense", "comfortable"],
    "detail": ["panel", "drawer"],
}

STATUSES = [("Draft", "pf-badge"), ("Done", "pf-badge pf-badge-success"), ("Pending", "pf-badge pf-badge-warning"),
            ("Done", "pf-badge pf-badge-success"), ("Failed", "pf-badge pf-badge-danger")]
DATES = ["Updated today", "Updated 2 Nov", "Pending 9 days", "Updated 28 Oct", "Failed"]


def _rows(p):
    """Table rows built from the brief's own feature titles, never a fixed domain."""
    feats = features(p)
    rows = []
    for i in range(5):
        f = feats[i % len(feats)]
        rows.append(("%04d" % (142 - i), f["title"], DATES[i], "%d" % (120 * (i + 3)), STATUSES[i][0], STATUSES[i][1]))
    return rows


def _shell_open(p, v: str) -> str:
    links = "".join('<a href="#"%s>%s</a>' % (' aria-current="page"' if i == 1 else "", E(x)) for i, x in enumerate(p.copy.get("nav", [])[:5]))
    if v == "sidebar":
        side = ('<aside class="pfd-sidebar"><span class="pf-wordmark">%s</span><nav class="pfd-sidenav">%s</nav>'
                '<div class="pfd-sidefoot"><span class="pfd-avatar" aria-hidden="true"></span><span class="pf-small">ada@%s.dev</span></div></aside>') % (
            E(brand(p)), links, E(brand(p).lower()))
        return '<div class="pfd-shell pfd-shell-sidebar">%s<div class="pfd-main">' % side
    top = ('<header class="pf-nav pfd-topbar"><span class="pf-wordmark">%s</span><div class="pf-nav-links">%s</div>'
           '<span class="pfd-avatar" aria-hidden="true"></span></header>') % (E(brand(p)), links)
    return '<div class="pfd-shell pfd-shell-topbar">%s<div class="pfd-main">' % top


def _table(p, v: str) -> str:
    rows = "".join('<tr><td><code>%s</code></td><td>%s</td><td class="pf-muted">%s</td><td class="pfd-num">%s</td><td><span class="%s">%s</span></td></tr>' % (
        E(a), E(b), E(c), E(d), cls, E(st)) for a, b, c, d, st, cls in _rows(p))
    toolbar = ('<div class="pfd-toolbar"><h1>%s</h1><div class="pf-row"><label class="pf-field"><input class="pf-input" type="search" placeholder="Search" aria-label="Search"></label>'
               '<button class="pf-btn pf-btn-secondary pf-btn-sm" type="button">Filter</button><button class="pf-btn pf-btn-primary pf-btn-sm" type="button">%s</button></div></div>') % (
        E(p.copy.get("nav", ["Items"])[1] if len(p.copy.get("nav", [])) > 1 else "Items"), E(p.copy.get("cta_primary", "New")))
    table = ('<table class="pfd-table pfd-table-%s"><thead><tr><th>Id</th><th>Name</th><th>Updated</th><th class="pfd-num">Count</th><th>Status</th></tr></thead>'
             '<tbody>%s</tbody></table>') % (E(v), rows)
    return section("table", v, toolbar + table)


def _detail(p, v: str) -> str:
    f = features(p)[0]
    body = ('<header class="pfd-detail-head"><div><p class="pf-kicker">Item 0142</p><h2>%s</h2></div><span class="pf-badge">Draft</span></header>'
            '<p>%s</p><dl class="pfd-kv"><dt>Owner</dt><dd>%s</dd><dt>Updated</dt><dd>Today</dd><dt>Count</dt><dd class="pfd-num">360</dd></dl>'
            '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="button">%s</button><button class="pf-btn pf-btn-secondary" type="button">Edit</button>'
            '<button class="pf-btn pf-btn-quiet" type="button">Delete</button></div>') % (E(f["title"]), E(f["body"]), E(brand(p)), E(p.copy.get("cta_primary", "Save")))
    if v == "panel":
        return section("detail", v, '<aside class="pfd-panel">%s</aside>' % body)
    return section("detail", v, '<div class="pfd-drawer-scrim"><aside class="pfd-drawer">%s</aside></div>' % body)


def _empty_and_settings(p) -> str:
    empty = ('<section class="pfd-empty" data-section="empty-state" data-variant="card"><div class="pf-card">'
             '<h3>No reports yet</h3><p class="pf-muted">Reports appear here once the first month closes. You can also build one by hand.</p>'
             '<button class="pf-btn pf-btn-primary" type="button">Create a report</button></div></section>')
    settings = ('<section class="pfd-settings" data-section="settings" data-variant="form"><h2>Settings</h2><form class="pfd-settings-form" onsubmit="return false">'
                '<label class="pf-field"><span>Business name</span><input class="pf-input" type="text" value="%s"></label>'
                '<label class="pf-field"><span>Currency</span><select class="pf-select"><option>EUR</option><option>USD</option></select></label>'
                '<label class="pf-switch"><input type="checkbox" role="switch" checked><span class="pf-switch-track"></span><span>Send reminders automatically</span></label>'
                '<div class="pf-row"><button class="pf-btn pf-btn-primary" type="submit">Save changes</button><button class="pf-btn pf-btn-quiet" type="button">Cancel</button></div>'
                '</form></section>') % E(brand(p))
    return empty + settings


def render(p) -> str:
    shell = pick(p, "shell", VARIANTS["shell"])
    return "".join([
        _shell_open(p, shell),
        section("shell", shell, "", "pfd-shell-marker"),
        '<div class="pfd-work">',
        _table(p, pick(p, "table", VARIANTS["table"])),
        _detail(p, pick(p, "detail", VARIANTS["detail"])),
        "</div>",
        _empty_and_settings(p),
        "</div></div>",
    ])
