# preview-first Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `preview-first` Claude Code skill: a developer sees three to five complete, distinct design directions in the browser (style tile, drafted page, device frames), tweaks and selects one, and the choice becomes a design contract that later Claude work follows.

**Architecture:** A curated knowledge graph (`graph.json`) plus deterministic standard-library Python scripts (recommend, build, serve, export, contrast, refresh, validate, import) exchange fixed-schema JSON files (`brief.json`, `directions.json`, `selection.json`) with Claude, which supplies judgement (brief normalisation, names, rationale, copy). The preview is static HTML, CSS and JavaScript generated from a closed vocabulary of component treatments and layout variants, served by a tiny local server that records the selection.

**Tech Stack:** Python 3.9+ standard library only (runtime). pytest for tests (dev only, via `uv run --with pytest`). Plain HTML, CSS, JavaScript. GitHub Actions. Playwright MCP for screenshots during development only.

**Spec:** `docs/superpowers/specs/2026-10-30-web-design-skill-design.md`

## Global Constraints

- Runtime scripts import only the Python standard library; Python 3.9 floor (no `match`, no `X | Y` type unions at runtime).
- Run Python as `uv run python3 ...` in this environment (a hook blocks bare `python3`); tests run as `uv run --with pytest pytest`.
- Everything under `skills/preview-first/` must be self-contained: scripts locate `knowledge/` and `assets/` relative to their own file.
- Scripts write only to `.design-preview/`, `design/`, the user cache dir, and one CLAUDE.md pointer line.
- Names: repo, plugin, marketplace, marketplace entry and skill directory are all `preview-first`. Slash command `/preview-first`.
- SKILL.md frontmatter uses only `name`, `description`, `license`, `metadata` (portable keys). SKILL.md under 500 lines.
- No AI-tell defaults in the preview chrome itself: no purple gradients, no all-caps eyebrows, no emoji icons, no arrows in link text, no identical radius everywhere, neutral grey chrome that does not colour the directions.
- Palettes authored in OKLCH, rendered to hex. Body text must pass WCAG 4.5:1 and APCA Lc 60 against its background in both modes, or the validator fails.
- Git identity: moraneus <moraneus@gmail.com>. No co-author trailers. Conventional commit prefixes (feat, fix, docs, test, chore).
- Licence MIT.

## Review Focus

1. A brief whose product type or mood is not in the graph (user typed "a dog grooming booking site, cozy"): recommend must still return bundles by falling back to nearest aliases and a generic product type, never crash or return zero. Test pinned in Task 7.
2. A brand colour that fails contrast as a primary (`#FFEB3B` on white): palette resolution must pick a dark `on_primary`, report the failure in the tile, and never silently pass. Test pinned in Task 8.
3. Offline preview: no network, Google Fonts unreachable; tile must render with the fallback stack and show the fallback notice. Test pinned in Task 9 (notice markup present) and Task 15 (manual check).
4. Re-export over a hand-edited DESIGN.md: free sections survive, generated sections update, previous files land in `design/history/`. Test pinned in Task 12.
5. Server left running from a previous session on a now-dead pid, or two projects open at once: `serve_preview.py` must detect a stale `server.json`, bind a fresh free port, and `--stop` must not kill an unrelated pid. Test pinned in Task 11.

---

## File structure

```
preview-first/
  README.md  LICENSE  CONTRIBUTING.md  CHANGELOG.md  .gitignore
  .claude-plugin/plugin.json  .claude-plugin/marketplace.json
  .github/workflows/ci.yml  .github/workflows/refresh.yml
  skills/preview-first/
    SKILL.md
    references/{process,color,typography,motion,components,layout,anti-patterns,devices,handoff,platform}.md
    knowledge/schema.json  graph.json  devices.json  sources.json  live/{fonts,features,releases,feeds}.json
    scripts/
      _common.py        paths, json io, cache dir, slug helpers (shared)
      contrast.py       colour maths and grading
      validate_graph.py schema + integrity + contrast validation
      recommend.py      brief -> bundles
      palette.py        palette resolution (overrides, on-colours, hex rendering)
      build_preview.py  directions -> .design-preview/
      drafts/__init__.py  drafts/marketing.py  drafts/app.py  drafts/content.py  drafts/store.py
      serve_preview.py  local server
      export_design.py  selection -> design/
      refresh_knowledge.py  live sources -> cache
      import_direction.py   css/tailwind/tokens/url -> direction skeleton
    assets/preview/
      shell.html  preview.css  preview.js  device-frames.css  tile.css
    assets/icons/{lucide,phosphor,heroicons,tabler,radix,material}.svg (sprite per set, 12 icons each)
  tests/
    conftest.py  fixtures/{mini_graph.json,brief_saas.json,brief_unknown.json,directions_two.json,
                 tailwind.config.js,tokens_dtcg.json,site.css,google_fonts_metadata.txt,web_features.json,
                 releases.atom,feed.xml}
    test_contrast.py test_validate_graph.py test_graph_content.py test_recommend.py test_palette.py
    test_build_preview.py test_drafts.py test_devices.py test_serve.py test_export.py
    test_refresh.py test_import.py test_skill_docs.py
  docs/superpowers/{specs,plans}  docs/research/  docs/assets/ (screenshots for README)
```

Every script exposes a `main(argv) -> int` and functions that tests import directly; `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`. Scripts add their own directory to `sys.path` so `import _common` works when run by path.

---

### Task 1: Repository scaffold, manifests, GitHub repo

**Files:**
- Create: `LICENSE`, `.gitignore`, `README.md` (stub: name, tagline, one paragraph, "work in progress"), `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/preview-first/SKILL.md` (frontmatter + one-line body placeholder), `tests/conftest.py`, `tests/test_manifests.py`
- Create: `skills/preview-first/scripts/_common.py`

**Interfaces:**
- Produces: `_common.SKILL_DIR: Path`, `_common.KNOWLEDGE_DIR`, `_common.ASSETS_DIR`, `_common.load_json(path) -> Any`, `_common.dump_json(path, obj) -> None` (indent 2, sorted keys off, trailing newline), `_common.cache_dir() -> Path` (XDG_CACHE_HOME or ~/.cache, then `preview-first`), `_common.slugify(text) -> str`, `_common.today() -> str` (ISO date).
- Produces: `conftest.py` fixture `scripts_path` that inserts `skills/preview-first/scripts` into `sys.path`, and fixture `tmp_project(tmp_path)` returning a directory with an empty `.git/` marker file.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_manifests.py
def test_plugin_and_marketplace_names_match():
    plugin = json.load(open(ROOT/".claude-plugin/plugin.json"))
    market = json.load(open(ROOT/".claude-plugin/marketplace.json"))
    assert plugin["name"] == "preview-first"
    assert market["name"] == "preview-first"
    assert market["plugins"][0]["name"] == "preview-first"
    assert market["plugins"][0]["source"] == "./"
    assert plugin["license"] == "MIT"

