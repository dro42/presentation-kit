# Brand spec — full reference (schema v1)

The brand spec is YAML. One file. Five top-level sections (`brand`, `palette`, `typography`, `logo`, `footer`, `variants`, plus `version`). Generators consume the spec and project it onto the four formats; this document covers every field with its default, type, and an example.

## Conventions

- **Hex colors** use the 6-digit `#RRGGBB` form. Three-digit shorthand (`#abc`) is rejected by the validator.
- **Token references** appear anywhere a color is accepted: write `"primary"` (string, no `#`) instead of a hex literal to refer back to `palette.primary`. Resolution is one-pass during validation; references to references work as long as the chain terminates in a hex literal.
- **Optional fields** can be omitted entirely (the documented default applies) or set to `null` (treated as "explicitly unset" — most commonly used for `palette.accent` to signal a monochromatic identity).
- **Unknown top-level keys** are warned about, not errored — so the spec can grow with new fields in a backwards-compatible way during the v1 series.

## `version` (REQUIRED)

```yaml
version: 1
```

Type: positive integer. Mandatory. The validator rejects specs without a `version` field. A spec declaring `version: 2` parses with a `version_future` warning — fields the v1 validator doesn't know are silently ignored.

## `brand` (REQUIRED)

```yaml
brand:
  name:  "Hochschule Campus Wien"      # human-readable; used in generator comments
  short: "hcw"                          # slug-safe; matches [a-z][a-z0-9-]{1,30}
```

| Field | Required? | Default | Notes |
|---|---|---|---|
| `name` | yes | — | Free-form. Surfaces in the generated CSS / .sty header comments. |
| `short` | yes | — | Slug. Used in filenames (`<short>.css`, `<short>-master.pptx`), Slidev theme dir name (`slidev-theme-<short>`), Pascal-cased for Beamer (`beamertheme<Pascal>.sty` and `\usetheme{<Pascal>}`). The Pascal form is derived automatically — `hcw` → `Hcw`, `my-co` → `MyCo`. |

## `palette` (REQUIRED)

```yaml
palette:
  # ── Body-text contrast pairs (HARD-error gated by WCAG AA 4.5:1) ──
  text: "#1A1A1A"
  bg:   "#FFFFFF"

  # ── Brand color band (WARN-gated by WCAG AA / Large) ──
  primary:      "#36566D"   # required — h1, brand surfaces, links
  secondary:    "#4B5059"   # h2, body emphasis
  primary_soft: "#7897AC"   # h3, subtitles
  accent:       null        # decorative spot; null = monochromatic identity

  # ── Surface / structural tokens ──
  bg_alt:    "#F1F4F7"      # code-block bg, blockquote bg
  rule:      "#4B5059"      # divider lines, h1 underline
  rule_soft: "#DDE3E8"      # table cell rules, footer separator

  # ── Inverted variant (used by section-divider slides) ──
  inverse:
    text: "#FFFFFF"
    bg:   "primary"          # token reference → palette.primary
```

### Required keys

| Field | Default | Use |
|---|---|---|
| `text` | — | Body text color. Must reach 4.5:1 against `bg`. |
| `bg` | — | Body background. Usually `#FFFFFF`. |
| `primary` | — | Brand primary; gets emitted as `--primary-color`, `BrandPrimary`, accent1. |

### Optional brand-color band (each falls back to `primary` if absent)

| Field | Default | Use |
|---|---|---|
| `secondary` | `primary` | h2, emphasis. |
| `primary_soft` | `primary` | h3, subtitles, soft brand accents. |
| `accent` | `null` | Decorative spot. Set to `null` for monochromatic brands; the marp generator omits the `--accent-color` rule entirely when null. |

### Optional surface tokens

| Field | Default | Use |
|---|---|---|
| `bg_alt` | `bg` | Code-block bg, blockquote bg. Body text contrast against this is also a hard WCAG check. |
| `rule` | `primary` | Solid divider lines, h1 underline. |
| `rule_soft` | `rule` | Table cell rules, footer separator. |

### `palette.inverse` (optional)

Sub-mapping with `text` and `bg` keys. Drives section-divider slides ("invert" in Marp, `\section{}` styling in Beamer, `section` layout in Slidev, Section Header in pptx).

