"""Deterministic, palette-driven SVG artwork for drafted pages.

Every generator returns an inline <svg> that uses the direction's colour tokens through CSS
variables, so the same art recolours when the developer swaps palettes. Seeds make output
stable per direction. No gradients, no stock imagery, nothing that reads as a wireframe.
"""
from __future__ import annotations

import html
import math
import random
from typing import Callable, Dict, List

E = html.escape
C = {
    "bg": "var(--pf-color-bg)", "surface": "var(--pf-color-surface)", "raised": "var(--pf-color-surface-raised)",
    "text": "var(--pf-color-text)", "muted": "var(--pf-color-text-muted)", "border": "var(--pf-color-border)",
    "primary": "var(--pf-color-primary)", "on_primary": "var(--pf-color-on-primary)", "accent": "var(--pf-color-accent)",
    "success": "var(--pf-color-success)", "warning": "var(--pf-color-warning)", "danger": "var(--pf-color-danger)",
}


def _rng(seed: str, salt: str) -> random.Random:
    return random.Random("%s|%s" % (seed, salt))


def _svg(w: int, h: int, body: str, label: str = "", cls: str = "") -> str:
    title = "<title>%s</title>" % E(label) if label else ""
    return ('<svg class="pfd-art %s" viewBox="0 0 %d %d" width="100%%" preserveAspectRatio="xMidYMid meet" '
            'xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="%s">%s%s</svg>'
            % (E(cls), w, h, "false" if label else "true", title, body))


# ---------------------------------------------------------------- generators

def ui_mock(seed: str, label: str = "") -> str:
    """A product window: title bar, sidebar, list rows, a chart. Reads as real software."""
    r = _rng(seed, "ui")
    w, h = 960, 600
    parts = ['<rect width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>' % (w, h, C["raised"], C["border"])]
    parts.append('<rect x="0" y="0" width="%d" height="44" rx="14" fill="%s"/><rect y="30" width="%d" height="14" fill="%s"/>' % (w, C["surface"], w, C["surface"]))
    for i, col in enumerate((C["danger"], C["warning"], C["success"])):
        parts.append('<circle cx="%d" cy="22" r="6" fill="%s" opacity=".8"/>' % (22 + i * 20, col))
    parts.append('<rect x="0" y="44" width="220" height="%d" fill="%s"/><line x1="220" y1="44" x2="220" y2="%d" stroke="%s"/>' % (h - 44, C["surface"], h, C["border"]))
    for i in range(7):
        y = 76 + i * 40
        wline = r.randint(80, 150)
        parts.append('<rect x="24" y="%d" width="16" height="16" rx="4" fill="%s" opacity="%s"/><rect x="52" y="%d" width="%d" height="10" rx="5" fill="%s" opacity=".55"/>'
                     % (y, C["primary"] if i == 1 else C["muted"], ".9" if i == 1 else ".35", y + 3, wline, C["text"]))
    parts.append('<rect x="252" y="76" width="300" height="20" rx="6" fill="%s" opacity=".85"/>' % C["text"])
    parts.append('<rect x="252" y="108" width="180" height="10" rx="5" fill="%s" opacity=".5"/>' % C["muted"])
    parts.append('<rect x="%d" y="72" width="120" height="36" rx="10" fill="%s"/><rect x="%d" y="86" width="64" height="8" rx="4" fill="%s"/>' % (w - 150, C["primary"], w - 122, C["on_primary"]))
    # chart
    parts.append('<rect x="252" y="140" width="%d" height="220" rx="10" fill="%s" stroke="%s"/>' % (w - 282, C["bg"], C["border"]))
    pts = []
    for i in range(14):
        x = 276 + i * ((w - 330) / 13)
        y = 330 - r.randint(20, 160) - i * 4
        pts.append("%d,%d" % (x, y))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>' % (" ".join(pts), C["primary"]))
    for i in range(14):
        x = 276 + i * ((w - 330) / 13)
        parts.append('<line x1="%d" y1="344" x2="%d" y2="348" stroke="%s"/>' % (x, x, C["border"]))
    # table rows
    for i in range(5):
        y = 388 + i * 38
        parts.append('<line x1="252" y1="%d" x2="%d" y2="%d" stroke="%s"/>' % (y + 28, w - 30, y + 28, C["border"]))
        parts.append('<rect x="252" y="%d" width="%d" height="9" rx="4" fill="%s" opacity=".7"/>' % (y + 6, r.randint(120, 220), C["text"]))
        parts.append('<rect x="%d" y="%d" width="60" height="9" rx="4" fill="%s" opacity=".5"/>' % (w - 260, y + 6, C["muted"]))
        pill = (C["success"], C["warning"], C["success"], C["muted"], C["danger"])[i]
        parts.append('<rect x="%d" y="%d" width="54" height="18" rx="9" fill="%s" opacity=".18"/><rect x="%d" y="%d" width="30" height="6" rx="3" fill="%s"/>' % (w - 110, y + 1, pill, w - 98, y + 7, pill))
    return _svg(w, h, "".join(parts), label, "pfd-art-ui")


