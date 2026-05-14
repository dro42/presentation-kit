---
name: theme-authoring
description: Generate per-format presentation themes (Marp CSS, Beamer .sty, Slidev directory theme, pptx master) from a single brand.yaml — colors, fonts, logo, footer, layout variants kept in sync as the brand evolves. Use this skill whenever the user wants to create a brand identity for slides, port a theme to another format, build an institutional/corporate theme, generate a Beamer + Marp + Slidev + pptx set from one source, mentions "brand spec", "brand identity", "theme generator", "cross-format theme", "make my marp theme work in Beamer too", "I want our company colors in slides", or asks to standardize how their decks look across formats. Trigger eagerly when the user says "create a theme", "make a theme for X", "convert this theme to <format>", "I have these brand colors", "use our institutional palette", or shows a hex palette / brand guideline they want applied.
---

# theme-authoring Skill

This skill turns one **brand.yaml** spec into four format-specific themes:

| Format | Output | Used by |
|---|---|---|
| Marp | `<short>.css` (+ logo file) | `marp --theme-set <css>` |
| Beamer | `beamertheme<Pascal>.sty` | `\usetheme{<Pascal>}` |
| Slidev | `slidev-theme-<short>/` directory | `theme: ./slidev-theme-<short>` |
| pptx | `<short>-master.pptx` | `python3 generate.py --template <pptx>` |

The brand becomes the unit of reuse. Per-format themes become generated artifacts. When the brand evolves, regenerate; the four themes stay in lockstep.

Companion skills: this skill **produces** themes that the four format skills (`marp`, `beamer`, `slidev`, `pptx`) consume. It depends on `scripts/save-theme.sh` for `--save` persistence and uses `slide-overflow-check` for end-to-end smoke verification.

## When to use this skill vs. the format-specific skills

- **Use this skill** when you want **the same brand across multiple formats**, or when you'll likely re-generate as the brand evolves.
- **Edit the format's minimal starter directly** (`skills/marp/assets/themes/minimal.css`, `skills/beamer/assets/themes/beamerthemeMinimal.sty`, `skills/slidev/assets/themes/slidev-theme-minimal/`) when you need **one format only** and want full hand-control over the CSS/LaTeX/Vue.
- **Use a hand-built `.pptx` master** when the brand requires PowerPoint-specific affordances (custom layouts, master slide diagrams) the curated `baseline.pptx` doesn't model.

## When to read what

- Author a brand spec for the first time → stay here (Workflow A) and copy `examples/hcw-brand.yaml`.
- Full schema reference, every field, defaults → `references/brand-spec.md`.
- "What does each format honor / drop / approximate?" → `references/per-format-notes.md`.
- WCAG contrast model, palette design tips, why body-text is a hard error → `references/color-design.md`.
- See an end-to-end real example → `examples/hcw-brand.yaml` + `examples/README.md`.
- Test that token substitution works for your spec → `tests/test_snapshots.py` (47 snapshot assertions).
- Render the canonical 6-slide deck through your generated themes → `tests/smoke_render.py`.

The reference files are small on purpose. Read the one you need; don't preload all of them.

## Quick reference card

The minimum viable spec:

```yaml
version: 1
brand:    { name: "Demo", short: "demo" }
palette:  { text: "#000000", bg: "#FFFFFF", primary: "#005FB8" }
```

Generate all four formats:

```bash
python3 scripts/new_theme.py brand.yaml
# → ./themes/marp/demo.css
# → ./themes/beamer/beamerthemeDemo.sty
# → ./themes/slidev/slidev-theme-demo/
# → ./themes/pptx/demo-master.pptx
```

A realistic spec with colors + fonts + logo + variants is ~50 lines. See `examples/hcw-brand.yaml` (the Hochschule Campus Wien identity reproduced as a brand spec) for the full shape.

## Workflow A: Author a new brand spec

1. **Copy the HCW reference example as a starting point:**
   ```bash
   cp examples/hcw-brand.yaml my-brand.yaml
   cp examples/hcw-logo.svg ./   # or replace with your own
   ```
2. **Edit the four mandatory fields:**
   - `brand.name` — human-readable, used in generated comments
   - `brand.short` — slug-safe (`[a-z][a-z0-9-]{1,30}`), used in filenames and `\usetheme{}` discovery
   - `palette.text` — body text color (e.g. `"#1A1A1A"`)
   - `palette.bg` — body background color (usually `"#FFFFFF"`)
   - `palette.primary` — brand primary color (h1, links, brand surfaces)
3. **Optionally add the brand-color band:**
   - `palette.secondary` (h2, body emphasis)
   - `palette.primary_soft` (h3, subtitles)
   - `palette.accent` (decorative spot — set to `null` if your brand intentionally has none, e.g. a monochromatic identity)
