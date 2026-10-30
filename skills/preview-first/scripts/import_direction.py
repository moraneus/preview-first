"""Import an existing look (CSS, Tailwind config, DTCG tokens or a URL) as a comparable direction.

Usage:
  import_direction.py (--css PATH | --tailwind PATH | --tokens PATH | --url URL) [--into directions.json] [--name NAME] [--id X]

The result is a direction with an inline palette and type pairing, so it appears in the preview
next to generated directions on equal terms.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
from contrast import hex_to_oklch, hex_to_rgb, rgb_to_hex, wcag_ratio  # noqa: E402
from palette import derive_roles  # noqa: E402

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}\"]+|\"[^\"]*\"[^;}]*)", re.I)
RADIUS_RE = re.compile(r"border-radius\s*:\s*([0-9.]+)px", re.I)
GENERIC = {"serif", "sans-serif", "monospace", "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace", "cursive", "fantasy",
           "inherit", "initial", "unset", "-apple-system", "blinkmacsystemfont", "segoe ui", "roboto", "helvetica neue", "arial",
           "noto sans", "liberation sans", "apple color emoji", "segoe ui emoji", "georgia", "times new roman", "menlo", "monaco", "consolas", "courier new"}
USER_AGENT = "preview-first/%s" % _common.VERSION
FAMILY_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _+.-]{0,63}$")


def _valid_family(fam: str) -> bool:
    """Imported names reach generated CSS and HTML, so only plain family names are accepted."""
    return bool(fam) and bool(FAMILY_OK.match(fam)) and fam.lower() not in GENERIC and not fam.lower().startswith("var(")


def _norm_hex(h: str) -> str:
    return rgb_to_hex(hex_to_rgb(h))


def _collect(text: str) -> dict:
    colours = Counter(_norm_hex(h) for h in HEX_RE.findall(text))
    fonts: List[str] = []
    for m in FONT_RE.findall(text):
        for fam in m.split(","):
            fam = fam.strip().strip("'\"").strip()
            if _valid_family(fam) and fam not in fonts:
                fonts.append(fam)
    radii = sorted({int(round(float(r))) for r in RADIUS_RE.findall(text) if float(r) > 0})
    return {"colors": [c for c, _ in colours.most_common()], "fonts": fonts, "radius": radii}


# ---------------------------------------------------------------- parsers

_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_HEADING_SEL = re.compile(r"\bh[1-6]\b|heading|title|display", re.I)
_BODY_SEL = re.compile(r":root|\bhtml\b|\bbody\b", re.I)


def _fonts_in(block: str) -> List[str]:
    out = []
    for m in FONT_RE.findall(block):
        for fam in m.split(","):
            fam = fam.strip().strip("'\"").strip()
            if _valid_family(fam) and fam not in out:
                out.append(fam)
    return out


def from_css(text: str) -> dict:
    obs = _collect(text)
    heading_fonts: List[str] = []
    body_fonts: List[str] = []
    for selector, block in _RULE_RE.findall(text):
        fams = _fonts_in(block)
        if not fams:
            continue
        if _HEADING_SEL.search(selector):
            heading_fonts += [f for f in fams if f not in heading_fonts]
        elif _BODY_SEL.search(selector):
            body_fonts += [f for f in fams if f not in body_fonts]
    obs["heading_fonts"] = heading_fonts
    obs["body_fonts"] = body_fonts
    obs["source"] = "css"
    return obs


def from_tailwind_config(text: str) -> dict:
    obs = _collect(text)
    # font families written as arrays: ["Manrope", "system-ui", ...]
    for arr in re.findall(r"\[([^\]]+)\]", text):
        for fam in arr.split(","):
            fam = fam.strip().strip("'\"").strip()
            if _valid_family(fam) and fam[0].isupper() and fam not in obs["fonts"]:
                obs["fonts"].append(fam)
    radii = {int(round(float(r))) for r in re.findall(r"\"?(?:xl|2xl|3xl|lg|md|sm|DEFAULT)\"?\s*:\s*\"([0-9.]+)px\"", text)}
    obs["radius"] = sorted(set(obs["radius"]) | radii)
    obs["source"] = "tailwind"
    return obs


def from_dtcg(tokens: dict) -> dict:
    colours: List[str] = []
    fonts: List[str] = []
    radii: List[int] = []

    def walk(node, path):
        if isinstance(node, dict) and "$value" in node:
            t, v = node.get("$type"), node["$value"]
            if t == "color" and isinstance(v, str) and HEX_RE.fullmatch(v.strip()):
                colours.append(_norm_hex(v.strip()))
            elif t == "fontFamily":
                fam = v[0] if isinstance(v, list) and v else v
                if isinstance(fam, str) and _valid_family(fam) and fam not in fonts:
                    fonts.append(fam)
            elif t == "dimension" and "radius" in "/".join(path).lower() and isinstance(v, str) and v.endswith("px"):
                radii.append(int(round(float(v[:-2]))))
        elif isinstance(node, dict):
            for k, sub in node.items():
                walk(sub, path + [k])

    walk(tokens, [])
    return {"colors": colours, "fonts": fonts, "radius": sorted(set(radii)), "source": "tokens"}


def _fetch(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def from_url(url: str, fetcher: Callable[..., str] = _fetch) -> dict:
    """Read a page's inline styles and same-origin stylesheets. Cross-origin CSS is ignored."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("only http(s) URLs can be imported")
    html = fetcher(url)
    texts = [html]
    origin = (parsed.scheme, parsed.netloc)
    for href in re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)[\"']", html, re.I) + \
            re.findall(r"<link[^>]+href=[\"']([^\"']+)[\"'][^>]*rel=[\"']stylesheet[\"']", html, re.I):
        full = urllib.parse.urljoin(url, href)
        p = urllib.parse.urlparse(full)
        if (p.scheme, p.netloc) != origin:
            continue
        try:
            texts.append(fetcher(full))
        except Exception:
            continue
    obs = _collect("\n".join(texts))
    obs["source"] = url
    return obs


