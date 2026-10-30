# Devices

Rules for the devices view of the preview, the catalogue in `knowledge/devices.json`, and what Claude checks on each class of screen. Research behind the numbers: `docs/research/2026-10-30-devices.md` and `docs/research/2026-10-30-devices.csv`.

## What the devices view shows

- The fourth preview view (`devices.html` per direction) renders the drafted page inside a frame for each device, at the device's true CSS viewport, scaled to fit its column. Nothing is emulated beyond width, height and the drawn chrome; the iframe is the same `draft.html?embed=1` the draft view shows, so what you see is the real CSS at that width.
- Frames are ranked by `share_rank` (1 is the most traffic) and grouped by vendor in the picker. The default set is shown; "Choose devices" expands checkboxes per vendor, "Show all" and "Hide all" toggle every frame.
- Each figure's caption gives vendor and model, `w × h`, the device pixel ratio, the year (or "generic"), and "viewport unverified" when `verified` is false.
- The chrome controls (palette, pairing, radius, density, motion, theme) reload every visible frame with the new state, so a tweak is checked on every screen at once.
- "Rotate" swaps width and height for that frame, moves the cutout to the left edge and the crease to horizontal, and recomputes the safe-area band for landscape.
- "Show safe areas" draws the inset bands on every frame.
- The grid is `repeat(auto-fill, minmax(280px, 1fr))`; tablets, foldables, laptops and desktops span two columns; under 700px wide everything is one column.

## How frames are drawn

Only CSS, from catalogue data (`assets/preview/device-frames.css`). No vendor artwork is bundled: Apple Design Resources and Meta Devices licences forbid redistribution, and no permissive library ships accurate 2025 to 2026 bezels. Structural reference: https://github.com/jhildenbiddle/css-device-frames (MIT).

- Shell: a dark rounded rectangle (`--shell: #1a1a1c`, 1px `--shell-edge`) with a 12px bezel (10px on laptops, 14px on desktops). Its radius is `corner_radius × scale + bezel`, so the frame corners match the screen corners.
- Screen: `overflow: hidden`, white background, radius `corner_radius × scale`. The iframe is sized at the exact viewport (`data-w`, `data-h`) and transformed with `scale(column width / viewport width)`; `preview.js` writes `--scale` on the figure so every overlay below scales with it.
- Cutouts, from `cutout`: `island` is a 125 by 37px black pill 11px from the top; `notch` on phones is 160 by 32px with 20px lower corners, on laptops 180 by 30px with 8px corners; `punch` is an 18px black circle 10px from the top; `none` draws nothing. Rotated phones move the island, punch or notch to the left edge, centred vertically.
- Home indicator: a 134 by 5px bar 8px from the bottom on phones and foldables and on tablets with `cutout` `none` (240px wide on tablets), drawn with `mix-blend-mode: difference` so it stays visible on light and dark pages.
- Crease: `.pf-crease`, a 2px vertical line at 50% with a soft shadow, drawn when `fold.crease` is true; horizontal when rotated.
- Laptops get a base strip with a trackpad notch under the shell; desktops get a trapezoid stand.
- Safe-area overlay: `.pf-safe` is an absolutely positioned border in `danger` colour at 25% alpha; border widths are `safe_area.top|right|bottom|left × scale`. Rotated phones use the portrait top value for both sides and 21px at the bottom (the iPhone landscape convention).

## Catalogue fields

`knowledge/devices.json` has `updated`, `source_report` and a `devices` array. Each entry must carry the fields `schema.json` lists under `files.device.required`.

