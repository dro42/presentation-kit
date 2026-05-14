# Per-format notes — what each format honors, drops, or approximates

The brand spec is a single source of truth. Each generator projects it onto its target format. Most fields project cleanly; a few don't, because of constraints in the underlying format. This document is the honest map of where the projection is exact, partial, or impossible — so you know what to expect before opening the rendered deck.

## The token-honor table

| Brand spec field | Marp | Beamer | Slidev | pptx |
|---|---|---|---|---|
| `palette.text` / `bg` | ✓ CSS body | ✓ `\setbeamercolor{normal text}` | ✓ CSS `--text-color` / body bg | ✓ theme XML `dk1` / `lt1` |
| `palette.primary` | ✓ `--primary-color` | ✓ `\definecolor{BrandPrimary}` | ✓ `--brand-primary` | ✓ theme XML `accent1` |
| `palette.secondary` | ✓ `--secondary-color` | ✓ `BrandSecondary` | ✓ `--brand-secondary` | ✓ theme XML `accent2` |
| `palette.primary_soft` | ✓ `--primary-soft` | ✓ `BrandSoft` | ✓ `--brand-soft` | ✓ theme XML `accent3` |
| `palette.accent` (when set) | ✓ `--accent-color` | ✓ `BrandAccent` | ✓ `--brand-accent` | ✓ theme XML `accent4` (patched) |
| `palette.accent: null` | ✓ rule omitted | ✓ macro omitted | ✓ var omitted | ✓ accent4 = `8064A2` (Office default; visually neutral) |
| `palette.bg_alt` | ✓ code/blockquote bg | ✓ `BrandBgAlt` (listings bg) | ✓ var | partial — pptx code rendering is image-based; bg_alt unused |
| `palette.rule` / `rule_soft` | ✓ borders | ✓ `\setbeamercolor{separation line}` | ✓ vars | partial — pptx tables editable per-cell, not theme-driven |
| `palette.inverse.text` / `bg` | ✓ `section.invert` | ✓ `\AtBeginSection` template | ✓ `section` layout | ✓ `lt2` / `dk2` (Section Header layout) |
| `typography.body` (font stack) | ✓ `font-family` | ✓ `\setsansfont{}` if XeLaTeX/LuaLaTeX; `\renewcommand{\sfdefault}` if pdfLaTeX | ✓ `font-family` | ✓ theme XML `<a:latin>` minorFont |
| `typography.headings` | ✓ `font-family` on h1-h3 | ✓ `\setbeamerfont{frametitle}` | ✓ `font-family` | ✓ theme XML majorFont |
| `typography.mono` | ✓ `font-family` on `code`/`pre` | ✓ `\setmonofont{}` (XeLaTeX) | ✓ `font-family` | partial — pptx mono only inside code-block image render |
| `typography.base_size_pt` | ✓ as-is | partial — quantized to 10/11/12pt with warning | ✓ as-is (Slidev uses px under the hood) | ✓ as theme default; per-deck overridable |
| `typography.code.bg` | ✓ | partial — depends on listings package config | ✓ | ✗ pptx code render is image-based |
| `typography.code.border_color` / `width` | ✓ left border | ✓ `\lstset{frame=L,rulecolor=}` | ✓ | ✗ |
| `typography.table.header_color` | ✓ | ✓ via `\rowcolors` | ✓ | partial — manual edit per-cell |
| `typography.table.cell_border_color` | ✓ | ✓ | ✓ | partial |
| `typography.table.stripe_bg` (if set) | ✓ | ✓ via `\rowcolors{2}{stripe}{}` | ✓ | partial |
| `spacing.slide_padding` | ✓ `padding` on `section` | partial — Beamer's frame margins are theme-controlled | ✓ canvas padding | ✓ via slide-master margins |
| `logo.path` | ✓ `background-image` | ✓ `\addtobeamertemplate{frametitle}{}{...includegraphics...}` | ✓ background-image | ✓ image placeholder per layout |
| `logo.position` | ✓ background-position | ✓ tikz overlay coordinates | ✓ background-position | ✓ via xfrm in master |
| `logo` (SVG file) | ✓ via CSS | ✗ pdfLaTeX needs raster sibling (`logo.png`); LuaLaTeX/XeLaTeX with `svg` package can read SVG | ✓ via CSS | ✗ python-pptx wants raster (PNG/JPG); SVG ignored |
| `footer.text` (with `{{year}}` etc.) | ✓ marp footer | ✓ `\setbeamertemplate{footline}` | ✓ slidev footer | ✓ footer placeholder per layout |
| `variants.title` | ✓ `section.lead` | ✓ `\titlepage` styling | ✓ `cover` layout | ✓ Title Slide layout |
| `variants.section` | ✓ `section.invert` | ✓ `\AtBeginSection[]` divider | ✓ `section` layout | ✓ Section Header layout |
| `variants.two_column` | ✓ `section.two-column` | ✓ via `\columns` env | ✓ `two-cols` layout | ✓ Two Content layout |

