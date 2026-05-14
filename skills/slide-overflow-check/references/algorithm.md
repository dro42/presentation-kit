# Algorithm reference — `slide-overflow-check`

Detailed notes on the footer-baseline detection heuristic, edge cases, and
threshold tuning. Read this when:

- The default `--footer-clearance 20` triggers false positives on a
  particular theme and you need to know what to dial.
- A deck with a clearly-clipped slide reports clean and you need to
  diagnose where the heuristic missed.
- You are considering swapping the pdftotext backend for PyMuPDF (the v2
  upgrade path).

## Why a clearance margin exists

The naive approach would treat the footer text's top y-coordinate as the
boundary above which body text must end. That is wrong for any theme that
puts a *visual band* (background fill, top rule, padding) above the footer
text.

Concrete example — the HCW Marp theme used to motivate this skill:

```css
footer {
  color: var(--hcw-secondary);
  font-size: 0.55em;
  border-top: 1px solid var(--hcw-rule-soft);
  padding-top: 0.4em;
}
```

The footer text sits at, say, y=510 on a 540pt-tall slide. But the visual
band — `border-top` plus `padding-top` plus the small font's ascent — starts
roughly 25-30pt higher, around y=485. A blockquote ending at y=505 is
visually inside the band and gets sliced, but its bbox y_max is *above* the
footer text's y_min. A footer-text-anchored algorithm would pass it.

`safe_zone_top = footer_text_top - footer_clearance` adds back a configurable
margin to model the band height. Default 20pt is conservative for typical
themes and catches the HCW bug; users tune per-theme as needed.

## Why position-based (not text-based) clustering

A naive cluster key like `(text, rounded_y)` would put the page-number
words `1`, `2`, `3`, … into separate clusters, missing the fact that they
all occupy the same screen real estate. We cluster by quantized
`(x_min, y_min)` position with a 10pt bucket. The bucket size matters:
too small and aliased text positions split clusters; too large and unrelated
positions collide. 10pt was chosen empirically — typical page-number rails
land within ~2pt across slides, well inside one bucket.

## Why footer clusters must be band-exclusive

If a deck has a recurring overflow at a stable position (e.g., every slide's
last bullet drops 5pt below the safe zone at the same x-coordinate because
all slides use the same template), the position passes the 60% coverage
threshold and would get classified as "the footer" — which would silence
the very issue we're trying to detect.

The fix: a position can only be a footer cluster if it appears *exclusively*
in the bottom 15% across all its pages. If the same `(x_band, y_band)` shows
up in body content (top 85%) on any page, it's not the footer — it's a
content position that happens to also appear in the footer zone on some
pages.

## Why the coverage denominator excludes non-paginated pages

Marp's `_paginate: false` (and similar in other tools) suppresses the page
number and footer on title / divider slides. A 6-slide deck with 2 such
slides would have footer text on only 4 pages — coverage is 4/6 ≈ 67% if
denominator is total pages, but the *intended* signal is 4/4 = 100%. Using
total-pages as the denominator would push borderline decks below the 60%
threshold and trigger the no-footer fallback path, masking real overflow.

The denominator is therefore the count of pages with at least one word in
the bottom 15% — i.e., pages that actually have a footer to cluster.

## Threshold tuning playbook

Symptoms → flag to tune:

| Symptom | Likely cause | Tuning |
|---|---|---|
| Real overflow not caught (text visibly clipped, exit 0) | clearance too small for theme's band | raise `--footer-clearance` to 30, 40, or higher |
| False positives — clean deck reports footer collisions | clearance too large for theme | lower `--footer-clearance` to 10 or 5 |
| "no recurring footer detected" on a deck that clearly has one | coverage threshold not met (decks with many divider slides) | lower `--footer-coverage-pct` to 0.4 or 0.3 |
| A repeating annotation at the slide bottom is ignored as footer when it shouldn't be | the band-exclusive constraint isn't strict enough — the annotation appears only in the bottom band | this is correct behavior; the annotation is being treated as part of the footer surface. Move it out of the bottom 15% if it should count as body content. |
| Float false positives (`xMax 720.00003 > 720.0`) | epsilon too small | raise `--epsilon` to 1.0 |

Once a per-theme tuning is found, document the chosen flags in the deck's
build script or as a comment near the render command — the defaults are not
universal.

## Known limitations

1. **Image overflow is invisible.** `pdftotext` only emits text bboxes.
   Figures bleeding off the canvas are missed. The v2 upgrade path uses
   PyMuPDF (`fitz.Page.get_images()` + `fitz.Page.get_image_rects()`) to
   pull image bboxes; the algorithm's overflow-flagging step then applies
   uniformly to text and images. Defer until the user reports image-overflow
   bugs in real decks.

2. **Outlined or rasterized text is invisible.** Some Beamer compiles outline
   fonts to glyph paths; some pptx → PDF conversions rasterize entire slides.
   These pages emit zero `<word>` elements and surface as the
   `not_analyzable` warn. Manual visual review is the only fallback.

3. **Rotated or transformed text** has axis-aligned bboxes that may not
   reflect the visual extent. Rare in slide decks; not addressed.

4. **Per-slide background images that contain text** (a screenshot of a
   terminal pasted as a PNG) are treated as images — see (1).

5. **The clearance heuristic is text-anchored.** A theme with a tall
   colored band but no footer text inside the band would fool the algorithm
   into treating the page edge as the boundary. The PyMuPDF v2 path can
   detect the band edge from the rendered raster (scan rows for color
   discontinuity) and remove the heuristic dependency.

## Known upstream issues

### poppler 26.x: `pdftotext -bbox-layout` SIGABRT on some Beamer PDFs

Observed on poppler 26.04.0 (April 2026 release): `pdftotext -bbox` and
`-bbox-layout` modes throw `libc++abi: std::out_of_range: basic_string` and
crash (exit -6) on PDFs produced by certain Beamer themes (notably ones
using `cm-super` Type 1 fonts with specific encoding subsets). Plain
`pdftotext` (no `-bbox*`) works fine on the same PDFs — the bug is in the
bbox-emission code path.

The script surfaces the crash with a clear error message. **Workarounds**:

1. **Re-render the PDF with embedded fonts converted to OpenType.** In Beamer,
   add `\usepackage[T1]{fontenc}\usepackage{lmodern}` and recompile.
2. **Wait for poppler 26.05+.** Track the upstream bug at
   <https://gitlab.freedesktop.org/poppler/poppler/-/issues>.
3. **Manual visual review** for the affected deck until the upstream is fixed.

This bug does NOT affect Marp- or Slidev-produced PDFs (Chromium-rendered),
which is the primary use case. It only impacts a subset of Beamer outputs.

## Future work (v2)

1. **PyMuPDF backend.** Adds image-bbox awareness, enables raster-based
   band detection for theme-agnostic accuracy. Cost: `pip install PyMuPDF`
   (~5MB native binaries). Gate behind a `--backend pymupdf` flag so the
   stdlib path stays the default.

2. **Source-side annotation.** Allow `<!-- slide-overflow-check: ignore -->`
   in the deck markdown (or `% slide-overflow-check: ignore` in LaTeX) to
   suppress flagging on a specific slide. Requires coordinated changes in
   the format skills' rendering pipeline.

3. **SARIF output** for native GitHub Actions integration. Convert the
   existing `--json` schema to SARIF 2.1.0; trivial wrapper.

4. **Visual-similarity / LLM-vision check** for "looks weird but doesn't
   strictly overflow" cases. Different problem class, much higher cost
   per slide; only justified if users repeatedly ask for it.