| Field | Meaning | Units and values |
|---|---|---|
| `id` | Stable key used by the checkbox and the `data-device-id` attribute | lowercase, hyphens, vendor first (`iphone-17`, `samsung-galaxy-s25`) |
| `vendor` | Picker group | `Apple`, `Samsung`, `Google`, `Xiaomi`, `OnePlus`, `Microsoft`, `Generic` |
| `model` | Caption text; may name identical-geometry siblings in parentheses | free text |
| `year` | Release year; `null` for generic resolution classes (caption shows "generic") | integer or null |
| `kind` | Frame shape, column span and which overlays apply | `phone`, `foldable`, `tablet`, `laptop`, `desktop` |
| `viewport` | Portrait CSS viewport of the browser's layout area, not physical pixels; for foldables the open inner display | `{w, h}` in CSS px |
| `dpr` | Device pixel ratio at the shipped default scaling (Samsung flagships ship FHD+, so 2.625 not 3.5; Windows 1080p at 125% is 1.25) | number |
| `safe_area` | Portrait insets where system chrome sits | `{top, bottom, left, right}` in CSS px |
| `cutout` | Camera housing to draw | `island`, `notch`, `punch`, `none` |
| `corner_radius` | Display corner radius (Apple values are points from ScreenCorners; 0 when unknown draws a square screen) | CSS px |
| `fold` | Only on foldables: cover display viewport and whether to draw a crease | `{folded: {w, h}, crease: true}` |
| `share_rank` | Position by traffic share (StatCounter resolutions plus Counterpoint model sales); drives order and the default set | integer, 1 is highest |
| `default` | Shown before the developer touches the picker | boolean |
| `source` | Where the viewport came from; required, one URL | URL |
| `verified` | True only when a primary source (vendor spec, Chrome `EmulatedDevices.ts`, useyourloaf, ios-resolution) confirms viewport and DPR; false when inferred from a sibling panel or a secondary site | boolean |
| `notes` | Share figures, sibling geometry, conflicts, landscape insets | free text |

## The default set and why

Twelve devices are `default: true`, chosen by share so the first screen covers most real traffic without scrolling through the whole catalogue (StatCounter September 2026: mobile 58.99%, desktop 39.26%, tablet 1.76%; Android 69.31% of mobile, iOS 30.66%; https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet).

| Rank | Device | Reason |
|---|---|---|
| 1 | 1080p desktop 1920x1080 | 28.08% of desktop, 10.69% of all traffic |
| 2 | iPhone 17 402x874 | Best-selling phone Q1 and Q2 2026 (Counterpoint), same geometry as 17 Pro and 16 Pro |
| 3 | iPhone 17 Pro Max 440x956 | Second best seller; the widest common phone |
| 5 | Windows laptop 1536x864 | Second desktop resolution, 9.99% of desktop |
| 6 | Galaxy S25 Ultra 412x891 | Top Android model (as S26 Ultra) |
| 10 | Galaxy S25 360x780 | The 360-wide class, 2.14% of all traffic; the narrowest default |
| 11 | iPhone 16e 390x844 | The notch class, 3.64% of all traffic |
| 12 | Pixel 10 412x924 | Chrome's reference Android preset |
| 20 | MacBook Air 13 1470x956 | Most common Mac laptop at default scaling |
| 22 | iPad Air 11 820x1180 | 5.06% of tablet traffic; shared with iPad 11th gen |
| 23 | Galaxy Z Flip7 360x840 | Clamshell, a tall 360 phone |
| 24 | Galaxy Z Fold7 984x1092 | The only near-square viewport; tests both widths |

Not default but in the catalogue: the remaining iPhones (17 Pro, Air, 16, 16 Plus, 16 Pro), Galaxy S25+, A56, A36, A17, Pixel 10 Pro and 9a, Xiaomi 15 Pro, OnePlus 13, iPad Pro 13, iPad 11, Tab S10 Ultra and S10+, MacBook Air 15, MacBook Pro 14 and 16, Surface Laptop 7, Windows 1366x768, 1440p and 4K monitors. Turn them on when the brief names a market (Xiaomi for China and India, 1366 for education and public sector, iPad Pro for creative tools).

## Full device table

From `knowledge/devices.json` (updated 2026-10-30). Viewport is portrait CSS px. Verified false means inferred or secondary-sourced; see `notes` in the file.

