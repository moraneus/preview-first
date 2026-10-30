"""Add the 0.3.0 styles, palettes and pairings drawn from the research sweep. Dev tool, idempotent.

uv run python3 tools/add_styles_030.py
"""
import json, sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/preview-first/scripts"))
from palette import derive_roles, resolve_palette  # noqa: E402
from contrast import hex_to_oklch, format_oklch  # noqa: E402

GRAPH = ROOT / "skills/preview-first/knowledge/graph.json"
FONTS = ROOT / "skills/preview-first/knowledge/live/fonts.json"
T = "2026-10-30"
SRC = "docs/research/2026-10-30-modern-design-ideas.md"

# name, temperature, scheme, hue_family, notes, light anchors (bg, text, primary, accent), dark anchors or None, inspired
PALETTES = [
 ("acid-lab", "Acid lab", "cool", "dark", "green", "Near-black, off-white and one acid green on under five percent of the page; the 2025 developer-tool signal colour.",
  ("#f4f5f0", "#111311", "#3f7a00", "#111311"), ("#0b0c0b", "#f2f3ee", "#c2ff00", "#f2f3ee"), ["https://warp.dev", "https://basement.studio"]),
 ("paper-signal", "Paper & signal red", "warm", "light", "red", "Warm paper, near-black ink and a signal red used for one rule, one word, one button.",
  ("#f4f1ea", "#141413", "#d6001c", "#141413"), None, ["https://press.stripe.com", "https://www.lrb.co.uk"]),
 ("archive-ink", "Archive ink", "neutral", "both", "blue", "Off-white and ink with the browser's own link blue as the only colour; reads as an index, not a brand.",
  ("#f6f5f1", "#1a1a1a", "#1d3fd1", "#1a1a1a"), ("#141414", "#ececea", "#9db0ff", "#ececea"), ["https://www.are.na", "https://read.cv"]),
 ("raw-document", "Raw document", "neutral", "light", "blue", "White, black, default link blue and visited purple: the honest document look of text-first sites.",
  ("#ffffff", "#000000", "#0000ee", "#551a8b"), None, ["https://craigmod.com", "https://berkeleygraphics.com"]),
 ("night-grain", "Night grain", "warm", "dark", "orange", "Warm near-black with grain, bone text and an amber accent; the warm dark of Warp and Resend rather than blue-black.",
  ("#f7f5f0", "#1c1917", "#b45309", "#1c1917"), ("#1c1917", "#f5f1ea", "#f59e0b", "#e7e5e4"), ["https://warp.dev", "https://resend.com"]),
 ("phosphor", "Phosphor", "cool", "dark", "green", "Black glass and phosphor green with a yellow warning tone; terminals, hardware, play.",
  ("#f2f7f3", "#0a1a0f", "#157a3b", "#8a6a00"), ("#050806", "#d8f3dc", "#33ff66", "#ffd166")  # text_muted lifted to #9fcfae after the check, ["https://teenage.engineering", "https://ghostty.org"]),
 ("cobalt-cream", "Cobalt & cream", "cool", "light", "blue", "Cream canvas with International Klein Blue blocks and a coral counterpoint; colour as structure.",
  ("#fffcec", "#11131a", "#2b35f0", "#d9431c"), None, ["https://arc.net", "https://www.cos.com"]),
 ("stone-serif", "Stone & serif", "warm", "light", "teal", "Stone white, warm black and a deep teal for links; built for very large serif type and long reading.",
  ("#f7f6f2", "#1f1d1b", "#1f5f5b", "#b5452b"), None, ["https://asteriskmag.com", "https://www.noemamag.com"]),
 ("signal-orange", "Signal orange", "warm", "light", "orange", "Mistral's cream and sunset orange with a yellow stripe colour; loud, warm and flat.",
  ("#fff8e0", "#1c1c1e", "#d93d00", "#b88a00"), None, ["https://mistral.ai", "https://cursor.com"]),
 ("clay-canvas", "Clay canvas", "warm", "light", "orange", "Anthropic's canvas, ink and clay with an olive second colour; soft without being pastel.",
  ("#faf9f5", "#141413", "#c2531f", "#5b6f00"), None, ["https://www.anthropic.com", "https://granola.ai"]),
 ("graphite-coral", "Graphite & coral", "cool", "dark", "red", "Raycast's near-black with a coral accent and an amber second tone; glass only where there is depth.",
  ("#f5f5f6", "#111214", "#c7342f", "#8a6200"), ("#07080a", "#f1f1f1", "#ff5f5f", "#ffb000"), ["https://www.raycast.com", "https://linear.app"]),
 ("bone-teal", "Bone & teal", "neutral", "light", "teal", "Perplexity's bone white, warm text and a single teal; quiet, trustworthy, no second colour.",
  ("#fdfbfa", "#27251e", "#016a71", "#27251e"), None, ["https://www.perplexity.ai", "https://www.anthropic.com"]),
]

# id, heading (family, category, weights), body (family, category, weights), mono (family or None), ratio, measure, fallbacks, moods, notes
PAIRINGS = [
 ("bricolage-grotesque-instrument-sans", ("Bricolage Grotesque", "grotesque", [500, 700, 800]), ("Instrument Sans", "grotesque", [400, 500, 600]), "Geist Mono", 1.333, 64,
  "'Helvetica Neue', Arial, sans-serif", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["studio", "confident", "editorial"], "A grotesque with ink traps and optical sizes over a quiet grotesque; the pair reads as one voice with two volumes."),
 ("big-shoulders-work-sans", ("Big Shoulders", "display", [600, 700, 800]), ("Work Sans", "grotesque", [400, 500]), "IBM Plex Mono", 1.414, 62,
  "'Arial Narrow', Impact, sans-serif", "'Helvetica Neue', Arial, sans-serif", ["bold", "event", "poster"], "A condensed display face at poster size with a plain grotesque body; the condensation does the work, no weight games."),
 ("newsreader-hanken-grotesk", ("Newsreader", "serif-transitional", [400, 500, 600]), ("Hanken Grotesk", "grotesque", [400, 500, 600]), "JetBrains Mono", 1.333, 66,
  "Georgia, 'Times New Roman', serif", "'Helvetica Neue', Arial, sans-serif", ["editorial", "literate", "calm"], "A newspaper serif with optical sizes over a neutral grotesque; set the serif at 300 for display and 400 for text."),
 ("libre-caslon-display-libre-franklin", ("Libre Caslon Display", "serif-old-style", [400]), ("Libre Franklin", "grotesque", [400, 500, 600]), None, 1.414, 64,
  "'Big Caslon', Georgia, serif", "'Franklin Gothic', Arial, sans-serif", ["classic", "editorial", "magazine"], "Caslon at display size only, Franklin for everything else; the American magazine pair."),
 ("gloock-instrument-sans", ("Gloock", "serif-didone", [400]), ("Instrument Sans", "grotesque", [400, 500]), None, 1.414, 62,
  "Didot, 'Bodoni MT', Georgia, serif", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["fashion", "dramatic", "luxury"], "A high-contrast didone for the H1 alone over a low-contrast grotesque body."),
 ("familjen-grotesk-martian-mono", ("Familjen Grotesk", "grotesque", [500, 600, 700]), ("Familjen Grotesk", "grotesque", [400, 500]), "Martian Mono", 1.25, 66,
  "'Helvetica Neue', Arial, sans-serif", "'Helvetica Neue', Arial, sans-serif", ["archive", "studio", "minimal"], "One grotesque superfamily with a wide mono for labels, dates and counts; the archive and index voice."),
 ("martian-mono-familjen-grotesk", ("Martian Mono", "mono", [500, 700]), ("Familjen Grotesk", "grotesque", [400, 500]), "Martian Mono", 1.25, 64,
  "ui-monospace, Menlo, monospace", "'Helvetica Neue', Arial, sans-serif", ["technical", "archive", "precise"], "A wide mono for headings at modest sizes with a grotesque body; headings stay under 48px."),
 ("doto-geist", ("Doto", "display", [600, 800, 900]), ("Geist", "neo-grotesque", [400, 500]), "Geist Mono", 1.333, 62,
  "'Courier New', monospace", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["hardware", "playful", "technical"], "A dot-matrix display face for the H1 and labels, a neutral grotesque for text; the pixel register without a pixel body."),
 ("pixelify-sans-ibm-plex-sans", ("Pixelify Sans", "display", [500, 700]), ("IBM Plex Sans", "grotesque", [400, 500, 600]), "IBM Plex Mono", 1.333, 64,
  "'Courier New', monospace", "'Helvetica Neue', Arial, sans-serif", ["playful", "retro", "games"], "A pixel display face at large sizes only, Plex for reading; both come from engineering lineages."),
 ("funnel-display-funnel-sans", ("Funnel Display", "display", [500, 600, 700]), ("Funnel Sans", "geometric", [400, 500]), "Geist Mono", 1.333, 64,
  "'Helvetica Neue', Arial, sans-serif", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["modern", "confident", "product"], "A 2024 superfamily with a display cut whose tight apertures read as drawn, not defaulted."),
 ("geologica-geologica", ("Geologica", "geometric", [600, 700]), ("Geologica", "geometric", [300, 400, 500]), "JetBrains Mono", 1.25, 64,
  "system-ui, -apple-system, 'Segoe UI', sans-serif", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["friendly", "modern", "clear"], "A variable geometric with a slant and sharpness axis; one family, two weights, no second voice."),
 ("mona-sans-kode-mono", ("Mona Sans", "neo-grotesque", [600, 700, 800]), ("Mona Sans", "neo-grotesque", [400, 500]), "Kode Mono", 1.25, 66,
  "'Helvetica Neue', Arial, sans-serif", "'Helvetica Neue', Arial, sans-serif", ["developer", "product", "modern"], "GitHub's variable sans with a width axis for headlines, and a mono with a visible personality for labels."),
 ("kode-mono-mona-sans", ("Kode Mono", "mono", [500, 700]), ("Mona Sans", "neo-grotesque", [400, 500]), "Kode Mono", 1.25, 64,
  "ui-monospace, Menlo, monospace", "'Helvetica Neue', Arial, sans-serif", ["technical", "terminal", "playful"], "A mono with character for headings under 48px, a variable sans body."),
 ("parkinsans-hanken-grotesk", ("Parkinsans", "geometric", [600, 700, 800]), ("Hanken Grotesk", "grotesque", [400, 500]), "IBM Plex Mono", 1.333, 64,
  "'Avenir Next', 'Segoe UI', sans-serif", "'Helvetica Neue', Arial, sans-serif", ["playful", "warm", "bold"], "A geometric with soft terminals for headlines over a plain grotesque."),
 ("bodoni-moda-inter-tight", ("Bodoni Moda", "serif-didone", [500, 600, 700]), ("Hanken Grotesk", "grotesque", [400, 500]), None, 1.414, 62,
  "Didot, 'Bodoni MT', Georgia, serif", "'Helvetica Neue', Arial, sans-serif", ["fashion", "luxury", "editorial"], "A variable didone with optical sizes over a plain grotesk; the fashion pair at any size."),
 ("italiana-hanken-grotesk", ("Italiana", "display", [400]), ("Hanken Grotesk", "grotesque", [400, 500]), None, 1.414, 62,
  "'Didot', Georgia, serif", "'Helvetica Neue', Arial, sans-serif", ["luxury", "elegant", "hospitality"], "A calligraphic display face for one line per page, a plain grotesque body."),
 ("cormorant-garamond-geist", ("Cormorant Garamond", "serif-old-style", [400, 500, 600]), ("Geist", "neo-grotesque", [400, 500]), "Geist Mono", 1.414, 62,
  "'Cormorant', Garamond, Georgia, serif", "system-ui, -apple-system, 'Segoe UI', sans-serif", ["giant serif", "elegant", "editorial"], "Cormorant at 10rem and above, where its small x-height becomes elegance; Geist keeps the page quiet beneath."),
]

STYLES = [
 dict(id="acid-lab", name="Acid lab", family="technical", summary="Black, off-white and one acid green on a visible grid; mono labels, bordered cells with corner crosses, a marquee of real nouns, dithered artwork.",
      traits=["one acid accent", "bordered cell grid", "mono labels", "dithered art", "square corners"], signals=["technical", "confident", "current", "sharp"],
      radius_scale="none", shadow="none", density="compact", art={"hero": "dither", "feature": "figure"},
      layout={"marketing": {"hero": "ticker", "features": "cells", "proof": "statement", "cta": "giant", "footer": "colophon"}, "app": {"shell": "rail", "table": "ledger", "detail": "inspector"}, "content": {"header": "minimal", "article": "with-toc", "list": "archive", "footer": "colophon"}, "store": {"hero": "tiles", "grid": "three", "product": "gallery-left", "cart": "page", "footer": "colophon"}},
      tells=["neon on dark for a non-technical product", "glow behind the accent"], inspired=["https://warp.dev", "https://basement.studio", "https://vercel.com/ship"],
      ideas=["one-hot-colour", "bordered-cells-crosses", "marquee-divider", "dithered-imagery", "bracket-button", "index-numbers-mono", "colophon-footer", "tight-display"],
      palettes=["acid-lab", "phosphor", "midnight-lime", "carbon-signal", "lime-graphite"], pairings=["mona-sans-kode-mono", "kode-mono-mona-sans", "familjen-grotesk-martian-mono", "geist-mono-geist", "bricolage-grotesque-instrument-sans"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="underline", card_edge="border", nav="compact", divider="hairline", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "underline-grow", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "page-crossfade-vt", "number-count-up", "menu-stagger-30"],
      icon="tabler", suits=["developer-tool", "saas", "ai-product", "event", "documentation"], moods=["technical", "bold", "modern", "energetic", "precise", "raw"], page_types=["marketing", "app", "content"]),
 dict(id="paper-signal", name="Paper & signal", family="editorial", summary="Warm paper, a transitional serif at broadsheet scale, hairline rules, signal red on one rule and one word; dates, issue numbers and archive lists everywhere.",
      traits=["broadsheet masthead", "signal red once", "hairlines", "archive lists", "numbered figures"], signals=["literate", "serious", "current", "trustworthy"],
      radius_scale="none", shadow="none", density="airy", art={"hero": "contours", "feature": "figure"},
      layout={"marketing": {"hero": "manifesto", "features": "numerals", "proof": "giant-quote", "cta": "inline", "footer": "colophon"}, "content": {"header": "broadsheet", "article": "side-notes", "list": "archive", "footer": "colophon"}, "store": {"hero": "collection", "grid": "editorial", "product": "sticky-buy", "cart": "page", "footer": "minimal"}},
      tells=["cream plus terracotta", "italic serif headline"], inspired=["https://press.stripe.com", "https://www.lrb.co.uk", "https://worksinprogress.co"],
      ideas=["broadsheet-masthead", "one-hot-colour", "giant-numerals-features", "single-giant-quote", "archive-index-list", "hanging-punctuation-quotes", "captioned-figures", "colophon-footer"],
      palettes=["paper-signal", "paper-ink", "cherry-paper", "stone-serif", "brick-parchment"], pairings=["newsreader-hanken-grotesk", "libre-caslon-display-libre-franklin", "source-serif-4-public-sans", "literata-albert-sans", "fraunces-figtree"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="underline", card_edge="flat", nav="airy", divider="hairline", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "accordion-height", "scroll-progress-bar", "scroll-reveal-once"],
      icon="phosphor", suits=["editorial", "nonprofit", "education", "community", "general-website"], moods=["serious", "classic", "trustworthy", "calm", "precise", "elegant"], page_types=["content", "marketing"]),
 dict(id="archive-index", name="Archive index", family="minimal", summary="An index rather than a brochure: one grotesque, a wide mono for dates and counts, hover rows that reveal images, ledger lists, a colophon with the local time.",
      traits=["index lists", "mono dates and counts", "hover image reveal", "no cards", "one link colour"], signals=["considered", "quiet", "current", "honest"],
      radius_scale="none", shadow="none", density="regular", art={"hero": "ruler", "feature": "figure"},
      layout={"marketing": {"hero": "index", "features": "hover-list", "proof": "none", "cta": "inline", "footer": "colophon"}, "content": {"header": "minimal", "article": "single", "list": "archive", "footer": "colophon"}, "store": {"hero": "tiles", "grid": "editorial", "product": "gallery-top", "cart": "page", "footer": "colophon"}},
      tells=["cards around list items", "gradient anything"], inspired=["https://www.are.na", "https://read.cv", "https://klim.co.nz"],
      ideas=["hover-list-image", "index-numbers-mono", "archive-index-list", "colophon-footer", "underline-offset-links", "tabular-everything", "split-nav-live-meta", "editorial-product-grid"],
      palettes=["archive-ink", "harbor-grey", "paper-ink", "bone-teal", "nordic-ice"], pairings=["familjen-grotesk-martian-mono", "martian-mono-familjen-grotesk", "inter-tight-inter", "host-grotesk-funnel-sans", "schibsted-grotesk-inter"],
      treatments=dict(button_shape="square", button_fill="ghost", input_edge="underline", card_edge="flat", nav="airy", divider="hairline", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "layout-flip", "menu-stagger-30"],
      icon="radix", suits=["portfolio", "agency", "editorial", "documentation", "luxury-commerce"], moods=["minimal", "quiet", "precise", "modern", "confident"], page_types=["marketing", "content", "store"]),
 dict(id="raw-document", name="Raw document", family="bold", summary="A web page that admits it is a document: system serif, default link blue, visible borders, tables, no cards, no shadows, square buttons with brackets; honest to the point of style.",
      traits=["system serif", "default link blue", "visible borders", "tables", "no decoration"], signals=["raw", "honest", "fast", "direct"],
      radius_scale="none", shadow="none", density="compact", art={"hero": "ruler", "feature": "figure"},
      layout={"marketing": {"hero": "letter", "features": "spec", "proof": "none", "cta": "inline", "footer": "minimal"}, "content": {"header": "minimal", "article": "single", "list": "lines", "footer": "minimal"}, "app": {"shell": "topbar", "table": "ledger", "detail": "panel"}},
      tells=["rounded cards", "icons in circles"], inspired=["https://craigmod.com", "https://berkeleygraphics.com", "https://100r.co"],
      ideas=["bracket-button", "tabular-everything", "underline-offset-links", "captioned-figures", "ledger-table", "colophon-footer"],
      palettes=["raw-document", "paper-ink", "archive-ink", "harbor-grey"], pairings=["system-serif-stack", "libre-caslon-display-libre-franklin", "newsreader-hanken-grotesk", "ibm-plex-mono-ibm-plex-sans", "system-ui-stack"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="hairline", card_edge="flat", nav="compact", divider="rule", image_corner="none", focus_ring="offset", link_style="both", elevation="none"),
      motion=["hover-tint", "underline-grow", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "page-crossfade-vt", "accordion-height", "layout-flip"],
      icon="radix", suits=["documentation", "portfolio", "community", "developer-tool", "editorial"], moods=["raw", "minimal", "serious", "precise", "classic"], page_types=["marketing", "content", "app"]),
 dict(id="night-grain", name="Night grain", family="dark", summary="Warm near-black with film grain, a serif display at scale, one amber accent, strands of generated line art, a single giant quote and a colophon; dark without the blue glow.",
      traits=["warm black", "film grain", "serif display", "amber accent", "line-art strands"], signals=["premium", "calm", "technical", "nocturnal"],
      radius_scale="sm", shadow="none", density="regular", art={"hero": "strands", "feature": "figure"},
      layout={"marketing": {"hero": "object", "features": "numerals", "proof": "giant-quote", "cta": "giant", "footer": "colophon"}, "app": {"shell": "rail", "table": "ledger", "detail": "inspector"}, "content": {"header": "minimal", "article": "with-toc", "list": "archive", "footer": "colophon"}},
      tells=["purple glow blobs", "medium grey body text"], inspired=["https://resend.com", "https://warp.dev", "https://www.raycast.com"],
      ideas=["film-grain", "single-giant-quote", "giant-numerals-features", "colophon-footer", "line-mask-reveal", "tabular-everything", "index-numbers-mono"],
      palettes=["night-grain", "graphite-amber", "graphite-coral", "obsidian-copper", "bronze-night"], pairings=["newsreader-hanken-grotesk", "cormorant-garamond-geist", "fraunces-figtree", "mona-sans-kode-mono", "instrument-serif-instrument-sans"],
      treatments=dict(button_shape="rounded", button_fill="soft", input_edge="filled", card_edge="border", nav="airy", divider="hairline", image_corner="sm", focus_ring="glow", link_style="underline", elevation="none"),
      motion=["hover-tint", "enter-fade-up-8", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "scroll-reveal-once", "number-count-up", "ambient-glow-slow"],
      icon="lucide", suits=["developer-tool", "ai-product", "saas", "fintech", "mobile-app"], moods=["premium", "calm", "technical", "confident", "elegant"], page_types=["marketing", "app", "content"]),
 dict(id="phosphor-terminal", name="Phosphor terminal", family="technical", summary="Black glass, phosphor green, a dot-matrix display face for the one big line, mono everywhere else, scanlines, ASCII artwork and bracket buttons; hardware and terminal brands.",
      traits=["dot-matrix display", "scanlines", "ascii art", "bracket buttons", "phosphor green"], signals=["technical", "playful", "nostalgic", "precise"],
      radius_scale="none", shadow="none", density="compact", art={"hero": "ascii", "feature": "figure"},
      layout={"marketing": {"hero": "specimen", "features": "spec", "proof": "none", "cta": "ticket", "footer": "colophon"}, "app": {"shell": "rail", "table": "ledger", "detail": "panel"}, "store": {"hero": "tiles", "grid": "three", "product": "gallery-left", "cart": "page", "footer": "colophon"}},
      tells=["typewriter text animation", "fake terminal typing"], inspired=["https://teenage.engineering", "https://ghostty.org", "https://play.date"],
      ideas=["scanlines", "ascii-field", "bracket-button", "ticket-cta", "tabular-everything", "colophon-footer", "graph-paper-grid", "command-palette-first"],
      palettes=["phosphor", "terminal-green", "acid-lab", "carbon-signal"], pairings=["doto-geist", "pixelify-sans-ibm-plex-sans", "kode-mono-mona-sans", "space-mono-space-grotesk", "jetbrains-mono-inter"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="underline", card_edge="border", nav="compact", divider="rule", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "menu-stagger-30", "number-count-up"],
      icon="tabler", suits=["developer-tool", "ecommerce", "mobile-app", "event", "community"], moods=["technical", "playful", "raw", "precise", "futuristic"], page_types=["marketing", "app", "store"]),
 dict(id="cobalt-block", name="Cobalt block", family="expressive", summary="Cream and International Klein Blue in full-bleed blocks, a display face stacked one word per line, the nav inverting over each block, fill-up buttons and a coral counter-colour used once.",
      traits=["colour-blocked sections", "stacked display words", "fill-up buttons", "inverting nav", "one counter colour"], signals=["bold", "confident", "cultural", "modern"],
      radius_scale="none", shadow="none", density="regular", art={"hero": "mark", "feature": "swiss"},
      layout={"marketing": {"hero": "stacked", "features": "bands", "proof": "statement", "cta": "band", "footer": "giant"}, "store": {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy", "cart": "drawer", "footer": "giant"}, "content": {"header": "broadsheet", "article": "single", "list": "archive", "footer": "giant"}},
      tells=["gradient between the two colours", "rounded pill buttons"], inspired=["https://arc.net", "https://www.cos.com", "https://www.polestar.com"],
      ideas=["colour-blocking-sections", "stacked-words-alt-face", "fill-up-button", "marquee-divider", "tight-display", "inverted-closing-section", "lookbook-opening"],
      palettes=["cobalt-cream", "cobalt-paper", "butter-cobalt", "signal-orange", "sky-tomato"], pairings=["big-shoulders-work-sans", "unbounded-onest", "funnel-display-funnel-sans", "syne-manrope", "archivo-black-archivo"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="underline", card_edge="flat", nav="airy", divider="space", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-slide-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "scroll-reveal-once", "hero-mask-reveal", "menu-stagger-30"],
      icon="phosphor", suits=["agency", "event", "ecommerce", "education", "nonprofit", "luxury-commerce"], moods=["bold", "confident", "energetic", "modern", "playful"], page_types=["marketing", "store", "content"]),
 dict(id="giant-serif", name="Giant serif", family="editorial", summary="A serif at ten rem and above as the whole image, a letter or manifesto as the first screen, side notes, hanging punctuation, warm stone white and one deep link colour; built for words.",
      traits=["serif display at 10rem", "letter hero", "side notes", "hanging punctuation", "one deep link colour"], signals=["literate", "elegant", "calm", "considered"],
      radius_scale="none", shadow="none", density="airy", art={"hero": "contours", "feature": "figure"},
      layout={"marketing": {"hero": "letter", "features": "ledger", "proof": "giant-quote", "cta": "inline", "footer": "colophon"}, "content": {"header": "masthead", "article": "side-notes", "list": "archive", "footer": "colophon"}, "store": {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy", "cart": "page", "footer": "minimal"}},
      tells=["italic serif as the only idea", "cream plus terracotta"], inspired=["https://arc.net", "https://asteriskmag.com", "https://www.noemamag.com"],
      ideas=["manifesto-hero", "hanging-punctuation-quotes", "single-giant-quote", "side-notes-column", "archive-index-list", "captioned-figures", "colophon-footer", "underline-offset-links"],
      palettes=["stone-serif", "paper-ink", "paper-signal", "espresso-cream", "clay-bone"], pairings=["cormorant-garamond-geist", "libre-caslon-display-libre-franklin", "newsreader-hanken-grotesk", "eb-garamond-onest", "bodoni-moda-inter-tight"],
      treatments=dict(button_shape="square", button_fill="ghost", input_edge="underline", card_edge="flat", nav="airy", divider="hairline", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "scroll-progress-bar", "scroll-reveal-once"],
      icon="phosphor", suits=["editorial", "luxury-commerce", "nonprofit", "education", "portfolio", "real-estate"], moods=["elegant", "calm", "classic", "quiet", "premium"], page_types=["marketing", "content", "store"]),
 dict(id="signal-orange", name="Signal orange", family="expressive", summary="Cream, warm black and a sunset orange used hard: a condensed display face, stickers with true words, a stat wall of sourced figures, a ticket call to action, flat everywhere.",
      traits=["sunset orange", "condensed display", "stickers", "stat wall", "flat colour"], signals=["energetic", "warm", "bold", "friendly"],
      radius_scale="sm", shadow="hard", density="regular", art={"hero": "stamp", "feature": "swiss"},
      layout={"marketing": {"hero": "poster", "features": "numerals", "proof": "stat-wall", "cta": "ticket", "footer": "giant"}, "store": {"hero": "product", "grid": "editorial", "product": "gallery-left", "cart": "drawer", "footer": "giant"}, "content": {"header": "masthead", "article": "single", "list": "archive", "footer": "giant"}},
      tells=["gradient orange", "emoji"], inspired=["https://mistral.ai", "https://cursor.com", "https://liquiddeath.com"],
      ideas=["one-hot-colour", "rotated-stickers", "stat-wall", "ticket-cta", "count-up-numbers", "marquee-divider", "tight-display"],
      palettes=["signal-orange", "poppy-cream", "tangerine-slate", "clay-canvas", "hazard-yellow"], pairings=["big-shoulders-work-sans", "anton-work-sans", "parkinsans-hanken-grotesk", "archivo-black-archivo", "bricolage-grotesque-instrument-sans"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="hairline", card_edge="border", nav="compact", divider="rule", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-lift-2", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "number-count-up", "spring-pop", "menu-stagger-30"],
      icon="tabler", suits=["ai-product", "local-business", "event", "ecommerce", "community", "education"], moods=["energetic", "bold", "warm", "friendly", "playful"], page_types=["marketing", "store", "content"]),
 dict(id="clay-canvas", name="Clay canvas", family="soft", summary="Anthropic's canvas: warm off-white, ink, one clay accent and an olive second; a serif body at reading size, cream and ink bands, captioned figures, hairline accordions, a colophon. Soft without pastel or gradient.",
      traits=["warm canvas", "clay accent", "serif body for reading", "cream and ink bands", "captioned figures"], signals=["calm", "trustworthy", "warm", "considered"],
      radius_scale="md", shadow="hairline", density="regular", art={"hero": "grain_disc", "feature": "contours"},
      layout={"marketing": {"hero": "statement", "features": "bands", "proof": "giant-quote", "cta": "inline", "footer": "colophon"}, "content": {"header": "masthead", "article": "side-notes", "list": "lines", "footer": "colophon"}, "app": {"shell": "sidebar", "table": "comfortable", "detail": "panel"}},
      tells=["cream plus terracotta as the whole idea", "rounded gradient cards"], inspired=["https://www.anthropic.com", "https://granola.ai", "https://www.craft.do"],
      ideas=["captioned-figures", "hairline-accordion", "single-giant-quote", "inverted-closing-section", "colophon-footer", "underline-offset-links", "view-transitions-pages"],
      palettes=["clay-canvas", "clay-bone", "bone-teal", "olive-ivory", "moss-cream"], pairings=["newsreader-hanken-grotesk", "fraunces-figtree", "geologica-geologica", "source-serif-4-public-sans", "funnel-display-funnel-sans"],
      treatments=dict(button_shape="rounded", button_fill="solid", input_edge="hairline", card_edge="border", nav="airy", divider="hairline", image_corner="sm", focus_ring="offset", link_style="underline", elevation="one"),
      motion=["hover-tint", "enter-fade-up-8", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "accordion-height", "scroll-reveal-once", "layout-flip"],
      icon="lucide", suits=["ai-product", "saas", "health", "education", "nonprofit", "general-website"], moods=["calm", "trustworthy", "warm", "friendly", "quiet", "serious"], page_types=["marketing", "content", "app"]),
]


def oklch_table(anchors, dark_anchors):
    bg, tx, pr, ac = anchors
    roles = derive_roles(bg, tx, pr, ac)
    if dark_anchors:
        d = derive_roles(*dark_anchors)
        roles["dark"] = d["dark"] if hex_to_oklch(dark_anchors[0])[0] < 0.5 else d["light"]
    return roles


def main():
    g = json.load(open(GRAPH, encoding="utf-8"))
    ids = {n["id"] for n in g["nodes"]}
    fams = {x["family"] for x in json.load(open(FONTS, encoding="utf-8"))["families"]}
    added = {"palette": 0, "type-pairing": 0, "style": 0}
    for slug, name, temp, scheme, hue, notes, light, dark, inspired in PALETTES:
        nid = "palette." + slug
        if nid in ids:
            continue
        roles = oklch_table(light, dark)
        node = {"id": nid, "kind": "palette", "name": name, "temperature": temp, "scheme": scheme, "hue_family": hue, "notes": notes,
                "light": roles["light"], "dark": roles["dark"], "source": SRC, "added": T, "last_verified": T, "confidence": 0.8, "inspired_by": inspired}
        res = resolve_palette(node)
        if res["warnings"]:
            print("PALETTE", slug, res["warnings"])
        g["nodes"].append(node); ids.add(nid); added["palette"] += 1
    for pid, h, b, mono, ratio, measure, fh, fb, moods, notes in PAIRINGS:
        nid = "type-pairing." + pid
        if nid in ids:
            continue
        for fam in (h[0], b[0], mono):
            if fam and fam not in fams:
                raise SystemExit("unknown Google family: %s" % fam)
        def face(f):
            return {"family": f[0], "category": f[1], "weights": f[2], "source": "google"}
        families = [(h[0], h[2]), (b[0], b[2])] + ([(mono, [400, 500])] if mono else [])
        parts = ["family=%s:wght@%s" % (quote_plus(f), ";".join(str(w) for w in sorted(set(ws)))) for f, ws in families]
        node = {"id": nid, "kind": "type-pairing", "name": "%s / %s" % (h[0], b[0]) if h[0] != b[0] else "%s / %s" % (h[0], mono or "system"),
                "heading": face(h), "body": face(b), "fallback_heading": fh, "fallback_body": fb, "scale_ratio": ratio, "measure_ch": measure,
                "css_url": "https://fonts.googleapis.com/css2?%s&display=swap" % "&".join(parts), "license": "OFL", "moods": moods, "notes": notes,
                "source": SRC, "added": T, "last_verified": T, "confidence": 0.8}
        if mono:
            node["mono"] = {"family": mono, "category": "mono", "weights": [400, 500], "source": "google"}
        g["nodes"].append(node); ids.add(nid); added["type-pairing"] += 1
    for s in STYLES:
        nid = "style." + s["id"]
        if nid in ids:
            continue
        node = {"id": nid, "kind": "style", "name": s["name"], "family": s["family"], "summary": s["summary"], "traits": s["traits"], "signals": s["signals"],
                "radius_scale": s["radius_scale"], "shadow": s["shadow"], "density": s["density"], "layout_defaults": s["layout"], "best_page_types": s["page_types"],
                "tells_to_avoid": s["tells"], "art": s["art"], "conventionality": "distinct", "inspired_by": s["inspired"], "ideas": ["idea." + i for i in s["ideas"]],
                "source": SRC, "added": T, "last_verified": T, "confidence": 0.8}
        for i in node["ideas"]:
            assert i in ids, i
        g["nodes"].append(node); ids.add(nid); added["style"] += 1
        for axis, val in s["treatments"].items():
            tid = "treatment.%s-%s" % (axis.replace("_", "-"), val); assert tid in ids, tid
            g["edges"].append({"from": nid, "to": tid, "kind": "defaults_to", "weight": 1.0, "evidence": []})
        for m in s["motion"]:
            mid = "motion-pattern." + m; assert mid in ids, mid
            g["edges"].append({"from": nid, "to": mid, "kind": "defaults_to", "weight": 1.0, "evidence": []})
        g["edges"].append({"from": nid, "to": "icon-set." + s["icon"], "kind": "pairs_with", "weight": 0.9, "evidence": []})
        for i, pal in enumerate(s["palettes"]):
            pid = "palette." + pal; assert pid in ids, pid
            g["edges"].append({"from": nid, "to": pid, "kind": "pairs_with", "weight": round(0.95 - i * 0.08, 2), "evidence": []})
        for i, pr in enumerate(s["pairings"]):
            pid = "type-pairing." + pr; assert pid in ids, pid
            g["edges"].append({"from": nid, "to": pid, "kind": "pairs_with", "weight": round(0.95 - i * 0.08, 2), "evidence": []})
        for i, pt in enumerate(s["suits"]):
            pid = "product-type." + pt; assert pid in ids, pid
            g["edges"].append({"from": pid, "to": nid, "kind": "suits", "weight": round(0.9 - i * 0.08, 2), "evidence": []})
        for i, m in enumerate(s["moods"]):
            mid = "mood." + m; assert mid in ids, mid
            g["edges"].append({"from": mid, "to": nid, "kind": "expresses", "weight": round(0.9 - i * 0.07, 2), "evidence": []})
        for i in node["ideas"]:
            if not any(e["from"] == i and e["to"] == nid for e in g["edges"]):
                g["edges"].append({"from": i, "to": nid, "kind": "pairs_with", "weight": 0.8, "evidence": []})
    json.dump(g, open(GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=False); open(GRAPH, "a", encoding="utf-8").write("\n")
    print("added", added)


if __name__ == "__main__":
    main()