def test_skill_frontmatter_portable_keys_only():
    text = (ROOT/"skills/preview-first/SKILL.md").read_text()
    assert text.startswith("---\n")
    fm = text.split("---")[1]
    keys = {line.split(":")[0].strip() for line in fm.strip().splitlines() if ":" in line and not line.startswith(" ")}
    assert keys <= {"name", "description", "license", "metadata"}
    assert "name: preview-first" in fm

def test_common_cache_dir_respects_xdg(monkeypatch, tmp_path, scripts_path):
    import _common
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert _common.cache_dir() == tmp_path / "preview-first"
```

- [ ] **Step 2: Run tests, expect failure (files missing)**

Run: `uv run --with pytest pytest tests/test_manifests.py -v`
Expected: FAIL (FileNotFoundError / ModuleNotFoundError)

- [ ] **Step 3: Create the files**

`plugin.json`: name, version `0.1.0`, description "See your design before you build it: palette, type, components, motion and device previews in the browser, then a design contract Claude follows.", author {name "Moran Omer", url github}, homepage/repository `https://github.com/moraneus/preview-first`, license MIT, keywords [design, web-design, ui, ux, preview, style-tile, design-tokens, color-palette, typography, device-preview, claude-code, agent-skills]. `marketplace.json` per spec research with `owner.name`, one plugin entry, `category: "design"`, `tags`. `.gitignore`: `__pycache__/`, `.pytest_cache/`, `.design-preview/`, `.venv/`, `dist/`. SKILL.md frontmatter name `preview-first`, description (keyword dense, third person, under 1024 chars) covering triggers: start a website or web app, landing page, redesign, choose colours or fonts, see the design before coding, device preview, design system, design tokens.

- [ ] **Step 4: Run tests, expect pass**

Run: `uv run --with pytest pytest tests/test_manifests.py -v`
Expected: PASS

- [ ] **Step 5: Commit, create the GitHub repository, push**

```bash
git add -A && git commit -m "chore: scaffold preview-first skill repository"
gh repo create preview-first --public --source=. --remote=origin --description "Look before you build. A Claude Code skill that shows your web design directions (palette, type, components, motion, device frames) in the browser before any code is written." --push
gh repo edit moraneus/preview-first --add-topic agent-skills --add-topic claude-code --add-topic claude-skills --add-topic claude-code-plugin --add-topic web-design --add-topic ui-design --add-topic design-system --add-topic design-tokens --add-topic color-palette --add-topic typography --add-topic style-tile --add-topic device-preview --add-topic codex --add-topic cursor --add-topic windsurf --add-topic opencode
```

Also commit the design doc, plan and research reports in this commit.

---

### Task 2: Colour maths and contrast grading

**Files:**
- Create: `skills/preview-first/scripts/contrast.py`
- Test: `tests/test_contrast.py`

**Interfaces:**
- Produces: `hex_to_rgb(hex) -> tuple[float,float,float]` (0..1), `rgb_to_hex(rgb) -> str` (lowercase `#rrggbb`), `oklch_to_rgb(l, c, h) -> tuple` (may be out of gamut), `rgb_to_oklch(rgb) -> tuple`, `oklch_to_hex(l, c, h) -> str` (gamut-mapped by reducing chroma until in gamut, step 0.005), `parse_oklch("oklch(0.98 0.01 90)") -> (l,c,h)`, `in_gamut(rgb) -> bool`, `relative_luminance(rgb) -> float`, `wcag_ratio(fg_hex, bg_hex) -> float`, `apca_lc(text_hex, bg_hex) -> float` (signed, APCA 0.1.9 constants), `grade(fg_hex, bg_hex, role) -> dict` with keys `wcag`, `apca`, `wcag_pass` (4.5 body, 3.0 large/ui), `apca_pass` (60 body, 45 large, 30 ui), `ok` where role in {"body","large","ui"}, `best_on_colour(bg_hex, candidates=("#ffffff","#111111")) -> str`.
- CLI: `contrast.py FG BG [--role body]` prints JSON grade.

- [ ] **Step 1: Write failing tests**

```python
def test_wcag_black_on_white(): assert round(wcag_ratio("#000000", "#ffffff"), 2) == 21.0
def test_wcag_known_pair(): assert abs(wcag_ratio("#777777", "#ffffff") - 4.48) < 0.02
def test_apca_known_pairs():
    assert abs(apca_lc("#000000", "#ffffff") - 106.04) < 0.5
    assert abs(apca_lc("#ffffff", "#000000") - (-107.88)) < 0.5
    assert abs(apca_lc("#888888", "#ffffff") - 63.06) < 0.5
def test_oklch_roundtrip_white(): assert oklch_to_hex(1.0, 0.0, 0.0) == "#ffffff"
def test_oklch_known_colour(): assert oklch_to_hex(0.6279, 0.2577, 29.23) == "#ff0000"  # sRGB red
def test_gamut_mapping_reduces_chroma(): assert in_gamut(hex_to_rgb(oklch_to_hex(0.7, 0.4, 150)))
def test_grade_roles():
    assert grade("#767676", "#ffffff", "body")["wcag_pass"] is True
    assert grade("#999999", "#ffffff", "body")["ok"] is False
def test_best_on_colour(): assert best_on_colour("#ffeb3b") == "#111111"
def test_parse_oklch(): assert parse_oklch("oklch(0.5 0.1 200)") == (0.5, 0.1, 200.0)
```

- [ ] **Step 2: Run, expect failure**

Run: `uv run --with pytest pytest tests/test_contrast.py -v` — Expected: FAIL, module missing

- [ ] **Step 3: Implement `contrast.py`**

OKLab matrices from Björn Ottosson's reference (linear sRGB to LMS, LMS to OKLab and inverses). APCA constants: 0.1.9 (`SA98G`: normBG 0.56, normTXT 0.57, revTXT 0.62, revBG 0.65, blkThrs 0.022, blkClmp 1.414, scaleBoW 1.14, scaleWoB 1.14, loBoWOffset 0.027, loWoBOffset 0.027, loClip 0.1, deltaYmin 0.0005).

- [ ] **Step 4: Run, expect pass** — same command, PASS

- [ ] **Step 5: Commit** `git commit -m "feat: colour maths with WCAG and APCA grading"`

---

### Task 3: Schema and graph validator

**Files:**
- Create: `skills/preview-first/knowledge/schema.json`, `skills/preview-first/scripts/validate_graph.py`
- Test: `tests/test_validate_graph.py`, `tests/fixtures/mini_graph.json`

