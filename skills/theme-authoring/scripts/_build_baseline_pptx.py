#!/usr/bin/env python3
"""Build templates/pptx/baseline.pptx — the unbranded master the pptx generator fills.

Run this ONCE after `pip install python-pptx`. Commit the resulting
binary alongside the other templates.

Why this exists: the plan called for a hand-built `baseline.pptx`.
Building it programmatically (per the pptx skill's own
`references/master-templates.md` fallback) gives us a deterministic,
regenerable artifact instead of an opaque binary. The trade-off is no
hand-tuned per-layout placeholder positioning — python-pptx's default
master is used as-is, which already ships the 11 standard PowerPoint
layouts (Title Slide, Title and Content, Section Header, Two Content,
Comparison, Title Only, Blank, Content with Caption, Picture with
Caption, Title and Vertical Text, Vertical Title and Text). Layout
indices match LAYOUT_MAP in skills/pptx/scripts/layouts.py, so generated
masters drop into the existing pptx generator without surprises.

If a future user wants nicer placeholder positioning, they can rebuild
this in PowerPoint and overwrite the file — the pptx generator only
cares about the theme XML and the master shape collection.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches
except ImportError:
    sys.exit(
        "error: python-pptx is required to build the baseline.\n"
        "  pip install python-pptx"
    )

OUT = Path(__file__).resolve().parent.parent / "templates" / "pptx" / "baseline.pptx"


def main() -> int:
    prs = Presentation()
    # 16:9 — matches the modern default and aligns with marp/slidev canvases.
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"Layouts ({len(prs.slide_layouts)}):")
    for i, layout in enumerate(prs.slide_layouts):
        print(f"  {i}: {layout.name!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
