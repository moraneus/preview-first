"""Merge the research sweep (ideas-*.json, sites-*.json) into graph.json as idea and reference-site nodes.

Idempotent: existing ids are skipped. Dev tool, not shipped with the skill.

    uv run python3 tools/merge_ideas.py /path/to/research-dir
"""
import glob, json, re, sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "skills/preview-first/knowledge/graph.json"
SCHEMA = ROOT / "skills/preview-first/knowledge/schema.json"
TODAY = "2026-10-30"

# keyword -> styles (ideas pair with these styles when their suits/pairs words match)
STYLE_WORDS = {
    "studio": ["studio-wrap", "poster-type"], "agency": ["studio-wrap", "poster-type"], "portfolio": ["studio-wrap"],
    "developer": ["mono-engineering", "dark-console", "lab-figures"], "devtool": ["mono-engineering", "dark-console"], "infrastructure": ["mono-engineering", "dark-console"],
    "terminal": ["dark-console"], "hardware": ["mono-engineering", "lab-figures"], "engineering": ["mono-engineering", "lab-figures"],
    "luxury": ["quiet-luxury"], "fashion": ["quiet-luxury", "poster-type"], "beauty": ["quiet-luxury", "warm-organic"],
    "editorial": ["paper-editorial", "lab-figures"], "publication": ["paper-editorial"], "magazine": ["paper-editorial"], "newsletter": ["paper-editorial"],
    "documentation": ["lab-figures", "mono-engineering"], "docs": ["lab-figures"], "foundry": ["poster-type", "swiss-grid"], "museum": ["swiss-grid", "paper-editorial"],
    "playful": ["playful-geometric", "neo-brutalist"], "consumer": ["playful-geometric", "soft-product"], "brutalist": ["neo-brutalist"], "raw": ["neo-brutalist"],
    "saas": ["soft-product", "bento-showcase"], "product": ["soft-product"], "startup": ["soft-product"], "b2b": ["soft-product", "data-dense"],
    "data": ["data-dense", "lab-figures"], "finance": ["data-dense", "swiss-grid"], "dashboard": ["data-dense"], "analytics": ["data-dense"],
    "dark": ["luminous-dark", "dark-console"], "premium": ["quiet-luxury", "luminous-dark"], "ai": ["luminous-dark", "mono-engineering"],
    "calm": ["warm-organic", "paper-editorial"], "warm": ["warm-organic"], "organic": ["warm-organic"], "wellness": ["warm-organic"], "food": ["warm-organic", "playful-geometric"],
    "swiss": ["swiss-grid"], "grid": ["swiss-grid"], "minimal": ["swiss-grid", "quiet-luxury"], "glass": ["glass-layered"], "commerce": ["quiet-luxury", "playful-geometric"],
    "ecommerce": ["quiet-luxury", "playful-geometric"], "store": ["quiet-luxury", "playful-geometric"], "event": ["poster-type", "neo-brutalist"], "music": ["poster-type", "dark-console"],
    "archive": ["paper-editorial", "studio-wrap"], "scientific": ["lab-figures"], "technical": ["mono-engineering", "lab-figures"],
}
# keyword -> render hook (conservative; applied only to renderable ideas)
HOOK_RULES = [
    (r"marquee|ticker", {"hero": "hero-ticker", "*": "section-marquee"}),
    (r"split nav|live (local )?time|local time|clock", {"navigation": "nav-split-meta", "footer": "footer-colophon"}),
    (r"menu.*(word|overlay)|overlay menu|full-?screen menu|hamburger", {"navigation": "nav-menu-word"}),
    (r"pill nav|floating nav|island nav|capsule", {"navigation": "nav-pill"}),
    (r"rail|side index|dot nav|section index", {"navigation": "nav-rail"}),
    (r"specimen", {"hero": "hero-specimen"}),
    (r"manifesto|letter|essay|paragraph hero|statement hero|first.person", {"hero": "hero-manifesto"}),
    (r"numbers? hero|big number|stat hero|figures hero", {"hero": "hero-numbers"}),
    (r"bleed|larger than the viewport|clipped|cropped (word|type)|oversized (word|type|wordmark)", {"hero": "hero-clip", "typography": "hero-clip"}),
    (r"stacked (words|lines)|one word per line|fragment", {"hero": "hero-stacked"}),
    (r"numeral|01, 02|index number|section number", {"section": "features-numerals", "typography": "type-index-numbers", "layout": "features-numerals"}),
    (r"stacking cards|sticky cards|card stack", {"*": "features-stack"}),
    (r"horizontal scroll|scroll.snap|carousel strip|filmstrip", {"*": "features-strip"}),
    (r"hover.*(image|preview|reveal)|image.*follows", {"*": "features-hover-list"}),
    (r"bordered cells|cell grid|grid lines|crosses|plus marks|intersections", {"section": "features-cells", "layout": "features-cells", "texture": "texture-crosses", "component": "features-cells"}),
    (r"accordion|faq|details", {"*": "features-accordion"}),
    (r"pull quote|giant quote|one quote|single quote|testimonial", {"*": "proof-giant-quote"}),
    (r"stat wall|stats? row|sourced figures|metrics row", {"*": "proof-stat-wall"}),
    (r"ticket|stub|perforat", {"*": "cta-ticket"}),
    (r"colophon|footer meta|version number|coordinates", {"footer": "footer-colophon"}),
    (r"grain|noise", {"*": "texture-grain"}),
    (r"graph paper|background grid|dot grid|grid background", {"*": "texture-grid"}),
    (r"scanline|crt", {"*": "texture-scanlines"}),
    (r"ruled|baseline rules|notebook lines", {"texture": "texture-rules"}),
    (r"outline(d)? (text|type|word)|text-stroke|stroke text", {"*": "type-outline"}),
    (r"mixed.face|contrasting face|serif accent|italic accent|one word in", {"*": "type-mixed-face"}),
    (r"vertical (text|label)|writing-mode|rotated label", {"*": "type-vertical-label"}),
    (r"tight (tracking|leading|display)|negative tracking|letter-spacing -", {"typography": "type-tight-display"}),
    (r"hanging punctuation", {"*": "type-hanging-punctuation"}),
    (r"tabular", {"*": "type-tabular"}),
    (r"bracket", {"*": "button-bracket"}),
    (r"fill(s)? (up|from)|wipe|slides? up on hover", {"component": "button-fill-up"}),
    (r"circle(d)? icon|icon in a circle|arrow circle", {"component": "button-circle-icon"}),
    (r"underline", {"component": "button-underline", "typography": "button-underline"}),
    (r"line.by.line|mask reveal|text reveal|lines rise|split text", {"*": "motion-line-reveal"}),
    (r"custom cursor|cursor (dot|ring)", {"*": "motion-cursor"}),
    (r"magnetic", {"*": "motion-magnetic"}),
    (r"preloader|loading counter|0 to 100|counter preload", {"*": "motion-preloader"}),
    (r"count.?up|number ticker|odometer", {"*": "motion-count-up"}),
    (r"image swap|second (shot|image) on hover|swap on hover", {"*": "motion-hover-swap"}),
    (r"scroll progress|progress (bar|line)|reading progress", {"*": "motion-scroll-progress"}),
    (r"view transition", {"*": "motion-view-transitions"}),
    (r"duotone|monochrome (image|photo)|tinted (image|photo)", {"*": "image-duotone"}),
    (r"dither", {"*": "image-dither"}),
    (r"ascii", {"*": "image-ascii"}),
    (r"caption", {"imagery": "image-caption", "typography": "image-caption", "art": "image-caption"}),
    (r"sticker|badge rotated|stamp", {"*": "image-sticker"}),
    (r"colou?r.block|inverted section|section (background|colour) (alternat|chang)|full.bleed colou?r", {"*": "color-blocking"}),
    (r"inverted (footer|ending|closing)|dark footer|ink footer", {"*": "color-inverted-section"}),
    (r"one (hot|accent|signal) colou?r|single accent|one colou?r", {"*": "color-single-accent"}),
]
PT_WORDS = {
    "developer": "developer-tool", "devtool": "developer-tool", "api": "developer-tool", "infrastructure": "developer-tool", "terminal": "developer-tool",
    "saas": "saas", "b2b": "saas", "product": "saas", "startup": "saas", "platform": "saas",
    "finance": "fintech", "fintech": "fintech", "payments": "fintech", "banking": "fintech",
    "ecommerce": "ecommerce", "e-commerce": "ecommerce", "store": "ecommerce", "retail": "ecommerce", "commerce": "ecommerce", "shop": "ecommerce",
    "luxury": "luxury-commerce", "fashion": "luxury-commerce", "beauty": "luxury-commerce", "jewellery": "luxury-commerce",
    "portfolio": "portfolio", "photographer": "portfolio", "designer": "portfolio", "personal": "portfolio",
    "studio": "agency", "agency": "agency", "consultancy": "agency",
    "editorial": "editorial", "publication": "editorial", "magazine": "editorial", "newsletter": "editorial", "journalism": "editorial", "blog": "editorial", "publishing": "editorial",
    "dashboard": "dashboard", "analytics": "dashboard", "admin": "dashboard", "internal": "dashboard", "data": "dashboard",
    "health": "health", "wellness": "health", "fitness": "health", "clinic": "health",
    "education": "education", "course": "education", "learning": "education", "school": "education",
    "ai": "ai-product", "llm": "ai-product", "assistant": "ai-product",
    "nonprofit": "nonprofit", "charity": "nonprofit", "museum": "nonprofit", "cultural": "nonprofit", "gallery": "nonprofit",
    "mobile": "mobile-app", "ios": "mobile-app", "app": "mobile-app",
    "documentation": "documentation", "docs": "documentation", "handbook": "documentation",
    "community": "community", "forum": "community", "membership": "community",
    "event": "event", "conference": "event", "festival": "event",
    "restaurant": "local-business", "cafe": "local-business", "food": "local-business", "hospitality": "local-business",
    "marketplace": "marketplace", "booking": "marketplace",
    "architecture": "real-estate", "interiors": "real-estate", "property": "real-estate", "furniture": "real-estate",
    "travel": "travel", "hotel": "travel", "tourism": "travel",
    "hardware": "developer-tool", "foundry": "agency", "type foundry": "agency", "music": "event",
}
SITE_PT = {"developer tool": "developer-tool", "saas": "saas", "studio": "agency", "portfolio": "portfolio", "fashion": "luxury-commerce", "luxury": "luxury-commerce",
           "hardware": "ecommerce", "publication": "editorial", "foundry": "agency", "template": "general-website", "app": "mobile-app", "store": "ecommerce",
           "nonprofit": "nonprofit", "event": "event", "other": "general-website"}
