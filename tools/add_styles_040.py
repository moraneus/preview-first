"""0.4.0: ideas for the showcase hooks, plus ten bolder styles with palettes and pairings. Idempotent."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "skills/preview-first/scripts"))
import add_styles_030 as base  # reuse the helpers and data shapes
from palette import resolve_palette
from contrast import hex_to_oklch, format_oklch

T = "2026-10-30"
SRC = "docs/research/2026-10-30-modern-design-ideas.md"
IDEAS = [
 ("split-screen-hero","Split-screen hero","hero","hero-split-screen","Two full-height panels with no gutter: text bottom-left on the page colour, artwork centred on a panel in the primary colour; the fold is a hard vertical edge.","A two-column grid at 88svh; the art panel background primary and colour on-primary; text aligned to the bottom.","low","Hard edges and a solid colour panel; no gradient, no screenshot.",["https://www.polestar.com","https://www.cos.com"],["cobalt-block","playful-geometric","signal-orange"]),
 ("diagonal-marquee-bands","Diagonal marquee bands","hero","hero-diagonal","Two marquee bands cross the first screen at opposite angles (about minus six and plus five degrees), one in ink, one in the primary colour, carrying the brand and the product nouns; the headline sits below them.","Absolutely positioned bands rotated with `rotate`, each with a duplicated track and a linear 30s animation, the second reversed; reduced motion stops them.","medium","A festival device; one page, two bands, never on a product page.",["https://dontboardme.com","https://basement.studio"],["neo-brutalist","poster-type","signal-orange"]),
 ("mosaic-hero","Mosaic hero","hero","hero-mosaic","The first screen is a four-column mosaic of artwork tiles with the headline and actions living in one dark tile that spans two columns and two rows.","CSS grid with span classes; the text tile inverts to ink with bg-coloured type; tiles have 1px hairlines.","low","Tiles of real work or product shots; the text tile is part of the grid, not floating over it.",["https://www.pentagram.com","https://www.figma.com"],["swiss-grid","studio-wrap","playful-geometric"]),
 ("kinetic-type-hero","Kinetic type hero","hero","hero-kinetic","Three giant lines of the headline, the middle one outlined, each indented a little more; as the page scrolls the lines slide at different speeds, the middle one the other way.","Scroll-driven animation: `animation-timeline: scroll()` on each row with a translate keyframe, the middle row reversed; static when the feature or motion is off.","medium","Kinetic type is a poster move; keep the lines to three and the motion to a few viewport widths.",["https://lusion.co","https://www.landonorris.com"],["poster-type","neo-brutalist","cobalt-block"]),
 ("fanned-cards-hero","Fanned cards hero","hero","hero-fan","Five rotated cards fanned from one corner beside the headline, each with artwork and a mono index; hovering lifts a card.","Absolutely positioned cards with `rotate: calc(-10deg + var(--i) * 5deg)` and a bottom-centre transform origin; translate on hover.","medium","Cards as objects, not as a grid; five, uneven, with real images.",["https://www.craft.do","https://granola.ai"],["clay-canvas","playful-geometric","soft-product"]),
 ("image-mosaic-features","Image mosaic features","section","features-mosaic","Features as an image-led masonry: wide and tall tiles with a caption strip at the bottom carrying an index, a title and (on large tiles) one sentence.","Grid with `grid-auto-flow: dense`, 200px rows, span classes; captions over a translucent bg strip.","low","Imagery with captions instead of icon cards.",["https://www.pentagram.com","https://www.ssense.com"],["studio-wrap","swiss-grid","quiet-luxury"]),
 ("poster-band","Poster band","section","section-poster-band","A full-bleed band of artwork with the wordmark across it at 20vw in difference blend, and one mono line in the corner; sits between features and proof as a breath.","A 70vh section, artwork absolutely positioned, the word in `mix-blend-mode: difference` so it reads on any colour.","medium","A poster moment, once per page.",["https://basement.studio","https://www.landonorris.com"],["poster-type","neo-brutalist","night-grain"]),
 ("parallax-giant-word","Parallax giant word","motion","motion-parallax-type","The giant wordmark in the footer or poster band drifts a few viewport widths sideways as it scrolls through the viewport.","`animation-timeline: view()` with a translate keyframe on the word; nothing else moves; reduced motion disables it.","low","Scroll-linked, reversible, one element.",["https://lusion.co","https://exo-ape.com"],["poster-type","studio-wrap","cobalt-block"]),
 ("hero-art-scroll-scale","Hero art scales out","motion","motion-scroll-scale","The hero artwork grows slightly and fades as it leaves the viewport, so the first screen releases into the page.","`animation-timeline: view()` with `animation-range: exit` and a scale and opacity keyframe.","low","Subtle, reversible, no library.",["https://www.apple.com/iphone/","https://linear.app"],["soft-product","night-grain","luminous-dark"]),
 ("skewed-marquee","Skewed marquee","motion","motion-skew-marquee","The marquee line skews a few degrees as it scrolls through the viewport, as if dragged by the scroll.","A second animation on the track driven by `animation-timeline: view()` with a skew keyframe.","medium","A studio flourish for one marquee.",["https://basement.studio","https://lamalama.com"],["neo-brutalist","poster-type"]),
 ("tilted-framed-images","Tilted framed images","imagery","image-frame-tilt","Images sit on a raised card with a hard offset shadow in ink, rotated a degree or two, like prints laid on a table.","`rotate: -1.5deg` and `box-shadow: 10px 12px 0 ink` on the artwork; alternate the angle per image.","low","A physical reference that depends on real photographs.",["https://www.craft.do","https://www.anthropic.com"],["clay-canvas","warm-organic","playful-geometric"]),
]
PALETTES = [
 ("lime-velodrome","Lime velodrome","cool","dark","green","Lando Norris's lime on near-black with cream for text panels; one hot colour at speed.",("#f4f3f1","#111112","#4d6b00","#111112"),("#111112","#efefe5","#d2ff00","#efefe5"),["https://www.landonorris.com"]),
 ("poster-red","Poster red","warm","light","red","Don't Board Me's bone white with a signal red and a mustard second; festival energy without gradients.",("#f3f3e9","#1a1a1a","#e33529","#a7a238"),None,["https://dontboardme.com"]),
 ("ultramarine-sand","Ultramarine & sand","cool","light","blue","Exo Ape's sand with a deep ultramarine; cool, architectural, calm.",("#e9e2d8","#0d0e13","#1f2bd6","#0d0e13"),("#0d0e13","#e4e0db","#8c96ff","#e0ccbb"),["https://exo-ape.com"]),
 ("pastel-studio","Pastel studio","warm","light","green","Craft's canvas with mint, butter and sky blocks; playful without a purple gradient.",("#fcf9f7","#030302","#1f7a3f","#c08532"),None,["https://www.craft.do","https://www.figma.com"]),
 ("ink-mustard","Ink & mustard","warm","dark","yellow","Warm black with a mustard primary and a bone second; poster contrast for events.",("#f6f1e6","#161412","#8a6200","#161412"),("#161412","#f6f1e6","#f0b429","#f6f1e6"),["https://www.hay.dk","https://www.walkerart.org"]),
 ("marine-coral","Marine & coral","cool","light","blue","Maven's lapis navy with a coral accent on a cool white; confident and warm at once.",("#f4f6fa","#080c28","#1d3bbf","#d3542b"),("#080c28","#f4f6fa","#9fb3ff","#f7804d"),["https://maven.com"]),
 ("sage-ink","Sage & ink","neutral","light","green","Causal's paint swatches: linen, sage, brick and ink.",("#ebe6dd","#2a1f17","#3d6b4f","#b63f2c"),None,["https://causal.so"]),
 ("blush-navy","Blush & navy","warm","light","blue","Headspace's blush off-white with a saturated blue and a yellow highlight; playful consumer.",("#f9f4f2","#2d2c2b","#0040ea","#b38a00"),None,["https://www.headspace.com"]),
]
PAIRINGS = [
 ("big-shoulders-mona-sans",("Big Shoulders","display",[700,800,900]),("Mona Sans","neo-grotesque",[400,500]),"Martian Mono",1.414,62,"'Arial Narrow', Impact, sans-serif","'Helvetica Neue', Arial, sans-serif",["speed","event","bold"],"A condensed display face at 900 over a variable grotesque; the Lando Norris register with free faces."),
 ("anton-instrument-sans",("Anton","display",[400]),("Instrument Sans","grotesque",[400,500,600]),"IBM Plex Mono",1.414,62,"Impact, 'Arial Narrow', sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["poster","festival","loud"],"A heavy condensed gothic for one line per screen with a grotesque body that stays out of the way."),
 ("unbounded-geist",("Unbounded","display",[600,700,800]),("Geist","neo-grotesque",[400,500]),"Geist Mono",1.414,62,"'Arial Black', sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["wide","bold","modern"],"A wide display face that fills a line with few words over a quiet grotesque."),
 ("archivo-black-hanken-grotesk",("Archivo Black","display",[400]),("Hanken Grotesk","grotesque",[400,500]),"Martian Mono",1.414,64,"'Arial Black', sans-serif","'Helvetica Neue', Arial, sans-serif",["poster","brutalist","direct"],"The heaviest free grotesque for wordmarks and clipped type; Hanken for everything else."),
 ("syne-instrument-sans",("Syne","display",[700,800]),("Instrument Sans","grotesque",[400,500]),"Kode Mono",1.333,64,"'Helvetica Neue', Arial, sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["studio","expressive","cultural"],"Syne widens as it gets heavier; at 800 it is a poster face. Kept to the H1."),
 ("bricolage-grotesque-geist",("Bricolage Grotesque","grotesque",[600,700,800]),("Geist","neo-grotesque",[400,500]),"Geist Mono",1.333,64,"'Helvetica Neue', Arial, sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["product","confident","warm"],"Bricolage at its compressed optical sizes over Geist; character in the headline, neutrality below."),
 ("fraunces-instrument-sans",("Fraunces","serif-old-style",[500,600,700]),("Instrument Sans","grotesque",[400,500]),"IBM Plex Mono",1.333,64,"'Iowan Old Style', Georgia, serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["soft","friendly","editorial"],"Fraunces with its WONK axis for a headline that smiles, a plain grotesque body."),
 ("parkinsans-geist",("Parkinsans","geometric",[600,700,800]),("Geist","neo-grotesque",[400,500]),"Geist Mono",1.333,64,"'Avenir Next', 'Segoe UI', sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["playful","consumer","warm"],"Soft terminals at display size over a neutral body."),
]
STYLES = [
 dict(id="velodrome", name="Velodrome", family="bold", summary="Lando Norris energy: near-black, lime and cream, a condensed display face at 900, kinetic type that slides with scroll, a marquee, a poster band and sourced count-ups. Speed as a design language.",
      traits=["lime on black", "condensed display at 900", "kinetic type", "marquee", "poster band"], signals=["energetic", "confident", "bold", "current"],
      radius_scale="none", shadow="none", density="regular", art={"hero": "bars", "feature": "figure"},
      layout={"marketing": {"hero": "kinetic", "features": "numerals", "proof": "stat-wall", "cta": "giant", "footer": "giant"}, "store": {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy", "cart": "drawer", "footer": "giant"}, "content": {"header": "minimal", "article": "single", "list": "archive", "footer": "giant"}},
      tells=["neon glow", "gradient on the lime"], inspired=["https://www.landonorris.com", "https://basement.studio"],
      ideas=["kinetic-type-hero", "one-hot-colour", "marquee-divider", "poster-band", "count-up-numbers", "tight-display", "parallax-giant-word", "split-nav-live-meta"],
      palettes=["lime-velodrome", "acid-lab", "midnight-lime", "ink-mustard", "carbon-signal"], pairings=["big-shoulders-mona-sans", "anton-instrument-sans", "archivo-black-hanken-grotesk", "unbounded-geist", "big-shoulders-work-sans"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="underline", card_edge="flat", nav="compact", divider="rule", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "underline-grow", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "page-slide-vt", "number-count-up", "scroll-reveal-once", "hero-mask-reveal"],
      icon="tabler", suits=["event", "ecommerce", "community", "portfolio", "agency", "mobile-app"], moods=["energetic", "bold", "confident", "modern", "futuristic"], page_types=["marketing", "store", "content"]),
 dict(id="festival-poster", name="Festival poster", family="expressive", summary="Bone white, signal red and mustard; a heavy condensed gothic; diagonal marquee bands crossing the hero; rays and stamps as artwork; a ticket for the call to action. Loud, flat, printed.",
      traits=["diagonal bands", "condensed gothic", "rays and stamps", "ticket call to action", "flat colour"], signals=["playful", "loud", "cultural", "direct"],
      radius_scale="none", shadow="hard", density="regular", art={"hero": "rays", "feature": "stamp"},
      layout={"marketing": {"hero": "diagonal", "features": "mosaic", "proof": "giant-quote", "cta": "ticket", "footer": "giant"}, "store": {"hero": "tiles", "grid": "editorial", "product": "gallery-left", "cart": "drawer", "footer": "giant"}, "content": {"header": "broadsheet", "article": "single", "list": "archive", "footer": "giant"}},
      tells=["gradient between the colours", "emoji"], inspired=["https://dontboardme.com", "https://www.walkerart.org"],
      ideas=["diagonal-marquee-bands", "image-mosaic-features", "ticket-cta", "rotated-stickers", "outline-giant-word", "colour-blocking-sections", "skewed-marquee", "marquee-divider"],
      palettes=["poster-red", "ink-mustard", "hazard-yellow", "poppy-cream", "cherry-paper"], pairings=["anton-instrument-sans", "archivo-black-hanken-grotesk", "big-shoulders-work-sans", "syne-instrument-sans", "anton-work-sans"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="hairline", card_edge="border", nav="compact", divider="rule", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-lift-2", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "menu-stagger-30", "spring-pop", "scroll-reveal-once"],
      icon="tabler", suits=["event", "community", "local-business", "nonprofit", "education", "ecommerce"], moods=["playful", "energetic", "bold", "raw", "friendly"], page_types=["marketing", "store", "content"]),
 dict(id="ultramarine", name="Ultramarine", family="minimal", summary="Exo Ape's sand and deep ultramarine, a hairline-weight display face, a split-screen first screen with the artwork on a solid blue panel, a torus of rings, mosaic features and a colophon. Architectural calm.",
      traits=["split-screen hero", "hairline display weight", "solid colour panel", "torus art", "sand canvas"], signals=["calm", "precise", "premium", "architectural"],
      radius_scale="none", shadow="none", density="airy", art={"hero": "torus", "feature": "figure"},
      layout={"marketing": {"hero": "split-screen", "features": "mosaic", "proof": "statement", "cta": "inline", "footer": "colophon"}, "store": {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy", "cart": "page", "footer": "colophon"}, "content": {"header": "minimal", "article": "side-notes", "list": "archive", "footer": "colophon"}},
      tells=["bold display weight", "rounded cards"], inspired=["https://exo-ape.com", "https://www.polestar.com"],
      ideas=["split-screen-hero", "image-mosaic-features", "tight-display", "colophon-footer", "line-mask-reveal", "hero-art-scroll-scale", "index-numbers-mono", "underline-offset-links"],
      palettes=["ultramarine-sand", "cobalt-paper", "marine-bone", "nordic-ice", "slate-signal"], pairings=["bricolage-grotesque-geist", "host-grotesk-funnel-sans", "inter-tight-inter", "mona-sans-kode-mono", "schibsted-grotesk-inter"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="underline", card_edge="flat", nav="airy", divider="hairline", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "hero-mask-reveal", "scroll-reveal-once"],
      icon="radix", suits=["real-estate", "agency", "luxury-commerce", "portfolio", "saas", "travel"], moods=["calm", "precise", "premium", "elegant", "minimal", "confident"], page_types=["marketing", "store", "content"]),
 dict(id="pastel-blocks", name="Pastel blocks", family="soft", summary="Craft and Figma's tinted blocks: a warm canvas, sections in mint, butter and sky with hard edges, a geometric display with soft terminals, fanned cards, tilted framed images and stickers. Playful without a gradient.",
      traits=["tinted section blocks", "fanned cards", "tilted frames", "soft geometric display", "stickers"], signals=["playful", "friendly", "warm", "current"],
      radius_scale="md", shadow="hard", density="regular", art={"hero": "blob", "feature": "figure"},
      layout={"marketing": {"hero": "fan", "features": "stack", "proof": "giant-quote", "cta": "band", "footer": "columns"}, "store": {"hero": "product", "grid": "three", "product": "gallery-left", "cart": "drawer", "footer": "columns"}, "app": {"shell": "sidebar", "table": "comfortable", "detail": "panel"}},
      tells=["purple gradient", "glass cards"], inspired=["https://www.craft.do", "https://www.figma.com", "https://brilliant.org"],
      ideas=["fanned-cards-hero", "tilted-framed-images", "colour-blocking-sections", "rotated-stickers", "stacking-cards", "count-up-numbers", "circle-icon-button"],
      palettes=["pastel-studio", "blush-navy", "butter-cobalt", "sky-tomato", "moss-cream"], pairings=["parkinsans-geist", "fraunces-instrument-sans", "parkinsans-hanken-grotesk", "geologica-geologica", "bricolage-grotesque-figtree"],
      treatments=dict(button_shape="pill", button_fill="solid", input_edge="hairline", card_edge="border", nav="airy", divider="space", image_corner="sm", focus_ring="offset", link_style="colour", elevation="one"),
      motion=["press-scale-97", "hover-lift-2", "enter-fade-up-8", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "page-crossfade-vt", "spring-pop", "number-count-up", "menu-stagger-30"],
      icon="phosphor", suits=["education", "mobile-app", "saas", "community", "health", "local-business"], moods=["playful", "friendly", "warm", "energetic", "modern"], page_types=["marketing", "store", "app"]),
 dict(id="mosaic-wall", name="Mosaic wall", family="expressive", summary="A poster wall: the first screen is a mosaic of tiles with the text as one dark tile, mosaic features, a wide display face, a marine palette with a coral counter; image-led from the first pixel.",
      traits=["mosaic hero", "image-led features", "wide display", "one counter colour", "hard tiles"], signals=["bold", "cultural", "confident", "current"],
      radius_scale="none", shadow="none", density="regular", art={"hero": "mosaic", "feature": "figure"},
      layout={"marketing": {"hero": "mosaic", "features": "mosaic", "proof": "statement", "cta": "giant", "footer": "giant"}, "store": {"hero": "tiles", "grid": "editorial", "product": "gallery-top", "cart": "page", "footer": "giant"}, "content": {"header": "masthead", "article": "single", "list": "archive", "footer": "giant"}},
      tells=["bento of equal cards", "gradient tiles"], inspired=["https://www.pentagram.com", "https://maven.com"],
      ideas=["mosaic-hero", "image-mosaic-features", "one-hot-colour", "tight-display", "poster-band", "index-numbers-mono", "hover-swap-images"],
      palettes=["marine-coral", "cobalt-cream", "sage-ink", "navy-gold", "ink-coral"], pairings=["unbounded-geist", "syne-instrument-sans", "big-shoulders-mona-sans", "funnel-display-funnel-sans", "archivo-black-archivo"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="underline", card_edge="flat", nav="compact", divider="space", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["hover-tint", "press-scale-97", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "scroll-reveal-once", "layout-flip"],
      icon="radix", suits=["agency", "portfolio", "event", "education", "nonprofit", "editorial"], moods=["bold", "confident", "energetic", "modern", "playful"], page_types=["marketing", "store", "content"]),
]

def main():
    g = json.load(open(base.GRAPH, encoding="utf-8")); ids = {n["id"] for n in g["nodes"]}
    added = 0
    for slug, name, cat, hook, what, impl, risk, note, seen, styles in IDEAS:
        nid = "idea." + slug
        if nid in ids: continue
        g["nodes"].append({"id": nid, "kind": "idea", "name": name, "category": cat, "what": what, "implementation": impl, "ai_tell_risk": risk, "ai_tell_note": note,
                           "seen_on": seen, "renders": hook, "first_seen_year": 2025, "source": SRC, "added": T, "last_verified": T, "confidence": 0.7})
        ids.add(nid); added += 1
        for st in styles:
            if "style." + st in ids:
                g["edges"].append({"from": nid, "to": "style." + st, "kind": "pairs_with", "weight": 0.7, "evidence": []})
    json.dump(g, open(base.GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(base.GRAPH, "a", encoding="utf-8").write("\n")
    print("ideas added", added)
    base.PALETTES[:] = PALETTES; base.PAIRINGS[:] = PAIRINGS; base.STYLES[:] = STYLES
    base.main()

if __name__ == "__main__":
    main()
