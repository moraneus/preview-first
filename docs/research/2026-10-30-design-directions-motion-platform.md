# Research: modern web UI directions, motion, platform CSS, AI tells, color systems (2026-10-30)

## 1. Style directions in use

### 1a. Dark luminous SaaS ("Linear look")
Near-black bg with faint cool tint, 1px low-alpha hairline borders, radial hero glow, blurred gradient blobs, glassy panels. Named in "The Linear effect" (https://rectangle.substack.com/p/the-linear-effect). 2026 variant swaps purple for vivid yellow/orange accents on dark (https://saaslandingpage.com/articles/5-design-trends-for-saas-and-ai-landing-pages-in-2026/). Type: tight grotesque (Inter/Geist/Söhne) + mono labels. Motion: slow ambient glow, product micro-demos; Linear's own 2026 refresh is calmer (https://linear.app/changelog/2026-03-12-ui-refresh). Suits dev tools, infra, AI. Clashes with consumer/health/finance trust, content-heavy. Now the #1 AI-slop signature; only use with a distinct accent and real product imagery.

### 1b. Monochrome engineering (Vercel/Geist)
Source: https://vercel.com/design.md. Geist Sans for prose/UI, Geist Mono only for code/paths/IDs/timestamps; monochrome by default, color only when it carries meaning plus a non-color cue; no gradients (except data scales); no ornamental shadows/glows; borders earned; no cards around every section; tabular numerals; prose 60-68ch; all-caps tracked eyebrows rejected; motion "default to stillness", bans marquees, typing cursors, pulsing indicators, parallax, bounce, scroll-reveal. Palette: black/white + 10-step gray + semantic status. Suits infra, docs, dashboards. Clashes with lifestyle, playful consumer.

### 1c. Warm editorial minimalism ("paper not glass")
Warm off-white canvas, warm near-black text, 1px rgba(0,0,0,.1) dividers, layered shadows under 5% total, 8px radius, one accent. Notion: #f6f5f4 / #31302e / #615d59 / #a39e98, accent #0075de (https://opendesigner.io/design-systems/notion). Serif display (Tiempos, Editorial New, GT America Serif, Fraunces, Instrument Serif) + quiet sans body. Avoid Didone + humanist sans. Suits knowledge tools, AI assistants, fintech/legal, publishing. Clashes with terminal aesthetics, neon, heavy glass. Warning: oversized italic serif headline is now an AI tell (https://tenex.studio/en/blog/ai-slop-8-signs/); cream + terracotta is the Claude-default tell.

### 1d. Gradient optimism (Stripe 2020 lineage)
White canvas, diagonal animated gradient bands, duotone icons, light-weight Söhne (https://fontsinuse.com/uses/35338/stripe-website-2020). Suits payments/platform. Generic gradient use is now a slop signal.

### 1e. Radical simplicity / product-screenshot led
Large type, whitespace, clean product shots (Linear, Attio). Suits products with strong UI; clashes with pre-product sites.

### 1f. Liquid Glass (Apple, Jun 2025) and web imitators
Translucent refracting material, specular highlights, concentric shapes (https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/). Raycast 2.0 adopted tastefully (https://www.raycast.com/blog/the-new-raycast). Legibility criticism. Web: backdrop-filter only on a real layered surface. Suits native-feeling companions, launchers, media. Clashes with text-dense UI, low-contrast palettes.

### 1g. Neo-brutalism / anti-design
Flat high-contrast fills, thick black borders, hard offset shadows, raw type; framed as an anti-AI signal (https://neubrutalism.com/). Suits indie tools, creative portfolios, Gen-Z consumer. Clashes with enterprise trust, dense data.

### 1h. Bento grids
Nested cells, mono labels; giving way to asymmetric flows. Suits feature overviews; clashes with longform.

Typography consensus: quiet grotesque body (Inter, Geist, Figtree, Söhne) + one personality display face (serif or mono) (https://www.gleamstudio.design/blog-post/font-trends-2026). Cal.com ships Cal Sans display (https://cal.com/font).

## 2. Motion practice

Emil Kowalski (https://emilkowal.ski/ui/agents-with-taste, https://emilkowal.ski/ui/great-animations): micro 100-150ms; tooltips/dropdowns 150-250ms; modals/drawers 200-300ms; keep UI under 300ms; exits ~20% faster; enter/exit viewport = ease-out, move/morph = ease-in-out, hover/color = ease, constant = linear; enter from scale(0.95) not 0; :active scale(0.97); transform-origin at trigger; animate only transform/opacity; interruptible; reduced motion = swap motion for fades. Curves: --ease-out: cubic-bezier(0.23, 1, 0.32, 1); --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1) (secondary source).
Rauno Freiberg (https://rauno.me/craft/interaction-design): respond to intent, interruptibility, immediate response during gesture, preserve momentum, animate selectively by frequency/novelty.
Material 3 (secondary): short 50/100/150/200, medium 250-400, long 450-600, extra-long 700-1000; standard cubic-bezier(0.2, 0, 0, 1); emphasized cubic-bezier(0.05, 0.7, 0.1, 1.0).
Springs: Apple model duration + bounce (0.15 barely, 0.3 noticeable, >0.4 exaggerated) (https://wwdcnotes.com/notes/wwdc23/10158). Motion: visualDuration + bounce (default 0.25), tween default 0.3s, spring() emits CSS (https://motion.dev/docs/spring). CSS linear() supported Chrome 113/FF 112/Safari 17.2.
View Transitions: same-document Chrome 111/Safari 18/Firefox 144; cross-document Chrome 126/Safari 18.2; Baseline 2025 (https://developer.chrome.com/blog/view-transitions-in-2025, https://web.dev/baseline/2025).
Scroll-driven animations: Chrome 115, Safari 26, Firefox 159; wrap in @supports (animation-timeline: scroll()).
Reduced motion: opt-in @media (prefers-reduced-motion: no-preference); keep fades; avoid the global 0.01ms hack (https://www.joshwcomeau.com/react/prefers-reduced-motion/).

## 3. Platform CSS support (caniuse, Sep 2026)

| Feature | Chrome | Firefox | Safari | Global |
|---|---|---|---|---|
| Container queries | 106 | 110 | 16.0 | 95.9% |
| :has() | 105 | 121 | 15.4 | 95.9% |
| oklch() | 111 | 113 | 15.4 | 95.1% |
| color-mix() | 111 | 113 | 16.2 | 94.8% |
| Relative color syntax | 131 | 133 | 18.0 | 93.5% |
| light-dark() | 123 | 120 | 17.5 | 91.3% |
| @property | 85 | 128 | 16.4 | 96.1% |
| @starting-style | 117 | 129 | 17.5 | 93.1% |
| Popover API | 114 | 125 | 17.0 | 93.6% |
| text-wrap: balance | 114 | 121 | 17.5 | wide |
| text-wrap: pretty | 117 | none | 26.0 | 87.6% |
| Anchor positioning | partial | partial | 27 | 87.4% |
| linear() easing | 113 | 112 | 17.2 | 94.0% |

Interop 2026: contrast-color(), attr(), shape(), scroll snap, container style queries, view transitions, scroll-driven animations, anchor positioning.
Tailwind v4: color-mix(in oklab), native @layer, @container, @theme tokens as custom properties.

## 4. AI-generated tells

Color/effects: indigo->purple / blue->violet gradients; gradient headline text; gradient CTA buttons; purple/blue/pink glows; glassmorphism without layering reason; perma dark + medium-grey body; 5+ gradient backgrounds (https://github.com/ravidsrk/slop-detect, https://www.925studios.co/blog/ai-slop-design-tells, https://tenex.studio/en/blog/ai-slop-8-signs/). Origin: Tailwind indigo-500 (https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p).
Type: unchosen Inter/Geist/Space Grotesk everywhere; centered hero in generic sans; oversized italic serif headline; uppercase letter-spaced eyebrow above H1.
Layout: centered hero + "Now in Beta" pill; exactly three icon-topped feature cards; six identical cards; rounded + soft shadow everywhere; decorative 01 02 03; fake "Trusted by" logo bar; gradient-initial avatars; unsourced stats bar; truncated testimonial names; no real images; cards around every section.
Copy: em-dash overload; emoji bullets; "It's not just X, it's Y"; "Whether you're X or Y"; tricolons; buzzwords; "Build faster. Ship smarter."; checkmark lists.
Motion: marquees, typing cursors, pulsing dots, parallax, bounce, scroll-reveal everywhere, hover zoom on imagery.
Fixes: explicit palette/typeface/reference; one solid accent; show the product; vary section layouts; real names; a tokens file the agent must obey.

## 5. Color systems

OKLCH (https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl): perceptual L; P3; state variants via relative color; provide sRGB base + @media (color-gamut: p3); lightness != contrast; tint neutrals.
Tailwind v4 (https://tailwindcss.com/docs/colors): oklch, 26 families, 11 steps 50-950, @theme overrides.
Radix 12-step (https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale): 1-2 backgrounds; 3-5 interactive bg; 6-8 borders; 9 solid (Sky/Mint/Lime/Yellow/Amber need dark text), 10 solid hover; 11 low-contrast text; 12 high-contrast text; APCA Lc 60/90 targets.
shadcn tokens (https://ui.shadcn.com/docs/theming): x / x-foreground pairs, --radius 0.625rem, .dark overrides.
Dark mode: semantic layer over primitives; color-scheme on :root; same hue, inverted lightness, lower chroma.
APCA vs WCAG (https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html): WCAG 2.x AA is the legal floor (EAA since 28 Jun 2025); APCA Lc 60 body / 75 / 90 as secondary design check.

## Low confidence
Material 3 values from mirrors; Emil Kowalski curves from mirrors; 2026 serif adoption claims by Stripe/Notion unverified.