SITE_STYLE = {"developer-tool": "mono-engineering", "saas": "soft-product", "agency": "studio-wrap", "portfolio": "studio-wrap", "luxury-commerce": "quiet-luxury",
              "ecommerce": "quiet-luxury", "editorial": "paper-editorial", "general-website": "swiss-grid", "mobile-app": "soft-product", "nonprofit": "swiss-grid", "event": "poster-type"}


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:60].strip("-")


def domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def words_of(idea):
    return " ".join([idea.get("slug", ""), idea.get("name", ""), idea.get("what", ""), " ".join(idea.get("suits", []) or []), " ".join(idea.get("pairs_with", []) or [])]).lower()


HOOK_OVERRIDES = {"transparent-floating-nav": "nav-bar", "underline-only-input": None, "hover-image-swap-scale": "motion-hover-swap",
                  "bracketed-figure-captions": "image-caption", "physical-material-ui": None, "hard-shadow-sticker": "image-sticker",
                  "sticker-filter-tabs": None, "build-version-stamp": "footer-colophon", "digit-roll-number-ticker": "motion-count-up",
                  "testimonial-flip-swap-hero": None, "bracketed-eyebrow-labels": "type-index-numbers", "hover-image-swap": "motion-hover-swap",
                  "studio-locator-tabs": None, "dashboard-card-with-real-numbers": None, "hover-image-swap-card": "motion-hover-swap", "tabular-numerals-for-data": "type-tabular"}