4. **Optionally add the surface band:** `bg_alt` (code blocks), `rule` (dividers), `rule_soft` (table borders).
5. **Optionally add inverse pair:** `palette.inverse: { text: "#FFFFFF", bg: "primary" }` controls section-divider slides. The `bg: "primary"` form is a **token reference** — resolves to `palette.primary`. Token refs work anywhere a color is accepted.
6. **Optionally add typography, spacing, logo, footer, variants** — see `references/brand-spec.md` for the full menu. Every field has a sensible default; only the four mandatory fields above are required.
7. **Validate before generating:**
   ```bash
   python3 scripts/new_theme.py my-brand.yaml --validate-only
   ```
   Validation has two layers: schema (required fields, hex format, slug-safe identifiers, logo path resolves) and WCAG contrast (body-text pairs are hard errors; brand-color pairs are warnings). See `references/color-design.md` for why the split.
8. **Generate:**
   ```bash
   python3 scripts/new_theme.py my-brand.yaml
   ```

## Workflow B: Generate themes and use them

By default, generated themes land under `./themes/<format>/`. Use them in-place:

```bash
# Marp
marp my-deck.md --theme-set ./themes/marp/demo.css --pdf -o deck.pdf

# Beamer (copy .sty next to the .tex source)
cp ./themes/beamer/beamerthemeDemo.sty ./
latexmk -pdf my-deck.tex

# Slidev (copy theme dir into project root, reference from frontmatter)
cp -R ./themes/slidev/slidev-theme-demo ./
# slides.md frontmatter:  theme: ./slidev-theme-demo

# pptx
python3 ${CLAUDE_PLUGIN_ROOT}/skills/pptx/scripts/generate.py \
  --content my-deck.yaml \
  --template ./themes/pptx/demo-master.pptx \
  --output deck.pptx
```

Or persist into XDG user theme directories so every deck across the system can use them by name:

```bash
python3 scripts/new_theme.py my-brand.yaml --save
# Lands at:
#   ~/.local/share/presentation-kit/themes/marp/demo.css
#   ~/.local/share/presentation-kit/themes/beamer/beamerthemeDemo.sty
#   ~/.local/share/presentation-kit/themes/slidev/slidev-theme-demo/
#   ~/.local/share/presentation-kit/themes/pptx/demo-master.pptx
```

After save, the format skills' theme-resolution logic discovers them by name. Marp via `marp --theme-set ~/.local/share/.../demo.css`; Beamer via `\usetheme{Demo}` after copying alongside the `.tex`; Slidev by referencing the saved directory; pptx via `--template demo-master`.

## Workflow C: Regenerate when the brand changes

The whole point of the skill: when `palette.primary` changes from `#36566D` to `#2B4A6B`, you don't hand-edit four files. You edit `brand.yaml` and re-run.

```bash
# Edit one line:
sed -i.bak 's|primary:.*"#36566D"|primary: "#2B4A6B"|' my-brand.yaml

# Regenerate (use --save to also update XDG)
python3 scripts/new_theme.py my-brand.yaml --save

# All four themes now carry the new primary; existing decks pick it up on next render.
```

Diff the regenerated files against the previous version to confirm the change touched what you expected (and nothing else):

```bash
git diff themes/   # if you commit themes/
```

## Workflow D: Verify a generated theme end-to-end

Two layers of verification, mirroring the format skills' two-layer test gate:

### Layer 1 — token snapshot (cheap, runs in seconds, no rendering)

```bash
python3 -m unittest tests.test_snapshots -v
```

47 assertions: each format's generated artifact is checked for expected substring presence (CSS custom property names, `\definecolor{}` macros, theme XML `<a:srgbClr>` entries, package.json names, layout files copied verbatim). Catches the "tokens didn't make it through substitution" failure mode without any visual rendering.

### Layer 2 — canonical deck render (visual gate)

```bash
python3 -m tests.smoke_render
# Optionally restrict:
python3 -m tests.smoke_render --formats marp,beamer
python3 -m tests.smoke_render --keep    # leave the work dir for inspection
```

Renders the same 6-slide canonical fixture (title, bullets, section divider, code, table, inverse closing) through each format's renderer. PDF is then run through `slide-overflow-check`. Per-format renderers that aren't installed are **skipped** (not failed) with the install command surfaced — tooling absence is a real environment condition, not a regression.

Skip behavior:

- `marp` — requires `marp-cli` (`npm i -g @marp-team/marp-cli`)
- `beamer` — requires `latexmk` (MacTeX or TeX Live)
- `slidev` — requires `npx` + `playwright-chromium` (~150 MB; opt-in via `npx playwright install chromium`)
- `pptx` — requires `python-pptx` and `LibreOffice` for PDF conversion (`brew install --cask libreoffice`)

Anything that runs is real verification. Anything skipped is communicated explicitly in the result table.

## CLI reference

```
python3 scripts/new_theme.py <brand.yaml> [options]

Options:
  --formats marp,beamer,slidev,pptx   Subset (default: all four)
  --out <dir>                          Output directory (default: ./themes)
  --save                               Also persist into XDG user theme dirs
  --validate-only                      Validate schema + WCAG; write nothing
  --no-wcag                            Skip WCAG contrast checks entirely
  --no-fail-on-warn                    Exit 0 even if warnings fire
  --json                               Machine-readable output for CI gates
  --quiet                              Suppress per-format success lines

Exit codes:
  0  clean — generators succeeded; warnings only when --no-fail-on-warn
  1  schema/asset error, body-text WCAG hard fail, write error,
     OR warnings (downgrade with --no-fail-on-warn)
```

