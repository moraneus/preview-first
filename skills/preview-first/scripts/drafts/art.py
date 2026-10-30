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
    kind = r.choice(["triangle", "disc", "square", "ring", "cross", "diamond", "pill", "star", "notch"])
    if kind == "cross":
        body = '<rect x="240" y="80" width="120" height="440" fill="%s"/><rect x="80" y="240" width="440" height="120" fill="%s"/>' % (C["text"], C["text"])
    elif kind == "diamond":
        body = '<polygon points="300,70 530,300 300,530 70,300" fill="%s"/>' % C["primary"]
    elif kind == "pill":
        body = '<rect x="90" y="190" width="420" height="220" rx="110" fill="%s"/>' % C["accent"]
    elif kind == "star":
        pts = " ".join("%.0f,%.0f" % (300 + (220 if i % 2 == 0 else 95) * math.cos(i * math.pi / 4 - math.pi / 2), 300 + (220 if i % 2 == 0 else 95) * math.sin(i * math.pi / 4 - math.pi / 2)) for i in range(8))
        body = '<polygon points="%s" fill="%s"/>' % (pts, C["text"])
    elif kind == "notch":
        body = '<path d="M80 80h440v300L380 520H80z" fill="%s"/>' % C["primary"]
    elif kind == "triangle":
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
    kinds = ["stack", "grid", "flow", "rings", "bars", "wave", "dots", "steps", "cross", "ladder", "arc", "target", "beam"]
    digits = "".join(ch for ch in seed if ch.isdigit())
    kind = kinds[(int(digits[-2:]) if len(digits) >= 2 else int(digits[-1])) % len(kinds)] if digits else r.choice(kinds)
    if kind == "wave":
        for k in range(5):
            pts = " ".join("%d,%.0f" % (x, 150 + (k - 2) * 22 + math.sin(x / 38 + k * .6) * 26) for x in range(40, 361, 8))
            parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>' % (pts, C["primary"] if k == 2 else C["text"], "1.8" if k == 2 else "1.1", "1" if k == 2 else ".55"))
    elif kind == "dots":
        for gx in range(9):
            for gy in range(6):
                rad = 2 + ((gx * 7 + gy * 5 + r.randint(0, 2)) % 6)
                parts.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (60 + gx * 35, 70 + gy * 32, rad, C["primary"] if rad > 6 else C["text"]))
    elif kind == "steps":
        x, y = 50, 240
        for i in range(7):
            parts.append('<path d="M%d %dh40v-28" fill="none" stroke="%s" stroke-width="1.5"/>' % (x, y, C["text"]))
            x += 40; y -= 28
        parts.append('<circle cx="%d" cy="%d" r="7" fill="%s"/>' % (x, y, C["primary"]))
    elif kind == "cross":
        parts.append('<line x1="200" y1="40" x2="200" y2="260" stroke="%s" stroke-width="1.2"/><line x1="60" y1="150" x2="340" y2="150" stroke="%s" stroke-width="1.2"/>' % (C["text"], C["text"]))
        parts.append('<circle cx="200" cy="150" r="60" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3 5"/><rect x="236" y="90" width="44" height="44" fill="%s"/>' % (C["text"], C["primary"]))
    elif kind == "ladder":
        for i in range(8):
            y = 50 + i * 28
            parts.append('<line x1="80" y1="%d" x2="320" y2="%d" stroke="%s" stroke-width="%s"/>' % (y, y, C["primary"] if i == 5 else C["text"], "3" if i == 5 else "1.2"))
        parts.append('<line x1="80" y1="40" x2="80" y2="260" stroke="%s"/><line x1="320" y1="40" x2="320" y2="260" stroke="%s"/>' % (C["text"], C["text"]))
    elif kind == "arc":
        for i in range(4):
            rad = 60 + i * 38
            parts.append('<path d="M%d 250 A%d %d 0 0 1 %d 250" fill="none" stroke="%s" stroke-width="%s"/>' % (200 - rad, rad, rad, 200 + rad, C["primary"] if i == 1 else C["text"], "2.4" if i == 1 else "1.2"))
        parts.append('<line x1="40" y1="250" x2="360" y2="250" stroke="%s"/>' % C["text"])
    elif kind == "target":
        for i in range(4):
            parts.append('<circle cx="200" cy="150" r="%d" fill="%s" stroke="%s" stroke-width="1.2"/>' % (110 - i * 27, C["primary"] if i == 3 else "none", C["text"]))
        parts.append('<line x1="200" y1="20" x2="200" y2="280" stroke="%s" stroke-dasharray="2 6"/>' % C["muted"])
    elif kind == "beam":
        parts.append('<polygon points="40,150 360,60 360,240" fill="%s" opacity=".12"/><polygon points="40,150 360,120 360,180" fill="%s"/>' % (C["primary"], C["primary"]))
        parts.append('<circle cx="40" cy="150" r="8" fill="%s"/>' % C["text"])
    elif kind == "rings":
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




