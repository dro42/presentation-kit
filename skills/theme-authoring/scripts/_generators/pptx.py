"""pptx theme generator — template-fill via python-pptx.

Loads templates/pptx/baseline.pptx (a minimal, plain-styled PowerPoint
master with the 11 standard layouts), patches the theme XML colors and
fonts to match the brand spec, drops the brand logo on the slide master
so it appears on every layout, and writes the result as
{short}-master.pptx.

Why template-fill, not master-from-scratch:
  Generating a slide master programmatically from zero is fragile —
  python-pptx's API doesn't cover the full OOXML surface (named layouts
  with placeholder positioning, custom theme effects, etc.). Loading a
  known-good baseline and patching only the brand-relevant pieces (color
  scheme, font scheme, master-level shapes) is what the pptx skill's
  own `references/master-templates.md` recommends as the OOXML-edit
  fallback.

The PowerPoint color scheme has 12 named slots; we map brand tokens:
  primary       → accent1 + hlink
  secondary     → accent2
  primary_soft  → accent3 + folHlink
  accent (opt)  → accent4
  text          → dk1
  bg            → lt1
  inverse.bg    → dk2  (dark variant — Section Header bg)
  inverse.text  → lt2
  accent5/6     → unchanged (chart series headroom)

Optional dependency: python-pptx. If absent, the caller catches the
ImportError-derived _GeneratorSkip and surfaces the install hint.
"""
from __future__ import annotations

import sys
from pathlib import Path

from _generators._common import normalize_palette, resolve_token

_TEMPLATE_REL = "templates/pptx/baseline.pptx"
_BUILDER_REL = "scripts/_build_baseline_pptx.py"

# OOXML namespaces — DrawingML is where theme XML lives.
_NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_THEME_RELTYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
)


class GeneratorSkip(Exception):
    """Raised when the generator can't run (missing dep or asset)."""


def generate(spec: dict, spec_path: Path, out_dir: Path, skill_root: Path) -> Path:
    """Generate a pptx master from `spec`. Returns the path to the .pptx file."""
    try:
        from pptx import Presentation
        from pptx.util import Emu
    except ImportError as e:
        raise GeneratorSkip(
            "python-pptx not installed; run `pip install python-pptx` to enable pptx output"
        ) from e

    baseline = skill_root / _TEMPLATE_REL
    if not baseline.exists():
        raise GeneratorSkip(
            f"baseline.pptx not found at {baseline.relative_to(skill_root)}; "
            f"build it once with `python3 {_BUILDER_REL}` after `pip install python-pptx`"
        )

    short = spec["brand"]["short"]
    name = spec["brand"]["name"]
    palette = spec["palette"]
    typography = spec.get("typography", {})
    logo = spec.get("logo")
    footer = spec.get("footer", {})

    pal = normalize_palette(palette)

    inverse = palette.get("inverse") or {}
    inv_palette = {**palette, "white": "#FFFFFF", "black": "#000000"}
    inv_text = resolve_token(inverse.get("text") or "white", inv_palette)
    inv_bg = resolve_token(inverse.get("bg") or "primary", inv_palette)

    # Pick the first concrete typeface from each font stack — PowerPoint themes
    # store a single typeface per major/minor slot, not a fallback chain. The
    # CSS/LaTeX generators use the full chain; for pptx we take the head.
    body_typeface = (typography.get("body") or ["Calibri"])[0]
    headings_typeface = (typography.get("headings") or [body_typeface])[0]

    prs = Presentation(str(baseline))
    _patch_theme(prs, pal, inv_text, inv_bg, body_typeface, headings_typeface)

    if logo and logo.get("path") and (logo.get("position") or "top-right") != "none":
        logo_path = (spec_path.parent / logo["path"]).resolve()
        if logo_path.exists():
            _add_logo_to_master(prs, logo_path, logo)

    # Core properties — surfaces the brand in PowerPoint's File Info pane.
    core = prs.core_properties
    core.title = name
    if footer.get("author"):
        core.author = footer["author"]

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{short}-master.pptx"
    prs.save(str(out_file))
    return out_file