**Interfaces:**
- `schema.json`: a JSON object `{"node_kinds": {kind: {"required": [...], "optional": [...], "enums": {field: [...]}}}, "edge_kinds": [...], "files": {"brief": {...}, "directions": {...}, "selection": {...}, "device": {...}}}`. Node kinds: style, palette, type-pairing, treatment, motion-pattern, product-type, mood, icon-set, platform-feature, reference-site. Edge kinds: pairs_with, suits, avoid_with, requires, expresses, defaults_to, evidence_for.
- Common required node fields: id (`<kind>.<slug>`), kind, name, source, added, last_verified, confidence (0..1). Kind-specific required fields as listed in the spec section 5.1 and refined here:
  - style: family (enum: minimal, editorial, technical, soft, expressive, dark, bold), traits[], signals[], radius_scale (enum: none, sm, md, lg, pill), shadow (enum: none, hairline, soft, layered, hard), density (enum: airy, regular, compact)
  - palette: temperature (warm, cool, neutral), scheme (light, dark, both), light{}, dark{} each with roles bg, surface, surface_raised, text, text_muted, border, primary, on_primary, accent, on_accent, success, warning, danger, focus as `oklch(...)` strings
  - type-pairing: heading{family, category, weights[], source}, body{...}, mono (optional), fallback_heading, fallback_body, scale_ratio, measure_ch, css_url (optional), license
  - treatment: axis (enum from components vocabulary), value, css_class
  - motion-pattern: trigger (hover, press, focus, enter, exit, page, scroll, ambient, layout), duration_ms, easing, communicates, implementation (css, view-transitions, scroll-driven, motion, gsap), reduced_motion, level (0..3)
  - product-type: aliases[], page_type (marketing, app, content, store)
  - mood: aliases[]
  - icon-set: stroke, license, url
  - platform-feature: baseline (widely, newly, limited), support{chrome, firefox, safari}, global_pct
  - reference-site: url, product_type, observed{}, seen
- `validate_graph.validate(graph: dict, schema: dict, strict: bool=False) -> list[Finding]` where `Finding = namedtuple("Finding", "level node_id message")`, level in {"error","warn"}. Errors: unknown kind, missing required, bad id prefix, duplicate id, dangling edge endpoint, unknown edge kind, weight outside 0..1, evidence id not a reference-site, palette role contrast failure (text on bg, text on surface, on_primary on primary, on_accent on accent, text_muted on bg at role "large"), oklch parse failure. Warns: empty evidence on pairs_with/suits/avoid_with edges, confidence < 0.6, last_verified older than 365 days.
- CLI: `validate_graph.py [--graph PATH] [--strict]` prints findings, exit 1 on any error (or any warn with `--strict`).

- [ ] **Step 1: Failing tests** using `mini_graph.json` (2 styles, 2 palettes with one deliberately failing contrast, 1 pairing, edges including one dangling):

```python
def test_valid_mini_graph_has_only_expected_errors():
    findings = validate(load(mini), load(schema))
    errors = [f for f in findings if f.level == "error"]
    assert {f.node_id for f in errors} == {"palette.bad-contrast", "edge:style.a->palette.missing"}
def test_contrast_error_message_names_roles():
    assert any("text on bg" in f.message for f in errors_for("palette.bad-contrast"))
def test_cli_exit_code(tmp_path): assert main(["--graph", str(mini)]) == 1
```

- [ ] **Step 2: Run, expect failure**
- [ ] **Step 3: Implement schema.json and validate_graph.py** (uses `contrast.grade`)
- [ ] **Step 4: Run, expect pass**
- [ ] **Step 5: Commit** `feat: knowledge schema and graph validator`

---

### Task 4: Seed the graph, part 1 (styles, treatments, motion, product types, moods, icon sets, platform features)

**Files:**
- Create: `skills/preview-first/knowledge/graph.json` (nodes of these kinds plus `defaults_to`, `expresses`, `suits`, `requires` edges)
- Test: `tests/test_graph_content.py`

**Interfaces:**
- Consumes: validator from Task 3. Research: `docs/research/2026-10-30-design-directions-motion-platform.md`.
- Produces: node ids other tasks rely on. Style ids (14): `style.paper-editorial`, `style.swiss-grid`, `style.mono-engineering`, `style.soft-product`, `style.dark-console`, `style.luminous-dark`, `style.quiet-luxury`, `style.neo-brutalist`, `style.playful-geometric`, `style.warm-organic`, `style.glass-layered`, `style.bento-showcase`, `style.poster-type`, `style.data-dense`. Treatment axes and values (closed vocabulary): `button_shape` {pill, rounded, square}, `button_fill` {solid, outline, ghost, soft}, `input_edge` {hairline, filled, underline}, `card_edge` {border, shadow, flat, inset}, `nav` {airy, compact, floating, sidebar}, `divider` {hairline, space, rule}, `image_corner` {none, sm, lg}, `focus_ring` {offset, inset, glow}, `link_style` {underline, colour, both}, `elevation` {none, one, layered}. Motion ids (25) across triggers with levels 0..3, e.g. `motion.press-scale-97`, `motion.hover-lift-2`, `motion.enter-fade-up-8`, `motion.enter-scale-95`, `motion.exit-fade-fast`, `motion.page-crossfade-vt`, `motion.page-slide-vt`, `motion.scroll-reveal-once`, `motion.scroll-progress-bar`, `motion.ambient-glow-slow`, `motion.layout-flip`, `motion.spring-pop`, `motion.underline-grow`, `motion.skeleton-shimmer`, `motion.toast-slide-in`, `motion.accordion-height`, `motion.tab-indicator-slide`, `motion.switch-thumb-spring`, `motion.button-loading-swap`, `motion.menu-stagger-30`, `motion.card-tilt-subtle`, `motion.hero-mask-reveal`, `motion.number-count-up`, `motion.focus-ring-pulse-once`, `motion.none`. Product types (22) and moods (20) with aliases. Icon sets (6). Platform features (13) from the research table.

- [ ] **Step 1: Failing content tests**

```python
def test_counts():
    g = load_graph(); by = kinds(g)
    assert len(by["style"]) >= 14 and len(by["treatment"]) >= 30 and len(by["motion-pattern"]) >= 25
    assert len(by["product-type"]) >= 20 and len(by["mood"]) >= 18 and len(by["icon-set"]) >= 6
    assert len(by["platform-feature"]) >= 12
def test_every_style_has_full_treatment_defaults():
    for s in styles: assert axes_covered(s) == ALL_AXES
def test_every_style_has_motion_defaults_at_each_level():
    for s in styles: assert {m.level for m in motion_defaults(s)} >= {1, 2}
def test_every_product_type_suits_at_least_three_styles(): ...
def test_every_mood_expresses_at_least_two_styles(): ...
def test_validator_has_no_errors(): assert not errors(validate(graph, schema))
```

- [ ] **Step 2: Run, expect failure**
- [ ] **Step 3: Author the nodes and edges.** Each style gets `summary`, `traits`, `signals`, `avoid_with` edges to clashing styles and moods, `requires` edges to platform features where relevant (glass-layered requires backdrop-filter; luminous-dark requires color-mix). Set `source` to the research report path, `added`/`last_verified` to 2026-10-30, `confidence` 0.8 unless evidenced.
- [ ] **Step 4: Run tests and `validate_graph.py`, expect pass**
- [ ] **Step 5: Commit** `feat(knowledge): styles, treatments, motion, product types, moods, icons, platform features`

---

### Task 5: Seed the graph, part 2 (palettes and type pairings)

**Files:**
- Modify: `skills/preview-first/knowledge/graph.json`
- Test: extend `tests/test_graph_content.py`

