"""Palette resolution (OKLCH to hex, overrides, contrast checks) and token CSS."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from contrast import (  # noqa: E402
    best_on_colour,
    format_oklch,
    grade,
    hex_to_oklch,
    oklch_to_hex,
    parse_oklch,
    to_hex,
)

ROLES = [
    "bg", "surface", "surface_raised", "text", "text_muted", "border",
    "primary", "on_primary", "accent", "on_accent",
    "success", "warning", "danger", "focus",
]

DEFAULT_CHECKS = [
    {"fg": "text", "bg": "bg", "role": "body"},
    {"fg": "text", "bg": "surface", "role": "body"},
    {"fg": "text", "bg": "surface_raised", "role": "body"},
    {"fg": "on_primary", "bg": "primary", "role": "label"},
    {"fg": "on_accent", "bg": "accent", "role": "label"},
    {"fg": "text_muted", "bg": "bg", "role": "large"},
    {"fg": "focus", "bg": "bg", "role": "ui"},
    {"fg": "danger", "bg": "bg", "role": "ui"},
    {"fg": "primary", "bg": "bg", "role": "ui"},
]

RADIUS = {
    "none": dict(xs="0", sm="0", md="0", lg="0", xl="0", full="0"),
    "sm": dict(xs="0.125rem", sm="0.25rem", md="0.375rem", lg="0.5rem", xl="0.75rem", full="9999px"),
    "md": dict(xs="0.25rem", sm="0.375rem", md="0.5rem", lg="0.75rem", xl="1rem", full="9999px"),
    "lg": dict(xs="0.375rem", sm="0.5rem", md="0.75rem", lg="1rem", xl="1.5rem", full="9999px"),
    "pill": dict(xs="0.5rem", sm="0.75rem", md="1rem", lg="1.5rem", xl="2rem", full="9999px"),
}
DENSITY = {"airy": 1.25, "regular": 1.0, "compact": 0.75}
TYPE_STEPS = [("xs", -2), ("sm", -1), ("base", 0), ("lg", 0.5), ("xl", 1), ("2xl", 2), ("3xl", 3), ("4xl", 4), ("5xl", 5)]
MONO_FALLBACK = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def _checks_spec() -> List[dict]:
    try:
        return _common.load_schema().get("palette_checks", DEFAULT_CHECKS)
    except (OSError, ValueError):
        return DEFAULT_CHECKS


def _entry(value: str) -> Dict[str, str]:
    """Normalise a colour given as oklch(...) or #hex into both renderings."""
    if value.strip().startswith("#"):
        hx = to_hex(value)
        return {"oklch": format_oklch(*hex_to_oklch(hx)), "hex": hx}
    l, c, h = parse_oklch(value)
    return {"oklch": format_oklch(l, c, h), "hex": oklch_to_hex(l, c, h)}


def resolve_palette(palette: dict, overrides: Optional[dict] = None) -> dict:
    """Render a palette node to hex in both modes, apply brand overrides, run checks."""
    overrides = overrides or {}
    out: dict = {"id": palette.get("id"), "name": palette.get("name"), "light": {}, "dark": {}, "checks": [], "warnings": []}
    for mode in ("light", "dark"):
        table = palette[mode]
        for role in ROLES:
            out[mode][role] = _entry(table[role])
        brand_primary = overrides.get("brand_primary")
        brand_accent = overrides.get("brand_accent")
        if brand_primary:
            out[mode]["primary"] = _entry(brand_primary)
            out[mode]["on_primary"] = _entry(best_on_colour(out[mode]["primary"]["hex"]))
        if brand_accent:
            out[mode]["accent"] = _entry(brand_accent)
            out[mode]["on_accent"] = _entry(best_on_colour(out[mode]["accent"]["hex"]))
        for check in _checks_spec():
            g = grade(out[mode][check["fg"]]["hex"], out[mode][check["bg"]]["hex"], check["role"])
            rec = {
                "mode": mode,
                "pair": "%s on %s" % (check["fg"], check["bg"]),
                "fg_role": check["fg"],
                "bg_role": check["bg"],
                "role": check["role"],
                "wcag": g["wcag"],
                "apca": g["apca"],
                "ok": g["ok"],
            }
            out["checks"].append(rec)
            if not g["ok"]:
                out["warnings"].append(
                    "%s: %s fails %s contrast (WCAG %.2f, APCA %.0f)" % (mode, rec["pair"], check["role"], g["wcag"], g["apca"])
                )
    return out