# ---------------------------------------------------------------- 0.3.0 generators (research sweep)

def ascii_field(seed: str, label: str = "") -> str:
    """A field of mono characters whose density maps to a wave and a disc; peaks in primary."""
    r = _rng(seed, "ascii")
    w, h = 800, 520
    cols, rows = 68, 25
    chars = " .:-=+*#%@"
    cx, cy = r.uniform(0.3, 0.7), r.uniform(0.35, 0.65)
    ph = r.random() * 6
    parts = []
    for j in range(rows):
        spans = []
        for i in range(cols):
            x, y = i / cols, j / rows
            d = math.hypot((x - cx) * 1.6, (y - cy))
            v = max(0.0, 1 - d * 2.2) + 0.22 * math.sin(x * 9 + ph) * math.cos(y * 7 + ph)
            k = int(max(0.0, min(1.0, v)) * (len(chars) - 1))
            ch = chars[k]
            spans.append((ch, k >= 7))
        text = ""
        run, hot = [], None
        for ch, is_hot in spans + [(None, None)]:
            if ch is not None and is_hot == hot:
                run.append(ch)
                continue
            if run:
                seg = E("".join(run)).replace(" ", "&#160;")
                text += ('<tspan fill="%s">%s</tspan>' % (C["primary"], seg)) if hot else seg
            run, hot = ([ch] if ch is not None else []), is_hot
        parts.append('<text x="12" y="%d" xml:space="preserve" style="font-family:var(--pf-font-mono);font-size:13px" fill="%s" opacity=".7">%s</text>' % (20 + j * 20, C["text"], text))
    return _svg(w, h, "".join(parts), label, "pfd-art-ascii")


def dither(seed: str, label: str = "") -> str:
    """Ordered (Bayer 4x4) dithering of a radial light and a horizon band, in two palette colours."""
    r = _rng(seed, "dither")
    w, h = 800, 600
    cell = 8
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    cx, cy = r.uniform(0.25, 0.75) * w, r.uniform(0.3, 0.62) * h
    rad = r.uniform(230, 330)
    d = []
    for j in range(h // cell):
        for i in range(w // cell):
            x, y = i * cell, j * cell
            dist = math.hypot(x + 4 - cx, (y + 4 - cy) * 1.1)
            v = max(0.0, min(1.0, 1 - dist / rad))
            v = max(v, 0.4 * max(0.0, 1 - abs(y - h * 0.74) / (h * 0.1)))
            if v > (bayer[j % 4][i % 4] + 0.5) / 16:
                d.append("M%d %dh%dv%dh-%dz" % (x, y, cell, cell, cell))
    parts = ['<path d="%s" fill="%s"/>' % ("".join(d), C["text"])]
    parts.append('<circle cx="%.0f" cy="%.0f" r="%d" fill="%s"/>' % (cx, cy, int(rad * 0.16), C["primary"]))
    return _svg(w, h, "".join(parts), label, "pfd-art-dither")


def flowfield(seed: str, label: str = "") -> str:
    """Particles traced through a smooth vector field; every ninth path in primary."""
    r = _rng(seed, "flow")
    w, h = 800, 600
    ph = r.random() * math.tau
    parts = []
    for k in range(72):
        x, y = r.uniform(0, w), r.uniform(0, h)
        pts = []
        for _ in range(70):
            a = math.sin(x / 140 + ph) * math.cos(y / 110) + 0.4 * math.sin((x + y) / 90)
            x += math.cos(a * 3.1) * 6
            y += math.sin(a * 3.1) * 6
            if not (0 <= x <= w and 0 <= y <= h):
                break
            pts.append("%.0f,%.0f" % (x, y))
        if len(pts) > 8:
            hot = k % 9 == 0
            parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s" stroke-linecap="round"/>' % (
                " ".join(pts), C["primary"] if hot else C["text"], "1.8" if hot else "1", ".95" if hot else ".45"))
    return _svg(w, h, "".join(parts), label, "pfd-art-flow")


