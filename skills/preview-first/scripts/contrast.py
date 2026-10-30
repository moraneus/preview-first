"""Colour maths: sRGB, OKLCH, WCAG 2 contrast and APCA (0.1.9) lightness contrast.

Standard library only. All hex values are lowercase ``#rrggbb``.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from typing import Dict, Sequence, Tuple

RGB = Tuple[float, float, float]

# WCAG 2 thresholds by role, APCA Lc thresholds by role.
# body: running text. label: button and form labels, 14px+ at medium weight.
# large: 24px+ or 19px bold. ui: non-text indicators, borders, focus rings.
WCAG_MIN = {"body": 4.5, "label": 4.5, "large": 3.0, "ui": 3.0}
APCA_MIN = {"body": 60.0, "label": 45.0, "large": 45.0, "ui": 30.0}


# ---------------------------------------------------------------- hex / rgb

def hex_to_rgb(value: str) -> RGB:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    if len(v) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", v):
        raise ValueError("bad hex colour: %r" % value)
    return tuple(int(v[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: Sequence[float]) -> str:
    return "#" + "".join("%02x" % int(round(_clamp01(c) * 255)) for c in rgb)


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def in_gamut(rgb: Sequence[float], tol: float = 1e-4) -> bool:
    return all(-tol <= c <= 1 + tol for c in rgb)


# ---------------------------------------------------------------- transfer

def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1 / 2.4)) - 0.055


# ---------------------------------------------------------------- OKLab / OKLCH

def _linear_rgb_to_oklab(r: float, g: float, b: float) -> Tuple[float, float, float]:
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = _cbrt(l), _cbrt(m), _cbrt(s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def _oklab_to_linear_rgb(L: float, a: float, b: float) -> RGB:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def oklch_to_rgb(l: float, c: float, h: float) -> RGB:
    """OKLCH (L 0..1, C, H degrees) to gamma-encoded sRGB floats, possibly out of gamut."""
    hr = math.radians(h)
    a, b = c * math.cos(hr), c * math.sin(hr)
    lin = _oklab_to_linear_rgb(l, a, b)
    return tuple(_linear_to_srgb(x) if x > 0 else -_linear_to_srgb(-x) for x in lin)  # type: ignore[return-value]


def rgb_to_oklch(rgb: Sequence[float]) -> Tuple[float, float, float]:
    lin = [_srgb_to_linear(c) for c in rgb]
    L, a, b = _linear_rgb_to_oklab(*lin)
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360 if c > 1e-6 else 0.0
    return (L, c, h)


def oklch_to_hex(l: float, c: float, h: float) -> str:
    """Render OKLCH to hex. Slightly out-of-gamut values (rounding noise) are
    clamped; genuinely out-of-gamut values have their chroma reduced by binary
    search until the colour fits sRGB, keeping lightness and hue."""
    rgb = oklch_to_rgb(l, c, h)
    if in_gamut(rgb, tol=0.003):
        return rgb_to_hex(rgb)
    lo, hi = 0.0, c
    for _ in range(24):
        mid = (lo + hi) / 2
        if in_gamut(oklch_to_rgb(l, mid, h), tol=0.003):
            lo = mid
        else:
            hi = mid
    return rgb_to_hex(oklch_to_rgb(l, lo, h))


def hex_to_oklch(value: str) -> Tuple[float, float, float]:
    return rgb_to_oklch(hex_to_rgb(value))


def format_oklch(l: float, c: float, h: float) -> str:
    return "oklch(%.3f %.3f %.1f)" % (l, c, h)


_OKLCH_RE = re.compile(
    r"oklch\(\s*([0-9.]+)(%?)\s+([0-9.]+)\s+([0-9.]+)(deg)?\s*(?:/\s*[0-9.%]+)?\s*\)",
    re.IGNORECASE,
)


def parse_oklch(text: str) -> Tuple[float, float, float]:
    m = _OKLCH_RE.fullmatch(text.strip())
    if not m:
        raise ValueError("bad oklch value: %r" % text)
    l = float(m.group(1))
    if m.group(2) == "%":
        l /= 100.0
    return (l, float(m.group(3)), float(m.group(4)))


def to_hex(value: str) -> str:
    """Accept ``#hex`` or ``oklch(...)`` and return hex."""
    v = value.strip()
    if v.startswith("#"):
        return rgb_to_hex(hex_to_rgb(v))
    return oklch_to_hex(*parse_oklch(v))