| Field | Default | Use |
|---|---|---|
| `inverse.text` | `"white"` (resolves to `#FFFFFF`) | Foreground on inverse slides. |
| `inverse.bg` | `"primary"` (resolves to `palette.primary`) | Background on inverse slides. The pair must reach 4.5:1 contrast — body text appears on inverse slides too. |

The `inverse` resolver knows two synthetic tokens: `"white"` (`#FFFFFF`) and `"black"` (`#000000`) in addition to the palette names.

## `typography` (optional)

```yaml
typography:
  body:     ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"]
  headings: ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"]
  mono:     ["SF Mono", "Menlo", "Consolas", "monospace"]
  base_size_pt: 24

  code:
    bg:                "bg_alt"
    border_color:      "primary"
    border_width_px:   3
    font_size_ratio:   0.72

  table:
    header_color:           "primary"
    header_border_width_px: 2
    cell_border_color:      "rule_soft"
```

### Font stacks

`body`, `headings`, `mono` are CSS-style font-family lists. The first entry is the preferred font; the rest are fallbacks (always include a generic family at the end).

If `fc-list` is on PATH, the validator warns when the primary body font isn't installed. If it's not on PATH, the check is skipped silently — the warning is best-effort, never a hard error.

### `typography.base_size_pt`

Default: `24`. Sets the body text base size in points (CSS px ≈ PDF pt at 1:1 in marp/slidev). For Beamer, mapped to nearest LaTeX `\documentclass[Npt]` (10/11/12pt) with a warning if rounding > 1pt. Override via `overrides.beamer.base_font_size`.

### `typography.code` (sub-mapping)

| Field | Default | Use |
|---|---|---|
| `code.bg` | `"bg_alt"` | Code block background. |
| `code.border_color` | `"primary"` | Left border / accent rule. |
| `code.border_width_px` | `3` | Border thickness in px. |
| `code.font_size_ratio` | `0.72` | Code font size relative to base body size (0.72 = ~17pt for base_size_pt: 24). |

### `typography.table` (sub-mapping)

| Field | Default | Use |
|---|---|---|
| `table.header_color` | `"primary"` | Header row fg color (or border-bottom emphasis depending on format). |
| `table.header_border_width_px` | `2` | Header border thickness. |
| `table.cell_border_color` | `"rule_soft"` | Cell separator. |

## `spacing` (optional)

```yaml
spacing:
  slide_padding:
    top:    110     # leaves room for top-anchored logo
    right:  70
    bottom: 60      # tight; bump if slide-overflow-check flags
    left:   70
```

Applies to Marp/Slidev `padding` and pptx slide-master margins. Beamer's frame margins are theme-controlled and only partially honor this (see `per-format-notes.md`).

If `logo.position` is top-anchored and `slide_padding.top` is unset, the marp generator bumps top to at least 110px to clear the logo.

## `logo` (optional)

```yaml
logo:
  path: "./hcw-logo.svg"     # resolved relative to brand.yaml location
  width_px: 160
  position: "top-right"      # top-right | top-left | bottom-right | bottom-left | none
  offset:
    top:   35
    right: 50
```

| Field | Default | Use |
|---|---|---|
| `path` | — | Required if `logo` mapping present. Resolved relative to brand.yaml location, NOT cwd. |
| `width_px` | `160` | Rendered width. Format-specific scaling applies (pptx converts to EMU; Beamer to TeX pt). |
| `position` | `"top-right"` | One of `top-right`, `top-left`, `bottom-right`, `bottom-left`, `none`. |
| `offset.{top,right,bottom,left}` | varies | Pixel offset from the chosen anchor. Generators read only the two relevant axes (`top` + `right` for `top-right`). |

The marp generator copies the logo file alongside the generated CSS so `background-image: url('hcw-logo.svg')` resolves at render time. Same pattern in Slidev. Beamer copies the logo into the theme directory; pptx embeds via `python-pptx`.

**Beamer + SVG**: pdfLaTeX can't ingest SVG. The Beamer generator looks for a sibling raster (`hcw-logo.png`) next to the SVG; if absent, the generated theme references the raster anyway and you'll need to convert manually (`rsvg-convert hcw-logo.svg -o hcw-logo.png`).

## `footer` (optional)

```yaml
footer:
  text:   "© {{year}} {{author}}"
  author: "Andreas Drozd"
```