# --- theme XML patching ----------------------------------------------------


def _theme_part(prs):
    """Return the python-pptx Part wrapping ppt/theme/theme1.xml.

    The theme is a *plain* Part (not an XmlPart), so it has no `.element`
    accessor — we work via the raw `.blob` bytes and write back to `._blob`
    after mutation. python-pptx's `prs.save()` re-zips from `_blob`, so the
    mutation propagates without needing any flush API.
    """
    master_part = prs.slide_masters[0].part
    for rel in master_part.rels.values():
        if rel.reltype == _THEME_RELTYPE:
            return rel.target_part
    raise RuntimeError("baseline.pptx is malformed: no theme part on slide master")


def _set_color_slot(clr_scheme, slot_name: str, hex_value: str) -> None:
    """Replace the child of `<a:{slot_name}>` with `<a:srgbClr val="RRGGBB"/>`.

    PowerPoint color slots can contain either `<a:srgbClr>` or `<a:sysClr>`
    (system color with `lastClr` fallback). We always normalize to srgbClr
    so the brand color is resolved deterministically across PowerPoint /
    Keynote / LibreOffice — sysClr lookups depend on the host theme.
    """
    from lxml import etree

    slot = clr_scheme.find(f"{{{_NS_A}}}{slot_name}")
    if slot is None:
        return  # Slot absent in this baseline; skip rather than fabricate.
    for child in list(slot):
        slot.remove(child)
    srgb = etree.SubElement(slot, f"{{{_NS_A}}}srgbClr")
    srgb.set("val", hex_value.lstrip("#").upper())


def _patch_theme(
    prs, pal: dict, inv_text: str, inv_bg: str,
    body_typeface: str, headings_typeface: str,
) -> None:
    """Mutate the theme XML in-place: color scheme + font scheme."""
    from lxml import etree

    theme_part = _theme_part(prs)
    root = etree.fromstring(theme_part.blob)

    # ── colors ────────────────────────────────────────────────────────────
    clr_scheme = root.find(f"{{{_NS_A}}}themeElements/{{{_NS_A}}}clrScheme")
    if clr_scheme is None:
        raise RuntimeError("baseline.pptx is malformed: no clrScheme")
    _set_color_slot(clr_scheme, "dk1", pal["text"])
    _set_color_slot(clr_scheme, "lt1", pal["bg"])
    _set_color_slot(clr_scheme, "dk2", inv_bg)
    _set_color_slot(clr_scheme, "lt2", inv_text)
    _set_color_slot(clr_scheme, "accent1", pal["primary"])
    _set_color_slot(clr_scheme, "accent2", pal["secondary"])
    _set_color_slot(clr_scheme, "accent3", pal["primary_soft"])
    if pal["accent"]:
        _set_color_slot(clr_scheme, "accent4", pal["accent"])
    _set_color_slot(clr_scheme, "hlink", pal["primary"])
    _set_color_slot(clr_scheme, "folHlink", pal["primary_soft"])

    # ── fonts ─────────────────────────────────────────────────────────────
    font_scheme = root.find(f"{{{_NS_A}}}themeElements/{{{_NS_A}}}fontScheme")
    if font_scheme is not None:
        for tag, typeface in (
            ("majorFont", headings_typeface),
            ("minorFont", body_typeface),
        ):
            font_el = font_scheme.find(f"{{{_NS_A}}}{tag}")
            if font_el is None:
                continue
            latin = font_el.find(f"{{{_NS_A}}}latin")
            if latin is not None:
                latin.set("typeface", typeface)

    # Serialize back. `standalone=True` matches the original XML declaration
    # PowerPoint emits; some readers are strict about declaration parity.
    theme_part._blob = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True,
    )


# --- logo placement --------------------------------------------------------


