"""0.5.0: styles built around the liveness hooks and distinctive display faces. Idempotent."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "skills/preview-first/scripts"))
import add_styles_030 as base

PALETTES = [
 ("led-board","LED board","neutral","dark","green","Black glass with bone-white dots and one green lamp colour; the register of a station board.",("#f2f2ee","#121212","#0b7a3b","#b36b00"),("#0a0a0a","#f2f2ee","#39ff6a","#ffb000"),[]),
 ("broadcast","Broadcast","cool","dark","blue","Charcoal, chalk and a broadcast blue with an amber second; a live graphics register.",("#f4f5f7","#15171a","#1540c8","#a56400"),("#15171a","#f4f5f7","#4f7dff","#ffb547"),[]),
 ("workshop","Workshop","warm","light","orange","Kraft paper, soot and safety orange; a workshop tag.",("#e9e2d3","#1f1b17","#c2410c","#1f1b17"),None,[]),
 ("ink-bloom","Ink & bloom","cool","light","pink","Paper white, ink and one magenta used like a highlighter.",("#f8f7f4","#141414","#b4126b","#141414"),None,[]),
]
PAIRINGS = [
 ("doto-mona-sans",("Doto","display",[600,800,900]),("Mona Sans","neo-grotesque",[400,500]),"Geist Mono",1.414,62,"'Courier New', monospace","'Helvetica Neue', Arial, sans-serif",["hardware","signal","live"],"A dot-matrix display face for the one line that matters, with a neutral variable sans for everything else; the dots are the picture."),
 ("silkscreen-ibm-plex-sans",("Silkscreen","display",[400,700]),("IBM Plex Sans","grotesque",[400,500,600]),"IBM Plex Mono",1.333,64,"'Courier New', monospace","'Helvetica Neue', Arial, sans-serif",["pixel","games","retro"],"A coarse pixel face at large sizes only; Plex keeps the body readable."),
 ("rubik-mono-one-archivo",("Rubik Mono One","display",[400]),("Archivo","grotesque",[400,500]),"Martian Mono",1.414,62,"'Arial Black', sans-serif","'Helvetica Neue', Arial, sans-serif",["broadcast","sport","bold"],"A wide heavy mono display for scoreboards and lower thirds over a plain grotesque."),
 ("bungee-work-sans",("Bungee","display",[400]),("Work Sans","grotesque",[400,500]),"IBM Plex Mono",1.414,64,"Impact, sans-serif","'Helvetica Neue', Arial, sans-serif",["signage","playful","loud"],"A sign-painter display face for one word per screen."),
 ("big-shoulders-stencil-mona-sans",("Big Shoulders Stencil","display",[700,800,900]),("Mona Sans","neo-grotesque",[400,500]),"Martian Mono",1.414,62,"'Arial Narrow', Impact, sans-serif","'Helvetica Neue', Arial, sans-serif",["workshop","stencil","industrial"],"A stencil cut of a condensed display for crate-stamp headlines."),
 ("bricolage-grotesque-opsz-geist",("Bricolage Grotesque","grotesque",[300,500,800]),("Geist","neo-grotesque",[400,500]),"Geist Mono",1.414,64,"'Helvetica Neue', Arial, sans-serif","system-ui, -apple-system, 'Segoe UI', sans-serif",["variable","editorial","expressive"],"Bricolage across its weight axis, so the headline can move from 300 to 800 under the pointer."),
 ("tiny5-geist",("Tiny5","display",[400]),("Geist","neo-grotesque",[400,500]),"Geist Mono",1.333,62,"'Courier New', monospace","system-ui, -apple-system, 'Segoe UI', sans-serif",["pixel","tiny","toy"],"A five-pixel face with a width axis for labels and one headline; Geist for text."),
]
STYLES = [
 dict(id="led-board", name="LED board", family="technical", summary="A station departure board: black glass, bone dots, one green lamp colour. The headline is drawn as a dot matrix that lights up under the pointer, the figures are tabular, the buttons are brackets, a blinking caret marks the action.",
      traits=["dot-matrix headline", "lamp green", "tabular figures", "bracket buttons", "blinking caret"], signals=["technical", "live", "precise", "nostalgic"],
      radius_scale="none", shadow="none", density="compact", art={"hero": "ascii", "feature": "figure"},
      layout={"marketing": {"hero": "specimen", "features": "ledger", "proof": "none", "cta": "ticket", "footer": "colophon"}, "app": {"shell": "none", "view": "board", "table": "dense", "detail": "none", "extras": "none"}, "store": {"hero": "tiles", "grid": "three", "product": "gallery-left", "cart": "page", "footer": "colophon"}, "content": {"header": "minimal", "article": "single", "list": "archive", "footer": "colophon"}},
      tells=["typewriter animation", "green glow"], inspired=[],
      ideas=["dot-matrix-headline", "decode-scramble", "blinking-caret-action", "bracket-button", "tabular-everything", "split-nav-live-meta", "colophon-footer", "pointer-dot-grid"],
      palettes=["led-board", "phosphor", "acid-lab", "carbon-signal", "terminal-green"], pairings=["doto-mona-sans", "tiny5-geist", "kode-mono-mona-sans", "silkscreen-ibm-plex-sans", "mona-sans-kode-mono"],
      treatments=dict(button_shape="square", button_fill="outline", input_edge="underline", card_edge="border", nav="compact", divider="hairline", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "number-count-up", "menu-stagger-30"],
      icon="tabler", suits=["developer-tool", "event", "travel", "mobile-app", "community", "saas"], moods=["technical", "precise", "energetic", "futuristic", "raw"], page_types=["marketing", "app", "store"]),
 dict(id="broadcast", name="Broadcast", family="bold", summary="Live graphics: charcoal, chalk and broadcast blue, a wide heavy mono display, a focus board with the one figure at display size, tickers that lean with scroll speed, count-ups, a pinned action.",
      traits=["wide mono display", "velocity skew", "focus board", "count-ups", "pinned action"], signals=["energetic", "live", "bold", "precise"],
      radius_scale="none", shadow="none", density="regular", art={"hero": "bars", "feature": "sparklines"},
      layout={"marketing": {"hero": "kinetic", "features": "numerals", "proof": "none", "cta": "band", "footer": "giant"}, "app": {"shell": "none", "view": "board", "table": "dense", "detail": "none", "extras": "none"}, "content": {"header": "minimal", "article": "single", "list": "archive", "footer": "giant"}, "store": {"hero": "tiles", "grid": "three", "product": "gallery-left", "cart": "drawer", "footer": "giant"}},
      tells=["glow behind numbers", "gradient scoreboard"], inspired=[],
      ideas=["scroll-velocity-skew", "count-up-numbers", "tabular-everything", "marquee-divider", "pinned-action-bar", "tight-display", "giant-numerals-features", "character-reveal"],
      palettes=["broadcast", "lime-velodrome", "graphite-coral", "carbon-signal", "slate-signal"], pairings=["rubik-mono-one-archivo", "big-shoulders-mona-sans", "anton-instrument-sans", "unbounded-geist", "martian-mono-familjen-grotesk"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="hairline", card_edge="flat", nav="compact", divider="rule", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-slide-vt", "number-count-up", "scroll-reveal-once", "hero-mask-reveal"],
      icon="tabler", suits=["event", "community", "saas", "dashboard", "mobile-app", "education"], moods=["energetic", "bold", "precise", "confident", "serious"], page_types=["marketing", "app", "content"]),
 dict(id="workshop", name="Workshop", family="expressive", summary="A workshop tag: kraft paper, soot, safety orange, a stencil display, diagonal stripe fields, stamps that turn slowly, object stand-ins on a seamless, a ticket to book.",
      traits=["stencil display", "diagonal stripes", "rotating stamp", "kraft paper", "safety orange"], signals=["raw", "warm", "honest", "playful"],
      radius_scale="none", shadow="hard", density="regular", art={"hero": "stamp", "feature": "object"},
      layout={"marketing": {"hero": "object", "features": "spec", "proof": "giant-quote", "cta": "ticket", "footer": "colophon"}, "store": {"hero": "product", "grid": "editorial", "product": "sticky-buy", "cart": "page", "footer": "colophon"}, "content": {"header": "minimal", "article": "single", "list": "lines", "footer": "colophon"}},
      tells=["distressed texture everywhere", "fake tape"], inspired=[],
      ideas=["diagonal-stripe-field", "rotating-badge", "rotated-stickers", "bracket-button", "ticket-cta", "captioned-figures", "colophon-footer", "artwork-trail"],
      palettes=["workshop", "signal-orange", "poster-red", "brick-parchment", "espresso-cream"], pairings=["big-shoulders-stencil-mona-sans", "archivo-black-hanken-grotesk", "anton-instrument-sans", "bungee-work-sans", "familjen-grotesk-martian-mono"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="hairline", card_edge="border", nav="compact", divider="rule", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-lift-2", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "spring-pop", "scroll-reveal-once"],
      icon="tabler", suits=["local-business", "ecommerce", "marketplace", "event", "community", "real-estate"], moods=["raw", "warm", "friendly", "playful", "confident"], page_types=["marketing", "store", "content"]),
 dict(id="variable", name="Variable", family="editorial", summary="Type that moves: a variable grotesque across its whole weight axis, the headline's weight following the pointer, characters revealing one by one, ink on paper with one magenta highlighter; everything else still.",
      traits=["weight follows the pointer", "character reveal", "ink and one highlighter", "hairlines", "tight display"], signals=["expressive", "literate", "current", "confident"],
      radius_scale="none", shadow="none", density="airy", art={"hero": "letterstack", "feature": "figure"},
      layout={"marketing": {"hero": "stacked", "features": "hover-list", "proof": "giant-quote", "cta": "inline", "footer": "colophon"}, "content": {"header": "broadsheet", "article": "side-notes", "list": "archive", "footer": "colophon"}, "store": {"hero": "lookbook", "grid": "editorial", "product": "sticky-buy", "cart": "page", "footer": "colophon"}},
      tells=["italic serif accent word", "gradient text"], inspired=[],
      ideas=["weight-follows-pointer", "character-reveal", "one-hot-colour", "hover-list-image", "tight-display", "hanging-punctuation-quotes", "colophon-footer", "outline-giant-word"],
      palettes=["ink-bloom", "paper-ink", "archive-ink", "paper-signal", "stone-serif"], pairings=["bricolage-grotesque-opsz-geist", "bricolage-grotesque-geist", "fraunces-instrument-sans", "big-shoulders-mona-sans", "mona-sans-kode-mono"],
      treatments=dict(button_shape="square", button_fill="ghost", input_edge="underline", card_edge="flat", nav="airy", divider="hairline", image_corner="none", focus_ring="offset", link_style="underline", elevation="none"),
      motion=["hover-tint", "underline-grow", "page-crossfade-vt", "exit-fade-fast", "press-scale-97", "focus-ring-pulse-once", "button-loading-swap", "hero-mask-reveal", "scroll-reveal-once"],
      icon="radix", suits=["agency", "portfolio", "editorial", "education", "nonprofit", "event"], moods=["bold", "confident", "modern", "elegant", "playful"], page_types=["marketing", "content", "store"]),
 dict(id="pixel-arcade", name="Pixel arcade", family="technical", summary="A cabinet and a cartridge: a coarse pixel display face, pixel-art marks, a pointer grid behind the hero, scramble on the headline, stickers, one hot colour on black or paper; playful without being childish.",
      traits=["pixel display", "pixel marks", "pointer grid", "scramble", "one hot colour"], signals=["playful", "technical", "nostalgic", "energetic"],
      radius_scale="none", shadow="hard", density="regular", art={"hero": "pixel", "feature": "figure"},
      layout={"marketing": {"hero": "mark", "features": "cells", "proof": "none", "cta": "giant", "footer": "giant"}, "app": {"shell": "bottom-tabs", "view": "board", "table": "dense", "detail": "none", "extras": "empty"}, "store": {"hero": "tiles", "grid": "three", "product": "gallery-left", "cart": "drawer", "footer": "giant"}},
      tells=["CRT filter on everything", "neon gradients"], inspired=[],
      ideas=["pointer-dot-grid", "decode-scramble", "rotated-stickers", "bracket-button", "one-hot-colour", "marquee-divider", "bordered-cells-crosses", "tabular-everything"],
      palettes=["phosphor", "led-board", "acid-lab", "hazard-yellow", "poster-red"], pairings=["silkscreen-ibm-plex-sans", "tiny5-geist", "pixelify-sans-ibm-plex-sans", "doto-mona-sans", "bungee-work-sans"],
      treatments=dict(button_shape="square", button_fill="solid", input_edge="hairline", card_edge="border", nav="compact", divider="rule", image_corner="none", focus_ring="inset", link_style="underline", elevation="none"),
      motion=["press-scale-97", "hover-tint", "exit-fade-fast", "button-loading-swap", "focus-ring-pulse-once", "underline-grow", "page-crossfade-vt", "spring-pop", "menu-stagger-30", "number-count-up"],
      icon="tabler", suits=["mobile-app", "event", "community", "education", "ecommerce", "developer-tool"], moods=["playful", "energetic", "technical", "raw", "futuristic"], page_types=["marketing", "app", "store"]),
]

def main():
    base.PALETTES[:] = PALETTES; base.PAIRINGS[:] = PAIRINGS; base.STYLES[:] = STYLES
    base.main()

if __name__ == "__main__":
    main()