# ---------------------------------------------------------------- WCAG 2

def relative_luminance(rgb: Sequence[float]) -> float:
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_ratio(fg: str, bg: str) -> float:
    lf, lb = relative_luminance(hex_to_rgb(fg)), relative_luminance(hex_to_rgb(bg))
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- APCA 0.1.9

_SA98G = dict(
    mainTRC=2.4,
    sRco=0.2126729, sGco=0.7151522, sBco=0.0721750,
    normBG=0.56, normTXT=0.57, revTXT=0.62, revBG=0.65,
    blkThrs=0.022, blkClmp=1.414, scaleBoW=1.14, scaleWoB=1.14,
    loBoWOffset=0.027, loWoBOffset=0.027, loClip=0.1, deltaYmin=0.0005,
)


def _apca_y(rgb: Sequence[float]) -> float:
    g = _SA98G
    r, gg, b = (c ** g["mainTRC"] for c in rgb)
    return g["sRco"] * r + g["sGco"] * gg + g["sBco"] * b


def apca_lc(text: str, bg: str) -> float:
    g = _SA98G
    ytxt, ybg = _apca_y(hex_to_rgb(text)), _apca_y(hex_to_rgb(bg))

    def soft_clamp(y: float) -> float:
        return y if y > g["blkThrs"] else y + (g["blkThrs"] - y) ** g["blkClmp"]

    ytxt, ybg = soft_clamp(ytxt), soft_clamp(ybg)
    if abs(ybg - ytxt) < g["deltaYmin"]:
        return 0.0
    if ybg > ytxt:  # dark text on light background
        sapc = (ybg ** g["normBG"] - ytxt ** g["normTXT"]) * g["scaleBoW"]
        out = 0.0 if sapc < g["loClip"] else sapc - g["loBoWOffset"]
    else:  # light text on dark background
        sapc = (ybg ** g["revBG"] - ytxt ** g["revTXT"]) * g["scaleWoB"]
        out = 0.0 if sapc > -g["loClip"] else sapc + g["loWoBOffset"]
    return out * 100.0


# ---------------------------------------------------------------- grading

def grade(fg: str, bg: str, role: str = "body") -> Dict[str, object]:
    if role not in WCAG_MIN:
        raise ValueError("role must be one of %s" % sorted(WCAG_MIN))
    ratio = wcag_ratio(fg, bg)
    lc = apca_lc(fg, bg)
    wcag_pass = ratio >= WCAG_MIN[role]
    apca_pass = abs(lc) >= APCA_MIN[role]
    return {
        "fg": fg.lower(),
        "bg": bg.lower(),
        "role": role,
        "wcag": round(ratio, 2),
        "apca": round(lc, 1),
        "wcag_pass": wcag_pass,
        "apca_pass": apca_pass,
        "ok": wcag_pass and apca_pass,
        "wcag_level": "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "AA-large" if ratio >= 3 else "fail",
    }


def best_on_colour(bg: str, candidates: Sequence[str] = ("#ffffff", "#111111")) -> str:
    return max(candidates, key=lambda c: wcag_ratio(c, bg))


# ---------------------------------------------------------------- CLI

def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Grade a foreground/background pair (hex or oklch).")
    ap.add_argument("fg")
    ap.add_argument("bg")
    ap.add_argument("--role", default="body", choices=sorted(WCAG_MIN))
    ns = ap.parse_args(list(argv))
    print(json.dumps(grade(to_hex(ns.fg), to_hex(ns.bg), ns.role), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