# 1 px @ 96 DPI = 9525 EMU. (1 inch = 914400 EMU = 96 px.)
_EMU_PER_PX = 9525


def _add_logo_to_master(prs, logo_path: Path, logo: dict) -> None:
    """Add the brand logo as a Picture on the slide master.

    python-pptx exposes `add_picture()` only on `SlideShapes` — not on
    `MasterShapes` or `LayoutShapes`. So we drop to the OOXML layer:
      1. Add the image as a part to the package.
      2. Relate the master part to it (yields the rId for the picture).
      3. Construct a `<p:pic>` element via `CT_Picture.new_pic`.
      4. Append it to the master's `<p:spTree>`.

    Putting the logo on the master (rather than each layout) means it
    inherits everywhere automatically; PowerPoint's per-slide "Hide
    Background Graphics" can suppress it on specific layouts.

    SVG handling: python-pptx pipes images through Pillow, which doesn't
    decode SVG. We mirror the Beamer generator's convention — if the spec
    points at `logo.svg`, look for a same-stem PNG/JPG sibling and use
    that instead. If no raster sibling exists, warn with the conversion
    command and skip the logo (master still ships, just unbranded).
    """
    from pptx.oxml.shapes.picture import CT_Picture
    from PIL import Image as PILImage

    if logo_path.suffix.lower() == ".svg":
        for ext in (".png", ".jpg", ".jpeg"):
            sibling = logo_path.with_suffix(ext)
            if sibling.exists():
                logo_path = sibling
                break
        else:
            print(
                f"warning: pptx: SVG logo {logo_path.name} cannot be embedded "
                f"(python-pptx requires a raster format). Convert to "
                f"{logo_path.stem}.png next to the .svg and re-run, e.g.:\n"
                f"  rsvg-convert -f png -o {logo_path.stem}.png {logo_path.name}\n"
                f"  qlmanage -t -s 800 -o . {logo_path.name} && "
                f"mv {logo_path.name}.png {logo_path.stem}.png",
                file=sys.stderr,
            )
            return

    master = prs.slide_masters[0]
    sw = prs.slide_width
    sh = prs.slide_height

    width_emu = int(logo.get("width_px", 160) * _EMU_PER_PX)
    offset = logo.get("offset") or {}
    pos = logo.get("position", "top-right")

    top_emu = int(offset.get("top", 35) * _EMU_PER_PX)
    right_emu = int(offset.get("right", 50) * _EMU_PER_PX)
    bottom_emu = int(offset.get("bottom", 35) * _EMU_PER_PX)
    left_emu = int(offset.get("left", 50) * _EMU_PER_PX)

    # Compute height from intrinsic aspect so the logo isn't squashed
    try:
        with PILImage.open(logo_path) as im:
            iw, ih = im.size
    except Exception as e:
        print(f"warning: pptx: cannot read logo {logo_path.name}: {e}", file=sys.stderr)
        return
    height_emu = int(width_emu * (ih / iw)) if iw else width_emu

    if pos == "top-right":
        left, top = sw - width_emu - right_emu, top_emu
    elif pos == "top-left":
        left, top = left_emu, top_emu
    elif pos == "bottom-right":
        left, top = sw - width_emu - right_emu, sh - bottom_emu - height_emu
    elif pos == "bottom-left":
        left, top = left_emu, sh - bottom_emu - height_emu
    else:
        left, top = sw - width_emu - right_emu, top_emu  # default top-right

    # python-pptx 1.x: BaseSlidePart.get_or_add_image_part returns a (part, rId)
    # tuple — it already creates the relationship internally. Calling relate_to
    # again would register a second, malformed rel pointing at the tuple itself.
    _, rId = master.part.get_or_add_image_part(str(logo_path))

    shape_id = master.shapes._next_shape_id
    pic = CT_Picture.new_pic(
        shape_id, "Brand Logo", "Brand Logo", rId,
        x=left, y=top, cx=width_emu, cy=height_emu,
    )
    master.element.spTree.append(pic)