| Vendor | Model | Kind | Viewport | DPR | Cutout | Safe top/bottom | Corner | Rank | Default | Verified |
|---|---|---|---|---|---|---|---|---|---|---|
| Apple | iPhone 17 | phone | 402x874 | 3 | island | 62/34 | 62 | 2 | yes | yes |
| Apple | iPhone 17 Pro Max | phone | 440x956 | 3 | island | 62/34 | 62 | 3 | yes | yes |
| Apple | iPhone 17 Pro | phone | 402x874 | 3 | island | 62/34 | 62 | 4 | no | yes |
| Apple | iPhone Air | phone | 420x912 | 3 | island | 68/34 | 62 | 27 | no | no |
| Apple | iPhone 16e | phone | 390x844 | 3 | notch | 47/34 | 47.33 | 11 | yes | no |
| Apple | iPhone 16 (15, 15 Pro, 14 Pro) | phone | 393x852 | 3 | island | 59/34 | 55 | 7 | no | yes |
| Apple | iPhone 16 Plus (15 Plus, 15 Pro Max) | phone | 430x932 | 3 | island | 59/34 | 55 | 15 | no | yes |
| Apple | iPhone 16 Pro | phone | 402x874 | 3 | island | 62/34 | 62 | 16 | no | yes |
| Samsung | Galaxy S25 Ultra (S26 Ultra) | phone | 412x891 | 2.625 | punch | 24/20 | 0 | 6 | yes | no |
| Samsung | Galaxy S25+ (S26+) | phone | 412x891 | 2.625 | punch | 24/20 | 0 | 17 | no | no |
| Samsung | Galaxy S25 (S26) | phone | 360x780 | 3 | punch | 24/20 | 0 | 10 | yes | no |
| Samsung | Galaxy Z Fold7 (cover 360x840, crease) | foldable | 984x1092 | 2 | punch | 24/20 | 0 | 24 | yes | no |
| Samsung | Galaxy Z Flip7 | phone | 360x840 | 3 | punch | 24/20 | 0 | 23 | yes | no |
| Samsung | Galaxy A56 | phone | 412x892 | 2.625 | punch | 24/20 | 0 | 13 | no | no |
| Samsung | Galaxy A36 | phone | 412x918 | 2.625 | punch | 24/20 | 0 | 14 | no | no |
| Samsung | Galaxy A17 | phone | 412x892 | 2.625 | punch | 24/20 | 0 | 8 | no | no |
| Google | Pixel 10 | phone | 412x924 | 2.625 | punch | 24/20 | 0 | 12 | yes | no |
| Google | Pixel 10 Pro | phone | 427x952 | 3 | punch | 24/20 | 0 | 25 | no | no |
| Google | Pixel 9a | phone | 412x924 | 2.625 | punch | 24/20 | 0 | 26 | no | no |
| Xiaomi | Xiaomi 15 Pro | phone | 412x914 | 3.5 | punch | 24/20 | 0 | 18 | no | no |
| OnePlus | OnePlus 13 | phone | 412x905 | 3.5 | punch | 24/20 | 0 | 28 | no | no |
| Apple | iPad Pro 13 (M4, M5) | tablet | 1032x1376 | 2 | none | 24/20 | 18 | 32 | no | no |
| Apple | iPad Air 11 (M3) | tablet | 820x1180 | 2 | none | 24/20 | 18 | 22 | yes | yes |
| Apple | iPad (A16) 11th gen | tablet | 820x1180 | 2 | none | 24/20 | 18 | 21 | no | yes |
| Samsung | Galaxy Tab S10 Ultra | tablet | 924x1480 | 2 | punch | 24/16 | 0 | 35 | no | no |
| Samsung | Galaxy Tab S10+ | tablet | 876x1400 | 2 | none | 24/16 | 0 | 34 | no | no |
| Apple | MacBook Air 13 (M4) | laptop | 1470x956 | 2 | none | 0/0 | 0 | 20 | yes | yes |
| Apple | MacBook Air 15 (M4) | laptop | 1710x1107 | 2 | none | 0/0 | 0 | 30 | no | no |
| Apple | MacBook Pro 14 (M4, M5) | laptop | 1512x982 | 2 | notch | 37/0 | 0 | 29 | no | no |
| Apple | MacBook Pro 16 (M4, M5) | laptop | 1728x1117 | 2 | notch | 37/0 | 0 | 31 | no | no |
| Microsoft | Surface Laptop 7 13.8 | laptop | 1536x1024 | 1.5 | none | 0/0 | 0 | 33 | no | no |
| Generic | Windows laptop 1366x768 | laptop | 1366x768 | 1 | none | 0/0 | 0 | 9 | no | yes |
| Generic | Windows laptop 1920x1080 at 125% | laptop | 1536x864 | 1.25 | none | 0/0 | 0 | 5 | yes | yes |
| Generic | 1080p desktop or monitor | desktop | 1920x1080 | 1 | none | 0/0 | 0 | 1 | yes | yes |
| Generic | 1440p monitor | desktop | 2560x1440 | 1 | none | 0/0 | 0 | 19 | no | yes |
| Generic | 4K monitor | desktop | 3840x2160 | 1 | none | 0/0 | 0 | 36 | no | yes |

