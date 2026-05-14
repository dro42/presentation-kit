"""Marp theme generator.

Reads templates/marp.css.tmpl, fills tokens from the brand spec, writes
{short}.css to the output directory. Copies the logo file alongside so
relative paths in the generated CSS resolve.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from _generators._common import normalize_palette, resolve_token, safe_substitute_tmpl

_TEMPLATE_REL = "templates/marp.css.tmpl"


def generate(spec: dict, spec_path: Path, out_dir: Path, skill_root: Path) -> Path:
    """Generate a Marp theme from `spec`. Returns the path to the .css file."""
    short = spec["brand"]["short"]
    name = spec["brand"]["name"]
    palette = spec["palette"]
    typography = spec.get("typography", {})
    spacing = spec.get("spacing", {})
    logo = spec.get("logo")
    variants = spec.get("variants", {})

    pal = normalize_palette(palette)
    inverse = palette.get("inverse") or {}
    inv_palette = {**palette, "white": "#FFFFFF", "black": "#000000"}
    inv_text = resolve_token(inverse.get("text") or "white", inv_palette)
    inv_bg = resolve_token(inverse.get("bg") or "primary", inv_palette)

    # Typography defaults
    body = typography.get("body") or ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"]
    headings = typography.get("headings") or body
    mono = typography.get("mono") or ["SF Mono", "Menlo", "Consolas", "monospace"]
    base_size = typography.get("base_size_pt", 24)

    # Code block tokens
    code = typography.get("code") or {}
    code_bg = resolve_token(code.get("bg") or "bg_alt", pal)
    code_border = resolve_token(code.get("border_color") or "primary", pal)
    code_border_width = code.get("border_width_px", 3)
    code_font_size = code.get("font_size_ratio", 0.72)

    # Table tokens
    table = typography.get("table") or {}
    table_header = resolve_token(table.get("header_color") or "primary", pal)
    table_header_border = table.get("header_border_width_px", 2)
    table_cell_border = resolve_token(table.get("cell_border_color") or "rule_soft", pal)

    # Spacing
    pad = (spacing.get("slide_padding") or {})
    pad_top = pad.get("top", 60)
    pad_right = pad.get("right", 70)
    pad_bottom = pad.get("bottom", 60)
    pad_left = pad.get("left", 70)
    # Default top padding bumps when logo is top-anchored to clear it
    if logo and (logo.get("position") or "").startswith("top") and "top" not in pad:
        pad_top = max(pad_top, 110)

    # Conditional blocks
    block_accent_var = (
        f"\n  --accent-color:     {pal['accent']};" if pal["accent"] else ""
    )

    block_logo_comment, block_logo_bg = "", ""
    if logo and logo.get("path") and logo.get("position") != "none":
        # Copy the logo next to the generated CSS so the relative URL holds
        src = (spec_path.parent / logo["path"]).resolve()
        logo_filename = src.name
        block_logo_bg = _logo_bg_block(logo, logo_filename)
        block_logo_comment = (
            f"\n   Logo positioned at {logo['position']} on every slide; the file"
            f"\n   `{logo_filename}` is shipped alongside this CSS."
        )

    block_lead = _lead_block(variants.get("title") or {}, pal)
    block_invert = _invert_block(variants.get("section") or {}, inv_text, inv_bg)
    block_two_column = _two_column_block(variants.get("two_column") or {})

    tokens = {
        "short": short, "name": name,
        "generated_by": f" * Generated from {spec_path.name}.",
        "primary": pal["primary"],
        "secondary": pal["secondary"],
        "primary_soft": pal["primary_soft"],
        "bg": pal["bg"],
        "bg_alt": pal["bg_alt"],
        "text": pal["text"],
        "rule": pal["rule"],
        "rule_soft": pal["rule_soft"],
        "font_body": _font_stack(body),
        "font_headings": _font_stack(headings),
        "font_mono": _font_stack(mono),
        "base_size": base_size,
        "code_bg": code_bg,
        "code_border": code_border,
        "code_border_width": code_border_width,
        "code_font_size": code_font_size,
        "table_header": table_header,
        "table_header_border": table_header_border,
        "table_cell_border": table_cell_border,
        "pad_top": pad_top, "pad_right": pad_right,
        "pad_bottom": pad_bottom, "pad_left": pad_left,
        "block_accent_var": block_accent_var,
        "block_logo_comment": block_logo_comment,
        "block_logo_bg": block_logo_bg,
        "block_lead": block_lead,
        "block_invert": block_invert,
        "block_two_column": block_two_column,
    }

    template_path = skill_root / _TEMPLATE_REL
    css = safe_substitute_tmpl(template_path, {k: str(v) for k, v in tokens.items()})

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{short}.css"
    out_file.write_text(css, encoding="utf-8")

    # Copy the logo file alongside the CSS
    if logo and logo.get("path") and logo.get("position") != "none":
        src = (spec_path.parent / logo["path"]).resolve()
        dst = out_dir / src.name
        if src != dst:
            shutil.copy2(src, dst)

    return out_file


# ─── Block builders ──────────────────────────────────────────────────────────


def _font_stack(stack: list[str]) -> str:
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
        f"\n  background-image: url('{logo_filename}');"
        f"\n  background-repeat: no-repeat;"
        f"\n  background-position: {pos_value};"
        f"\n  background-size: {width}px auto;"
    )


def _lead_block(title: dict, pal: dict) -> str:
    if not title.get("enabled", True):
        return ""
    align = title.get("align", "center")
    h1_size = title.get("h1_size", "3.0em")
    return (
        "\n\n/* ─── Lead / title slide ──────────────────────────────────────────────── */"
        "\nsection.lead {"
        f"\n  text-align: {align};"
        "\n  display: flex;"
        "\n  flex-direction: column;"
        "\n  justify-content: center;"
        "\n}"
        "\nsection.lead h1 {"
        f"\n  font-size: {h1_size};"
        "\n  margin-bottom: 0.5em;"
        "\n  line-height: 1.05;"
        "\n}"
        "\nsection.lead h2 { color: var(--primary-soft); font-weight: 400; }"
    )


def _invert_block(section: dict, inv_text: str, inv_bg: str) -> str:
    if not section.get("enabled", True):
        return ""
    return (
        "\n\n/* ─── Inverted / section divider slide ────────────────────────────────── */"
        "\nsection.invert {"
        f"\n  background-color: {inv_bg};"
        "\n  background-image: none;"
        f"\n  color: {inv_text};"
        "\n  display: flex;"
        "\n  flex-direction: column;"
        "\n  justify-content: center;"
        "\n}"
        f"\nsection.invert h1 {{ color: {inv_text}; border-bottom-color: rgba(255,255,255,0.5); }}"
        "\nsection.invert h2,"
        "\nsection.invert h3 { color: rgba(255,255,255,0.85); }"
        "\nsection.invert strong { color: #FFFFFF; }"
        "\nsection.invert code   { background: rgba(255,255,255,0.12); color: #FFFFFF; }"
        "\nsection.invert pre    { background: rgba(255,255,255,0.08); border-left-color: rgba(255,255,255,0.6); }"
        "\nsection.invert pre code { color: #FFFFFF; }"
        "\nsection.invert blockquote {"
        "\n  background: rgba(255,255,255,0.08);"
        "\n  border-left-color: rgba(255,255,255,0.6);"
        "\n  color: rgba(255,255,255,0.9);"
        "\n}"
        "\nsection.invert footer { color: rgba(255,255,255,0.7); border-top-color: rgba(255,255,255,0.2); }"
    )


def _two_column_block(tc: dict) -> str:
    if not tc.get("enabled", True):
        return ""
    cols = tc.get("column_count", 2)
    gap = tc.get("column_gap_rem", 2.5)
    return (
        "\n\n/* ─── Two-column layout (use `<!-- _class: two-column -->`) ─────────── */"
        "\nsection.two-column {"
        f"\n  column-count: {cols};"
        f"\n  column-gap: {gap}rem;"
        "\n  column-rule: 1px solid var(--rule-soft);"
        "\n}"
        "\nsection.two-column h1 {"
        "\n  display: block;"
        "\n  width: 100%;"
        "\n  column-span: all;"
        "\n  -webkit-column-span: all;"
        "\n  margin-bottom: 0.6em;"
        "\n}"
        "\nsection.two-column h2,"
        "\nsection.two-column h3 { break-after: avoid; }"
        "\nsection.two-column ul,"
        "\nsection.two-column ol,"
        "\nsection.two-column pre,"
        "\nsection.two-column blockquote { break-inside: avoid; }"
    )
