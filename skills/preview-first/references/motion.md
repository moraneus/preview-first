# Motion

Rules Claude applies when assigning, authoring and implementing motion for preview-first. Patterns live in `knowledge/graph.json` as `motion-pattern.*` nodes; the motion level comes from the brief (`constraints.motion_level`), the moods, or the style, and `motion_tokens` in `scripts/palette.py` turns it into `--pf-dur-*` and `--pf-ease-*` tokens.

Default to stillness. Motion answers a person's action, explains a change of state, or marks one orchestrated moment per page. Anything else is decoration. Sources: https://emilkowal.ski/ui/great-animations, https://rauno.me/craft/interaction-design, https://vercel.com/design.md.

## The four motion levels

| Level | Name | Permits | Forbidden (from `MOTION_FORBIDDEN` in export_design.py) |
|---|---|---|---|
| 0 | None | State changes snap. Only `motion-pattern.none`. All duration tokens are `0ms` | All animation |
| 1 | Subtle | Hover, press, focus, enter and exit of overlays, loading swaps, tab and accordion layout moves, page crossfade, reading progress | Ambient motion, scroll-driven effects, springs with visible bounce, page-load sequences |
| 2 | Expressive | Everything in 1 plus springs on switches, menu stagger, shared-element page slides, one scroll reveal on the hero, FLIP reorders, number count-up | Ambient glow, card tilt, page-load mask reveals |
| 3 | Showcase | Everything in 2 plus a single hero mask reveal, spring pop on new items, subtle card tilt, slow ambient glow on dark directions | Motion that blocks input or runs longer than 800ms (ambient glow excepted) |

Rules:
- A pattern is allowed only when its `level` is less than or equal to the direction's level. The recommender filters `defaults_to` edges by level; the exporter re-filters on override.
- Level 1 is the default for app, content and store pages. Level 2 for marketing. Level 3 only when the brief asks for showcase, launch, or a mood that carries `motion_level: 3`.
- One orchestrated moment per page at most, at any level.
- Animate only `transform` (or `translate`, `scale`, `rotate`) and `opacity`. Height, width, top, left, box-shadow and filter animate off the compositor and stutter. `clip-path` is the one exception, for the hero mask reveal.
- Every animation is interruptible: use CSS transitions or Motion, never a chained timeline that must finish before the next input counts.

## Duration and easing tokens

`motion_tokens(level)` emits these exact values:

| Token | Level 0 | Level 1 | Level 2 | Level 3 | Use |
|---|---|---|---|---|---|
| `--pf-dur-fast` | 0ms | 120ms | 140ms | 160ms | Hover, press, colour, focus ring |
| `--pf-dur-base` | 0ms | 200ms | 240ms | 280ms | Tooltips, dropdowns, popovers, toasts, tabs, accordions |
| `--pf-dur-slow` | 0ms | 320ms | 400ms | 480ms | Modals, drawers, layout moves, shared-element slides |
| `--pf-dur-page` | 0ms | 240ms | 320ms | 400ms | View transitions between routes |

| Token | Value | Use |
|---|---|---|
| `--pf-ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | Anything entering the viewport or growing from a trigger |
| `--pf-ease-in-out` | `cubic-bezier(0.77, 0, 0.175, 1)` | Anything already on screen that moves or morphs |
| `--pf-ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Exits, fast and decisive |
| `--pf-ease-spring` | `linear(0, 0.4 20%, 0.95 45%, 1.04 65%, 1)` | Switch thumbs, chips snapping into place; level 2 and above |
| `--pf-motion-level` | 0 to 3 | Read it in JS to pick a Motion or GSAP config |