def strands(seed: str, label: str = "") -> str:
    """Horizontal wave strands that bunch in the middle, three of them in primary."""
    r = _rng(seed, "strand")
    w, h = 800, 600
    base = r.random() * 3
    parts = []
    for i in range(30):
        pts = " ".join("%d,%.0f" % (x, h * 0.5 + (i - 15) * 9 + math.sin(x / 90 + i * 0.25 + base) * 46 * math.sin(x / w * math.pi)) for x in range(0, w + 1, 10))
        hot = i in (12, 13, 14)
        parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>' % (pts, C["primary"] if hot else C["text"], "1.6" if hot else "1.1", ".95" if hot else ".4"))
    return _svg(w, h, "".join(parts), label, "pfd-art-strands")


def stamp(seed: str, label: str = "") -> str:
    """A rotated circular stamp with text on a path, like a sticker on a parcel."""
    r = _rng(seed, "stamp")
    rot = r.randint(-14, 14)
    words = ["Est. 2026", "Made by hand", "No template", "Open source", "Version 0.3"]
    text = (words[r.randint(0, 4)] + " · ") * 4
    pid = "pfs-" + E(seed).replace(" ", "")
    parts = ['<defs><path id="%s" d="M300,300 m-200,0 a200,200 0 1,1 400,0 a200,200 0 1,1 -400,0"/></defs><g transform="rotate(%d 300 300)">' % (pid, rot)]
    parts.append('<circle cx="300" cy="300" r="250" fill="none" stroke="%s" stroke-width="6"/><circle cx="300" cy="300" r="236" fill="none" stroke="%s" stroke-width="1.5"/>' % (C["primary"], C["primary"]))
    parts.append('<text style="font-family:var(--pf-font-mono);font-size:30px;letter-spacing:.18em" fill="%s"><textPath href="#%s">%s</textPath></text>' % (C["primary"], pid, E(text)))
    parts.append('<circle cx="300" cy="300" r="150" fill="none" stroke="%s" stroke-width="3"/><polygon points="300,205 380,340 220,340" fill="%s"/></g>' % (C["primary"], C["primary"]))
    return _svg(600, 600, "".join(parts), label, "pfd-art-stamp")


def ruler(seed: str, label: str = "") -> str:
    """Measurement ticks with one highlighted span, like a spec sheet."""
    r = _rng(seed, "ruler")
    parts = ['<line x1="40" y1="200" x2="760" y2="200" stroke="%s" stroke-width="1.5"/>' % C["text"]]
    for i in range(73):
        x = 40 + i * 10
        ln = 28 if i % 10 == 0 else (16 if i % 5 == 0 else 8)
        parts.append('<line x1="%d" y1="200" x2="%d" y2="%d" stroke="%s"/>' % (x, x, 200 - ln, C["text"]))
        if i % 10 == 0:
            parts.append('<text x="%d" y="160" text-anchor="middle" style="font-family:var(--pf-font-mono);font-size:11px" fill="%s">%d</text>' % (x, C["muted"], i * 10))
    a, b = 40 + r.randint(5, 25) * 10, 40 + r.randint(40, 70) * 10
    parts.append('<rect x="%d" y="226" width="%d" height="26" fill="%s"/>' % (a, b - a, C["primary"]))
    parts.append('<text x="%d" y="282" style="font-family:var(--pf-font-mono);font-size:12px" fill="%s">%d mm</text>' % (a, C["text"], b - a))
    return _svg(800, 300, "".join(parts), label, "pfd-art-ruler")


