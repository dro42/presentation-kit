# `templates/pptx/`

This directory holds the **baseline.pptx** — an unbranded PowerPoint master
that the pptx generator clones and patches per brand spec. It is a binary
asset committed alongside the text templates.

## Provenance

`baseline.pptx` is built by `scripts/_build_baseline_pptx.py`. Build it once:

```bash
pip install python-pptx
python3 scripts/_build_baseline_pptx.py
# Wrote .../templates/pptx/baseline.pptx (NN bytes)
# Layouts (11):
#   0: 'Title Slide'
#   1: 'Title and Content'
#   2: 'Section Header'
#   ...
```

The result is python-pptx's default master at 16:9 aspect ratio, with the 11
standard PowerPoint layouts in their canonical positions. These line up with
the existing pptx skill's `LAYOUT_MAP` in
`skills/pptx/scripts/layouts.py`, so masters generated from this baseline
drop into the existing pptx generator without surprises.

## Why programmatic, not hand-built

The plan called for a hand-built PowerPoint master. Programmatic build is
the documented OOXML-edit fallback (see
`skills/pptx/references/master-templates.md` §"Editing the master OOXML
directly"). The trade-off: no hand-tuned per-layout placeholder positioning.
The plus: the artifact is reproducible — anyone with `python-pptx` can
rebuild it identically; no opaque binary diffs.

If you want nicer per-layout placeholder positioning later:

1. Open `baseline.pptx` in PowerPoint or LibreOffice Impress.
2. Tweak placeholders, save back over `baseline.pptx`.
3. Commit the new binary. The generator only cares about the theme XML
   (which it overwrites) and the master shape collection (which it
   inherits) — your manual layout edits will be preserved through generated
   masters.

## What the generator overwrites vs. preserves

When `_generators/pptx.py` runs against a baseline:

| Element                                  | Action      |
|------------------------------------------|-------------|
| `ppt/theme/theme1.xml` color slots       | overwritten |
| `ppt/theme/theme1.xml` font typefaces    | overwritten |
| Slide master shapes (logo)               | appended    |
| Per-layout placeholder positioning       | preserved   |
| Per-layout default text                  | preserved   |
| Theme effects, fills, line styles        | preserved   |
| Core properties (title, author)          | overwritten |
