"""Beamer theme generator.

Reads templates/beamer.sty.tmpl, fills tokens from the brand spec, writes
beamertheme<ShortPascal>.sty to the output directory. Copies the logo file
alongside so TikZ overlay paths resolve.

Notes on Beamer specifics:
  - LaTeX base class accepts only 8/9/10/11/12/14/17/20pt. We round
    typography.base_size_pt to the nearest of {10, 11, 12} (Beamer's
    common range). overrides.beamer.base_font_size bypasses the rounding.
  - The theme name is Pascal-cased from brand.short to match the
    \\usetheme{Foo} / beamerthemeFoo.sty convention.
  - Hex values are stripped of '#' for \\definecolor{}{HTML}{RRGGBB}.
  - Template substitution: control-sequence math like $\\blacktriangleright$
    is safe from string.Template because '$\\' isn't a valid placeholder
    prefix. The `protect_tex_math` helper exists for templates that contain
    *value-style* math like $x = 1$ where 'x' could collide with a token —
    not used here. (It would in fact corrupt this template, since its loose
    regex would treat `${a}foo{$b}` as a math region.)
"""
from __future__ import annotations

import re
import shutil
from datetime import date
from pathlib import Path

from _generators._common import normalize_palette, resolve_token, safe_substitute_tmpl

_TEMPLATE_REL = "templates/beamer.sty.tmpl"
_BEAMER_BASE_SIZES_PT = (10, 11, 12)


def generate(spec: dict, spec_path: Path, out_dir: Path, skill_root: Path) -> Path:
    """Generate a Beamer theme. Returns the path to the .sty file."""
    short = spec["brand"]["short"]
    short_pascal = _pascal_case(short)
    name = spec["brand"]["name"]
    palette = spec["palette"]
    typography = spec.get("typography", {})
    logo = spec.get("logo")
    footer = spec.get("footer", {})
    overrides = (spec.get("overrides") or {}).get("beamer") or {}

    pal = normalize_palette(palette)

    inverse = palette.get("inverse") or {}
    inv_palette = {**palette, "white": "#FFFFFF", "black": "#000000"}
    inv_text = resolve_token(inverse.get("text") or "white", inv_palette)
    inv_bg = resolve_token(inverse.get("bg") or "primary", inv_palette)

    # Conditional accent block — only emit \definecolor{BrandAccent} if accent set
    block_accent_color = (
        f"\n\\definecolor{{BrandAccent}}{{HTML}}{{{_hex(pal['accent'])}}}"
        if pal["accent"] else ""
    )
    block_alerted_color = (
        "\n\\setbeamercolor{block title alerted}{fg=BrandInverseText,bg=BrandAccent}"
        "\n\\setbeamercolor{block body alerted}{fg=BrandText,bg=BrandAccent!10}"
        "\n\\setbeamercolor{alerted text}{fg=BrandAccent}"
        if pal["accent"] else ""
    )

    # Logo via TikZ overlay — only if logo configured AND not "none"
    block_logo_packages, block_logo_overlay, logo_filename = "", "", None
    if logo and logo.get("path") and (logo.get("position") or "top-right") != "none":
        block_logo_packages, block_logo_overlay, logo_filename = _logo_blocks(logo, spec_path)

    # Section divider — Beamer's \section{} doesn't render a slide by default;
    # the `section` variant in the brand spec turns it into a colored divider.
    variants = spec.get("variants") or {}
    block_section_page = _section_page_block(variants.get("section") or {})

    # Footer text — escape LaTeX specials and resolve {{year}}/{{author}} templating
    footer_text_tex = _resolve_footer_tex(footer)

    # Font size mapping (purely informational in the .sty; the deck's documentclass owns it,
    # but we surface the recommended class option in a comment).
    base_size_pt = overrides.get("base_font_size") or _round_to_beamer_size(
        typography.get("base_size_pt", 11)
    )
    base_size_str = base_size_pt if isinstance(base_size_pt, str) else f"{base_size_pt}pt"

    generated_by_lines = [
        f"% Generated from {spec_path.name}.",
        f"% Recommended documentclass: \\documentclass[{base_size_str},aspectratio=169]{{beamer}}",
    ]

    tokens = {
        "short": short,
        "short_pascal": short_pascal,
        "name": name,
        "date_today": date.today().isoformat().replace("-", "/"),
        "generated_by": "\n".join(generated_by_lines),
        "primary_hex":      _hex(pal["primary"]),
        "secondary_hex":    _hex(pal["secondary"]),
        "primary_soft_hex": _hex(pal["primary_soft"]),
        "text_hex":         _hex(pal["text"]),
        "bg_hex":           _hex(pal["bg"]),
        "bg_alt_hex":       _hex(pal["bg_alt"]),
        "rule_hex":         _hex(pal["rule"]),
        "rule_soft_hex":    _hex(pal["rule_soft"]),
        "inverse_text_hex": _hex(inv_text),
        "inverse_bg_hex":   _hex(inv_bg),
        "footer_text_tex":  footer_text_tex,
        "block_accent_color":   block_accent_color,
        "block_alerted_color":  block_alerted_color,
        "block_logo_packages":  block_logo_packages,
        "block_logo_overlay":   block_logo_overlay,
        "block_section_page":   block_section_page,
    }

    template_path = skill_root / _TEMPLATE_REL
    rendered = safe_substitute_tmpl(template_path, {k: str(v) for k, v in tokens.items()})

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"beamertheme{short_pascal}.sty"
    out_file.write_text(rendered, encoding="utf-8")

    # Copy the logo next to the .sty so the TikZ overlay path resolves
    if logo_filename:
        src = (spec_path.parent / logo["path"]).resolve()
        dst = out_dir / src.name
        if src != dst:
            shutil.copy2(src, dst)

    return out_file