def terminal(seed: str, label: str = "") -> str:
    r = _rng(seed, "term")
    w, h = 880, 520
    parts = ['<rect width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>' % (w, h, C["surface"], C["border"])]
    parts.append('<rect x="24" y="18" width="120" height="8" rx="4" fill="%s" opacity=".5"/>' % C["muted"])
    y = 70
    colours = [C["primary"], C["text"], C["muted"], C["accent"], C["success"]]
    for i in range(11):
        x = 28
        parts.append('<text x="%d" y="%d" font-family="var(--pf-font-mono)" font-size="14" fill="%s">$</text>' % (x, y + 5, C["accent"]))
        x += 22
        for j in range(r.randint(2, 5)):
            wseg = r.randint(40, 160)
            parts.append('<rect x="%d" y="%d" width="%d" height="9" rx="4" fill="%s" opacity="%s"/>' % (x, y - 4, wseg, colours[(i + j) % 5], ".9" if j == 0 else ".55"))
            x += wseg + 14
        y += 38
    parts.append('<rect x="28" y="%d" width="10" height="18" fill="%s" class="pfd-cursor"/>' % (y - 10, C["primary"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-terminal")


def blueprint(seed: str, label: str = "") -> str:
    """Fine grid, dimension lines and an isometric outline, like an engineering figure."""
    r = _rng(seed, "bp")
    w, h = 800, 600
    parts = ['<defs><pattern id="pfg-%s" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="%s" stroke-width=".6" opacity=".7"/></pattern></defs>' % (E(seed), C["border"])]
    parts.append('<rect width="%d" height="%d" fill="url(#pfg-%s)"/>' % (w, h, E(seed)))
    cx, cy = 400, 300
    size = 120 + r.randint(0, 40)
    layers = r.randint(3, 5)
    for i in range(layers):
        off = i * 34
        pts = [(cx, cy - size * .5 - off), (cx + size * .87, cy - off), (cx, cy + size * .5 - off), (cx - size * .87, cy - off)]
        poly = " ".join("%d,%d" % p for p in pts)
        parts.append('<polygon points="%s" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="1.5"/>' % (poly, C["bg"], ".85", C["text"]))
        if i == 0:
            depth = 28
            side = "%d,%d %d,%d %d,%d %d,%d" % (pts[3][0], pts[3][1], pts[2][0], pts[2][1], pts[2][0], pts[2][1] + depth, pts[3][0], pts[3][1] + depth)
            side2 = "%d,%d %d,%d %d,%d %d,%d" % (pts[2][0], pts[2][1], pts[1][0], pts[1][1], pts[1][0], pts[1][1] + depth, pts[2][0], pts[2][1] + depth)
            parts.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/><polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (side, C["surface"], C["text"], side2, C["surface"], C["text"]))
    parts.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="4 6"/>' % (cx, cy - (layers - 1) * 34, int(size * .32), C["primary"]))
    # dimension lines
    parts.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/><line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/><line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                 % (cx - size * .87, cy + 80, cx + size * .87, cy + 80, C["muted"], cx - size * .87, cy + 72, cx - size * .87, cy + 88, C["muted"], cx + size * .87, cy + 72, cx + size * .87, cy + 88, C["muted"]))
    parts.append('<text x="%d" y="%d" font-family="var(--pf-font-mono)" font-size="12" fill="%s" text-anchor="middle">%d</text>' % (cx, cy + 104, C["muted"], int(size * 1.74)))
    for (x, y) in ((60, 60), (w - 60, 60), (60, h - 60), (w - 60, h - 60)):
        parts.append('<path d="M%d %dh16M%d %dv16" stroke="%s" stroke-width="1.2" fill="none" transform="translate(-8 -8)"/>' % (x, y, x + 8, y - 8, C["muted"]))
    if label:
        parts.append('<text x="60" y="%d" font-family="var(--pf-font-mono)" font-size="12" fill="%s">%s</text>' % (h - 36, C["muted"], E(label)))
    return _svg(w, h, "".join(parts), label, "pfd-art-blueprint")


def isometric(seed: str, label: str = "") -> str:
    """Line-art isometric slabs stacked with an offset, drawn only in strokes."""
    r = _rng(seed, "iso")
    w, h = 600, 520
    parts = []
    n = r.randint(4, 7)
    for i in range(n):
        off = (n - i) * 26
        cx, cy = 300 + r.randint(-6, 6), 330 - off
        sw, sh = 190 - i * 6, 95 - i * 3
        pts = "%d,%d %d,%d %d,%d %d,%d" % (cx, cy - sh, cx + sw, cy, cx, cy + sh, cx - sw, cy)
        parts.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4"/>' % (pts, C["bg"], C["text"]))
        parts.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.4"/>' % (cx - sw, cy, cx, cy + sh, cx, cy + sh + 14, cx - sw, cy + 14, C["surface"], C["text"]))
        parts.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="1.4"/>' % (cx, cy + sh, cx + sw, cy, cx + sw, cy + 14, cx, cy + sh + 14, C["surface"], C["text"]))
        if i == n - 1:
            parts.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s" opacity=".9"/>' % (cx, cy - 6, sw * .35, sh * .35, C["primary"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-iso")