JSON output shape (for CI integration):

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "outputs": {
    "marp":   "./themes/marp/demo.css",
    "beamer": "./themes/beamer/beamerthemeDemo.sty",
    "slidev": "./themes/slidev/slidev-theme-demo",
    "pptx":   "./themes/pptx/demo-master.pptx"
  },
  "saved":   { "marp": "/Users/.../marp/demo.css", ... },
  "skipped": {}
}
```

## Brand spec model — the conceptual map

Three reusable concepts a brand spec author needs to internalize:

1. **Token references vs literal hex.** Anywhere a color is accepted, you can write `"#36566D"` (literal) or `"primary"` (refers back to `palette.primary`). Token refs let you express "the inverse background should be the brand primary" without duplicating the hex. Resolution is one-pass: refs are flattened during validation, then generators only see hex.
2. **Body-text vs brand-color contrast pairs.** WCAG splits into hard errors (text on bg, text on bg_alt, inverse.text on inverse.bg — these contain real reading text and gate generation) vs warnings (primary on bg, secondary on bg, etc. — used for headings or decoration where AA Large 3:1 is often the relevant threshold and "fails AA but looks fine" is a deliberate brand choice). Read `references/color-design.md` for the exact split and rationale.
3. **Sensible defaults.** Only `version`, `brand.{name,short}`, and `palette.{text,bg,primary}` are required. Everything else (`secondary` falls back to `primary`, `bg_alt` falls back to `bg`, `rule_soft` falls back to `rule`, etc.) has a documented default in `references/brand-spec.md`. Author the four mandatory fields first; add granularity only when the visual result demands it.

## Common pitfalls

- **`brand.short` invalid** — must match `[a-z][a-z0-9-]{1,30}`. Pascal-cased names (`HCW`) or names with spaces fail schema validation. The Pascal form for `\usetheme{}` is derived automatically (`hcw` → `Hcw`).
- **Body-text WCAG fails generation** — exit 1 with an error like `palette.text on palette.bg contrast 1.27:1 is below WCAG AA body-text threshold 4.5:1`. This is by design — body-text contrast is the one accessibility metric we don't compromise on. Use `--no-wcag` to skip if you genuinely need to (rare).
- **Brand-color WCAG fails as warning, but exits 1 anyway** — also by design. Pass `--no-fail-on-warn` to downgrade. Only do this when you've consciously accepted the contrast trade-off.
- **`palette.accent: null` produces no accent CSS rules** — explicitly setting null is correct and matches HCW's monochromatic identity. Omitting the key has the same effect. Setting `accent: "#FFFFFF"` (which would be invisible) is a brand bug not detected by validation.
- **Logo path resolves relative to brand.yaml location**, not cwd. If your `brand.yaml` is at `/proj/branding/brand.yaml` and `logo.path: "./logo.svg"`, the generator looks at `/proj/branding/logo.svg`. The marp generator copies the logo file alongside the generated CSS so the relative URL holds at render time.
- **Beamer base font size is discrete (10/11/12pt)** — `typography.base_size_pt: 24` is mapped to nearest with a warning. Override via `overrides.beamer.base_font_size: "11pt"` if the warning is noisy.
- **Slidev theme directory must be co-located with `slides.md`** — the frontmatter `theme: ./slidev-theme-demo` is resolved relative to the deck. Either copy the generated directory in, or `--save` and reference the XDG path explicitly.
- **pptx generator skipped silently when `python-pptx` isn't installed** — surfaces the install command (`pip install python-pptx`) in the `skipped` field of the JSON output and in the human report. Don't auto-install.

## Quality checklist before delivering

- [ ] `--validate-only` exits 0 (schema clean, body-text WCAG clean).
- [ ] All four formats generated successfully (or skipped with a clear reason — `python-pptx` missing, etc.).
- [ ] Token snapshot tests pass: `python3 -m unittest tests.test_snapshots`.
- [ ] Smoke render exits 0 for every format whose renderer is installed: `python3 -m tests.smoke_render`.
- [ ] Eyeballed at least one rendered PDF (Marp or Beamer or pptx) — the brand color shows on h1/title, the inverse slide is inverted, the logo appears.
- [ ] If `--save` was used: the four expected files exist under `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/{marp,beamer,slidev,pptx}/` with format-discoverable names (`<short>.css`, `beamertheme<Pascal>.sty`, `slidev-theme-<short>/`, `<short>-master.pptx`).
- [ ] Brand-color warnings reviewed — either they're acceptable for the intended decorative use, or the palette has been adjusted to clear AA Large (3:1).
- [ ] `brand.yaml` committed (or otherwise stored) alongside the generated themes — the spec is the source of truth, the generated artifacts are derivatives.