# --- helpers ---------------------------------------------------------------


def _hex(value: str) -> str:
    """'#36566D' -> '36566D' for LaTeX \\definecolor{}{HTML}{...}."""
    return value.lstrip("#").upper()


def _pascal_case(short: str) -> str:
    """'hcw' -> 'Hcw'; 'my-org-2026' -> 'MyOrg2026'."""
    parts = re.split(r"[-_]+", short)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _round_to_beamer_size(pt) -> int:
    """Round a CSS-canvas pt value to the nearest Beamer base class size."""
    try:
        n = int(round(float(pt)))
    except (TypeError, ValueError):
        return 11
    # CSS-canvas sizes (24pt @ 1280×720) are far above LaTeX class sizes;
    # clamp to {10, 11, 12} which is the practical Beamer range.
    if n <= 10:
        return 10
    if n >= 12:
        return 12
    return 11


def _resolve_footer_tex(footer: dict) -> str:
    """Resolve {{year}}/{{author}} templating, escape LaTeX specials."""
    text = footer.get("text") or ""
    author = footer.get("author") or ""
    text = text.replace("{{year}}", str(date.today().year))
    text = text.replace("{{author}}", author)
    text = text.replace("{{date}}", date.today().isoformat())
    # Escape the few LaTeX specials likely to appear in footer text
    return (text
            .replace("\\", r"\textbackslash{}")
            .replace("&", r"\&")
            .replace("%", r"\%")
            .replace("#", r"\#")
            .replace("_", r"\_")
            .replace("$", r"\$")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("©", r"\textcopyright{}")
            .replace("·", r"\textperiodcentered{}"))


def _logo_blocks(logo: dict, spec_path: Path) -> tuple[str, str, str]:
    """Build TikZ overlay block for a corner-anchored logo.

    Emits `\\includegraphics{<stem>}` (no extension) so pdfLaTeX picks
    whichever supported format (.pdf, .png, .jpg) is available next to the
    .sty. SVGs are copied as-is; the user converts them with rsvg-convert,
    inkscape, or a one-shot `pdflatex --shell-escape` + `\\includesvg`.
    """
    src = (spec_path.parent / logo["path"]).resolve()
    logo_filename = src.name
    logo_stem = src.stem
    pos = logo.get("position", "top-right")
    width_px = logo.get("width_px", 160)
    # Convert px → mm (1 px ≈ 0.265 mm at 96 DPI) for TikZ
    width_mm = round(width_px * 0.265, 1)
    offset = logo.get("offset") or {}
    top_mm = round(offset.get("top", 35) * 0.265, 1)
    right_mm = round(offset.get("right", 50) * 0.265, 1)
    left_mm = round(offset.get("left", 50) * 0.265, 1)
    bottom_mm = round(offset.get("bottom", 35) * 0.265, 1)

    anchor_map = {
        "top-right":    (f"current page.north east", f"-{right_mm}mm,-{top_mm}mm", "north east"),
        "top-left":     (f"current page.north west", f"{left_mm}mm,-{top_mm}mm", "north west"),
        "bottom-right": (f"current page.south east", f"-{right_mm}mm,{bottom_mm}mm", "south east"),
        "bottom-left":  (f"current page.south west", f"{left_mm}mm,{bottom_mm}mm", "south west"),
    }
    anchor, shift, node_anchor = anchor_map.get(pos, anchor_map["top-right"])

    packages = (
        "\n\\RequirePackage{tikz}"
        "\n\\RequirePackage{graphicx}"
    )

    is_svg = src.suffix.lower() == ".svg"
    svg_note = (
        f"\n% NOTE: source logo is SVG. pdfLaTeX cannot include SVG directly.\n"
        f"% Convert {logo_filename} to {logo_stem}.pdf (or .png) next to this .sty:\n"
        f"%   rsvg-convert -f pdf -o {logo_stem}.pdf {logo_filename}\n"
        f"%   inkscape --export-type=pdf {logo_filename}\n"
        if is_svg else ""
    )

    overlay = (
        f"\n\n% --- Logo overlay (every frame, {pos}) ---------------------------------\n"
        f"{svg_note}"
        "\\addtobeamertemplate{background canvas}{}{%\n"
        "  \\begin{tikzpicture}[remember picture,overlay]\n"
        f"    \\node[anchor={node_anchor},xshift={shift.split(',')[0]},yshift={shift.split(',')[1]}] at ({anchor})\n"
        f"      {{\\includegraphics[width={width_mm}mm]{{{logo_stem}}}}};\n"
        "  \\end{tikzpicture}%\n"
        "}"
    )
    return packages, overlay, logo_filename


def _section_page_block(section: dict) -> str:
    """Configure section title pages (\\section commands trigger a divider slide)."""
    if not section.get("enabled", True):
        return ""
    return (
        "\n\n% --- Section divider page (rendered on \\section{...}) ----------------\n"
        "\\AtBeginSection[]{%\n"
        "  \\begin{frame}[plain,noframenumbering]%\n"
        "    \\begin{beamercolorbox}[wd=\\paperwidth,ht=\\paperheight,center,sep=2em]{palette primary}%\n"
        "      \\usebeamerfont{title}\\insertsectionhead%\n"
        "    \\end{beamercolorbox}%\n"
        "  \\end{frame}%\n"
        "}"
    )