def swiss(seed: str, label: str = "") -> str:
    r = _rng(seed, "swiss")
    w, h = 800, 800
    parts = ['<rect width="%d" height="%d" fill="%s"/>' % (w, h, C["bg"])]
    cols = [C["primary"], C["accent"], C["text"]]
    for i in range(r.randint(3, 5)):
        kind = r.choice(["circle", "quarter", "bar"])
        col = cols[i % 3]
        if kind == "circle":
            parts.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (r.randint(150, 650), r.randint(150, 650), r.randint(80, 220), col))
        elif kind == "quarter":
            x, y, rad = r.randint(0, 400), r.randint(0, 400), r.randint(200, 400)
            parts.append('<path d="M%d %d h%d a%d %d 0 0 1 -%d %d z" fill="%s"/>' % (x, y, rad, rad, rad, rad, rad, col))
        else:
            parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (r.randint(0, 500), r.randint(0, 700), r.randint(200, 400), r.randint(24, 60), col))
    for i in range(1, 4):
        parts.append('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="%s" stroke-width="1" opacity=".6"/>' % (i * 200, i * 200, h, C["border"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-swiss")


def contours(seed: str, label: str = "") -> str:
    """Topographic contour lines from a smooth deformed circle."""
    r = _rng(seed, "topo")
    w, h = 800, 600
    cx, cy = 400 + r.randint(-80, 80), 300 + r.randint(-60, 60)
    phases = [r.random() * math.tau for _ in range(4)]
    amps = [r.uniform(8, 26) for _ in range(4)]
    parts = []
    for ring in range(1, 13):
        base = ring * 26
        pts = []
        for k in range(72):
            a = k / 72 * math.tau
            rad = base + sum(amps[i] * math.sin((i + 2) * a + phases[i]) * (ring / 12) for i in range(4))
            pts.append("%.1f,%.1f" % (cx + rad * math.cos(a) * 1.25, cy + rad * math.sin(a)))
        parts.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>' % (
            " ".join(pts), C["primary"] if ring % 4 == 0 else C["text"], "1.6" if ring % 4 == 0 else "1", ".9" if ring % 4 == 0 else ".45"))
    return _svg(w, h, "".join(parts), label, "pfd-art-contours")


def halftone(seed: str, label: str = "") -> str:
    r = _rng(seed, "half")
    w, h = 800, 600
    parts = []
    # keep the focal point out of the centre so overlaid text stays readable
    fx, fy = r.choice([r.randint(90, 230), r.randint(570, 710)]), r.choice([r.randint(80, 200), r.randint(400, 520)])
    for gy in range(0, h, 24):
        for gx in range(0, w, 24):
            d = math.hypot(gx - fx, gy - fy)
            rad = max(0.6, 10 - d / 40)
            parts.append('<circle cx="%d" cy="%d" r="%.1f" fill="%s"/>' % (gx + 12, gy + 12, rad, C["text"]))
    parts.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (fx, fy, 70, C["accent"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-halftone")


def orbit(seed: str, label: str = "") -> str:
    r = _rng(seed, "orbit")
    w, h = 800, 800
    parts = []
    for i in range(1, 8):
        parts.append('<circle cx="400" cy="400" r="%d" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>' % (i * 52, C["text"], ".8" if i % 2 else "1.2", ".25" if i % 2 else ".45"))
        a = r.random() * math.tau
        parts.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s"/>' % (400 + i * 52 * math.cos(a), 400 + i * 52 * math.sin(a), 5 if i % 2 else 8, C["primary"] if i % 3 else C["accent"]))
    parts.append('<circle cx="400" cy="400" r="34" fill="%s"/>' % C["primary"])
    parts.append('<line x1="40" y1="400" x2="760" y2="400" stroke="%s" stroke-dasharray="2 8" opacity=".5"/><line x1="400" y1="40" x2="400" y2="760" stroke="%s" stroke-dasharray="2 8" opacity=".5"/>' % (C["muted"], C["muted"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-orbit")


def stickers(seed: str, label: str = "") -> str:
    r = _rng(seed, "stick")
    w, h = 800, 600
    parts = []
    words = ["NEW", "100%", "OK", "YES", "NO. 1", "RAW", "BETA"]
    cols = [C["primary"], C["accent"], C["warning"], C["success"], C["bg"]]
    for i in range(6):
        x, y = r.randint(60, 600), r.randint(60, 440)
        rot = r.randint(-18, 18)
        col = cols[i % 5]
        bw, bh = r.randint(140, 220), r.randint(70, 110)
        parts.append('<g transform="translate(%d %d) rotate(%d)">' % (x, y, rot))
        parts.append('<rect x="8" y="8" width="%d" height="%d" fill="%s"/>' % (bw, bh, C["text"]))
        parts.append('<rect width="%d" height="%d" fill="%s" stroke="%s" stroke-width="4"/>' % (bw, bh, col, C["text"]))
        parts.append('<text x="%d" y="%d" font-family="var(--pf-font-heading)" font-weight="800" font-size="34" text-anchor="middle" fill="%s">%s</text>' % (bw // 2, bh // 2 + 12, C["text"] if col != C["text"] else C["bg"], words[i % len(words)]))
        parts.append("</g>")
    return _svg(w, h, "".join(parts), label, "pfd-art-stickers")


def sparklines(seed: str, label: str = "") -> str:
    r = _rng(seed, "spark")
    w, h = 900, 560
    parts = ['<rect width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (w, h, C["raised"], C["border"])]
    for row in range(3):
        for col in range(3):
            x0, y0 = 30 + col * 290, 30 + row * 175
            parts.append('<rect x="%d" y="%d" width="260" height="150" rx="8" fill="%s" stroke="%s"/>' % (x0, y0, C["bg"], C["border"]))
            val = r.randint(10, 990)
            parts.append('<text x="%d" y="%d" font-family="var(--pf-font-heading)" font-size="30" font-weight="600" fill="%s" style="font-variant-numeric:tabular-nums">%s</text>' % (x0 + 18, y0 + 46, C["text"], "{:,}".format(val * 7)))
            parts.append('<rect x="%d" y="%d" width="%d" height="8" rx="4" fill="%s" opacity=".5"/>' % (x0 + 18, y0 + 62, r.randint(60, 140), C["muted"]))
            pts = []
            for i in range(16):
                pts.append("%d,%d" % (x0 + 18 + i * 15, y0 + 135 - r.randint(0, 48)))
            parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>' % (" ".join(pts), [C["primary"], C["accent"], C["success"]][(row + col) % 3]))
    return _svg(w, h, "".join(parts), label, "pfd-art-sparklines")


def mark(seed: str, label: str = "") -> str:
    """One large geometric mark, like a wordmark's symbol used as the whole image."""
    r = _rng(seed, "mark")
    w, h = 600, 600
    kind = r.choice(["triangle", "disc", "square", "ring"])
    if kind == "triangle":
        body = '<polygon points="300,90 520,500 80,500" fill="%s"/>' % C["text"]
    elif kind == "disc":
        body = '<circle cx="300" cy="300" r="220" fill="%s"/>' % C["accent"]
    elif kind == "square":
        body = '<rect x="110" y="110" width="380" height="380" fill="%s" transform="rotate(%d 300 300)"/>' % (C["primary"], r.randint(0, 20))
    else:
        body = '<circle cx="300" cy="300" r="200" fill="none" stroke="%s" stroke-width="58"/>' % C["text"]
    return _svg(w, h, body, label, "pfd-art-mark")


def glass(seed: str, label: str = "") -> str:
    r = _rng(seed, "glass")
    w, h = 800, 600
    parts = ['<circle cx="%d" cy="%d" r="260" fill="%s" opacity=".9"/>' % (r.randint(250, 550), r.randint(200, 400), C["primary"])]
    for i in range(3):
        x, y = 160 + i * 110, 120 + i * 90
        parts.append('<rect x="%d" y="%d" width="380" height="240" rx="18" fill="%s" fill-opacity=".55" stroke="%s" stroke-opacity=".5"/>' % (x, y, C["raised"], C["raised"]))
        parts.append('<rect x="%d" y="%d" width="140" height="12" rx="6" fill="%s" opacity=".8"/><rect x="%d" y="%d" width="220" height="8" rx="4" fill="%s" opacity=".5"/>' % (x + 24, y + 28, C["text"], x + 24, y + 54, C["text"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-glass")


def figure(seed: str, label: str = "") -> str:
    """A small captioned line figure for feature cells (fig 0.1 style)."""
    r = _rng(seed, "fig")
    w, h = 400, 300
    parts = []
    kinds = ["stack", "grid", "flow", "rings", "bars"]
    digits = "".join(ch for ch in seed if ch.isdigit())
    kind = kinds[int(digits[-1]) % len(kinds)] if digits else r.choice(kinds)
    if kind == "rings":
        for i in range(5):
            parts.append('<circle cx="200" cy="150" r="%d" fill="none" stroke="%s" stroke-width="1.3"/>' % (24 + i * 24, C["text"]))
        parts.append('<circle cx="%d" cy="150" r="7" fill="%s"/>' % (200 + 96, C["primary"]))
    elif kind == "bars":
        for i in range(8):
            hgt = r.randint(30, 170)
            parts.append('<rect x="%d" y="%d" width="26" height="%d" fill="%s" stroke="%s" stroke-width="1.2"/>' % (70 + i * 36, 230 - hgt, hgt, C["primary"] if i == 5 else C["bg"], C["text"]))
        parts.append('<line x1="60" y1="230" x2="360" y2="230" stroke="%s"/>' % C["text"])
    elif kind == "stack":
        for i in range(4):
            y = 200 - i * 34
            parts.append('<polygon points="200,%d 300,%d 200,%d 100,%d" fill="%s" stroke="%s" stroke-width="1.3"/>' % (y - 40, y, y + 40, y, C["bg"], C["text"]))
    elif kind == "grid":
        for gx in range(5):
            for gy in range(4):
                parts.append('<rect x="%d" y="%d" width="44" height="44" rx="6" fill="%s" stroke="%s" stroke-width="1.2"/>' % (80 + gx * 52, 60 + gy * 52, C["primary"] if (gx + gy) == 4 else C["bg"], C["text"]))
    else:
        parts.append('<path d="M60 230 C 140 230, 140 70, 220 70 S 300 230, 340 230" fill="none" stroke="%s" stroke-width="1.6"/>' % C["text"])
        for x, y in ((60, 230), (220, 70), (340, 230)):
            parts.append('<circle cx="%d" cy="%d" r="8" fill="%s"/>' % (x, y, C["primary"]))
    if label:
        parts.append('<text x="20" y="284" font-family="var(--pf-font-mono)" font-size="11" fill="%s">%s</text>' % (C["muted"], E(label)))
    return _svg(w, h, "".join(parts), label, "pfd-art-figure")


GENERATORS: Dict[str, Callable[[str, str], str]] = {
    "ui_mock": ui_mock, "terminal": terminal, "blueprint": blueprint, "isometric": isometric, "swiss": swiss,
    "contours": contours, "halftone": halftone, "orbit": orbit, "stickers": stickers, "sparklines": sparklines,
    "mark": mark, "glass": glass, "figure": figure,
}


def render(kind: str, seed: str = "A", label: str = "") -> str:
    return GENERATORS.get(kind, blueprint)(seed, label)