def tokens_css(resolved: dict, selector: str = ":root", scheme: str = "both") -> str:
    """CSS custom properties for a resolved palette: light under ``selector``, dark under
    ``[data-theme="dark"]`` and the system preference when no explicit theme is set."""

    def block(sel: str, mode: str, extra: str = "") -> str:
        lines = [sel + " {"]
        if extra:
            lines.append("  " + extra)
        for role in ROLES:
            e = resolved[mode][role]
            lines.append("  --pf-color-%s: %s;" % (role.replace("_", "-"), e["hex"]))
            lines.append("  --pf-color-%s-oklch: %s;" % (role.replace("_", "-"), e["oklch"]))
        lines.append("}")
        return "\n".join(lines)

    light_sel = selector
    dark_sel = selector + '[data-theme="dark"]' if selector != ":root" else '[data-theme="dark"]'
    if selector.startswith("["):
        dark_sel = '[data-theme="dark"] %s, %s[data-theme="dark"]' % (selector, selector)
    auto_sel = (":root:not([data-theme=\"light\"])" if selector == ":root"
                else ':root:not([data-theme="light"]) %s' % selector)
    parts = [block(light_sel, "light", "color-scheme: light dark;")]
    if scheme in ("both", "dark"):
        parts.append(block(dark_sel, "dark"))
        parts.append("@media (prefers-color-scheme: dark) {\n" + _indent(block(auto_sel, "dark")) + "\n}")
    return "\n".join(parts) + "\n"


def _indent(text: str) -> str:
    return "\n".join("  " + line for line in text.splitlines())


