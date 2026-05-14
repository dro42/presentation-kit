"""Slidev theme generator.

Walks templates/slidev-theme/ as a directory tree. Files ending in `.tmpl`
are token-substituted and written without the `.tmpl` suffix; everything
else is copied verbatim. The output is a complete `slidev-theme-<short>/`
directory ready to be referenced as `theme: ./slidev-theme-<short>` in a
Slidev deck's frontmatter.

Why the `.tmpl` extension matters: Slidev themes are Vue-based packages.
Static `.vue` layout files contain `${...}` syntax (Vue template
interpolation) that would collide with Python's string.Template if we
substituted indiscriminately. The `.tmpl` extension is an explicit opt-in
for substitution.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from _generators._common import normalize_palette, resolve_token, safe_substitute_tmpl

_TEMPLATE_DIR_REL = "templates/slidev-theme"


def generate(spec: dict, spec_path: Path, out_dir: Path, skill_root: Path) -> Path:
    """Generate a Slidev theme directory. Returns the path to the directory root."""
    short = spec["brand"]["short"]
    name = spec["brand"]["name"]
    palette = spec["palette"]
    typography = spec.get("typography", {})
    spacing = spec.get("spacing", {})
    logo = spec.get("logo")

    pal = normalize_palette(palette)

    inverse = palette.get("inverse") or {}
    inv_palette = {**palette, "white": "#FFFFFF", "black": "#000000"}
    inv_text = resolve_token(inverse.get("text") or "white", inv_palette)
    inv_bg = resolve_token(inverse.get("bg") or "primary", inv_palette)

    body = typography.get("body") or ["Inter", "system-ui", "sans-serif"]
    headings = typography.get("headings") or body
    mono = typography.get("mono") or ["SF Mono", "Menlo", "monospace"]

    code = typography.get("code") or {}
    code_bg = resolve_token(code.get("bg") or "bg_alt", pal)
    code_border = resolve_token(code.get("border_color") or "primary", pal)
    code_border_width = code.get("border_width_px", 3)
    code_font_size = code.get("font_size_ratio", 0.72)

    table = typography.get("table") or {}
    table_header = resolve_token(table.get("header_color") or "primary", pal)
    table_header_border = table.get("header_border_width_px", 2)
    table_cell_border = resolve_token(table.get("cell_border_color") or "rule_soft", pal)

    pad = (spacing.get("slide_padding") or {})
    pad_top = pad.get("top", 60)
    pad_right = pad.get("right", 70)
    pad_bottom = pad.get("bottom", 60)
    pad_left = pad.get("left", 70)
    if logo and (logo.get("position") or "").startswith("top") and "top" not in pad:
        pad_top = max(pad_top, 110)

    block_accent_var = (
        f"\n  --brand-accent:    {pal['accent']};" if pal["accent"] else ""
    )

    block_logo_bg, logo_filename = "", None
    if logo and logo.get("path") and (logo.get("position") or "top-right") != "none":
        src = (spec_path.parent / logo["path"]).resolve()
        logo_filename = src.name
        block_logo_bg = _logo_bg_block(logo, logo_filename)

    tokens = {
        "short": short,
        "name": name,
        "generated_by": f" * Generated from {spec_path.name}.",
        "primary": pal["primary"],
        "secondary": pal["secondary"],
        "primary_soft": pal["primary_soft"],
        "bg": pal["bg"],
        "bg_alt": pal["bg_alt"],
        "text": pal["text"],
        "rule": pal["rule"],
        "rule_soft": pal["rule_soft"],
        "inverse_text": inv_text,
        "inverse_bg": inv_bg,
        "font_body": _font_stack_css(body),
        "font_headings": _font_stack_css(headings),
        "font_mono": _font_stack_css(mono),
        "slidev_font_sans": json.dumps(", ".join(body)),
        "slidev_font_mono": json.dumps(", ".join(mono)),
        "code_bg": code_bg,
        "code_border": code_border,
        "code_border_width": code_border_width,
        "code_font_size": code_font_size,
        "table_header": table_header,
        "table_header_border": table_header_border,
        "table_cell_border": table_cell_border,
        "pad_top": pad_top,
        "pad_right": pad_right,
        "pad_bottom": pad_bottom,
        "pad_left": pad_left,
        "block_accent_var": block_accent_var,
        "block_logo_bg": block_logo_bg,
    }
    str_tokens = {k: str(v) for k, v in tokens.items()}

    template_root = skill_root / _TEMPLATE_DIR_REL
    theme_dir = out_dir / f"slidev-theme-{short}"
    theme_dir.mkdir(parents=True, exist_ok=True)

    for src in template_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(template_root)
        if src.suffix == ".tmpl":
            # strip .tmpl from the destination filename
            dst_rel = rel.with_suffix("")
            dst = theme_dir / dst_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(safe_substitute_tmpl(src, str_tokens), encoding="utf-8")
        else:
            dst = theme_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Copy the logo so the relative URL in styles/index.css resolves
    if logo_filename:
        src = (spec_path.parent / logo["path"]).resolve()
        dst = theme_dir / src.name
        if src != dst:
            shutil.copy2(src, dst)

    return theme_dir


# --- helpers ---------------------------------------------------------------


def _font_stack_css(stack: list[str]) -> str:
    """Build a CSS-safe font-family value: quote names with spaces, leave generics bare."""
    parts = []
    for name in stack:
        if " " in name and not (name.startswith("'") or name.startswith('"')):
            parts.append(f"'{name}'")
        else:
            parts.append(name)
    return ", ".join(parts)


def _logo_bg_block(logo: dict, logo_filename: str) -> str:
    pos = logo.get("position", "top-right")
    width = logo.get("width_px", 160)
    offset = logo.get("offset") or {}
    top = offset.get("top", 35)
    right = offset.get("right", 50)
    left = offset.get("left", 50)
    bottom = offset.get("bottom", 35)

    pos_value = {
        "top-right":    f"top {top}px right {right}px",
        "top-left":     f"top {top}px left {left}px",
        "bottom-right": f"bottom {bottom}px right {right}px",
        "bottom-left":  f"bottom {bottom}px left {left}px",
    }.get(pos, f"top {top}px right {right}px")

    return (
        f"\n  background-image: url('./{logo_filename}');"
        f"\n  background-repeat: no-repeat;"
        f"\n  background-position: {pos_value};"
        f"\n  background-size: {width}px auto;"
    )
