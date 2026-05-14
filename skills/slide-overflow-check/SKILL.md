---
name: slide-overflow-check
description: Detect text that collides with the footer band or runs off the page in a rendered slide PDF. Format-agnostic post-render verification that works on output from Marp, Beamer, Slidev, or any other slide tool that produces a PDF. Use this skill whenever the user mentions "check overflow", "verify slides", "did the slide get clipped", "slides cut off", "content cropped", "collides with footer", "after rendering", or asks to validate a deck before sending/presenting it. Also trigger automatically as the closing step of any of the marp / beamer / slidev / pptx render workflows in the presentation-kit.
---

# slide-overflow-check Skill

Detects the most common "looked fine in preview, looks broken in the PDF"
failure mode in slide decks: text that runs into the footer band or off the
page edge. Operates on the rendered PDF, so it works regardless of which
upstream tool produced the deck (Marp, Beamer, Slidev, pptx-via-LibreOffice).

This is a **detection** skill, not a fixer. It tells you *which slides* and
*which text*; the user decides whether to fix in the deck (split a slide,
trim a bullet) or in the theme (more bottom padding, smaller base font).

## When to use

Trigger after any deck has been rendered to PDF. In practice that means:

- The user asks to "check overflow" or "verify the slides" by name.
- The user just exported a deck and wants a final pass before sending.
- You (Claude) are finishing a Workflow C in the marp / beamer / slidev /
  pptx skill — invoke this skill on the output PDF before reporting success.
- Someone hands the user an existing PDF and asks "is this deck OK?"

## When NOT to use

- For source-code-level slide review (typos, structure, narrative). This
  skill operates on rendered geometry, not content.
- For accessibility / contrast / color review. Different problem class.
- For PPTX or KEY files directly — convert to PDF first via LibreOffice
  headless (`soffice --headless --convert-to pdf deck.pptx`) or Keynote
  export, then run the check on the PDF.

## How to invoke

```bash
python3 scripts/check_overflow.py <path-to-deck.pdf>
```

Common flag combinations:

```bash
# Default human-readable output
python3 scripts/check_overflow.py deck.pdf

# JSON for downstream tools / CI
python3 scripts/check_overflow.py deck.pdf --json

# Tighter clearance for themes with thin footers (no band, just a thin rule)
python3 scripts/check_overflow.py deck.pdf --footer-clearance 10

# Looser clearance for themes with tall colored footer bands
python3 scripts/check_overflow.py deck.pdf --footer-clearance 35

# CI-friendly — only fail on hard errors, not warns
python3 scripts/check_overflow.py deck.pdf --no-fail-on-warn
```

Exit codes (linter convention):
- `0` — clean (no errors, no warnings)
- `1` — at least one error, OR warnings present (suppress with `--no-fail-on-warn`)

## What it detects

| Issue | Severity | Example |
|---|---|---|
| Text collides with footer band | error | a blockquote line ends 5pt below the slide's footer rule |
| Text past the page bottom | error | trailing words of a paragraph render at y > page_height |
| Text past the page right / left / top | error | a long table column extends past the slide canvas |
| Page near the edge with no footer detected | warn | content within last 5% of page on a footer-less slide |
| Page has zero extracted text | warn | rasterized / outlined-font page that can't be analyzed |

## What it does NOT detect (v1)

- **Image overflow.** `pdftotext` doesn't see image bboxes. If a figure
  bleeds off the slide, this check misses it. Verify visually as a backup.
  *(v2 path: switch to PyMuPDF `get_pixmap` for image-aware analysis.)*
- **Visual collisions that don't cross thresholds** (text legally inside
  the canvas but visually too close to the logo). Subjective; out of scope.
- **Color contrast / accessibility.** Different problem class.
- **Auto-fixing.** Detection + remediation hints only.

## Reading the output