Known conflicts and gaps (also in `notes`): Pixel 10 Pro is 427x952 at 3 in Chrome's preset for the identical Pixel 9 Pro panel but 410x914 at 3.125 elsewhere; iPhone Air landscape bottom inset is reported as 29; the Z Fold7 cover viewport is inferred from the Flip7 panel; all Android insets are platform conventions (status bar about 24, gesture bar 16 to 24); the MacBook Pro camera notch sits inside the 37px menu bar, so browsers never render under it.

## Adding or correcting a device

1. Find a primary source for the CSS viewport and DPR: the vendor's spec page, Chrome's `EmulatedDevices.ts` (https://chromium.googlesource.com/devtools/devtools-frontend/+/main/front_end/models/emulation/EmulatedDevices.ts), useyourloaf for iPhones (https://useyourloaf.com/blog/iphone-17-screen-sizes/), ios-resolution (https://www.ios-resolution.com/), ScreenCorners for Apple corner radii (https://github.com/kylebshr/ScreenCorners). yesviz and screensizechecker are secondary; an entry built only on them is `verified: false`.
2. Add the entry with every required field. `source` is required and must be one URL; the validator rejects an entry without it. Put share figures, sibling geometry and anything inferred in `notes`.
3. Set `verified: true` only when viewport and DPR come from a primary source. Inferred insets alone do not make an entry unverified, but say in `notes` that they are approximations.
4. Choose `share_rank` by inserting the device into the existing order using StatCounter resolution share and Counterpoint model rankings (https://counterpointresearch.com/en/insights/iphone-17-global-best-selling-smartphone-in-q2-2026); shift the ranks below it. Set `default: true` only if it displaces a lower-share default; keep the default set at twelve or fewer.
5. For a foldable, `viewport` is the open inner display, `fold.folded` is the cover display, `fold.crease` is true for book-style folds and absent for clamshells (the Z Flip7 is a `phone`).
6. Update `updated` in the file, add the row to `docs/research/2026-10-30-devices.csv` and the table above, then run `validate_graph.py` and the tests, and rebuild a preview to see the frame.
7. To correct a value, change it, replace `source` with the better one, flip `verified` if the new source is primary, and note the old value in `notes` so the conflict is visible.

## Previewing a real running page

- Append `?url=http://localhost:3000` to the devices view, or paste the address into "Preview another page in these frames" and press "Load". Every frame then loads that page instead of the draft; the chrome controls stop affecting the frames because the page is not built from the direction's tokens.
- Only `http:` and `https:` are accepted; `javascript:`, `data:` and `file:` are ignored.
- Use it after handoff to check the real build at every width, and during a redesign to compare the current site with the directions side by side.
- If a frame stays blank for five seconds the view shows a notice. The cause is a frame-blocking header: `X-Frame-Options: DENY` or `SAMEORIGIN`, or a `Content-Security-Policy` with `frame-ancestors`. The preview is served from `localhost:<port>` and a different port is a different origin, so even `SAMEORIGIN` or `frame-ancestors 'self'` blocks it (https://developer.mozilla.org/docs/Web/HTTP/Headers/X-Frame-Options, https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors).
- Fix it in development only: drop the header for the dev server, or add the preview origin to `frame-ancestors` behind an environment check (Next.js `headers()` in `next.config`, Django `X_FRAME_OPTIONS`, Rails `config.action_dispatch.default_headers`, Helmet `frameguard`). Never weaken the header in production for the sake of the preview.
- Production sites behind login or with cookies set `SameSite=Strict` will render logged out inside the frame; preview the local build instead.

## Landscape and foldables

- Rotate a phone to check video, tables and galleries; iPhone landscape puts the island on the left with side insets equal to the portrait top value and a 21px bottom inset, which the overlay draws.
- Landscape phone heights (360 to 440px) break full-height heroes; with `100dvh` a hero must still show its headline and button, so cap hero height with `min(100dvh, 720px)` or let it scroll.
- Foldables are two devices: the cover display (Z Fold7 cover 360x840, a tall narrow phone) and the open display (984x1092, near square). Layouts that switch at 768 or 1024 will flip between the two states, so check both; the open display is wide enough for two columns but short enough that a sidebar plus a 360px panel leaves under 400px for content.
- Draw nothing important under the crease: at 984 wide it sits at 492px; avoid putting a button, a column gutter or a form field across the centre line on near-square viewports.
- Android tablets and the Fold open in landscape are the main place a 1024-wide layout actually appears; treat 1024 as a tablet landscape breakpoint, not a small desktop.

## What to check on each class of device

Phones (360 to 440 wide, 780 to 956 tall):

- Thumb reach: the primary action, the nav trigger and the cart or submit button are in the lower half of the screen or sticky at the bottom with `env(safe-area-inset-bottom)` padding; nothing essential sits only in the top corners.
- Every target 44 by 44px with 8px between targets; the primary button full width at 360.
- Headline fits in three lines at 360; the first screen shows headline, one sentence and the primary action without scrolling on 780-tall devices.
- Nothing under the island, notch or punch; nothing inside the safe-area bands; no horizontal scroll.
- Type 16px minimum in inputs; body no smaller than the pairing's base.

Foldables:

- Both widths: cover display behaves as a 360 phone; open display behaves as a small tablet. The layout must not flash between one and two columns on an intermediate width while the device unfolds.
- Two-column layouts on the open display keep each column at least 400px; otherwise stay single column.
- Nothing straddles the crease.

Tablets (820 to 1032 portrait, 1180 to 1376 landscape):

- Two-column layouts appear where they should (article with table of contents, split hero, sidebar shell in landscape) and collapse cleanly in portrait.
- Touch targets as on phones; hover is not the only way to reveal anything.
- The sidebar shell collapses to a top strip under 860 in the draft; a real build needs a toggle or a rail, not hidden navigation.
- Modal and drawer widths are capped (380px) and do not cover the whole screen.

Laptops (1366 and 1536 wide, 768 to 1024 tall):

- At 1366x768 the hero plus nav fit in 768px of height with the primary action visible; a 100dvh hero shows its content, not just a headline.
- At 1536 the 1200px container has visible margins and nothing stretches to the edges except full-bleed bands.
- MacBook Pro: the browser never renders under the notch, so no special handling; the menu bar takes 37px of the 982 or 1117 height.
- Text at 1.25 and 1.5 DPR (Windows laptop and Surface) stays crisp: use SVG icons and no 1px hairlines in half-pixel positions (`border` not `box-shadow` for rules).

Desktops (1920 and above):

- The container stays at 1200px and content does not scale to fill 1920 or 2560; margins grow.
- Line length stays at or under `--pf-measure` (66ch) in articles, lead paragraphs and cards; wide cards wrap their text in a measure-limited column.
- Hover states exist for every interactive element, and focus rings match (keyboard use is common here).
- At 2560x1440 at 1x, 14px text is small; the base size should be 16px or more and the type scale should not drop below `--pf-text-sm` for body copy.
- 4K is almost always scaled (150% gives 2560x1440 at 1.5, 200% gives 1920x1080 at 2), so test those two and not the native 3840 width.

Sources: `docs/research/2026-10-30-devices.md`; StatCounter screen resolutions and vendors (https://gs.statcounter.com/screen-resolution-stats, https://gs.statcounter.com/vendor-market-share/mobile); Counterpoint Q2 2026 model ranking (https://counterpointresearch.com/en/insights/iphone-17-global-best-selling-smartphone-in-q2-2026); Chrome emulated devices (https://chromium.googlesource.com/devtools/devtools-frontend/+/main/front_end/models/emulation/EmulatedDevices.ts); ScreenCorners (https://github.com/kylebshr/ScreenCorners); css-device-frames (https://github.com/jhildenbiddle/css-device-frames); Apple MacBook specs (https://www.apple.com/macbook-air/specs/, https://www.apple.com/macbook-pro/specs/); safe-area `env()` (https://developer.mozilla.org/docs/Web/CSS/env).