**Interfaces:**
- Consumes: Task 2 contrast functions (to author and check), Task 4 style ids.
- Produces: 40+ palette nodes authored in OKLCH with light and dark sets, `temperature`, `scheme`; 30+ type-pairing nodes with Google Fonts or system sources, `fallback_heading`/`fallback_body` stacks, `category` per face (grotesque, humanist, geometric, serif-transitional, serif-didone, serif-slab, mono, display), `css_url` for Google Fonts families, `license` (OFL, Apache, system); `pairs_with` edges style to palette (each style at least 3 palettes with distinct temperatures where the style allows) and style to type-pairing (at least 3 each), `avoid_with` edges for known clashes (didone + humanist sans; neon accents + quiet-luxury).

- [ ] **Step 1: Failing tests**

```python
def test_palette_and_pairing_counts(): assert len(by["palette"]) >= 40 and len(by["type-pairing"]) >= 30
def test_each_style_has_three_palettes_and_pairings(): ...
def test_palettes_pass_contrast_in_both_modes(): assert not [f for f in validate(...) if "palette." in f.node_id and f.level == "error"]
def test_pairings_have_fallback_stacks(): for p in pairings: assert "," in p["fallback_body"]
def test_not_every_pairing_is_inter(): assert sum("Inter" in p["body"]["family"] for p in pairings) <= 3
def test_palette_temperature_spread(): assert {p["temperature"] for p in palettes} == {"warm","cool","neutral"}
```

- [ ] **Step 2: Run, expect failure**
- [ ] **Step 3: Author palettes and pairings.** Use `contrast.py` while authoring: for each palette compute text/bg, on_primary/primary; adjust L until passing. Dark sets keep hue, invert lightness, reduce chroma ~20%. Include at least: paper-ink (warm neutral), slate-signal (cool), graphite-amber (dark-first), moss-cream, ink-coral, ocean-sand, plum-linen, forest-brass, midnight-lime, clay-bone, steel-cyan, lavender-stone, terminal-green (dark), ruby-chalk, cobalt-paper, olive-ivory, cocoa-peach, navy-gold, arctic-teal, charcoal-saffron, and 20 more with distinct hue families. Pairings must span categories: serif+sans (Fraunces/Figtree, Instrument Serif/Geist, Newsreader/Inter Tight, Source Serif 4/Source Sans 3, Libre Caslon/Karla, Playfair Display/Lato), sans+sans (Geist/Geist, Manrope/Manrope, Plus Jakarta Sans/Inter, Outfit/Nunito Sans, Bricolage Grotesque/Albert Sans, Onest/Onest, Schibsted Grotesk/Hanken Grotesk, Sora/Work Sans), mono-led (JetBrains Mono/IBM Plex Sans, Geist Mono/Geist, Space Mono/Space Grotesk, Commit Mono/Atkinson Hyperlegible), display-led (Syne/Karla, Unbounded/Manrope, Archivo Black/Archivo, Clash Display via Fontshare noted as source "fontshare"), slab (Roboto Slab/Roboto Flex, Zilla Slab/Lato), system (system-ui stack, `-apple-system`), and others to reach 30.
- [ ] **Step 4: Run tests and validator, expect pass**
- [ ] **Step 5: Commit** `feat(knowledge): 40 OKLCH palettes and 30 type pairings with edges`

---

### Task 6: Seed the graph, part 3 (reference sites, evidence, devices)

**Files:**
- Modify: `skills/preview-first/knowledge/graph.json` (reference-site nodes, evidence on edges)
- Create: `skills/preview-first/knowledge/devices.json`
- Test: `tests/test_devices.py`, extend `tests/test_graph_content.py`

**Interfaces:**
- Consumes: `docs/research/2026-10-30-template-survey-and-live-sources.md` (pairings survey; written when the research agent returns) and `docs/research/2026-10-30-devices.md`.
- Produces: 60+ `reference-site` nodes with `observed` fields and `seen` date, attached as `evidence` on at least 80 edges. `devices.json`: `{"updated": "2026-10-30", "devices": [ {id, vendor, model, year, kind (phone, foldable, tablet, laptop, desktop), viewport {w, h}, dpr, safe_area {top, bottom, left, right}, cutout (island, notch, punch, none), corner_radius, fold (optional: {folded: {w, h}, crease: true}), share_rank, default (bool), source, verified} ] }` with at least 25 devices covering the list in spec 4.4; `default: true` on 12 of them.
- `_common.load_devices() -> list[dict]`.

- [ ] **Step 1: Failing tests**

```python
def test_device_count_and_vendors():
    d = load_devices(); assert len(d) >= 25
    assert {"Apple","Samsung","Google"} <= {x["vendor"] for x in d}
def test_device_fields_and_sanity():
    for x in d: assert 320 <= x["viewport"]["w"] <= 3840 and 1 <= x["dpr"] <= 4 and x["source"].startswith("http")
def test_fold_devices_have_folded_viewport(): assert all("folded" in x["fold"] for x in d if x["kind"] == "foldable")
def test_defaults_are_twelve(): assert sum(x["default"] for x in d) == 12
def test_reference_sites_and_evidence(): assert len(by["reference-site"]) >= 60 and edges_with_evidence(g) >= 80
```

- [ ] **Step 2: Run, expect failure**
- [ ] **Step 3: Author reference sites, attach evidence, write devices.json** from the research reports; mark `verified: false` on any number the report flagged.
- [ ] **Step 4: Run, expect pass**
- [ ] **Step 5: Commit** `feat(knowledge): reference sites as evidence and device catalogue`

---

### Task 7: Recommender

**Files:**
- Create: `skills/preview-first/scripts/recommend.py`
- Test: `tests/test_recommend.py`, `tests/fixtures/brief_saas.json`, `tests/fixtures/brief_unknown.json`

**Interfaces:**
- Consumes: graph (Task 4 to 6), `schema.json` `files.brief`.
- `brief.json` schema: `{product: str, audience: str, product_type: str (node id or free text), moods: [str], page_type: "marketing"|"app"|"content"|"store", constraints: {brand_colors: [hex], fonts: [str], scheme: "light"|"dark"|"both", motion_level: 0..3 (optional)}, admired: [url], words: {name: str, tagline: str} }`.
- Produces: `recommend(brief: dict, graph: dict, count: int = 4) -> list[Bundle]` where `Bundle` is a dict: `{style, palette, type_pairing, treatments: {axis: value}, motion: [motion ids], motion_level, icon_set, radius_scale, density, alternatives: {palettes: [ids], type_pairings: [ids], icon_sets: [ids]}, justification: [{from, to, kind, weight, evidence: [ids]}], score: float}`.
- `resolve_product_type(text, graph) -> str` (exact id, then alias match, then token overlap, then `product-type.general-website`). `resolve_moods(list, graph) -> list[str]` (unknown words dropped, never fails).
- Diversity rules: distinct `style.family` across bundles; at most two bundles share palette `temperature`; at most two share the (heading category, body category) pair. Scheme constraint filters palettes by `scheme`. `motion_level` default 1 (2 for moods playful, bold, energetic; 0 for mood calm plus product-type documentation).
- CLI: `recommend.py --brief PATH [--count N] [--graph PATH]` prints `{"bundles": [...]}`; `recommend.py --list product-types|moods|styles|palettes|type-pairings` prints `id\tname\taliases`.

- [ ] **Step 1: Failing tests**