```
slide-overflow-check: deck.pdf — 8 pages, 2 issues
  footer text top: y=505  ·  clearance: 20pt  ·  safe_zone_top: y=485

  Page 4 — error — footer collision:
    "useful for citations and pull-quotes." at yMax=508/540 (threshold 485)
```

The header line shows the deck-level state: how many pages, how many issues,
and the detected footer geometry. `safe_zone_top` is the y-coordinate above
which body text must end; anything below is flagged.

Each issue lists the offending text, its bottom edge, the page height, and
the threshold it crossed. PDF page numbers are 1-indexed and match what the
user sees in Preview / a PDF viewer.

## Remediation

After a non-zero exit, surface both options to the user — the right fix
depends on whether the overflow is a one-off or a pattern:

1. **Theme-side fix (preferred when overflow recurs across decks).**
   - Increase the slide's bottom padding (e.g. `section { padding-bottom: 80px; }`).
   - Lower the body font-size base.
   - Move the footer further down or shrink it.
   - Check the `--footer-clearance` value matches the theme's actual band height.

2. **Content-side fix (preferred for one-or-two-slide problems).**
   - Split the slide.
   - Trim a bullet or shorten a sentence.
   - Use a smaller table or break it across two slides.
   - Move detail into a backup slide and reference it verbally.

After applying a fix, re-render and re-run the check.

## Algorithm at a glance

1. Run `pdftotext -bbox-layout` to get per-word bounding boxes per page.
2. Cluster words in the bottom 15% of each page across the whole deck;
   positions appearing on ≥60% of *paginated* pages are the recurring footer.
3. Subtract `--footer-clearance` from the footer text top to get the
   `safe_zone_top` (accounts for the visual band above the footer text).
4. Flag any non-footer word whose `yMax` exceeds `safe_zone_top` (or any
   other page-canvas boundary).

For the heuristic's design rationale, edge cases, and tuning notes, see
[references/algorithm.md](references/algorithm.md).

## Dependencies

- **Required:** `pdftotext` (poppler-utils). On macOS: `brew install poppler`.
  On Linux: `apt-get install poppler-utils`. The skill checks `command -v
  pdftotext` first and prints the install hint if missing — **never
  auto-installs**.
- **Required:** `python3` (3.10+ recommended for type-hint syntax). System
  Python on macOS is fine. Pure stdlib — no `pip install`.

## Verification

The skill ships with regression fixtures in `fixtures/`:

- `hcw-overflow.pdf` — reproduces the originating bug. Must report exactly
  2 errors (page 4 footer collision, page 5 footer collision).
- `clean-deck.pdf` — minimal overflow-free deck. Must exit 0.

Run the regression suite from the skill directory:

```bash
python3 scripts/check_overflow.py fixtures/hcw-overflow.pdf  # expect exit 1, 2 errors
python3 scripts/check_overflow.py fixtures/clean-deck.pdf    # expect exit 0
```

Re-run after any algorithm or threshold change.

## Output schema (`--json`)

Stable contract — downstream tooling depends on field names.

```json
{
  "pdf_path": "/abs/path/to/deck.pdf",
  "pages_total": 8,
  "pages_with_issues": 2,
  "footer_baseline": 505.0,
  "footer_clearance": 20.0,
  "safe_zone_top": 485.0,
  "issues": [
    {
      "page": 4,
      "severity": "error",
      "kind": "footer_collision",
      "text": "useful for citations and pull-quotes.",
      "bbox": {"xMin": 70.0, "yMin": 503.0, "xMax": 410.0, "yMax": 518.0},
      "page_size": {"width": 960.0, "height": 540.0},
      "threshold_used": 485.0
    }
  ]
}
```

`severity` is `"error"` or `"warn"`. `kind` is one of: `footer_collision`,
`page_bottom`, `off_canvas_right`, `off_canvas_left`, `off_canvas_top`,
`off_canvas_bottom`, `near_page_edge`, `not_analyzable`.