✓ = projected exactly. partial = projected approximately; the surface is there but full fidelity needs hand-tuning. ✗ = not projected; format constraint.

## Format-by-format details

### Marp

The cleanest target — CSS custom properties map 1:1 to brand spec tokens. Generated CSS is structurally identical to `skills/marp/assets/themes/minimal.css`, with `${primary}` etc. substituted. Conditional blocks (lead, invert, two-column) are emitted only when `variants.<name>.enabled` is true.

**What you get:** a single `<short>.css` file plus the logo file copied alongside. Reference via `marp deck.md --theme-set <css>` or `theme: <short>` in deck frontmatter (after registration).

**Caveats:**
- Custom fonts via `@font-face` don't survive PDF export. Stick to system fonts in `typography.body[0]`.
- The `--accent-color` CSS variable is omitted entirely when `palette.accent: null` (intentional — monochromatic identities don't carry an unused variable).

### Beamer

Token surface is `\definecolor{Brand<Token>}{HTML}{...}` macros at the top of `beamertheme<Pascal>.sty`. The Pascal-cased identifier is derived from `brand.short`: `hcw` → `Hcw`, `my-co` → `MyCo`. The deck references the theme via `\usetheme{Hcw}` (matches the Pascal form, NOT the filename).

**What you get:** `beamertheme<Pascal>.sty` plus the logo (raster preferred). Copy alongside the `.tex` source before compiling — Beamer needs to find it on `TEXINPUTS`.

**Caveats:**
- **Font sizing is discrete.** Beamer's base font size is `\documentclass[Npt]{beamer}` where N ∈ {10, 11, 12}. `typography.base_size_pt: 24` maps to nearest with a warning. Override via `overrides.beamer.base_font_size: "11pt"`.
- **SVG logos need a raster sibling.** pdfLaTeX (the default driver) can't ingest SVG. Generate via `rsvg-convert hcw-logo.svg -o hcw-logo.png` and place alongside.
- **Custom fonts require XeLaTeX or LuaLaTeX.** pdfLaTeX falls back to Computer Modern + `\renewcommand{\sfdefault}`. The theme works either way, but font-stack fidelity is highest with XeLaTeX/LuaLaTeX (`latexmk -xelatex` or `-lualatex`).
- **Frame margins are theme-controlled.** `spacing.slide_padding` only partially applies; Beamer's `\setbeamersize{text margin left=...}` is the lever, but the bundled theme uses Madrid's defaults.

### Slidev

Token surface is CSS custom properties (same as Marp) plus a `package.json` declaring `slidev.defaults.fonts`. The generator walks `templates/slidev-theme/`, substitutes `.tmpl` files, copies `.vue` layouts verbatim. The output is a directory ready to be referenced as `theme: ./slidev-theme-<short>`.

**What you get:** `slidev-theme-<short>/` directory containing `package.json`, `styles/index.css`, and the `layouts/` directory (cover, section, default, etc., copied from the bundled minimal). Logo file is also copied in.

**Caveats:**
- The frontmatter `theme:` value must be a relative path (`./slidev-theme-<short>`) or an npm package name. Using `theme: <short>` alone makes Slidev try to resolve `slidev-theme-<short>` from npm (404).
- PDF export requires Playwright + Chromium (~150 MB). First-run install: `npx playwright install chromium`.
- PPTX export is experimental in Slidev — formatting drift is normal. If pptx is the target, generate from the brand spec via the pptx generator instead.

### pptx

The most constrained target. The generator loads a curated `templates/pptx/baseline.pptx` (5 layouts: Title / Title+Content / Section Header / Two Content / Image+Caption) and patches:

1. **Theme XML colors** via `theme1.xml` — `dk1`/`lt1`/`dk2`/`lt2` (text/bg + inverse text/bg) and `accent1`-`accent4` (primary/secondary/primary_soft/accent).
2. **Theme XML fonts** — `<a:majorFont>`/`<a:minorFont>` `<a:latin>` typeface for headings/body.
3. **Logo** — image placeholder on the master + every layout, replaced via `python-pptx`.
4. **Footer text** — applied to master footer placeholder, inherited by layouts.

**What you get:** `<short>-master.pptx` ready to be passed to `skills/pptx/scripts/generate.py --template <pptx>`.

**Caveats:**
- **`palette.accent: null` ≠ "no accent4 slot"**. The theme XML always has 6 accent slots (accent1-accent6). When `accent` is null, accent4 falls back to PowerPoint's Office default (`8064A2`). It's visually unobtrusive (a soft purple) but technically present. If you really need accent4 to be empty, edit the master in PowerPoint after generation.
- **Code blocks render as embedded images, not native text.** This is a python-pptx + PowerPoint limitation, not a generator choice. `typography.code.bg` and friends are unused for pptx.
- **Tables are added per-cell**, not theme-driven. `typography.table.header_color` is honored at generation time when the deck-yaml declares a table layout, but you can't change the brand later and have existing decks pick it up automatically.
- **SVG logos are dropped.** python-pptx wants raster (PNG/JPG/EMF). Provide a PNG sibling alongside the SVG.
- **The curated baseline `baseline.pptx` is 5 layouts.** PowerPoint's full standard is 11. If the deck-yaml uses a layout name not in the master, the pptx generator falls back to layout index 1 (Title and Content). Verify available layouts via:
  ```bash
  python3 -c "from pptx import Presentation; p = Presentation('hcw-master.pptx'); [print(l.name) for l in p.slide_layouts]"
  ```

## When projection isn't enough

If the per-format result needs more than the spec can express:

- **For one-off tweaks** to a single format, edit the generated artifact directly (and don't regenerate, or you'll lose the edit).
- **For format-specific persistent tweaks**, use the `overrides.<format>` escape hatch in the brand spec (e.g. `overrides.beamer.base_font_size: "11pt"`).
- **For brand-wide changes that cross formats**, edit `brand.yaml` and regenerate. This is the common case; the spec is designed for it.
- **For format-specific affordances that don't fit cross-format**, fall back to editing that format's minimal starter directly. The brand spec exists for the 80 % of cases where consistency matters; for the 20 % where one format needs a deep custom layout, the per-format theming workflow is still available.

## Verification gates

After generating, before delivering:

1. **Token snapshot** — `python3 -m unittest tests.test_snapshots`. Confirms substitution worked. ~2 sec, no rendering.
2. **Smoke render** — `python3 -m tests.smoke_render`. Renders the canonical 6-slide deck through each available toolchain. ~30 sec for marp+beamer; longer for slidev (Playwright) and pptx (LibreOffice).
3. **Visual eyeball** — open at least one rendered PDF and confirm: brand color shows on h1, inverse divider is inverted, logo appears, fonts are right.

The snapshot test is the cheap continuous-integration gate. The smoke render is the per-release / per-brand-change gate. The visual eyeball is what catches "the colors are right but the visual hierarchy is broken" — the one failure mode no automated check finds.