def globe(seed: str, label: str = "") -> str:
    """A wireframe globe with a few markers."""
    r = _rng(seed, "globe")
    R = 230
    parts = ['<circle cx="300" cy="300" r="%d" fill="none" stroke="%s" stroke-width="1.5"/>' % (R, C["text"])]
    for k in range(-3, 4):
        ry = R * math.cos(k * math.pi / 8)
        parts.append('<ellipse cx="300" cy="%.0f" rx="%.0f" ry="%.0f" fill="none" stroke="%s" opacity=".5"/>' % (300 + R * math.sin(k * math.pi / 8), ry, ry * 0.22, C["text"]))
    for k in range(6):
        rx = max(1.0, R * abs(math.cos(k * math.pi / 6)))
        parts.append('<ellipse cx="300" cy="300" rx="%.0f" ry="%d" fill="none" stroke="%s" opacity=".5"/>' % (rx, R, C["text"]))
    for _ in range(6):
        a, d = r.random() * math.tau, r.uniform(0.2, 0.9) * R
        parts.append('<circle cx="%.0f" cy="%.0f" r="5" fill="%s"/>' % (300 + d * math.cos(a), 300 + d * math.sin(a) * 0.9, C["primary"]))
    return _svg(600, 600, "".join(parts), label, "pfd-art-globe")


def specimen(seed: str, label: str = "") -> str:
    """A type specimen block in the direction's own heading face, with mono metadata."""
    parts = ['<line x1="0" y1="40" x2="800" y2="40" stroke="%s"/><line x1="0" y1="560" x2="800" y2="560" stroke="%s"/>' % (C["border"], C["border"])]
    parts.append('<text x="16" y="330" style="font-family:var(--pf-font-heading);font-size:300px;font-weight:600;letter-spacing:-.04em" fill="%s">Aa</text>' % C["text"])
    parts.append('<text x="470" y="200" style="font-family:var(--pf-font-heading);font-size:72px" fill="%s">Rg</text>' % C["primary"])
    parts.append('<text x="470" y="330" style="font-family:var(--pf-font-heading);font-size:40px;font-variant-numeric:tabular-nums" fill="%s">0123456789</text>' % C["text"])
    for i, m in enumerate(["Display 300 px", "Weight 600", "Tracking -4", "Leading 0.9"]):
        parts.append('<text x="%d" y="520" style="font-family:var(--pf-font-mono);font-size:12px;letter-spacing:.06em" fill="%s">%s</text>' % (24 + i * 190, C["muted"], E(m)))
    return _svg(800, 600, "".join(parts), label, "pfd-art-specimen")


def pixel(seed: str, label: str = "") -> str:
    """A coarse symmetric pixel shape, like an 8-bit mark."""
    r = _rng(seed, "pixel")
    n, cell = 12, 50
    grid = [[0] * n for _ in range(n)]
    for j in range(n):
        for i in range(n // 2):
            d = math.hypot(i - n / 2 + 0.5, j - n / 2 + 0.5)
            on = (d < n * 0.2) or (d < n * 0.42 and r.random() < 0.72)
            grid[j][i] = grid[j][n - 1 - i] = 1 if on else 0
    parts = []
    for j in range(n):
        for i in range(n):
            if grid[j][i]:
                parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (i * cell, j * cell, cell - 2, cell - 2, C["primary"] if (i + j) % 7 == 0 else C["text"]))
    return _svg(600, 600, "".join(parts), label, "pfd-art-pixel")


