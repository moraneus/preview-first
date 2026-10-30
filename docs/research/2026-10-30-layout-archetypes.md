# Layout archetypes: what makes a site read as designed, not generated (2026-10-30)

**Method.** 47 homepages loaded in headless Chromium at 1440×900 and 390×844 (viewport, +900px, +1800px, footer and mobile screenshots) and probed for computed styles: h1 size/alignment/offset, faces in use, 1px rules and their alpha, `tabular-nums`, sticky, card-like boxes, uppercase labels, mono/serif runs, footer height and link count. Text extracts supplemented. **Blocked / from memory:** lusion.co (preloader only; described from memory), ssense.com (Cloudflare on `/`; category page probed), arket.com (Akamai denied), uncommonstudio.com.au (video-only first frame), by-kin.com (loader), rewind.ai (domain now an unrelated AI-tool aggregator; dropped), cron.com → notion.com/product/calendar. Framer "top sellers" are self-reported; I used the marketplace Trending tab (Caspia, Soren, Jett, Arpeggio, Neiden). Webflow best-seller previews 404'd and were not surveyed.

## 1. Survey (first screen → footer)

Columns: first screen · grid · section separation · type (display/body, faces) · cards · imagery · footer · the handmade tell.

| Site | First screen | Grid | Separation | Type | Cards | Imagery | Footer | Handmade tell |
|---|---|---|---|---|---|---|---|---|
| [linear.app](https://linear.app) | Left-set 2-line H1 64px (Inter 510, −1.4px) at x=78, one-line subhead, **no buttons**, "New · Loops →" far right; product UI bleeds off bottom | 1344px, left-anchored | Whitespace + 84 alpha hairlines | 64/14 ≈ 4.6×; Inter + Berkeley Mono labels | 21 UI panels | Real UI, line-art isometrics | 494px, 5 cols | Two-tone lede paragraph; mono `FIG 0.1`; `tabular-nums` ×62 |
| [vercel.com](https://vercel.com) | Left 2-word H1 64px Geist 400 −3.8px at x=24, two pills, 3D triangle centre, plain 3-line list right | Asymmetric 3-col | `<hr>`, whitespace | 64/14; Geist + mono status | 0 | Canvas sculpture, UI | **846px**, 81 links, 2×6 cols | Section 2: left headline+UI, right plain feature list |
| [resend.com](https://resend.com) | Left H1 96px **Domaine serif**, 2 buttons, 3D object right | 1280 | 107 alpha hairlines | 96/18 ≈ 5.3×; serif + Inter + Commit Mono | 36 | 3D, code editor | 52px | Serif display on a dev tool; line-numbered code as section hero |
| [clerk.com](https://clerk.com) | Left H1 56px, **one** button + "Copy prompt" chip; UI composites right | 1280 | 19 `<hr>`, dark bands | 56/11; Söhne Mono | 64 UI fragments | Real auth UI, dark bento | 413px | Agent prompt in hero; `Name — tagline` headings |
| [raycast.com](https://raycast.com) | Centered H1 64px on full-bleed abstract render; one button + mono fine print | Centered | Art per section; 68 hairlines | 64/18; Inter + Geist Mono | 24 | Abstract 3D + UI | Giant multi-col | ⌘ ↵ as text; `FIG_0`; "Favorite Feature:" |
| [cal.com](https://cal.com) | Split inside a **bordered container**: H1 64px Cal Sans + 2 stacked buttons; UI stack right | Inset frame | Centered H2s, mono `01 02 03` | 64/16 | 45 | UI mockups | 4 cols | Closest to generic SaaS in the set |
| [warp.dev](https://warp.dev) | Left H1 54px **Azeret Mono**, 2 buttons, "fig. 1 — the factory" block diagram in a frame, blue `[C] [S] [Q]` key nav | 1132 doc | 84 hairlines, 01–06 tiles, tabs | 54/16 all mono | framed figures | ASCII diagrams, YAML | 335px | `>_ fig. 2 · quickstart ⌗`; `WARP · HOME · 2026` running head |
| [planetscale.com](https://planetscale.com) | **No display type**: 16px bold mono title, prose, logo grid in 1px cells | 1088 column | 82 hairlines, 4 `<hr>` | 16/16 mono | 0 | Box-drawing diagrams | Box-drawing table | A man-page; `text-wrap: balance` everywhere |
| [neon.com](https://neon.com) | Full-bleed canvas, H1 56px left at x=32, 2 buttons, logos | Bleed + 1152 | Giant mono `01 02 03`; black/green bands | 56/18; Geist Mono kickers | 0 | Real UI | 430px | Two-tone H2s |
| [posthog.com](https://posthog.com) | **Desktop-OS metaphor**: wallpaper, window with sidebar + tabs, H1 36px inside | Window chrome | Tabs/windows | 36/17; 28 `<figcaption>` | 1 | Illustration + UI | Inside OS | Fake OS, "Shameless CTA" |
| [arc.net](https://arc.net) | Centered H1 76px Exposure + 2 lines + one button | 473px measure | Black→white | 76/21; mono uppercase labels | 4 | 38 signatures | 675px | A signed letter with dated timeline |
| [superlist.com](https://superlist.com) | Centered H1 64px Haffer, one button, screenshot | 1390 | Kickers `01 / GET IT OUT…` | 64/18 | 46 | UI + photo | 804px, version no. | Two-tone lede; pixel accent face |
| [amie.so](https://amie.so) | Left H1 56px, 2 small buttons, changelog line, badges; screenshot | 672 text | Green eyebrows | 56/20 | 2 | Real UI | 577px | "Within 47 seconds:" lead; "Designed by the beach" |
| [diabrowser.com](https://diabrowser.com) | Script "Dia" 390px+ behind, H1 39px centered **Exposure serif**, one button + availability line; browser frame bleeds; leaf-shadow texture | Centered on curved sheet | Mono `01 02 03` rail left | 39/14 ABC Oracle + Favorit Mono | 9 | UI with editorial content | 266px, mono | Hand-drawn curved edge |
| [notion.com/product/calendar](https://www.notion.com/product/calendar) | Centered "It's time." 64px, 2 buttons, video, sticker illustrations | 1024/500 | Grey bands ×11 | 64/16; one Lyon serif quote | 40 | Real UI | 397px + McLuhan | Closing serif epigraph |
| lusion.co (memory; preloader `005`) | WebGL scene, H1 36px, "scroll to explore" | Canvas | Scroll-driven | Aeonik; `CONCEPT • WEB • DESIGN` tags | 12 | 3D | Address + credit | Counter preloader |
| [rauno.me](https://rauno.me) | Poster board: 5-line indented H1 32px on a white card, yellow disc overlapping; cards scroll sideways | 6648px horizontal canvas | Objects | 32px; 720px glyph "Craft" | 2 | Vector, pixel cursor | 3 icons | Indented verse setting; links to 2023/2022 versions |
| [emilkowal.ski](https://emilkowal.ski) | Name + role 16px, **644px column**, no H1 | 644 | Label headings | 16/16 one size | 0 | None | None | "1 day left to join." |
| [paco.me](https://paco.me) | Name 16px, italic **Newsreader** lead, 640px column, 3 sub-columns | 640 → 3×208 | Whitespace | 16/16 Söhne + serif italic | 0 | None | 48px sentence + year | 13 underline offsets; ↗ glyphs |
| [basement.studio](https://basement.studio) | Black canvas, H1 87px at x=16 **below the fold**, mono `HUMAN / MACHINE` toggle | Bleed, 16px gutters | Logo grid in 1px cells | 87/20 Geist + Geist Mono | 0 | Canvas | 848px, **"BSMNT.26"** giant | `(26)` counts; year in wordmark |
| [locomotive.ca](https://locomotive.ca) | Text-only top (store item "30 USD"), 70px serif H1 lower | 40px gutters | Hairline rows | 70/26 Helvetica Now + serif | 0 | One photo | 663px, address in **dingbat glyphs** | Work as serif rows with inline thumbs; `Extras (13)` |
| [darkroom.engineering](https://darkroom.engineering) | H1 200px condensed uppercase red on black; mono 14px else; video | Bleed | 120px H2s alternating left/right | 200/14 ≈ 14× | 0 | Video | 22px, then giant "DARKROOM" | `[ DARKROOM ], NOUN` |
| [area17.com](https://area17.com) | **Statement only**: 3-line H1 55px over 2/3 width, no CTA, no media | 16px gutters | Full-bleed photos | 55/16 Suisse | 89 | Photo/video | 690px, 55px type | Client names set over image like credits |
| [pudding.cool](https://pudding.cool) | Masthead + mono filter tabs; 3-up covers | 1280, 3 cols | Hairlines | 32px lowercase Gooper + Atlas Grotesk + Typewriter | covers | Dataviz on flat colour | 460px, stickers | `#226 · OCT 2026` on every card |
| [press.stripe.com](https://press.stripe.com) | Dark 3D shelf of spines, 17px serif title top-left | Canvas | n/a | Ivar serif 25px body | 0 | 3D books | 1120px narrow serif | Spine navigation |
| [aesop.com](https://www.aesop.com/us/) | Full-bleed video, 36px H1 400 left; one text link | 1170 + bleeds | Cream bands | 36/14 Suisse; Zapf serif accents | 0 | Film + photo | 1027px, 71 links | Nothing above 36px on a luxury site |
| [mubi.com](https://mubi.com) | Full-bleed still, uppercase H1 60px left-middle, inline email + button | 158px left margin | Bands | 60/16 Riforma + Tiempos | 0 | Stills | Compact, QR | "ANY FILM. ANY SCREEN." staccato lines |
| [ssense.com](https://www.ssense.com/en-us/women) (category; `/` blocked) | 3-col product grid, 11px uppercase nav | Dense | Hairlines | 11px uppercase | 0 | Product photos | 40px | Nothing above 12px |
| [lamalama.com](https://lamalama.com) SOTM Jul 26 | Loader → video; H1 72px uppercase; mono Sometype UI | Bleed | 36 hairline rows | 72/20 | 0 | Video | 720px, 80px type | `[ we are lama lama ]`; work ledger rows with 3 thumbs |
| [floema.com/en](https://www.floema.com/en) SOTM May 26 | Full-bleed photo, H1 57px centered, "Scroll to Explore ↓", pill nav | Bleed | **01–05 with counts `(51)`** | 57/15 | 2 | Photo + line sketches | 1160px yellow, cropped logo | Catalog PDF card bottom-right |
| [oryzo.ai](https://oryzo.ai) SOTM Apr 26 | Loader → 3D coaster centre, H2 51px left, body right | Centred object | Bands | 123px max; Literata asides | 0 | 3D | Dark + disclaimer | "ISSUE NO. 00124"; `[ 4.9/5 ]` |
| [sondaven.com/en](https://sondaven.com/en) SOTM Jun 26 | ASCII-sheep loader; 144px dot-matrix wordmark; 10px uppercase body | Bleed | Dark/beige bands | 144/10 ≈ 14× | 1 | CGI | 585px | `'26 '29` years; giant F-A-Q letters |
| [era-residence.com](https://www.era-residence.com) SOTM Aug 26 | Rotated side-rail labels, 173px serif uppercase wordmark over pool render, script "Cookies" | Side-rail frame | Plum/sky/ivory bands | 349/11.7 ≈ 30× | 0 | CGI | 1800px, phone number as display | Doubled labels for roll-over; `00 / 25` |
| [terminal-industries.com](https://terminal-industries.com) SOTM Sep 25 | Floating pill nav, full-bleed truck, headline arrives on scroll with last-letter highlight | Bleed | Film-strip corners | 82px / Geist Mono `01 FAST START` | 13 | 3D | Compact | Kinetic single-letter emphasis |
| [mindmarket.com](https://mindmarket.com) SOTM Dec 25 | Centered H1 140px Inter −8px on green, 2-word subhead, no button | Centered | Colour bands | 140/30 | 10 | Illustration | 901px yellow | Floating white pill nav |
| [soren-template.framer.website](https://soren-template.framer.website) Framer $149 | Centered serif name, hairline, 2-line bio, mono ASCII band | Centered | `[01]` indices | Chivo Mono + Halibut serif | 0 | Photos | 593px | Live clock "SWE 10:18" |
| [caspia.framer.media](https://caspia.framer.media) Framer $79 | Wordmark centered, **images drifting at absolute positions** | Collage | n/a | Switzer; `[ ]` labels | 0 | Photo stickers | 54px | Corner metadata "BASED IN NEW YORK" |
| [gojett.framer.website](https://gojett.framer.website) Framer free | 160px extra-condensed uppercase name, photo bleed | Bleed | Giant section titles | 160/12 ≈ 13×; Martian Mono | 0 | Photo | 64px + "LET'S TALK" | `[ Intro ]` |
| [arpeggio.framer.website](https://arpeggio.framer.website) $129 | Photo bleed, 27px lede top-left, 130px wordmark bottom-left, Playfair italic | Corner lockup | B/W bands | Inter Display + Playfair | 7 | Photo | 1036px, timezone clock | Live local time |
| [neiden.framer.website](https://neiden.framer.website) $99 | Loader; statement 60px over two offset photos | Offset 2-col | `001 / 002` | DM Sans + Patung; `tabular-nums` ×209 | 4 | Photos | 398px, 350px wordmark | Bilingual `[ Nº — WHO WE ARE / 我是 ]` |

**Cross-cutting counts.** H1 left-anchored (not centered) on 19 of 35 real sites; **zero** hero buttons on 11 (Linear, basement, Area17, Locomotive, Lusion, Lama Lama, Darkroom, MindMarket, Rauno, Emil, PlanetScale); exactly one button on 8; the "two buttons" pattern on only 7. Icon-card triplets: none. Hairlines at alpha (`rgba(255,255,255,.08)`-ish) in 14 sites, with Resend (107), Linear (84), Warp (84), Raycast (68) leaning on them as the primary structure. Mono used as a *labelling* face (captions, indices, dates, kickers) on 17 sites; serif as a *display* or *aside* face on 9. Footer heights: either ≤70px (Resend, Darkroom, Paco, Caspia, Jett) or ≥650px (Vercel, Aesop, Stripe Press, basement, Floema, Era, Arpeggio, MindMarket, Superlist)—almost nobody ships the 350px four-column middle.

## 2. Fourteen layout archetypes (not the generic template)

The generic AI template for reference: eyebrow pill → centered H1 → subhead → two buttons → screenshot → logo bar → three icon cards → stats → testimonials → CTA band → 4-col footer. Every archetype below breaks at least three of those links.

### A1. Left-anchored statement + bleeding product
Headline sits at the left gutter, set as two short lines; the product UI starts in the lower third and runs off the viewport so the fold cuts *through* the product. No eyebrow; at most one quiet link on the right. Linear, Neon, Clerk, Amie.

```
|logo        nav          login [signup]|   |[logo] [logo] [logo] [logo] [logo] [logo]|
|                                        |   |                                          |
| The product development                |   | A new species of product tool. Purpose-  |
| system for teams and agents            |   | built for modern teams…(grey continues)  |
| one-line subhead             New Loops→|   |                                          |
|┌──────────────────────────────────────┐|   | [wire-   ] [wire-   ] [wire-   ]         |
|│ sidebar │ issue view  …  │ AI panel ││   | Purpose    Powered    Designed           |
|│         │                │          ││   | 2-line body 2-line    2-line (no boxes)  |
```
**Mobile:** headline stays left, product image crops to its left 60% (`object-position: left top`), still bleeds. **Suits:** dev tools, B2B SaaS with a real UI. **CSS:** `grid-template-columns: minmax(var(--gutter),1fr) minmax(0,84rem) minmax(var(--gutter),1fr)`; media in a full-width grid cell with `margin-bottom: calc(-1 * var(--bleed))` and parent `overflow: clip`; headline `font-size: clamp(2.5rem, 4.4vw, 4rem); letter-spacing: -0.022em; text-wrap: balance`. **Pitfalls:** adding the second button and the eyebrow pill collapses it back into the template; a fake "window" with three dots is the tell—use the product's own chrome or none.

### A2. Monospace specification sheet
The page is a document: one mono face at one size, section titles as plain bold lines, figures framed with 1px rules and captioned `fig. 1`, nav as bracket keys. Persuasion is replaced by information density. PlanetScale (purest), Warp, Vercel's status-line footer.

```
| warp   [C] Configuration [S] SDLC [Q]… |   | # CONFIGURATION ──────────────────────── |
| Open infrastructure for                |   | Your software factory, defined in code.  |
| cloud software factories               |   | ┌ DEFINITION │ AGENTS │ AUTOMATIONS │… ┐ |
| [REQUEST ACCESS] [DOWNLOAD TERMINAL]   |   | │ factory.yaml        1 apiVersion …  │ |
| ┌ fig. 1 — the factory ────── · live ┐ |   | │                     2 name: …       │ |
| │ ░░▓░░░▓▓░░ ▓░░░░▓ ░░▓░░░ ▓▓░░░░░ │ |   | └──────────────────────────────────────┘ |
| │ 224 tasks · 0 active · 1,422 PRs   │ |   | 01 opinionated, but flexible   02 factories as code |
```
**Mobile:** no reflow needed except figures become horizontally scrollable `<pre>`. **Suits:** infra, databases, APIs, security, anything whose buyers read docs. **CSS:** `font-family: ui-monospace, "Berkeley Mono"`; `font-variant-numeric: tabular-nums`; borders `1px solid color-mix(in oklab, currentColor 14%, transparent)`; `<figure>/<figcaption>`; `text-wrap: balance` on prose; `counter-reset: fig` for captions. **Pitfalls:** mono body below 15px is unreadable; mixing in rounded gradient buttons breaks the register; ASCII diagrams must be real content, not decoration.

### A3. Ledger (index rows, not cards)
Work, posts or products as full-width rows separated by hairlines: big title left, metadata and small thumbnails right, counts in parentheses. Locomotive, Lama Lama, Rauno's craft list, Pudding's issue numbers, Soren `[01]`.

```
| Featured work                          |   | Extras (13)                              |
|─────────────────────────────────────── |   |───────────────────────────────────────── |
| Lightship                [img]   2024 →|   | Articles                                 |
|─────────────────────────────────────── |   |  Seven years of Locomotive        2025 → |
| Wolverine Worldwide      [img][img]   →|   |  On craft and compromise          2024 → |
|─────────────────────────────────────── |   |───────────────────────────────────────── |
| The [img] Drake Hotel                 →|   | Culture   (2024) Locomotive in Jamaica → |
```
**Mobile:** rows stack title/meta, thumbnails drop or become a 3-up strip under the title. **Suits:** studios, portfolios, editorial archives, changelogs. **CSS:** `display:grid; grid-template-columns: 1fr auto auto; border-block-start: 1px solid`; title `font-size: clamp(2rem,5vw,4.5rem)`; `font-variant-numeric: tabular-nums` on counts and dates; inline images via `display:inline-block; height:1em; vertical-align:-0.15em`. **Pitfalls:** hover reveal must not shift row height; rows with identical thumbnail shapes read as a table of cards—vary counts (1–3 thumbs) by actual content.

### A4. Two-tone lede paragraph
Replace headline+subhead with one large paragraph (36–48px) where the first clause is in text colour and the remainder in muted colour. Linear ("A new species of product tool."), Neon, Superlist, Amie ("Within 47 seconds:").

```
|                                        |   | ┌──────────────┐ Intake and integrations |
| A new species of product tool. Purpose-|   | │ screenshot   │ Automatically turn      |
| built for modern teams with AI workflows   | │              │ conversations…          |
| at its core, Linear sets a new standard|   | │              │                         |
| for planning and building products.    |   | └──────────────┘ ▸ Slack  ▸ Intercom     |
```
**Mobile:** 24–28px, same two colours. **Suits:** any product with a one-paragraph thesis; section openers. **CSS:** `<p class="lede"><strong>…</strong> rest</p>`; `strong{color:var(--fg)} .lede{color:var(--fg-muted); font-size:clamp(1.5rem,3vw,3rem); line-height:1.15; letter-spacing:-0.01em; max-width:30ch; text-wrap:pretty}`. **Pitfalls:** more than two tones or a coloured accent word becomes the "single accented headline word" tell; keep the strong clause to a sentence.

### A5. Single-column personal document
One measure (≈640px), one size (16px), headings are small labels, lists not cards, no imagery, footer is a sentence. Emil Kowalski, Paco Coursey, rauno.me's manifesto block.

```
|                                        |   | Writing                                  |
|      Emil Kowalski                     |   |  You Don't Need Animations               |
|      Design Engineer                   |   |  Why you are animating more often than…  |
|                                        |   |  Agents with Taste                       |
|      Today                             |   |  How to transfer taste into an AI.       |
|      Currently taking a break…         |   |                                          |
|      Projects                          |   | More                                     |
|      aiforui.dev — AI for Designers    |   |  Twitter · GitHub   Sit with ambition 2026|
```
**Mobile:** identical. **Suits:** personal sites, small tools, "about" pages, docs landing. **CSS:** `max-width: 40rem; margin-inline:auto; padding: clamp(3rem,10vh,8rem) 1.25rem`; headings `font-size:inherit; color:var(--fg-muted)`; links `text-decoration-thickness:1px; text-underline-offset:.2em; text-decoration-color:color-mix(…, 40%)`; optional serif italic for one lead clause (Paco uses Newsreader). **Pitfalls:** any card, badge or avatar grid kills it; keep one size and let whitespace do hierarchy.

### A6. Numbered chapters
Content that is genuinely sequential gets large indices (`01`–`05`) with optional counts, often as a sticky rail, and chapter-sized type. Floema `01 Urban (51)`, Superlist `01 / GET IT OUT OF YOUR HEAD`, Dia `01 02 03` gutter rail, Neon's 128px `01`.

```
| [full-bleed photo]                     |   | 01            Signage, furniture and     |
|                                        |   | Urban (51)    equipment for welcoming    |
|   Spaces for people, made for life.    |   |               urban spaces  →            |
|            Scroll to explore ↓         |   | ┌──────────────────────────────────────┐ |
|                                        |   | │ product photo full width             │ |
|                                        |   | 02 Nature (41)  03 RePlastic (73)  …     |
```
**Mobile:** index sits above the title at 12px mono; rails un-stick. **Suits:** catalogs, onboarding, process pages, multi-product suites. **CSS:** `counter-increment` with `::before{content: counter(sec,decimal-leading-zero)}`; `position: sticky; top: var(--nav-h)` on the index column; counts `font-variant-numeric: tabular-nums`. **Pitfalls:** numbering three identical feature blurbs is the AI tell—number only when order matters and items differ in size.

### A7. Wordmark-as-hero poster
The brand name at 150–350px (condensed/uppercase or serif) is the first screen's whole composition; body copy drops to 10–14px; the footer repeats the wordmark even bigger. Darkroom (200px), Jett/Navarro (160px), Era Residence (173/349px), Son Daven (144px), basement's `BSMNT.26`, Arpeggio, Neiden's 350px footer.

```
| name            [intro] work about ctc |   | ─ [ Intro ]                              |
| WHERE THINGS GET DEVELOPED             |   |   I'm Cole Navarro, a photographer…      |
| (200px, full width, 4 words)           |   |             ┌──────────┐                 |
| ┌──────────────────────────────────┐   |   |             │ portrait │                 |
| │ video / photo bleed              │   |   |             └──────────┘                 |
| │                                  │   |   | SELECTED WORK (giant)                    |
| └──────────────────────────────────┘   |   | RED ROOM ─────────────── 2026 →          |
```
**Mobile:** wordmark set with `font-size: 22vw` and allowed to wrap per word. **Suits:** studios, photographers, hospitality/real estate, fashion. **CSS:** `font-size: clamp(5rem, 14vw, 22rem); line-height:.85; letter-spacing:-0.04em; text-transform:uppercase; text-wrap:balance`; footer `overflow:hidden` with the wordmark `translateY(25%)` cropped; body `font-size:.75rem` mono. **Pitfalls:** needs an extended/condensed display face with real presence—Inter at 300px is still Inter; cropping must never hide letters needed to read the name.

### A8. Full-bleed media with corner-anchored lockup
Video or still fills the viewport; the headline sits left-middle or bottom-left, nav and labels pinned to corners, CTA is an inline email field or a single text link. MUBI, Aesop, Terminal, Area17 screen 2, Lama Lama, Floema.

```
| MUBI                          LOG IN ≡ |   | [still]       ANY FILM.                  |
| [film still full bleed]                |   |               ANY SCREEN.                |
|                                        |   |               ANY TIME.                  |
|   WATCH GREAT CINEMA                   |   |               ANY WHERE.                 |
|   LIKE NOWHERE ELSE                    |   |──────────────────────────────────────────|
|   TRY 7 DAYS FREE                      |   | MUBI    EVERYWHERE'S BEST CINEMA.        |
|   [email            ][GET STARTED]     |   |         CURATED BY FILM LOVERS. BY HAND. |
```
**Mobile:** media 100svh, lockup moves to bottom third, email field full width. **Suits:** streaming, commerce, luxury, agencies with film. **CSS:** `min-height:100svh; display:grid; grid-template: "nav" auto "." 1fr "lockup" auto / 1fr`; media `position:absolute; inset:0; object-fit:cover`; text with `mix-blend-mode: difference` or a gradient scrim; `padding: clamp(1rem,3vw,3rem)`. **Pitfalls:** stock footage is the tell—needs owned imagery; centered lockups over media regress to template.

### A9. Statement first, media second
The first screen is a single typographic sentence over two-thirds width, nothing else—no CTA, no image; the second screen delivers the full-bleed proof. Area17, basement (87px line below), Uncommon, Lusion.

```
| A/            Clients Capabilities …   |   | ┌──────────────────────────────────────┐ |
|                                        |   | │ aerial photo full bleed              │ |
| We partner with the world's most       |   | │  ElevenLabs                          │ |
| influential organizations to realize   |   | │  Lucas Museum of Narrative Art       │ |
| their vision and achieve their         |   | │  Saint Laurent                       │ |
| greatest impact.                       |   | │  Fondation Cartier                   │ |
| [photo strip peeking at the fold]      |   | └──────────────────────────────────────┘ |
```
**Mobile:** sentence at 32px fills the screen; image follows. **Suits:** consultancies, studios, foundations. **CSS:** `max-width: 24ch; font-size: clamp(2rem,3.8vw,3.5rem); font-weight:450; line-height:1.1; margin-left:0`; the image strip uses `height: 15svh; overflow:hidden` as a tease. **Pitfalls:** the sentence must be specific (clients, numbers, verbs); "We build the future of X" exposes it as template copy immediately.

### A10. Letter / essay
Narrow measure (28–32em), serif or humanist sans at 20px+, title centered, first-person prose, signatures or a date line; sections are paragraphs, not boxes. Arc's farewell, Stripe Press book pages, MUBI manifesto, Notion Calendar's closing McLuhan quote.

```
|            [mark]                      |   | We've decided to sunset Arc on           |
|      A farewell to Arc                 |   | December 22, 2026                        |
|  Arc is sunsetting on December 22, 2026|   |                                          |
|  Scroll to read what's happening…      |   | That's not an easy sentence to write. We |
|          (Read more)                   |   | spent years building Arc and celebrating…|
|                                        |   |                                          |
|                                        |   |  Josh   Ben   Rishi   Tara   Kasper …    |
```
**Mobile:** measure becomes full width minus 20px; keep 19–21px. **Suits:** announcements, manifestos, founders' notes, publishing. **CSS:** `max-width: 30rem` (473px at Arc); `font-size:1.3rem; line-height:1.45; hanging-punctuation: first; text-wrap: pretty`; `h1{text-align:center}` only here; timeline as `<dl>` with mono dates. **Pitfalls:** adding a sidebar, cards, or a CTA band mid-letter breaks the voice; signatures must be real.

### A11. Framed object / fake OS
The page is drawn inside a visible frame—a window, a bordered sheet, a browser—so the layout has chrome: title bar, sidebar, tabs. PostHog (desktop with grass wallpaper), Cal.com (bordered inset container), Dia (browser frame bleeding), Rauno (poster board with scroll ruler).

```
| ▣ wallpaper                             |  | ┌ Ask PostHog anything ─ Give agents … ─┐ |
| ┌ PostHog ───────────────── _ □ × ┐    |  | │ What can I help you with?             │ |
| │ ⌂ │ Your product's context layer │    |  | │ [Describe the task in detail…      →] │ |
| │ ▤ │ PostHog ingests and stores… │    |  | │ ○ Auto  ○ Default · Claude Sonnet 5   │ |
| │ ▦ │ [Get started] [Install w/AI]│    |  | └───────────────────────────────────────┘ |
| └─────────────────────────────────┘    |  |   Product analytics · Session replay …   |
```
**Mobile:** frame becomes full-screen (chrome collapses to a 44px bar). **Suits:** tools with strong UI identity, playful brands. **CSS:** outer `padding: clamp(.5rem,2vw,2rem)`; frame `border:1px solid; border-radius: 12px; box-shadow: 0 1px 0 rgba(0,0,0,.04), 0 30px 60px -30px rgba(0,0,0,.25); overflow:clip`; inner scroll via `position:sticky` tabs. **Pitfalls:** traffic-light dots on a screenshot are the AI tell; the frame has to be a *working* metaphor (PostHog's windows move) or a real design decision (Cal's border), not decoration.

### A12. Drift collage around a wordmark
A centered name or statement with 4–8 images at absolute, deliberately uneven positions and sizes, sometimes slowly drifting; corner metadata lines. Caspia, rauno.me, Floema's sketches, Pudding stickers, Oryzo's sticker pile.

```
|  [img]                 [img]           |   | (images re-shuffle; wordmark stays)      |
|        CASPIA  (giant)                 |   |  [img]  CASPIA        [img]              |
|  I design visual identities for studios|   |        I design visual identities…       |
| [img]            [img]        [img]    |   |  [img]           [img]                   |
| BRAND STRATEGIST      BASED IN NEW YORK|   | BRAND STRATEGIST       BASED IN NEW YORK |
```
**Mobile:** images reduce to 3, placed above/below the wordmark, no overlap on text. **Suits:** designers, photographers, agencies, fashion. **CSS:** container `position:relative; min-height:100svh`; images with `position:absolute; inset: auto; width: clamp(80px, 12vw, 220px); rotate: var(--r)`; `@media (prefers-reduced-motion: no-preference)` for drift with `animation` on `translate`; corner labels `position:fixed; font: 11px/1 mono; text-transform:uppercase; letter-spacing:.08em`. **Pitfalls:** evenly spaced or mirrored images read as a grid again—positions must be hand-set; respect reduced motion.

### A13. Product-first split with plain-text feature list
Hero or section split 55/45 where one side is a large real UI capture and the other is a short headline plus a *plain list* (no icons, no boxes) of 3–6 one-line facts, often with a stat sentence. Vercel section 2, Cal.com, Amie, Notion Calendar, Dia screen 2.

```
| Build agents on infrastructure         |   | Zapier serves over 100 million monthly   |
| that thinks like them                  |   | website visits on Vercel.                |
| ┌────────────────────────┐  Notion     |   | ┌──────────────────────┐ Features         |
| │ New AI chat            │  powers…    |   | │ zapier UI            │ Global Delivery  |
| │ How can I help you?    │  Features   |   | │                      │ Deployment Envs  |
| │ ▸ Translate this page  │  Durable…   |   | │                      │ Serverless Fns   |
| └────────────────────────┘  Sandboxed… |   | └──────────────────────┘ 450K+ 9,000+ 3.3M+|
```
**Mobile:** list first, image second (`order`), image allowed to overflow right edge. **Suits:** SaaS, productivity, any product with real screens. **CSS:** `grid-template-columns: 1.2fr .8fr; align-items:start; gap: clamp(1.5rem,4vw,5rem)`; list `ul{list-style:none} li{padding-block:.5rem; border-top:1px solid var(--rule)}`; stats `font-variant-numeric: tabular-nums`. **Pitfalls:** turning the list into three cards with icons returns to template; alternate the split direction only when content differs, not rhythmically.

### A14. Catalog with metadata
Grid of covers/products where every item carries structured meta—issue number, date, byline, category—set in mono or small caps, with lowercase or title display. Pudding, SSENSE, Stripe Press, Lama Lama, Neiden `001 / 002`.

```
| The Pudding   OUR FAVES POPULAR VIDEO… |   | #223  JUL 2026   #222 JUN 2026  #221 JUN |
| #226  OCT 2026  #225 OCT 2026 #224 AUG |   | ┌──────┐        ┌──────┐       ┌──────┐  |
| ┌──────┐        ┌──────┐      ┌──────┐ |   | │cover │        │cover │       │cover │  |
| │cover │        │cover │      │cover │ |   | └──────┘        └──────┘       └──────┘  |
| └──────┘        └──────┘      └──────┘ |   | english vocab   ethical nba    menu hist |
| kevin bacon     life after    mowing   |   | How the words…  Which teams…   What do…  |
| Demystifying…   A room of…    Why some…|   |                                          |
```
**Mobile:** 2-up with meta line above the cover. **Suits:** publications, commerce, film, archives. **CSS:** `grid-template-columns: repeat(auto-fill, minmax(18rem,1fr)); gap: 2rem 1.5rem`; meta `font: 11px/1.2 mono; letter-spacing:.06em; display:flex; justify-content:space-between`; covers `aspect-ratio: 4/5; object-fit:cover`; titles lowercase or sentence case. **Pitfalls:** uniform cover heights plus uniform dek length reads as generated—allow real covers and truncate deks at the sentence, not a character count.

## 3. Recurring craft details on handmade sites

Typography
- **Mono as the labelling voice**, never the body (except A2): captions `FIG 0.1`, running heads `WARP · HOME · 2026`, dates `OCT 22, 2026`, indices `[01]`, counts `(51)`, status lines "All systems normal". 11–12px, `letter-spacing: .04–.08em`, uppercase.
- **A second face carries the personality**, in a small dose: serif italic lead (Paco/Newsreader, Arpeggio/Playfair), serif display on a dev tool (Resend/Domaine, Dia/Exposure), condensed display (Darkroom, Jett), script for one word (Era "Cookies", Dia).
- **Tight negative tracking only above ~40px** (Linear −0.022em, Vercel −0.06em, basement −0.04em); body tracking untouched.
- **Display:body ratios of 4–6× for products, 13–30× for posters**; the template's 2.5–3× is the giveaway.
- `tabular-nums` on anything that counts (Linear ×62, Neiden ×209); `text-wrap: balance` on headings, `pretty` on prose; `hanging-punctuation: first` on serif ledes.
- Sentence case everywhere except deliberate mono labels; headings that end in a full stop ("It's time." "Make it.").
- Two-tone paragraphs (A4) instead of headline + subhead.

Rules, spacing, structure
- 1px rules in `currentColor` at 8–15% alpha (Linear 84, Resend 107, Warp 84, Raycast 68) as the *primary* separator; `<hr>` or colour bands only when the content register changes (Clerk's dark bands, Neon's green).
- Uneven gutters: 16–40px outer gutters on studio sites (basement 16, Area17 16, Locomotive 40) vs. 120–200px on product sites; both avoid the 24px-everywhere look.
- Section padding varies by section importance; no `py-24` on everything.
- Visible numbering only when content is a sequence (Floema's catalog, Dia's three steps) and paired with counts or dates.
- Corner-pinned metadata (`position: fixed`) on studio sites: role, city, local time with timezone (Soren, Arpeggio), language toggle.

Imagery
- Real UI cropped by the viewport edge, or real photography; abstract 3D only when it is the product (Resend, Oryzo). Line-art/wireframe illustrations in a single stroke weight (Linear, Floema).
- `<figure>` + `<figcaption>` with numbered captions; captions set in mono.
- Inline images in text at `1em` height (Locomotive "The [img] Drake Hotel").

Interaction and motion
- Hover underlines with `text-underline-offset: .2em` and thickness 1px, often from a muted colour to full (Paco ×13, Vercel ×33, Notion ×36).
- One orchestrated load: counter preloader (Lusion `005`, Son Daven `0% loaded`), or a single staggered reveal; then nothing animates on scroll except kinetic type that stays legible (Terminal's last-letter highlight, Locomotive's word-by-word hero).
- Doubled label markup for roll-over text swaps (Era, Lama Lama).
- Links show destination glyphs: `↗` external, `→` internal, `↓` download/scroll.

Footers
- Either a one-line colophon (Paco: sentence + year; Resend 52px) or a giant footer that is itself a composition: wordmark cropped at the edge (basement `BSMNT.26`, Neiden, Darkroom), address set as display type (Locomotive, Era's phone number), epigraph (Notion/McLuhan), version number (Superlist "version 1.58.0").
- Address, local time, and "Made by" credit appear in 60% of studio footers.

Copy as layout material
- Specific nouns and numbers in the first sentence ("1,422 PRs shipped", "Within 47 seconds:", "#226"); counts next to categories; dates on everything.
- Bracketed labels `[ we are lama lama ]`, `[ Intro ]`, `[ 4.9/5 ]` as a cheap, legible kicker style that is not a pill.
- Dictionary/colophon jokes (`[ DARKROOM ], NOUN`, "Curated by film lovers. By hand.").

## 4. Tells confirmed as template-only
None of the admired sites used: eyebrow pill + centered H1 + two buttons + framed screenshot with traffic lights; three equal icon cards; 01/02/03 on non-sequential features; left-border accent cards; one `border-radius` on everything; a single accent-coloured headline word; a 350px four-column footer; identical section padding; Inter alone at a 2.5× display ratio.

Sources beyond the surveyed pages: [Awwwards Sites of the Month](https://www.awwwards.com/websites/sites_of_the_month/), [Awwwards SOTD October 2026](https://www.awwwards.com/websites/sites_of_the_day/), [Framer marketplace trending](https://www.framer.com/marketplace/templates/), [avoid-ai-design tells catalog](https://github.com/funboy322/avoid-ai-design), [925 Studios AI-slop guide](https://www.925studios.co/blog/ai-slop-web-design-guide), [Sikora: signs a site was built by AI](https://sikora.software/blog/ai-website-design), [hontran.dev award-winning sites 2026](https://www.hontran.dev/blog/best-award-winning-websites-2026).