```python
def test_returns_requested_count_with_distinct_families(): b = recommend(saas, g, 4); assert len(b) == 4 and len({x["style_family"] for x in b}) == 4
def test_temperature_diversity(): assert max(Counter(temp(x) for x in b).values()) <= 2
def test_unknown_product_type_falls_back(): b = recommend(unknown, g, 3); assert len(b) == 3
def test_dark_only_scheme_filters_palettes(): assert all(scheme(x) in ("dark","both") for x in recommend(dark_brief, g))
def test_justification_cites_edges(): assert all(x["justification"] for x in b)
def test_alternatives_pair_with_style(): for x in b: for pid in x["alternatives"]["palettes"]: assert edge_exists(g, x["style"], pid, "pairs_with")
def test_list_cli_prints_ids(capsys): main(["--list","moods"]); assert "mood." in capsys.readouterr().out
def test_deterministic(): assert recommend(saas, g) == recommend(saas, g)
```

- [ ] **Step 2: Run, expect failure**
- [ ] **Step 3: Implement.** Scoring: style score = Σ suits(product_type→style)·1.0 + Σ expresses(mood→style)·0.7 − Σ avoid_with(mood→style)·1.0 − Σ avoid_with(product_type→style)·1.0; tie-break by node id. Palette for a style: pairs_with weight + 0.3 if palette temperature matches a mood's `temperature_hint` (optional mood field) − 1 if avoid_with any mood; same shape for pairings. Greedy selection with the diversity constraints; if constraints cannot be met, relax temperature rule first, then category rule, never the family rule unless fewer families than count exist.
- [ ] **Step 4: Run, expect pass**
- [ ] **Step 5: Commit** `feat: graph recommender with diversity constraints`

---

### Task 8: Palette resolution and token CSS

**Files:**
- Create: `skills/preview-first/scripts/palette.py`
- Test: `tests/test_palette.py`

**Interfaces:**
- Consumes: `contrast.py`.
- Produces: `resolve_palette(palette_node: dict, overrides: dict | None = None) -> ResolvedPalette` where `ResolvedPalette = {"light": {role: {"oklch": str, "hex": str}}, "dark": {...}, "checks": [{"mode", "pair", "fg_role", "bg_role", "wcag", "apca", "ok"}], "warnings": [str]}`. Overrides: `{"brand_primary": "#hex", "brand_accent": "#hex"}` replace `primary`/`accent` in both modes; `on_primary`/`on_accent` recomputed with `best_on_colour`; any failing check appends a warning string naming mode and pair.
- `tokens_css(resolved, selector=":root", scheme="both") -> str` emits custom properties `--pf-color-<role>` for light under the selector with `color-scheme: light dark`, dark under `[data-theme="dark"]` and `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) ... }`. Also `--pf-color-<role>-oklch`.
- `scale_tokens(radius_scale, density, type_pairing) -> str` emits `--pf-radius-{xs,sm,md,lg,xl,full}`, `--pf-space-{1..12}`, `--pf-font-{heading,body,mono}`, `--pf-text-{xs,sm,base,lg,xl,2xl,3xl,4xl,5xl}` computed from `scale_ratio` (base 1rem), `--pf-leading-{tight,normal,loose}`, `--pf-measure`.

- [ ] **Step 1: Failing tests**

```python
def test_resolve_renders_hex_for_every_role(): r = resolve_palette(p); assert set(r["light"]) == ROLES and all(v["hex"].startswith("#") for v in r["light"].values())
def test_brand_override_recomputes_on_primary(): r = resolve_palette(p, {"brand_primary": "#ffeb3b"}); assert r["light"]["on_primary"]["hex"] == "#111111"
def test_failing_override_is_warned_not_hidden(): r = resolve_palette(p, {"brand_primary": "#fff59d"}); assert any("primary" in w for w in r["warnings"]); assert any(not c["ok"] for c in r["checks"])
def test_tokens_css_has_light_and_dark(): css = tokens_css(r); assert "--pf-color-bg:" in css and '[data-theme="dark"]' in css and "prefers-color-scheme: dark" in css
def test_scale_tokens_ratio(): css = scale_tokens("md", "regular", pairing); assert "--pf-text-xl: 1.25rem" in css  # ratio 1.25 fixture
def test_radius_scale_none_is_zero(): assert "--pf-radius-md: 0" in scale_tokens("none", "regular", pairing)
```

- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: palette resolution with overrides and token CSS`

---

### Task 9: Preview build, part 1 (shell, gallery, style tile)

**Files:**
- Create: `skills/preview-first/scripts/build_preview.py`, `skills/preview-first/assets/preview/shell.html`, `preview.css`, `tile.css`, `preview.js`, `skills/preview-first/assets/icons/*.svg`
- Test: `tests/test_build_preview.py`, `tests/fixtures/directions_two.json`

**Interfaces:**
- Consumes: Tasks 7, 8; `schema.json` `files.directions`.
- `directions.json` schema: `{version: 1, brief: <brief>, directions: [ {id: "A", name, rationale, bundle: <Bundle from Task 7 minus score>, overrides: {brand_primary?}, copy: {headline, subhead, cta_primary, cta_secondary, nav: [str], features: [{title, body}], proof: str, form: {title, fields: [str], submit}, footer: str}, layout: {hero, features, proof, cta, footer} } ] }`. `copy` and `layout` optional; defaults from `drafts.default_copy(brief)` and style `defaults_to`.
- Produces: `build(directions: dict, out: Path, graph: dict, devices: list, vendor_fonts: bool = False) -> BuildReport` where `BuildReport = {"pages": [paths], "warnings": [str]}`; writes `out/index.html` (gallery), `out/<id>/tile.html`, `out/<id>/draft.html` (Task 10), `out/<id>/devices.html` (Task 10), `out/<id>/tokens.css`, `out/<id>/variants.css` (tokens for each alternative palette and pairing under `[data-palette="<id>"]`, `[data-pairing="<id>"]`, `[data-radius="<scale>"]`, `[data-density="<d>"]`, `[data-motion="<n>"]`), `out/assets/{preview.css,tile.css,preview.js,device-frames.css}`, `out/assets/icons/*.svg`, `out/data.json` (directions, devices, resolved palettes, checks).
- `render_template(name, slots: dict) -> str`: reads `assets/preview/<name>`, replaces `{{slot}}` exact tokens; unknown slots raise.
- Tile sections and required DOM hooks (tests grep for them): `section[data-section="palette"]` with one `.pf-swatch[data-role]` per role showing hex, oklch and `.pf-contrast` grade badge; `section[data-section="type"]` with `.pf-type-sample[data-step]` for each scale step and a 60-70ch paragraph; `[data-section="spacing"]`, `[data-section="radius"]`, `[data-section="elevation"]`, `[data-section="icons"]` with 12 inline icons from the bundle's set; `[data-section="components"]` with `button.pf-btn[data-state]` for default, hover (forced via class), focus, active, disabled, loading; inputs `[data-state]` default, focus, error, disabled; select, checkbox, switch, card, badge, alert, tabs, nav bar, footer; `[data-section="motion"]` with one `.pf-motion-demo[data-motion-id]` per motion in the bundle, each with a play button, printed duration and easing, and a reduced-motion toggle; `.pf-font-notice[hidden]` fallback notice toggled by `preview.js` via `document.fonts.check`.
- Controls bar (shared by tile, draft, devices): `select[data-control="palette"]` (options = bundle palette + alternatives), `[data-control="pairing"]`, `[data-control="radius"]`, `[data-control="density"]`, `[data-control="motion"]`, theme toggle `[data-control="theme"]`, `button[data-action="select"]`. `preview.js` applies selections as `data-*` attributes on `<html>`, persists per direction in `localStorage`, and on select POSTs `{direction, overrides: {palette, pairing, radius, density, motion, theme}}` to `/select`, falling back to downloading `selection.json` when the POST fails (file:// case).
- CLI: `build_preview.py --directions PATH [--out DIR] [--vendor-fonts] [--graph PATH]`; default out `.design-preview` in cwd.

- [ ] **Step 1: Failing tests** (parse output with `html.parser`, assert the hooks above exist; assert no `linear-gradient` with purple hues in `preview.css`; assert `index.html` lists both directions with names from the fixture; assert `variants.css` contains `[data-palette="` for each alternative; assert `tokens.css` embeds the font `css_url` as `<link>` in the page head and the `.pf-font-notice` exists; assert build with a direction missing `copy` still succeeds)
- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: preview shell, gallery and style tile`

---

### Task 10: Preview build, part 2 (draft pages, layout variants, devices view)

**Files:**
- Create: `skills/preview-first/scripts/drafts/__init__.py`, `drafts/marketing.py`, `drafts/app.py`, `drafts/content.py`, `drafts/store.py`, `skills/preview-first/assets/preview/device-frames.css`
- Modify: `build_preview.py` (wire draft and devices pages)
- Test: `tests/test_drafts.py`, extend `tests/test_devices.py`

**Interfaces:**
- `drafts.default_copy(brief: dict) -> dict` (neutral copy from `brief.product`, `words.name`, product type; never lorem ipsum; no em dashes, no emoji, no arrows).
- `drafts.render(page_type: str, direction: dict, resolved_palette: dict, graph: dict) -> str` dispatching to a module with `SECTIONS: list[str]` and `VARIANTS: dict[section, list[variant]]` and `render(direction, copy, layout) -> str`. Variants: marketing hero {split, centered, editorial, product-shot, poster}, features {bento, list, alternating, columns}, proof {quote, logos-text, stats-sourced, none}, cta {band, inline, form}, footer {columns, minimal}. app: shell {sidebar, topbar}, table {dense, comfortable}, detail {panel, drawer}, empty-state, settings-form. content: header {masthead, minimal}, article {single, with-toc}, list {cards, lines}. store: hero {product, collection}, grid {two, three, four}, product {gallery-left, gallery-top}, cart {drawer, page}.
- Layout choice: `direction.layout` wins; else style `defaults_to` edge to a `layout.<section>.<variant>` pseudo-node is not used (keep graph clean); instead each style node carries `layout_defaults: {section: variant}` for its best page types; else first variant.
- Devices page: `out/<id>/devices.html` renders the draft (`draft.html`) in `iframe` per device sized to `viewport` with `transform: scale()` to fit a fixed 280px-wide column (laptops 420px), frame drawn by `device-frames.css` classes `.pf-device[data-kind][data-cutout]`, crease overlay for `fold.crease`, safe-area overlay toggle, label `vendor model · WxH @DPRx`, checklist of devices (`input[type=checkbox][data-device-id]`, defaults checked), rotate button, and `?url=` support: when present, iframes load that URL instead and a notice explains frame-blocking headers if `load` never fires in 5 s.
- `device-frames.css` must itself pass the anti-tell constraint and draw: rounded shell, Dynamic Island pill for `island`, notch bar for `notch`, centred dot for `punch`, home indicator bar, fold crease line, laptop bezel and base.

- [ ] **Step 1: Failing tests**

```python
def test_each_page_type_renders_every_variant(): for pt in PAGE_TYPES: for section, variants in VARIANTS[pt].items(): for v in variants: html = render(pt, direction_with(layout={section: v}), ...); assert f'data-variant="{v}"' in html
def test_default_copy_has_no_tells(): c = default_copy(brief); text = json.dumps(c); assert "—" not in text and "→" not in text and not EMOJI_RE.search(text) and "lorem" not in text.lower()
def test_two_styles_do_not_share_layout(): assert render("marketing", dirA) != render("marketing", dirB) and hero_variant(dirA) != hero_variant(dirB)
def test_devices_page_lists_defaults_and_frames(): html = build(...)/"A/devices.html"; assert html.count('class="pf-device') >= 12 and 'data-cutout="island"' in html and 'data-device-id="samsung-galaxy-z-fold7"' in html
def test_devices_url_param_script_present(): assert "URLSearchParams" in html and "url" in html
```

- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: draft pages with layout variants and device frames view`

---

### Task 11: Local preview server

**Files:**
- Create: `skills/preview-first/scripts/serve_preview.py`
- Test: `tests/test_serve.py`

**Interfaces:**
- `start(dir: Path, port: int = 0, open_browser: bool = False) -> ServerInfo` where `ServerInfo = {"port", "pid", "url", "started"}`; writes `dir/server.json`. Serves static files from `dir` with correct MIME types, `Cache-Control: no-store`, and `POST /select` (JSON body validated against `schema.json` `files.selection`: `{direction: str, overrides: {...}, selected_at: iso}`) writing `dir/selection.json` and replying 204. Rejects requests with a `Host` header that is not localhost/127.0.0.1 (403) and any path escaping `dir` (403).
- `stop(dir: Path) -> bool`: reads `server.json`, checks the pid is alive and its command line contains `serve_preview.py` and this `dir` before sending SIGTERM; removes `server.json`; returns whether a process was stopped.
- `is_stale(dir) -> bool`: `server.json` exists but pid is dead or belongs to another command.
- `wait_for_selection(dir, timeout_s) -> dict | None`.
- CLI: `serve_preview.py --dir DIR [--port N] [--open] [--wait SECONDS] [--stop] [--status]`. Default mode daemonises (double fork on POSIX; on Windows uses `subprocess.Popen` with `DETACHED_PROCESS`) and prints `{"url": ...}`. `--status` prints server.json or `{"running": false}`.

- [ ] **Step 1: Failing tests** (use `threading` to run the handler in-process on port 0):

```python
def test_serves_index_and_sets_no_store(server): r = urlopen(server.url + "/index.html"); assert r.status == 200 and r.headers["Cache-Control"] == "no-store"
def test_post_select_writes_file(server): post(server.url + "/select", {"direction": "B", "overrides": {"palette": "palette.x"}}); assert json.load(open(server.dir/"selection.json"))["direction"] == "B"
def test_post_invalid_selection_is_400(server): assert post(..., {"nope": 1}).status == 400
def test_path_traversal_forbidden(server): assert get(server.url + "/../secret").status == 403
def test_foreign_host_forbidden(server): assert get(server.url + "/index.html", headers={"Host": "evil.example"}).status == 403
def test_stale_server_json_detected(tmp_path): write server.json with pid 999999; assert is_stale(tmp_path)
def test_stop_refuses_unrelated_pid(tmp_path, monkeypatch): write server.json with os.getpid(); monkeypatch cmdline reader to return "python other.py"; assert stop(tmp_path) is False
def test_wait_for_selection_times_out(tmp_path): assert wait_for_selection(tmp_path, 0.2) is None
```

- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** with `http.server.ThreadingHTTPServer` — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: local preview server with selection endpoint`

---

### Task 12: Design contract export

**Files:**
- Create: `skills/preview-first/scripts/export_design.py`
- Test: `tests/test_export.py`

**Interfaces:**
- `export(selection: dict, directions: dict, project: Path, graph: dict, devices: list) -> ExportReport` where `ExportReport = {"written": [paths], "history": path | None, "claude_md_updated": bool}`.
- Writes `project/design/DESIGN.md` with generated sections between `<!-- preview-first:generated:start -->` and `<!-- preview-first:generated:end -->` and a free block after the markers titled "Project notes" that is preserved verbatim on re-export. Generated sections, in order: Identity (name, one-paragraph rationale, style, the brief), Palette (table: role, light hex, dark hex, oklch, usage; contrast table of checked pairs with WCAG and APCA; rules: one accent, where primary may appear), Typography (faces, source and licence, loading snippet, fallback stacks, scale table in rem, roles, measure, weights), Spacing and radius, Elevation, Layout (grid, breakpoints 360/768/1024/1280/1536, density, container queries note), Components (one subsection per component with states and the tokens used), Motion (tokens `--pf-dur-*`, `--pf-ease-*`, allowed patterns with trigger and duration, forbidden patterns, reduced-motion rule), Iconography (set, stroke, licence, no emoji), Imagery, Writing style (sentence case, active voice, no em dashes, no filler), Accessibility floor (WCAG 2.2 AA, focus visible, 44px targets, zoom), Device checks (the default device list with viewports), Do not (direction-specific list merged with global anti-patterns).
- Writes `design/tokens.json` in W3C DTCG format (`$type`, `$value`, groups color.light / color.dark / font / size / radius / space / duration / easing), `design/tokens.css` (from `palette.tokens_css` + `scale_tokens` + motion tokens), `design/tailwind.css` only if `tailwind.config.*` or `@import "tailwindcss"` is detected in the project, containing an `@theme` block mapping `--color-*`, `--font-*`, `--radius-*`.
- Before writing, if `design/DESIGN.md` exists copy `design/*` to `design/history/<YYYYMMDD-HHMMSS>/`.
- CLAUDE.md: append (create if missing) the line `UI work follows design/DESIGN.md. Read it before touching styles, and use design/tokens.css values rather than raw colours, sizes or durations.` once, idempotent.
- Adds `.design-preview/` to `.gitignore` if not present.
- CLI: `export_design.py --selection PATH --directions PATH [--project DIR]`.

- [ ] **Step 1: Failing tests** (fresh export writes all files and the marker pair; DTCG tokens validate: every leaf has `$type` and `$value`; tailwind.css only when `tailwind.config.js` exists; re-export preserves text added under "Project notes" and bumps the generated palette when the selection's palette override differs; history directory created with previous DESIGN.md; CLAUDE.md line appears exactly once after two exports; `.gitignore` contains `.design-preview/`)
- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: export design contract, DTCG tokens and CSS`

---

### Task 13: Live knowledge refresh and workflows

**Files:**
- Create: `skills/preview-first/scripts/refresh_knowledge.py`, `skills/preview-first/knowledge/sources.json`, `skills/preview-first/knowledge/live/{fonts,features,releases,feeds}.json` (initial snapshots), `.github/workflows/refresh.yml`, `.github/workflows/ci.yml`
- Test: `tests/test_refresh.py`, fixtures `google_fonts_metadata.txt`, `web_features.json`, `releases.atom`, `feed.xml`

**Interfaces:**
- `sources.json`: `{"fonts": {"url": "https://fonts.google.com/metadata/fonts", "parser": "google_fonts_metadata"}, "features": {"url": "https://unpkg.com/web-features/data.json", "parser": "web_features", "ids": [...]}, "releases": [{"name": "motion", "url": "https://github.com/motiondivision/motion/releases.atom"}, gsap, tailwindcss, shadcn-ui, radix-primitives, lucide], "npm": [{"name": "motion"}, ...] using `https://api.npmjs.org/downloads/point/last-week/<name>`, "feeds": [{"name": "web.dev", "url": "https://web.dev/feed.xml"}, Chrome for Developers blog feed, Smashing Magazine, CSS-Tricks, Josh Comeau, Rauno Freiberg, Emil Kowalski, Tailwind blog, Linear changelog, Vercel blog]} (exact URLs from the live-sources research report; any that the report could not verify are marked `"verify": true` and skipped with a warning).
- Parsers (pure functions taking text and returning dicts, so fixtures test them): `parse_google_fonts_metadata(text) -> {"fetched", "families": [{family, category, popularity, trending, last_modified}]}` (strip the `)]}'` prefix), `parse_web_features(text, ids) -> {"features": {id: {"baseline": "high"|"low"|False, "baseline_low_date", "support": {...}}}}`, `parse_atom(text) -> [{title, link, updated}]`, `parse_rss(text) -> [...]`, `parse_npm_point(text) -> {"downloads": int}`.
- `fetch(url, timeout=15) -> str` via `urllib.request` with a User-Agent `preview-first/<version>`; `refresh(sources, out_dir, fetcher=fetch) -> RefreshReport = {"ok": [names], "failed": [{name, error}], "out_dir"}`; writes one JSON per group with `fetched` ISO timestamp; never raises on a single failure.
- `newest_live_dir() -> Path` returns whichever of cache and bundled `knowledge/live/` has the newer `fetched` timestamps; `is_stale(days=7) -> bool`.
- Annotation: `annotate_graph(graph, live) -> dict` returns a copy where `type-pairing` nodes gain `live: {popularity_rank, trending}` and `platform-feature` nodes gain `live: {baseline, as_of}`; `recommend.py` uses the annotated graph when live data exists (trending adds +0.05 to a pairing score; a feature that is no longer Baseline adds a warning to any style that `requires` it).
- `refresh.yml`: cron weekly (Monday 06:00 UTC), runs refresh into `skills/preview-first/knowledge/live/`, runs validator and tests, opens a PR with `peter-evans/create-pull-request` titled "chore(knowledge): weekly live refresh". `ci.yml`: on push and PR, Python 3.9 and 3.12 matrix, runs `validate_graph.py --strict` (allow warn in non-strict for now: use non-strict) and pytest, and a smoke build of the fixture directions into a temp dir.

- [ ] **Step 1: Failing tests** (parsers against fixtures; `refresh` with a fake fetcher that raises for one source records a failure and still writes the others; `annotate_graph` adds `live` to the pairing whose family appears in the fixture; `is_stale` true for an old timestamp)
- [ ] **Step 2: Run, expect failure** — **Step 3: Implement**, then run a real refresh once to create the initial `knowledge/live/` snapshots — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: live knowledge refresh, CI and weekly refresh workflow`

---

### Task 14: Import an existing look as a direction

**Files:**
- Create: `skills/preview-first/scripts/import_direction.py`
- Test: `tests/test_import.py`, fixtures `tailwind.config.js`, `tokens_dtcg.json`, `site.css`

**Interfaces:**
- `from_css(text) -> Observed`, `from_tailwind_config(text) -> Observed`, `from_dtcg(obj) -> Observed`, `from_url(url, fetcher=fetch) -> Observed` (reads HTML, inline styles and linked stylesheets on the same origin only). `Observed = {"colors": [hex...] (deduped, ordered by frequency), "fonts": [family...], "radius": [px...], "source": str}`.
- `to_direction(observed, graph, id="X", name="Current look") -> dict` building a direction with a custom palette node embedded inline (`bundle.palette_inline`) whose `bg` is the lightest frequent colour, `text` the darkest, `primary` the most saturated, remaining roles derived with `palette.derive_roles(bg, text, primary)` and checked; `type_pairing_inline` from the first two fonts with fallbacks; nearest style via a simple heuristic (radius 0 and high contrast: neo-brutalist; serif heading: paper-editorial; dark bg: dark-console; else soft-product). `build_preview` accepts `palette_inline` and `type_pairing_inline` anywhere a node id is expected.
- CLI: `import_direction.py (--css PATH | --tailwind PATH | --tokens PATH | --url URL) [--into directions.json]` appends the direction.

- [ ] **Step 1: Failing tests** (fixtures produce expected colours and fonts; `to_direction` yields a direction that `build_preview.build` accepts; URL import with a fake fetcher ignores cross-origin stylesheets)
- [ ] **Step 2: Run, expect failure** — **Step 3: Implement** — **Step 4: Pass**
- [ ] **Step 5: Commit** `feat: import an existing look as a comparable direction`

---

### Task 15: SKILL.md and references

**Files:**
- Modify: `skills/preview-first/SKILL.md`
- Create: `skills/preview-first/references/{process,color,typography,motion,components,layout,anti-patterns,devices,handoff,platform}.md`
- Test: `tests/test_skill_docs.py`

**Interfaces:**
- SKILL.md body (imperative voice, under 500 lines): Overview (what it is, what it is not: it does not write the app); When to run and when to offer (the trigger rules from spec 4.1); The flow as numbered steps with the exact commands: read the project for constraints, ask up to four brief questions, write `.design-preview/brief.json`, run `recommend.py --brief`, author `directions.json` (names, rationale quoting the brief, copy rules: sentence case, active voice, no em dashes, no emoji, no arrows, real nouns from the product), run `build_preview.py`, run `serve_preview.py --open`, tell the developer the URL and stop and wait, on reply read `selection.json` or take the choice from words, run `export_design.py`, confirm what was written, then continue building under the contract; Mutations and imports; After handoff rules (read DESIGN.md first, tokens not raw values, contrast check new colours, offer device preview with `?url=`); Refresh rule (`refresh_knowledge.py` when stale and online; web search for "right now" requests); Quick reference table of scripts and flags; Common mistakes (showing one direction, letting all directions share a family, lorem ipsum, skipping the wait, writing app code before selection); pointer list to references.
- Each reference file: 150 to 400 lines, distilled from `docs/research/` with source links, written as rules Claude applies, not essays. `anti-patterns.md` is the authoritative tells list and the refusal rule ("unless the brief asks for it by name"). `components.md` is the authoritative treatment vocabulary (must match `schema.json` enums; test checks this). `devices.md` explains the catalogue fields, how to add a device, and the share-based default set. `handoff.md` documents the DESIGN.md sections and marker contract.

- [ ] **Step 1: Failing tests** (SKILL.md under 500 lines; every script name in `scripts/` appears in SKILL.md; every reference file linked from SKILL.md exists; `components.md` lists every treatment axis and value present in `schema.json`; description under 1024 chars and contains the words "preview", "design", "before")
- [ ] **Step 2: Run, expect failure** — **Step 3: Write the documents** — **Step 4: Pass**
- [ ] **Step 5: Commit** `docs: SKILL.md workflow and reference library`

---

### Task 16: End-to-end dogfood, screenshots, README, release

**Files:**
- Create: `docs/assets/{gallery,tile,draft,devices}.png`, `CONTRIBUTING.md`, `docs/research/` already present
- Modify: `README.md`, `CHANGELOG.md`, `.claude-plugin/*.json` (version 0.1.0 confirmed)

- [ ] **Step 1: Dogfood in a scratch project.** In the scratchpad directory create an empty project, write a real brief (for example a developer-tools SaaS, moods: precise, calm, trustworthy; and a second brief for a bakery store, moods: warm, playful), run recommend, author `directions.json` by hand as Claude would, build, serve, open with Playwright MCP, screenshot gallery, tile, draft and devices views at 1440 wide, click "Select", confirm `selection.json`, run export, read `design/DESIGN.md`. Record any defect as a failing test in the owning task's test file, fix, commit.
- [ ] **Step 2: Visual review against the anti-tell list** for the preview chrome and for each generated direction; fix styles or graph defaults; commit.
- [ ] **Step 3: README.** Structure per the packaging research: title and tagline; hero image (gallery screenshot) and a row of tile, draft, devices screenshots; three-sentence "what you get"; install for Claude Code (two lines, plus one-liner), `npx skills add moraneus/preview-first`, manual copy, and per-agent paths in `<details>` for Cursor, Codex, OpenCode, Windsurf, Gemini CLI; "How it works" with the human checkpoint drawn as a short numbered flow; what the contract contains with a short DESIGN.md excerpt; the knowledge graph in numbers (styles, palettes, pairings, motion patterns, devices, reference sites) as badges and a sentence on weekly refresh; device preview section; "Not an AI website generator" paragraph; contributing; licence. No em dashes, no emoji headers.
- [ ] **Step 4: CONTRIBUTING.md** (how to add a style, palette, pairing, device, reference site; run validator and tests; evidence rule) and CHANGELOG `0.1.0`.
- [ ] **Step 5: Run full test suite and validator, `claude plugin validate --strict .` if available, commit, tag `v0.1.0`, push, create a GitHub release with notes.**

```bash
uv run --with pytest pytest -q && uv run python3 skills/preview-first/scripts/validate_graph.py
git add -A && git commit -m "docs: README, contributing guide and 0.1.0 release notes"
git tag v0.1.0 && git push && git push --tags
gh release create v0.1.0 --title "preview-first 0.1.0" --notes-file CHANGELOG.md
```

---

## Execution notes

- Tasks 2, 3 then 4 to 6 are the foundation. Tasks 5 and 6 (content) can run in parallel with Task 7 and 8 once Task 4's ids exist. Tasks 9 to 12 depend on 7 and 8. Tasks 13 and 14 are independent of 9 to 12. Task 15 depends on all scripts existing. Task 16 is last.
- Content tasks (5, 6) are good candidates for subagents with the research reports as input and the validator as the acceptance test; script tasks with shared interfaces (7 to 12) are best done in one context to keep names consistent.