# ---------------------------------------------------------------- direction

def _pick_roles(colours: List[str]) -> Dict[str, str]:
    if not colours:
        colours = ["#ffffff", "#111111", "#1d4ed8"]
    by_l = sorted(colours, key=lambda h: hex_to_oklch(h)[0])
    darkest, lightest = by_l[0], by_l[-1]
    # background is whichever extreme is more frequent in the source order (colours arrive by frequency)
    bg = lightest if colours.index(lightest) <= colours.index(darkest) else darkest
    text = darkest if bg == lightest else lightest
    if wcag_ratio(text, bg) < 4.5:
        text = "#111111" if hex_to_oklch(bg)[0] > 0.5 else "#f5f5f5"
    chromatic = [h for h in colours if hex_to_oklch(h)[1] > 0.06 and h not in (bg, text)]
    primary = chromatic[0] if chromatic else ("#1d4ed8" if hex_to_oklch(bg)[0] > 0.5 else "#7aa2f7")
    accent = next((h for h in chromatic[1:] if abs(hex_to_oklch(h)[2] - hex_to_oklch(primary)[2]) > 30), None)
    return {"bg": bg, "text": text, "primary": primary, "accent": accent}


def _nearest_style(bg: str, fonts: List[str], radii: List[int], graph: dict) -> str:
    idx = _common.node_index(graph)
    dark = hex_to_oklch(bg)[0] < 0.5
    heading = (fonts[0] if fonts else "").lower()
    serif_hint = any(w in heading for w in ("serif", "fraunces", "newsreader", "playfair", "garamond", "caslon", "literata", "lora", "tiempos", "editorial"))
    if dark:
        choice = "style.dark-console"
    elif serif_hint:
        choice = "style.paper-editorial"
    elif radii and max(radii) == 0:
        choice = "style.swiss-grid"
    elif radii and max(radii) >= 16:
        choice = "style.soft-product"
    else:
        choice = "style.mono-engineering"
    return choice if choice in idx else next(n["id"] for n in graph["nodes"] if n["kind"] == "style")


def _category(family: str) -> str:
    f = family.lower()
    if any(w in f for w in ("mono", "code")):
        return "mono"
    if any(w in f for w in ("serif", "fraunces", "newsreader", "playfair", "garamond", "caslon", "literata", "lora", "merriweather")):
        return "serif-transitional"
    if any(w in f for w in ("grotesk", "geist", "inter", "helvetica", "roboto", "arial")):
        return "neo-grotesque"
    return "humanist"


def _google_url(families: List[str]) -> Optional[str]:
    fams = [f for f in families if f]
    if not fams:
        return None
    parts = ["family=%s:wght@400;500;600" % urllib.parse.quote(f).replace("%20", "+") for f in fams]
    return "https://fonts.googleapis.com/css2?%s&display=swap" % "&".join(parts)