Templating: `{{year}}` resolves at generation time to the current year (Anthropic-style 4-digit year), `{{author}}` resolves to `footer.author`, `{{date}}` resolves to ISO `YYYY-MM-DD`. These are simple text substitutions, not full template engines — only the three documented placeholders are recognized.

## `variants` (optional)

A closed enum of three known variants: `title`, `section`, `two_column`. Unknown keys produce a `variant_unknown` warning.

```yaml
variants:
  title:
    enabled: true
    align: "left"
    h1_size: "3.0em"
  section:
    enabled: true
    bg: "primary"
    fg: "white"
  two_column:
    enabled: true
    column_count: 2
    column_gap_rem: 2.5
```

### `variants.title` (hero / lead slide)

| Field | Default | Use |
|---|---|---|
| `enabled` | `true` | Set false to omit the variant. |
| `align` | `"center"` | `left` / `center` / `right`. |
| `h1_size` | `"3.0em"` | CSS font-size string. |

### `variants.section` (section-divider slide)

| Field | Default | Use |
|---|---|---|
| `enabled` | `true` | Set false to omit. |
| `bg` | `"primary"` | Token ref or hex. Section-divider background. |
| `fg` | `"white"` | Foreground text color. Combined with `bg` should clear AA 4.5:1. |

### `variants.two_column`

| Field | Default | Use |
|---|---|---|
| `enabled` | `true` | Set false to omit. |
| `column_count` | `2` | CSS `column-count`. |
| `column_gap_rem` | `2.5` | Gap between columns in rem. |

## `overrides` (optional, per-format escape hatches)

```yaml
overrides:
  beamer:
    base_font_size: "11pt"   # explicit LaTeX class option; overrides typography.base_size_pt mapping
  pptx:
    aspect_ratio: "16:9"     # explicit slide-master aspect ratio override
```

This section exists for cases where the cross-format token surface can't express a format-specific need. Use sparingly; if you find yourself reaching for `overrides` often, consider whether the field should become a first-class brand-spec key.

## Minimal valid spec

```yaml
version: 1
brand:    { name: "Demo", short: "demo" }
palette:  { text: "#000000", bg: "#FFFFFF", primary: "#005FB8" }
```

Three lines beyond the version. Everything else falls back to documented defaults. Generates four valid themes; the marp/slidev/pptx outputs are visually plain but functionally complete; Beamer's output is identical to `beamerthemeMinimal.sty` retinted with `#005FB8`.

## Validation reference

| Code | Severity | Triggers |
|---|---|---|
| `version_missing` | error | No `version` field in spec. |
| `version_invalid` | error | `version` is not a positive integer. |
| `version_future` | warn | `version > 1`. |
| `brand_missing` | error | No `brand` section. |
| `brand_name_missing` | error | `brand.name` empty. |
| `brand_short_missing` | error | `brand.short` empty. |
| `brand_short_invalid` | error | `brand.short` doesn't match `[a-z][a-z0-9-]{1,30}`. |
| `palette_missing` | error | No `palette` section. |
| `palette_required` | error | Required `text`/`bg`/`primary` missing. |
| `palette_hex_invalid` | error | Color value not `#RRGGBB`, not `null`, not a known token. |
| `palette_inverse_unresolved` | error | `inverse.text`/`inverse.bg` token ref doesn't resolve. |
| `typography_invalid` | error | `typography` not a mapping. |
| `font_stack_invalid` | error | font field not a list of strings. |
| `font_missing` | warn | Primary body font not found by `fc-list`. |
| `spacing_invalid` | error | `spacing` not a mapping. |
| `spacing_value_invalid` | error | Padding value not numeric. |
| `logo_invalid` | error | `logo` not a mapping. |
| `logo_not_found` | error | Resolved logo path doesn't exist. |
| `logo_position_invalid` | error | Position not one of the 5 valid values. |
| `footer_invalid` | error | `footer` not a mapping. |
| `variants_invalid` | error | `variants` not a mapping. |
| `variant_unknown` | warn | Variant name not in `{title, section, two_column}`. |
| `wcag_body_fail` | error | Body-text contrast pair < 4.5:1. |
| `wcag_brand_warn` | warn | Brand-color contrast against bg < 4.5:1. |
| `unknown_key` | warn | Unknown top-level key. |