def _fmt(value: float) -> str:
    from decimal import ROUND_HALF_UP, Decimal

    s = str(Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return s or "0"


def _font_stack(face: dict, fallback: str) -> str:
    family = face["family"]
    quoted = family if family.startswith(("system-ui", "-apple-system", "ui-")) else "'%s'" % family
    return "%s, %s" % (quoted, fallback)


def scale_tokens(radius_scale: str, density: str, pairing: dict) -> str:
    """Radius, spacing, type scale and font tokens."""
    lines = [":root {"]
    for key, val in RADIUS[radius_scale].items():
        lines.append("  --pf-radius-%s: %s;" % (key, val))
    factor = DENSITY[density]
    for n in range(1, 13):
        lines.append("  --pf-space-%d: %srem;" % (n, _fmt(n * 0.25 * factor)))
    ratio = float(pairing.get("scale_ratio", 1.25))
    for name, power in TYPE_STEPS:
        lines.append("  --pf-text-%s: %srem;" % (name, _fmt(ratio ** power)))
    lines.append("  --pf-font-heading: %s;" % _font_stack(pairing["heading"], pairing["fallback_heading"]))
    lines.append("  --pf-font-body: %s;" % _font_stack(pairing["body"], pairing["fallback_body"]))
    mono = pairing.get("mono")
    lines.append("  --pf-font-mono: %s;" % (_font_stack(mono, MONO_FALLBACK) if mono else MONO_FALLBACK))
    body_serif = str(pairing["body"].get("category", "")).startswith("serif")
    lines.append("  --pf-leading-tight: 1.15;")
    lines.append("  --pf-leading-normal: %s;" % ("1.6" if body_serif else "1.5"))
    lines.append("  --pf-leading-loose: 1.75;")
    lines.append("  --pf-measure: %sch;" % pairing.get("measure_ch", 66))
    lines.append("  --pf-density: %s;" % _fmt(factor))
    lines.append("}")
    return "\n".join(lines) + "\n"


def motion_tokens(level: int) -> str:
    """Duration and easing tokens for a motion level 0..3."""
    if level <= 0:
        dur = dict(fast="0ms", base="0ms", slow="0ms", page="0ms")
    elif level == 1:
        dur = dict(fast="120ms", base="200ms", slow="320ms", page="240ms")
    elif level == 2:
        dur = dict(fast="140ms", base="240ms", slow="400ms", page="320ms")
    else:
        dur = dict(fast="160ms", base="280ms", slow="480ms", page="400ms")
    lines = [":root {"]
    for k, v in dur.items():
        lines.append("  --pf-dur-%s: %s;" % (k, v))
    lines.append("  --pf-ease-out: cubic-bezier(0.23, 1, 0.32, 1);")
    lines.append("  --pf-ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);")
    lines.append("  --pf-ease-in: cubic-bezier(0.4, 0, 1, 1);")
    lines.append("  --pf-ease-spring: linear(0, 0.4 20%, 0.95 45%, 1.04 65%, 1);")
    lines.append("  --pf-motion-level: %d;" % level)
    lines.append("}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- deriving from a few colours

def _shift(l: float, c: float, h: float, dl: float = 0.0, cm: float = 1.0, dh: float = 0.0) -> str:
    return format_oklch(min(1.0, max(0.0, l + dl)), max(0.0, c * cm), (h + dh) % 360)


def derive_roles(bg_hex: str, text_hex: str, primary_hex: str, accent_hex: Optional[str] = None) -> dict:
    """Build full light and dark role tables from a background, a text colour and a primary.
    Used when importing an existing look. Returned values are oklch strings; callers run
    ``resolve_palette`` to check them."""
    bl, bc, bh = hex_to_oklch(bg_hex)
    tl, tc, th = hex_to_oklch(text_hex)
    pl, pc, ph = hex_to_oklch(primary_hex)
    if accent_hex:
        al, ac, ah = hex_to_oklch(accent_hex)
    else:
        al, ac, ah = pl, pc, (ph + 40) % 360
    light_bg_is_light = bl >= 0.5

    def table(bg, text, prim, acc, dark: bool) -> Dict[str, str]:
        (bl_, bc_, bh_), (tl_, tc_, th_), (pl_, pc_, ph_), (al_, ac_, ah_) = bg, text, prim, acc
        sign = 1 if dark else -1
        roles = {
            "bg": format_oklch(bl_, bc_, bh_),
            "surface": _shift(bl_, bc_, bh_, dl=sign * 0.03),
            "surface_raised": _shift(bl_, bc_, bh_, dl=sign * 0.06),
            "text": format_oklch(tl_, tc_, th_),
            "text_muted": format_oklch(tl_ + (bl_ - tl_) * 0.35, tc_, th_),
            "border": _shift(bl_, bc_, bh_, dl=sign * 0.14),
            "primary": format_oklch(pl_, pc_, ph_),
            "accent": format_oklch(al_, ac_, ah_),
            "success": format_oklch(0.72 if dark else 0.5, 0.14, 150),
            "warning": format_oklch(0.8 if dark else 0.62, 0.14, 80),
            "danger": format_oklch(0.72 if dark else 0.52, 0.19, 25),
            "focus": format_oklch(pl_, pc_, ph_),
        }
        roles["on_primary"] = format_oklch(*hex_to_oklch(best_on_colour(oklch_to_hex(pl_, pc_, ph_))))
        roles["on_accent"] = format_oklch(*hex_to_oklch(best_on_colour(oklch_to_hex(al_, ac_, ah_))))
        return roles

    light = table((bl, bc, bh), (tl, tc, th), (pl, pc, ph), (al, ac, ah), dark=not light_bg_is_light)
    # Dark counterpart: keep hues, invert lightness, lower chroma.
    dark = table(
        (0.16, min(bc, 0.02), bh), (0.95, min(tc, 0.02), th),
        (max(pl, 0.72), pc * 0.8, ph), (max(al, 0.74), ac * 0.8, ah), dark=True,
    )
    if light_bg_is_light:
        return {"light": light, "dark": dark}
    # The imported look is already dark: it becomes the dark set, and a light set is synthesised.
    synth_light = table((0.985, min(bc, 0.01), bh), (0.2, min(tc, 0.02), th),
                        (min(pl, 0.5), pc, ph), (min(al, 0.52), ac, ah), dark=False)
    return {"light": synth_light, "dark": light}
