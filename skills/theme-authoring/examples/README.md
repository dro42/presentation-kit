# Examples

Reference brand specs you can use as starting points for your own.

## `hcw-brand.yaml` — Hochschule Campus Wien

Reproduces the HCW visual identity as a brand spec:

- Petrol-blue primary (`#36566D`) + slate-grey secondary (`#4B5059`) + soft tint (`#7897AC`).
- Monochromatic — `accent: null` (HCW intentionally uses no yellow).
- Logo top-right, 160 px wide, 35 px / 50 px offset.
- Helvetica Neue stack, base 24 pt.
- Three layout variants enabled: `title` (left-aligned hero), `section` (inverse divider), `two_column`.

### Generate from this example

```bash
# All four formats into ./themes/
python3 ../scripts/new_theme.py hcw-brand.yaml

# Just marp + beamer, custom out dir
python3 ../scripts/new_theme.py hcw-brand.yaml --formats marp,beamer --out /tmp/hcw/

# Validate only
python3 ../scripts/new_theme.py hcw-brand.yaml --validate-only

# Persist into XDG dirs (so other decks can use them by name)
python3 ../scripts/new_theme.py hcw-brand.yaml --save
```

### Verify the result

```bash
# Token snapshot — fast, no rendering, ~2 sec
python3 -m unittest tests.test_snapshots -v

# Full render of the canonical 6-slide fixture through each available toolchain
python3 -m tests.smoke_render

# Restrict to formats whose renderers you have installed
python3 -m tests.smoke_render --formats marp,beamer
```

## `hcw-logo.svg` / `hcw-logo.png`

The HCW logo in two formats. The marp/slidev generators consume the SVG via CSS `background-image`. The Beamer generator (when used with pdfLaTeX) and pptx generator (always) require the PNG raster — both are shipped here so the example works out of the box.

Replace these with your own logo when authoring a custom brand spec. The marp generator copies the logo file alongside the generated CSS so the relative path (`./hcw-logo.svg`) holds at render time.

## Authoring a new brand spec

1. Copy `hcw-brand.yaml` to a new name (e.g. `mycompany-brand.yaml`).
2. Edit the four mandatory fields: `brand.name`, `brand.short`, `palette.text`, `palette.bg`, `palette.primary`.
3. Optionally edit the rest. See `../references/brand-spec.md` for the full schema.
4. Run `python3 ../scripts/new_theme.py mycompany-brand.yaml --validate-only` to confirm the schema is clean.
5. If validation passes, generate.

The HCW spec is a complete real-world example of a monochromatic identity with full typography + variants + logo. Use it as a structural template, not as visual inspiration for your own brand.