def scan(seed: str, label: str = "") -> str:
    """An oscilloscope panel: grid, one primary waveform, scanlines."""
    r = _rng(seed, "scan")
    pid = "pfsl-" + E(seed).replace(" ", "")
    parts = ['<rect width="800" height="500" fill="%s"/>' % C["surface"]]
    parts.append('<defs><pattern id="%s" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="%s" opacity=".1"/></pattern></defs>' % (pid, C["text"]))
    for gx in range(0, 800, 50):
        parts.append('<line x1="%d" y1="0" x2="%d" y2="500" stroke="%s" opacity=".15"/>' % (gx, gx, C["text"]))
    for gy in range(0, 500, 50):
        parts.append('<line x1="0" y1="%d" x2="800" y2="%d" stroke="%s" opacity=".15"/>' % (gy, gy, C["text"]))
    f = r.uniform(1.5, 3.5)
    pts = " ".join("%d,%.0f" % (x, 250 + math.sin(x / 800 * math.tau * f) * 120 * math.exp(-((x - 400) / 300) ** 2)) for x in range(0, 801, 4))
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (pts, C["primary"]))
    parts.append('<rect width="800" height="500" fill="url(#%s)"/>' % pid)
    return _svg(800, 500, "".join(parts), label, "pfd-art-scan")


def grain_disc(seed: str, label: str = "") -> str:
    """One large flat disc with film grain, no gradient, and a horizon line."""
    r = _rng(seed, "grain")
    fid = "pfgr-" + E(seed).replace(" ", "")
    cx = r.randint(300, 520)
    parts = ['<defs><filter id="%s"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
             '<feColorMatrix type="saturate" values="0"/><feColorMatrix values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 .5 0"/>'
             '<feComposite in2="SourceGraphic" operator="in"/></filter></defs>' % fid]
    parts.append('<circle cx="%d" cy="300" r="230" fill="%s"/><circle cx="%d" cy="300" r="230" fill="%s" filter="url(#%s)"/>' % (cx, C["primary"], cx, C["text"], fid))
    parts.append('<line x1="0" y1="440" x2="800" y2="440" stroke="%s" stroke-width="1.5"/>' % C["text"])
    return _svg(800, 600, "".join(parts), label, "pfd-art-grain")


def ticket(seed: str, label: str = "") -> str:
    """A ticket with a perforation, a serial number and a barcode."""
    r = _rng(seed, "ticket")
    parts = ['<rect x="2" y="2" width="796" height="316" rx="10" fill="%s" stroke="%s" stroke-width="2"/>' % (C["raised"], C["text"])]
    parts.append('<line x1="560" y1="2" x2="560" y2="318" stroke="%s" stroke-width="2" stroke-dasharray="6 8"/><circle cx="560" cy="2" r="14" fill="%s"/><circle cx="560" cy="318" r="14" fill="%s"/>' % (C["text"], C["bg"], C["bg"]))
    parts.append('<text x="36" y="80" style="font-family:var(--pf-font-mono);font-size:12px;letter-spacing:.06em" fill="%s">Admit one · 2026</text>' % C["muted"])
    parts.append('<text x="36" y="190" style="font-family:var(--pf-font-heading);font-size:88px;font-weight:600;letter-spacing:-.03em" fill="%s">No. %03d</text>' % (C["text"], r.randint(1, 999)))
    parts.append('<rect x="36" y="230" width="260" height="34" fill="%s"/>' % C["primary"])
    x = 600
    while x < 770:
        wd = r.choice([2, 2, 3, 5])
        parts.append('<rect x="%d" y="60" width="%d" height="200" fill="%s"/>' % (x, wd, C["text"]))
        x += wd + r.choice([2, 3, 4])
    return _svg(800, 320, "".join(parts), label, "pfd-art-ticket")


GENERATORS.update({
    "ascii": ascii_field, "dither": dither, "flowfield": flowfield, "strands": strands, "stamp": stamp, "ruler": ruler,
    "globe": globe, "specimen": specimen, "pixel": pixel, "scan": scan, "grain_disc": grain_disc, "ticket": ticket,
})


def render(kind: str, seed: str = "A", label: str = "") -> str:
    return GENERATORS.get(kind, blueprint)(seed, label)
