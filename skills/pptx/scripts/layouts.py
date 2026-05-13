"""
layouts.py — slide-layout renderers for generate.py.

Each layout has a render_<name>(prs, spec, yaml_dir) function that:
  1. Picks the right master-template layout (by name or fallback index).
  2. Adds a slide using that layout.
  3. Populates placeholders from the YAML spec.
  4. Adds speaker notes if `notes:` is present in the spec.

The LAYOUT_MAP dict declares the (preferred-name, fallback-index) pair
per layout. Lookup is case-insensitive and ignores spaces/dashes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt

# (preferred layout name in master, fallback index)
LAYOUT_MAP: dict[str, tuple[str, int]] = {
    "title":      ("Title Slide",          0),
    "section":    ("Section Header",       2),
    "bullets":    ("Title and Content",    1),
    "image":      ("Picture with Caption", 8),
    "two_column": ("Two Content",          3),
    "code":       ("Title and Content",    1),
    "quote":      ("Title and Content",    1),
    "end":        ("Title Slide",          0),
}


def _normalize(s: str) -> str:
    return s.lower().replace(" ", "").replace("-", "").replace("_", "")


def pick_layout(prs: Presentation, layout_name: str):
    """Resolve a YAML layout name to a python-pptx slide layout."""
    # 1. Direct name match (case-insensitive, ignore spaces/dashes/underscores)
    target = _normalize(layout_name)
    for layout in prs.slide_layouts:
        if _normalize(layout.name) == target:
            return layout

    # 2. Canonical-name match via LAYOUT_MAP
    if layout_name in LAYOUT_MAP:
        canonical_name, fallback_idx = LAYOUT_MAP[layout_name]
        canonical_target = _normalize(canonical_name)
        for layout in prs.slide_layouts:
            if _normalize(layout.name) == canonical_target:
                return layout
        # 3. Fallback to canonical index
        if fallback_idx < len(prs.slide_layouts):
            return prs.slide_layouts[fallback_idx]

    # 4. Last-resort default
    print(f"Warning: layout '{layout_name}' not found; using slide_layouts[1]")
    return prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]


def _set_placeholder_text(slide, idx: int, text: str) -> None:
    """Set text on a placeholder by index, no-op if absent."""
    try:
        ph = slide.placeholders[idx]
        ph.text = text
    except KeyError:
        pass


def _add_notes(slide, notes: str | None) -> None:
    if not notes:
        return
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes


def _resolve_path(path_str: str, yaml_dir: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (yaml_dir / p).resolve()


# ─── Layout renderers ────────────────────────────────────────────────────


def _render_title(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "title")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    if spec.get("subtitle"):
        _set_placeholder_text(slide, 1, spec["subtitle"])
    _add_notes(slide, spec.get("notes"))


def _render_section(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "section")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    _add_notes(slide, spec.get("notes"))


def _render_bullets(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "bullets")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))
    # Body placeholder usually at index 1
    try:
        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()
        bullets = spec.get("bullets", [])
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = str(b)
            p.level = 0
    except KeyError:
        pass
    _add_notes(slide, spec.get("notes"))


def _render_image(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "image")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))

    img_path = _resolve_path(spec["image"], yaml_dir)
    width_frac = float(spec.get("width", 0.85))

    slide_w = prs.slide_width
    slide_h = prs.slide_height
    img_w = int(slide_w * width_frac)
    # Read intrinsic aspect to compute height
    try:
        from PIL import Image
        with Image.open(img_path) as im:
            ratio = im.height / im.width if im.width else 0.5625
    except Exception:
        ratio = 0.5625  # 16:9 fallback
    img_h = int(img_w * ratio)
    # Cap height at 70% of slide
    max_h = int(slide_h * 0.70)
    if img_h > max_h:
        img_h = max_h
        img_w = int(img_h / ratio) if ratio else img_w

    left = int((slide_w - img_w) / 2)
    top = int(slide_h * 0.18)
    slide.shapes.add_picture(str(img_path), left, top, width=img_w, height=img_h)

    if spec.get("caption"):
        from pptx.util import Emu
        caption_top = top + img_h + Inches(0.2)
        caption_box = slide.shapes.add_textbox(
            left, caption_top, img_w, Inches(0.4)
        )
        tf = caption_box.text_frame
        tf.text = spec["caption"]
        tf.paragraphs[0].font.size = Pt(12)
        tf.paragraphs[0].font.italic = True

    _add_notes(slide, spec.get("notes"))


def _render_two_column(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "two_column")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))

    def _fill_side(ph_idx: int, side: dict | None) -> None:
        if not side:
            return
        try:
            ph = slide.placeholders[ph_idx]
        except KeyError:
            return
        if "bullets" in side:
            tf = ph.text_frame
            tf.clear()
            for i, b in enumerate(side["bullets"]):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = str(b)
        elif "text" in side:
            ph.text = str(side["text"])
        elif "image" in side:
            # Replace placeholder with image
            img_path = _resolve_path(side["image"], yaml_dir)
            left, top, width, height = ph.left, ph.top, ph.width, ph.height
            sp = ph._element
            sp.getparent().remove(sp)
            slide.shapes.add_picture(str(img_path), left, top, width=width, height=height)

    _fill_side(1, spec.get("left"))
    _fill_side(2, spec.get("right"))
    _add_notes(slide, spec.get("notes"))


def _render_code(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "code")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", ""))

    if spec.get("code_file"):
        code = _resolve_path(spec["code_file"], yaml_dir).read_text()
    else:
        code = spec.get("code", "")

    try:
        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()
        # Render as monospaced
        highlight = set(spec.get("highlight_lines", []))
        for i, line in enumerate(code.splitlines(), start=1):
            p = tf.paragraphs[0] if i == 1 else tf.add_paragraph()
            p.text = line if line else " "
            for run in p.runs:
                run.font.name = "Menlo"
                run.font.size = Pt(14)
                if i in highlight:
                    run.font.bold = True
    except KeyError:
        pass
    _add_notes(slide, spec.get("notes"))


def _render_quote(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "quote")
    slide = prs.slides.add_slide(layout)
    # Use title placeholder for the cite, body for the quote
    _set_placeholder_text(slide, 0, spec.get("cite", ""))
    try:
        body = slide.placeholders[1]
        tf = body.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = f'"{spec["text"]}"'
        for run in p.runs:
            run.font.italic = True
            run.font.size = Pt(28)
    except KeyError:
        pass
    _add_notes(slide, spec.get("notes"))


def _render_end(prs: Presentation, spec: dict, yaml_dir: Path) -> None:
    layout = pick_layout(prs, "end")
    slide = prs.slides.add_slide(layout)
    _set_placeholder_text(slide, 0, spec.get("title", "Thank you"))
    if spec.get("subtitle"):
        _set_placeholder_text(slide, 1, spec["subtitle"])
    _add_notes(slide, spec.get("notes"))


# Dispatch table
_RENDERERS = {
    "title":      _render_title,
    "section":    _render_section,
    "bullets":    _render_bullets,
    "image":      _render_image,
    "two_column": _render_two_column,
    "code":       _render_code,
    "quote":      _render_quote,
    "end":        _render_end,
}


def render_slide(prs: Presentation, spec: dict[str, Any], yaml_dir: Path) -> None:
    layout = spec.get("layout", "bullets")
    renderer = _RENDERERS.get(layout)
    if renderer is None:
        # Unknown layout — render as bullets with the title and any bullets
        print(f"Warning: unknown layout '{layout}'; rendering as bullets")
        _render_bullets(prs, spec, yaml_dir)
    else:
        renderer(prs, spec, yaml_dir)
