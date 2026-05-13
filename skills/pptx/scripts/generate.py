#!/usr/bin/env python3
"""
generate.py — produce a .pptx deck from a YAML spec via python-pptx.

Usage:
  python3 generate.py --content deck.yaml --output deck.pptx
  python3 generate.py --content deck.yaml --template ./brand.pptx --output deck.pptx
  python3 generate.py --content deck.yaml --validate-only

The YAML schema is documented in references/deck-yaml-spec.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml", file=sys.stderr)
    print("Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(127)

# Known layout names (mirrors LAYOUT_MAP in layouts.py — kept in sync).
# Declared here so --validate-only doesn't need to import python-pptx.
VALID_LAYOUTS: set[str] = {
    "title", "section", "bullets", "image",
    "two_column", "code", "quote", "end",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r") as f:
        return yaml.safe_load(f)


def validate(spec: dict[str, Any], yaml_dir: Path) -> list[str]:
    """Return a list of human-readable validation errors. Empty list = valid."""
    errors: list[str] = []

    if not isinstance(spec, dict):
        return ["top-level YAML must be a mapping"]

    if "meta" not in spec or not isinstance(spec["meta"], dict):
        errors.append("missing 'meta' top-level mapping")
    else:
        meta = spec["meta"]
        if not meta.get("title"):
            errors.append("meta.title is required")

    if "slides" not in spec or not isinstance(spec["slides"], list):
        errors.append("missing 'slides' top-level list")
        return errors  # can't validate further without slides

    for i, slide in enumerate(spec["slides"]):
        prefix = f"slides[{i}]"
        if not isinstance(slide, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue

        layout = slide.get("layout")
        if not layout:
            errors.append(f"{prefix}: missing 'layout' field")
            continue
        if layout not in VALID_LAYOUTS and not isinstance(layout, str):
            errors.append(f"{prefix}: 'layout' must be a string")
            continue
        if layout in VALID_LAYOUTS:
            # known layout — check required props
            if layout == "bullets" and not slide.get("bullets"):
                errors.append(f"{prefix}: layout=bullets requires 'bullets' list")
            if layout == "image":
                img = slide.get("image")
                if not img:
                    errors.append(f"{prefix}: layout=image requires 'image' path")
                else:
                    img_path = (yaml_dir / img).resolve() if not Path(img).is_absolute() else Path(img)
                    if not img_path.exists():
                        errors.append(f"{prefix}: image not found: {img_path}")
            if layout == "two_column":
                if not slide.get("left") and not slide.get("right"):
                    errors.append(f"{prefix}: layout=two_column requires 'left' and/or 'right'")
            if layout == "code":
                if not slide.get("code") and not slide.get("code_file"):
                    errors.append(f"{prefix}: layout=code requires 'code' or 'code_file'")
                if slide.get("code_file"):
                    cp = (yaml_dir / slide["code_file"]).resolve() if not Path(slide["code_file"]).is_absolute() else Path(slide["code_file"])
                    if not cp.exists():
                        errors.append(f"{prefix}: code_file not found: {cp}")
            if layout == "quote" and not slide.get("text"):
                errors.append(f"{prefix}: layout=quote requires 'text'")

    return errors


def build(spec: dict[str, Any], template: "Path | None", yaml_dir: Path):
    """Build a Presentation from the validated spec. Requires python-pptx."""
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except ImportError:
        print("Missing dependency: python-pptx", file=sys.stderr)
        print("Install with: pip install python-pptx Pillow", file=sys.stderr)
        sys.exit(127)

    # Import layouts.py here so it can pull in pptx
    sys.path.insert(0, str(Path(__file__).parent))
    from layouts import render_slide

    if template:
        prs = Presentation(str(template))
    else:
        prs = Presentation()

    # Apply aspect ratio if requested and no template (template wins otherwise)
    meta = spec.get("meta", {})
    if not template:
        aspect = meta.get("aspect_ratio", "16:9")
        if aspect == "16:9":
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
        elif aspect == "4:3":
            prs.slide_width = Inches(10)
            prs.slide_height = Inches(7.5)
        elif aspect == "16:10":
            prs.slide_width = Inches(12)
            prs.slide_height = Inches(7.5)

    # Render each slide
    for slide_spec in spec.get("slides", []):
        render_slide(prs, slide_spec, yaml_dir)

    # Metadata
    core = prs.core_properties
    if meta.get("title"):
        core.title = meta["title"]
    if meta.get("author"):
        core.author = meta["author"]
    if meta.get("language"):
        core.language = meta["language"]

    return prs


def resolve_template(name_or_path: str | None) -> Path | None:
    """Resolve a template name to a real path. None if not specified."""
    if not name_or_path:
        return None

    p = Path(name_or_path).expanduser()
    if p.exists():
        return p.resolve()

    # Try XDG user-data
    import os
    xdg = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    user_dir = xdg / "presentation-kit" / "themes" / "pptx"
    candidate = user_dir / f"{name_or_path}.pptx"
    if candidate.exists():
        return candidate

    # Try bundled
    bundled = Path(__file__).resolve().parent.parent / "assets" / "themes" / f"{name_or_path}.pptx"
    if bundled.exists():
        return bundled

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a .pptx deck from a YAML spec.")
    parser.add_argument("--content", required=True, help="Path to deck YAML")
    parser.add_argument("--output", default="deck.pptx", help="Output .pptx path (default: deck.pptx)")
    parser.add_argument("--template", help="Brand master template (name or path; falls back to XDG and bundled)")
    parser.add_argument("--validate-only", action="store_true", help="Validate the YAML; don't generate")
    args = parser.parse_args(argv)

    yaml_path = Path(args.content).resolve()
    if not yaml_path.exists():
        print(f"YAML file not found: {yaml_path}", file=sys.stderr)
        return 1

    spec = load_yaml(yaml_path)
    yaml_dir = yaml_path.parent

    errors = validate(spec, yaml_dir)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if args.validate_only:
        slide_count = len(spec.get("slides", []))
        print(f"OK: {yaml_path} ({slide_count} slides)")
        return 0

    template = None
    template_name = args.template or spec.get("meta", {}).get("template")
    if template_name:
        template = resolve_template(template_name)
        if not template:
            print(f"Warning: template '{template_name}' not found; using python-pptx default", file=sys.stderr)

    prs = build(spec, template, yaml_dir)

    out_path = Path(args.output).resolve()
    prs.save(str(out_path))
    print(f"Wrote {out_path} ({len(prs.slides)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