def classify_hook(idea, hooks):
    if idea.get("slug") in HOOK_OVERRIDES:
        return HOOK_OVERRIDES[idea.get("slug")]
    if not idea.get("renderable_in_static_draft", True):
        return None
    if idea.get("ai_tell_risk") == "high":
        return None
    text = (idea.get("slug", "") + " " + idea.get("name", "")).lower().replace("-", " ")
    cat = idea.get("category", "")
    for pattern, by_cat in HOOK_RULES:
        if re.search(pattern, text):
            hook = by_cat.get(cat) or by_cat.get("*")
            if hook in hooks:
                return hook
    return None


def reclassify():
    """Re-run the hook classifier over research ideas already in the graph (after a rule change)."""
    g = json.load(open(GRAPH, encoding="utf-8"))
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    hooks = set(schema["node_kinds"]["idea"]["render_hooks"])
    changed = 0
    for n in g["nodes"]:
        if n["kind"] != "idea" or "research sweep" not in n.get("source", ""):
            continue
        hook = classify_hook({"slug": n["id"][5:], "name": n["name"], "what": n["what"], "category": n["category"], "ai_tell_risk": n["ai_tell_risk"],
                              "renderable_in_static_draft": True}, hooks)
        if hook != n.get("renders"):
            changed += 1
            if hook:
                n["renders"] = hook
            else:
                n.pop("renders", None)
    json.dump(g, open(GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(GRAPH, "a", encoding="utf-8").write("\n")
    print("reclassified", changed)
    for n in g["nodes"]:
        if n["kind"] == "idea" and n.get("renders") and "research sweep" in n.get("source", ""):
            print(n["renders"].ljust(24), n["id"][5:50].ljust(46), n["what"][:80])


def main(research_dir):
    g = json.load(open(GRAPH, encoding="utf-8"))
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    cats = set(schema["node_kinds"]["idea"]["enums"]["category"])
    hooks = set(schema["node_kinds"]["idea"]["render_hooks"])
    ids = {n["id"] for n in g["nodes"]}
    names = {slug(n["name"]) for n in g["nodes"] if n["kind"] == "idea"}
    style_ids = {n["id"].split(".", 1)[1] for n in g["nodes"] if n["kind"] == "style"}
    pt_ids = {n["id"].split(".", 1)[1] for n in g["nodes"] if n["kind"] == "product-type"}
    moods = {n["id"]: [n["name"].lower()] + [a.lower() for a in n.get("aliases", [])] for n in g["nodes"] if n["kind"] == "mood"}
    sites_by_domain = {domain(n["url"]): n["id"] for n in g["nodes"] if n["kind"] == "reference-site"}

    # reference sites first so ideas can cite them as evidence
    added_sites = 0
    for f in sorted(glob.glob(str(Path(research_dir) / "sites-*.json"))):
        for s in json.load(open(f, encoding="utf-8")):
            d = domain(s.get("url", ""))
            if not d or d in sites_by_domain:
                continue
            pt = SITE_PT.get(str(s.get("product_type", "other")).lower(), "general-website")
            nid = "reference-site." + slug(d.split(".")[0] + ("-" + d.split(".")[1] if d.count(".") > 1 else ""))
            if nid in ids:
                nid = "reference-site." + slug(d)
            if nid in ids:
                continue
            node = {"id": nid, "kind": "reference-site", "name": s.get("name") or d, "url": s["url"], "product_type": "product-type." + pt,
                    "observed": {"style": "style." + SITE_STYLE.get(pt, "swiss-grid"), "traits": s.get("traits", []), "fonts": s.get("fonts", []),
                                 "colours": s.get("colours", []), "distinctness": s.get("distinctness"), "confirmed": bool(s.get("opened"))},
                    "notes": "; ".join(s.get("traits", [])[:6]), "seen": TODAY, "source": "research sweep 2026-10-30 (%s)" % Path(f).name,
                    "added": TODAY, "last_verified": TODAY, "confidence": 0.8 if s.get("opened") else 0.65}
            if s.get("year"):
                node["observed"]["year"] = s["year"]
            g["nodes"].append(node); ids.add(nid); sites_by_domain[d] = nid; added_sites += 1

    added, skipped = 0, []
    for f in sorted(glob.glob(str(Path(research_dir) / "ideas-*.json"))):
        src = Path(f).name
        for i in json.load(open(f, encoding="utf-8")):
            sl = slug(i.get("slug") or i.get("name", ""))
            nid = "idea." + sl
            seen = [u for u in (i.get("seen_on") or []) if str(u).startswith("http")]
            if not sl or nid in ids or slug(i.get("name", "")) in names or not seen:
                skipped.append(sl); continue
            cat = i.get("category") if i.get("category") in cats else "craft"
            risk = i.get("ai_tell_risk") if i.get("ai_tell_risk") in ("low", "medium", "high") else "medium"
            conf = i.get("confidence", 0.7)
            conf = max(0.6, min(0.95, float(conf) if isinstance(conf, (int, float)) else 0.7))
            node = {"id": nid, "kind": "idea", "name": str(i.get("name", sl))[:80], "category": cat,
                    "what": str(i.get("what", "")).strip(), "why": str(i.get("why_it_works", "")).strip(),
                    "implementation": str(i.get("implementation", "")).strip() or "See the description.",
                    "pitfalls": str(i.get("pitfalls", "")).strip(), "ai_tell_risk": risk, "ai_tell_note": str(i.get("ai_tell_note", "")).strip(),
                    "seen_on": seen[:4], "opened": [u for u in (i.get("opened") or []) if str(u).startswith("http")][:4],
                    "suits_words": [str(w) for w in (i.get("suits") or [])][:8], "pairs_words": [str(w) for w in (i.get("pairs_with") or [])][:8],
                    "avoid_words": [str(w) for w in (i.get("avoid_with") or [])][:8],
                    "source": "research sweep 2026-10-30 (%s)" % src, "added": TODAY, "last_verified": TODAY, "confidence": conf}
            if isinstance(i.get("first_seen_year"), int):
                node["first_seen_year"] = i["first_seen_year"]
            hook = classify_hook(i, hooks)
            if hook:
                node["renders"] = hook
            if cat in ("commerce",):
                node["page_types"] = ["store"]
            elif cat in ("content",):
                node["page_types"] = ["content", "marketing"]
            elif cat in ("app-shell",):
                node["page_types"] = ["app"]
            g["nodes"].append(node); ids.add(nid); names.add(slug(node["name"])); added += 1
            # edges
            ev = sorted({sites_by_domain[domain(u)] for u in seen if domain(u) in sites_by_domain})
            text = words_of(i)
            styles = []
            for w, sts in STYLE_WORDS.items():
                if re.search(r"\b" + re.escape(w) + r"\b", text):
                    styles += sts
            for st in sorted(set(styles)):
                if st in style_ids:
                    g["edges"].append({"from": nid, "to": "style." + st, "kind": "pairs_with", "weight": 0.6 if risk == "low" else 0.4, "evidence": ev})
            pts = set()
            for w, pt in PT_WORDS.items():
                if re.search(r"\b" + re.escape(w) + r"\b", " ".join(i.get("suits") or []).lower()):
                    pts.add(pt)
            for pt in sorted(pts):
                if pt in pt_ids:
                    g["edges"].append({"from": "product-type." + pt, "to": nid, "kind": "suits", "weight": 0.6, "evidence": ev})
            suits_text = " ".join(i.get("suits") or []).lower()
            for mid, als in moods.items():
                if any(re.search(r"\b" + re.escape(a) + r"\b", suits_text) for a in als):
                    g["edges"].append({"from": mid, "to": nid, "kind": "expresses", "weight": 0.5, "evidence": ev})
    json.dump(g, open(GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(GRAPH, "a", encoding="utf-8").write("\n")
    total = sum(1 for n in g["nodes"] if n["kind"] == "idea")
    print("sites added", added_sites, "| ideas added", added, "| skipped", len(skipped), "| ideas total", total, "| nodes", len(g["nodes"]), "| edges", len(g["edges"]))
    with_hook = sum(1 for n in g["nodes"] if n["kind"] == "idea" and n.get("renders"))
    print("ideas with a render hook", with_hook)


if __name__ == "__main__":
    if sys.argv[1] == "--reclassify":
        reclassify()
    else:
        main(sys.argv[1])