Norms behind the numbers (https://emilkowal.ski/ui/agents-with-taste): micro interactions 100 to 150ms; tooltips and dropdowns 150 to 250ms; modals and drawers 200 to 300ms; keep UI under 300ms; exits about 20 percent faster than entries. Material 3 agrees on the bands (short 50 to 200, medium 250 to 400, long 450 to 600; secondary source). Components use the tokens, never literal milliseconds.

## Easing decision rule

Ask what the element is doing, not what it is.

- Entering or leaving the viewport (popover opens, toast arrives, dialog closes): `--pf-ease-out` in, `--pf-ease-in` out. Fast start, settled finish.
- Moving or morphing while already visible (tab indicator slides, accordion unfolds, list reorders, shared element travels): `--pf-ease-in-out`.
- Hover, press and colour changes: the browser's `ease` keyword. It is short enough that the curve barely shows.
- Constant motion (progress bars, skeleton shimmer, ambient drift, spinners): `linear`. Any curve on a loop reads as a hiccup.
- Never `ease-in` for an entry and never `linear` for anything a person triggered.
- Enter from `scale(0.95)` and 8px of translate, never from `scale(0)` or from off-screen, unless the element genuinely came from an edge (toast, drawer).
- Press feedback is `:active { transform: scale(0.97) }` on buttons and cards, with `transform-origin` at the trigger for popovers so they grow from where the pointer was.

## Springs

Describe a spring by duration and bounce, not stiffness and damping. Apple's model: bounce 0.15 is barely perceptible, 0.3 is noticeable, above 0.4 is exaggerated (https://wwdcnotes.com/notes/wwdc23/10158). Motion uses `visualDuration` and `bounce` with a default bounce of 0.25 (https://motion.dev/docs/spring).

- In CSS, `linear()` lets a spring run without JS. The token `--pf-ease-spring` is a 4-point approximation of duration 0.26s, bounce about 0.2. Generate a better one with Motion's `spring()` helper, which emits a `linear()` string, or with https://linear-easing-generator.netlify.app.
- `linear()` is Baseline widely available (Chrome 113, Firefox 112, Safari 17.2). Declare a plain `ease-out` first so an old engine still animates.
- Motion: `transition={{ type: "spring", visualDuration: 0.4, bounce: 0.25 }}`.
- In GSAP, `ease: "elastic.out(1, 0.6)"` approximates a 0.3 bounce; `"back.out(1.4)"` approximates 0.15.
- Springs belong on physical controls (switch thumb, slider knob, chip snap, drag release) and on `motion-pattern.spring-pop` at level 3. Never on page transitions, text or anything over 400ms.
- Under reduced motion, springs become `linear` or `--pf-ease-out` at `--pf-dur-fast`.

## View transitions

Support: same-document Chrome 111, Safari 18, Firefox 144; cross-document Chrome 126, Safari 18.2, Firefox later; Baseline newly available since October 2025 (https://developer.chrome.com/blog/view-transitions-in-2025, https://web.dev/baseline/2025). `platform-feature.view-transitions` carries the live status.

```css
@view-transition { navigation: auto; }           /* cross-document, MPA */
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: var(--pf-dur-page);
  animation-timing-function: var(--pf-ease-in-out);
}
.card-title { view-transition-name: var(--vt-name); } /* one unique name per element */
```

Rules:
- `motion-pattern.page-crossfade-vt` (level 1) is the default route transition: opacity only, `--pf-dur-page`.
- `motion-pattern.page-slide-vt` (level 2) names one element that persists across pages (a cover image, a title). Names must be unique per page; set them from data, not a static class.
- Same-document: wrap the DOM update in `document.startViewTransition(() => update())` and let CSS do the rest. Guard with `if (!document.startViewTransition) update();`.
- Keep the old and new snapshots under 400ms; long transitions make navigation feel slower, not richer.
- Reduced motion: `@media (prefers-reduced-motion: reduce) { ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important; } }`.

## Scroll-driven animations

Support: Chrome 115, Safari 26, Firefox 159; Baseline limited (`platform-feature.scroll-driven-animations`). Always guard:

```css
@supports (animation-timeline: scroll()) {
  .progress { animation: grow linear both; animation-timeline: scroll(root); }
  .hero-figure { animation: rise var(--pf-ease-out) both; animation-timeline: view(); animation-range: entry 0% entry 60%; }
}
```

Rules:
- Two patterns only: `motion-pattern.scroll-progress-bar` (level 1, `scroll(root)`, linear) and `motion-pattern.scroll-reveal-once` (level 2, `view()`, one section, the hero).
- Never attach `view()` to every section. One reveal per page.
- Without support the element is simply visible; never hide content behind a scroll animation that may not run.
- Do not use an IntersectionObserver polyfill to fake it on older engines; the fallback is the static page.

## Reduced motion

Source: https://www.joshwcomeau.com/react/prefers-reduced-motion/.

- Opt in, do not opt out. Write movement inside `@media (prefers-reduced-motion: no-preference)`. The default stylesheet then has no movement, which is also what a browser with no preference support gets.
- Keep fades. Opacity changes do not trigger vestibular symptoms; replace translate, scale, rotate and parallax with an opacity transition at `--pf-dur-fast`. Each pattern node's `reduced_motion` field says what to swap to.
- Keep durations under 200ms under `reduce`; DESIGN.md states this.
- No global `* { animation-duration: 0.01ms !important }` hack. It breaks `transitionend` and `animationend` logic, hides loading indicators and leaves state machines waiting. Target the patterns that move.
- In JS: `const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;` and pick the fade variant. Motion: `<MotionConfig reducedMotion="user">`. GSAP: `gsap.matchMedia()` with a `(prefers-reduced-motion: no-preference)` condition.
- Still test with the preference on: open the preview tile, toggle the OS setting, and confirm nothing jumps.

## Motion pattern ids

From `knowledge/graph.json`. Duration is `duration_ms`; the implementation column is the node's `implementation` field.

| Id | Trigger | ms | Level | Impl | Reduced motion |
|---|---|---|---|---|---|
| `motion-pattern.none` | ambient | 0 | 0 | css | n/a |
| `motion-pattern.press-scale-97` | press | 120 | 1 | css | keep (no translation) |
| `motion-pattern.hover-lift-2` | hover | 160 | 1 | css | replace with background tint |
| `motion-pattern.hover-tint` | hover | 150 | 1 | css | keep |
| `motion-pattern.underline-grow` | hover | 200 | 1 | css | keep (opacity only) |
| `motion-pattern.focus-ring-pulse-once` | focus | 180 | 1 | css | snap |
| `motion-pattern.enter-fade-up-8` | enter | 240 | 1 | css | fade only |
| `motion-pattern.enter-scale-95` | enter | 200 | 1 | css | fade only |
| `motion-pattern.exit-fade-fast` | exit | 150 | 1 | css | keep |
| `motion-pattern.button-loading-swap` | layout | 200 | 1 | css | keep |
| `motion-pattern.skeleton-shimmer` | ambient | 1400 | 1 | css | static grey blocks |
| `motion-pattern.toast-slide-in` | enter | 260 | 1 | css | fade only |
| `motion-pattern.tab-indicator-slide` | layout | 220 | 1 | css | snap |
| `motion-pattern.accordion-height` | layout | 240 | 1 | css | snap |
| `motion-pattern.page-crossfade-vt` | page | 220 | 1 | view-transitions | instant swap |
| `motion-pattern.scroll-progress-bar` | scroll | 0 | 1 | scroll-driven | keep |
| `motion-pattern.switch-thumb-spring` | press | 260 | 2 | css | linear 150ms |
| `motion-pattern.menu-stagger-30` | enter | 180 | 2 | css | no stagger, fade |
| `motion-pattern.page-slide-vt` | page | 320 | 2 | view-transitions | crossfade |
| `motion-pattern.scroll-reveal-once` | scroll | 400 | 2 | scroll-driven | static |
| `motion-pattern.layout-flip` | layout | 300 | 2 | motion | snap |
| `motion-pattern.number-count-up` | enter | 800 | 2 | css | static |
| `motion-pattern.spring-pop` | enter | 400 | 3 | motion | fade |
| `motion-pattern.card-tilt-subtle` | hover | 200 | 3 | css | none |
| `motion-pattern.hero-mask-reveal` | enter | 700 | 3 | css | fade |
| `motion-pattern.ambient-glow-slow` | ambient | 12000 | 3 | css | static gradient |

Notes on a few: `number-count-up` only for a real, sourced figure (no invented stats); `menu-stagger-30` delays 30ms per item and caps at six items; `ambient-glow-slow` only on dark directions and only behind a real product image; `card-tilt-subtle` rotates 2 degrees at most and is pointer-only.

## Forbidden motion

Each is a tell for unchosen, generated design or a known usability failure (https://vercel.com/design.md, https://github.com/ravidsrk/slop-detect, https://www.925studios.co/blog/ai-slop-design-tells). Refuse unless the brief names it, and say so in the rationale.

- Marquees and infinite logo tickers.
- Typing cursors and typewriter headlines.
- Pulsing dots, breathing badges, "live" indicators that pulse forever.
- Parallax backgrounds and mouse-follow layers.
- Bounce easings on entries, buttons or page transitions.
- Scroll-reveal on every section; fade-up cascades down the whole page.
- Hover zoom on imagery; cards that scale on hover.
- Gradient backgrounds that animate continuously (ambient glow at level 3 is the single exception, 12s and slower, dark directions only).
- Page-load sequences that hold content back for more than 700ms, or any animation that blocks input.
- Spinners where a skeleton or an inline label swap would do.
- Animated counters for numbers that were not real.

## Implementation notes

CSS (default for every pattern marked `css`):
- Transitions on `transform`, `translate`, `scale`, `opacity`, `background-color`, `text-decoration-color`, `box-shadow` (focus ring only). Use `transition-property` lists, never `transition: all`.
- Enter animations for popovers, dialogs and toasts use `@starting-style` with `transition-behavior: allow-discrete` so `display: none` elements animate in; guard with a fallback that simply shows the element (see references/platform.md).
- Accordion: `grid-template-rows: 0fr` to `1fr` on a wrapper with `overflow: hidden` on the inner element. No `max-height` hacks.
- Tab indicator: one absolutely positioned element moved with `translate` and `scale`, not left and width.
- Button loading swap: lock `min-inline-size` to the resting width, crossfade label and spinner.
- Number count-up: register `@property --n { syntax: "<integer>"; initial-value: 0; inherits: false }` and animate it; render with `counter-reset` and `content: counter(n)`.
- Hero mask reveal: `clip-path: inset(0 100% 0 0)` to `inset(0)` with `--pf-ease-in-out` over 700ms, once per session (store a flag in `sessionStorage`).

Motion (https://motion.dev, `npm i motion`; patterns marked `motion`):
- Use for layout animations (`layout` prop on a `motion.div`) and springs with bounce. Pass `transition={{ duration: 0.24, ease: [0.23, 1, 0.32, 1] }}` for tweens so the curve matches `--pf-ease-out`.
- `AnimatePresence` for exit animations in React; `mode="popLayout"` for lists.
- `<MotionConfig reducedMotion="user">` at the root honours the OS preference.
- Prefer `motion/react` and the lightweight `animate()` from `motion` for vanilla; do not import the whole framer legacy package.

GSAP (https://gsap.com/docs/v3/; patterns a direction chose for timeline work):
- Use only when a sequence needs a scrubbed timeline (a product demo, a showcase hero). Everything else is CSS or Motion.
- `gsap.matchMedia()` with `(prefers-reduced-motion: no-preference)` wraps every tween; the reduce branch sets end states instantly.
- ScrollTrigger only for the single allowed scroll moment; `scrub: true` with `once: true` and never pinned sections on content pages.
- Custom eases: `CustomEase.create("pfOut", "0.23, 1, 0.32, 1")` so GSAP and CSS share curves.
- GSAP ships under its own free licence since 2025; check the current terms at https://gsap.com/licensing/ before bundling.

Whatever the tool, read `--pf-motion-level` from `getComputedStyle(document.documentElement)` and refuse to run a pattern above it.