def to_direction(observed: dict, graph: dict, id: str = "X", name: str = "Current look") -> dict:
    roles = _pick_roles(list(observed.get("colors", [])))
    tables = derive_roles(roles["bg"], roles["text"], roles["primary"], roles.get("accent"))
    dark_first = hex_to_oklch(roles["bg"])[0] < 0.5
    palette = {
        "id": "palette.imported-%s" % _common.slugify(name) or "palette.imported",
        "kind": "palette", "name": "Imported from %s" % observed.get("source", "existing styles"),
        "temperature": "neutral", "scheme": "dark" if dark_first else "light", "hue_family": "imported",
        "light": tables["light"], "dark": tables["dark"],
        "source": observed.get("source", "import"), "added": _common.today(), "last_verified": _common.today(), "confidence": 0.5,
    }
    fonts = list(observed.get("fonts", []))
    heading_fonts = list(observed.get("heading_fonts") or [])
    body_fonts = list(observed.get("body_fonts") or [])
    heading = heading_fonts[0] if heading_fonts else (fonts[0] if fonts else "system-ui")
    body = body_fonts[0] if body_fonts else next((f for f in fonts if f != heading), heading)
    hcat, bcat = _category(heading), _category(body)
    pairing = {
        "id": "type-pairing.imported-%s" % _common.slugify(name) or "type-pairing.imported",
        "kind": "type-pairing", "name": "%s / %s" % (heading, body),
        "heading": {"family": heading, "category": hcat, "weights": [600], "source": "system" if heading == "system-ui" else "google"},
        "body": {"family": body, "category": bcat, "weights": [400, 500], "source": "system" if body == "system-ui" else "google"},
        "fallback_heading": "Georgia, 'Times New Roman', serif" if hcat.startswith("serif") else "system-ui, -apple-system, 'Segoe UI', sans-serif",
        "fallback_body": "system-ui, -apple-system, 'Segoe UI', sans-serif",
        "scale_ratio": 1.25, "measure_ch": 66, "license": "unknown (imported)",
        "css_url": _google_url([f for f in {heading, body} if f != "system-ui"]),
        "source": observed.get("source", "import"), "added": _common.today(), "last_verified": _common.today(), "confidence": 0.5,
        "notes": "Imported from the existing styles; verify the licence and loading before shipping.",
    }
    if not pairing["css_url"]:
        pairing.pop("css_url")
    style_id = _nearest_style(roles["bg"], fonts, list(observed.get("radius", [])), graph)
    idx = _common.node_index(graph)
    style = idx[style_id]
    treatments = {}
    motion = []
    for e in graph.get("edges", []):
        if e["from"] == style_id and e["kind"] == "defaults_to":
            node = idx.get(e["to"])
            if not node:
                continue
            if node["kind"] == "treatment":
                treatments[node["axis"]] = node["value"]
            elif node["kind"] == "motion-pattern" and node.get("level", 0) <= 1:
                motion.append(node["id"])
    radii = list(observed.get("radius", []))
    radius_scale = "none" if radii and max(radii) == 0 else "sm" if not radii or max(radii) <= 8 else "md" if max(radii) <= 12 else "lg" if max(radii) <= 20 else "pill"
    icon = next((e["to"] for e in graph.get("edges", []) if e["from"] == style_id and e["kind"] == "pairs_with" and e["to"].startswith("icon-set.")), "icon-set.lucide")
    return {
        "id": id,
        "name": name,
        "rationale": "The look the project already has, rebuilt as a direction so it can be compared on equal terms. Nearest style: %s." % style["name"],
        "bundle": {
            "style": style_id, "style_family": style["family"], "palette": palette, "type_pairing": pairing, "treatments": treatments,
            "motion": sorted(motion), "motion_level": 1, "icon_set": icon, "radius_scale": radius_scale, "density": style.get("density", "regular"),
            "alternatives": {"palettes": [], "type_pairings": [], "icon_sets": []},
        },
        "imported": {"colors": observed.get("colors", [])[:12], "fonts": fonts, "radius": radii, "source": observed.get("source")},
    }


# ---------------------------------------------------------------- CLI

def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Import an existing look as a preview-first direction.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--css")
    src.add_argument("--tailwind")
    src.add_argument("--tokens")
    src.add_argument("--url")
    ap.add_argument("--into", help="directions.json to append to (otherwise print the direction)")
    ap.add_argument("--name", default="Current look")
    ap.add_argument("--id")
    ap.add_argument("--graph", default=str(_common.KNOWLEDGE_DIR / "graph.json"))
    ns = ap.parse_args(list(argv))
    if ns.css:
        obs = from_css(Path(ns.css).read_text(encoding="utf-8"))
    elif ns.tailwind:
        obs = from_tailwind_config(Path(ns.tailwind).read_text(encoding="utf-8"))
    elif ns.tokens:
        obs = from_dtcg(_common.load_json(ns.tokens))
    else:
        obs = from_url(ns.url)
    graph = _common.load_json(ns.graph)
    if ns.into:
        directions = _common.load_json(ns.into)
        used = {d["id"] for d in directions["directions"]}
        new_id = ns.id or next(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in used)
        directions["directions"].append(to_direction(obs, graph, new_id, ns.name))
        _common.dump_json(ns.into, directions)
        print(json.dumps({"added": new_id, "into": ns.into, "observed": obs}, indent=2))
    else:
        print(json.dumps(to_direction(obs, graph, ns.id or "X", ns.name), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
