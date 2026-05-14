"""Brand spec schema validator with WCAG contrast checks.

Two layers:
  1. Schema — required fields, hex format, slug-safe identifiers, logo path
  2. WCAG  — body-text pairs are HARD ERRORS, brand-color pairs are WARNINGS

Returns (errors, warnings). The CLI uses the split to map onto exit codes.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# yaml is loaded by the caller (new_theme.py) and the spec is passed in pre-parsed.

from _generators._common import contrast_ratio, resolve_token  # noqa: E402

SCHEMA_VERSION = 1

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_SHORT_RE = re.compile(r"^[a-z][a-z0-9-]{1,30}$")

# AA body-text contrast threshold per WCAG 2.1.
_AA_BODY = 4.5
# AA large-text threshold (used only as advisory in warnings).
_AA_LARGE = 3.0


@dataclass
class Issue:
    severity: str  # "error" | "warn"
    code: str
    message: str
    path: str | None = None  # JSON-pointer-ish path into the spec


@dataclass
class ValidationResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate(spec: dict, spec_path: Path, *, run_wcag: bool = True) -> ValidationResult:
    """Validate a parsed brand spec.

    spec_path is the brand.yaml location used to resolve relative file references
    (logo.path) — passed in rather than discovered so the caller controls cwd.
    """
    r = ValidationResult()
    _validate_version(spec, r)
    _validate_brand(spec, r)
    palette = _validate_palette(spec, r)
    _validate_typography(spec, r)
    _validate_spacing(spec, r)
    _validate_logo(spec, spec_path, r)
    _validate_footer(spec, r)
    _validate_variants(spec, r)
    if run_wcag and palette is not None:
        _validate_wcag(palette, r)
    _warn_unknown_keys(spec, r)
    return r


# ─── Section validators ──────────────────────────────────────────────────────


def _validate_version(spec, r):
    v = spec.get("version")
    if v is None:
        r.errors.append(Issue("error", "version_missing",
                              "spec missing required `version` field (must be 1)",
                              path="version"))
        return
    if not isinstance(v, int) or v < 1:
        r.errors.append(Issue("error", "version_invalid",
                              f"`version` must be a positive integer, got {v!r}",
                              path="version"))
        return
    if v > SCHEMA_VERSION:
        r.warnings.append(Issue("warn", "version_future",
                                f"spec version {v} is newer than this validator's "
                                f"v{SCHEMA_VERSION} — unknown fields will be ignored",
                                path="version"))


def _validate_brand(spec, r):
    b = spec.get("brand")
    if not isinstance(b, dict):
        r.errors.append(Issue("error", "brand_missing",
                              "spec missing required `brand` section",
                              path="brand"))
        return
    if not b.get("name"):
        r.errors.append(Issue("error", "brand_name_missing",
                              "`brand.name` is required",
                              path="brand.name"))
    short = b.get("short")
    if not short:
        r.errors.append(Issue("error", "brand_short_missing",
                              "`brand.short` is required (slug-safe identifier)",
                              path="brand.short"))
    elif not _SHORT_RE.match(short):
        r.errors.append(Issue("error", "brand_short_invalid",
                              f"`brand.short` must match [a-z][a-z0-9-]{{1,30}}, got {short!r}",
                              path="brand.short"))


def _validate_palette(spec, r) -> dict | None:
    p = spec.get("palette")
    if not isinstance(p, dict):
        r.errors.append(Issue("error", "palette_missing",
                              "spec missing required `palette` section",
                              path="palette"))
        return None
    required = ["text", "bg", "primary"]
    for key in required:
        if not p.get(key):
            r.errors.append(Issue("error", "palette_required",
                                  f"`palette.{key}` is required",
                                  path=f"palette.{key}"))
    # Validate hex format on every color-bearing field
    for key, value in p.items():
        if value is None:
            continue
        if isinstance(value, dict):
            # nested (e.g. inverse: {text, bg})
            for sub_key, sub_val in value.items():
                if sub_val is None or _is_token_ref(sub_val):
                    continue
                if isinstance(sub_val, str) and not _HEX_RE.match(sub_val):
                    r.errors.append(Issue("error", "palette_hex_invalid",
                                          f"`palette.{key}.{sub_key}` must be #RRGGBB or token name, got {sub_val!r}",
                                          path=f"palette.{key}.{sub_key}"))
            continue
        if _is_token_ref(value):
            continue
        if not _HEX_RE.match(value):
            r.errors.append(Issue("error", "palette_hex_invalid",
                                  f"`palette.{key}` must be #RRGGBB or token name, got {value!r}",
                                  path=f"palette.{key}"))
    return p


def _is_token_ref(v) -> bool:
    return isinstance(v, str) and not v.startswith("#") and v.replace("_", "").isalnum()


def _validate_typography(spec, r):
    t = spec.get("typography")
    if t is None:
        return  # all optional; defaults applied by generators
    if not isinstance(t, dict):
        r.errors.append(Issue("error", "typography_invalid",
                              "`typography` must be a mapping",
                              path="typography"))
        return
    for key in ("body", "headings", "mono"):
        v = t.get(key)
        if v is None:
            continue
        if not isinstance(v, list) or not all(isinstance(s, str) for s in v):
            r.errors.append(Issue("error", "font_stack_invalid",
                                  f"`typography.{key}` must be a list of font names",
                                  path=f"typography.{key}"))
    # Font availability check (best effort — only if fc-list is on PATH)
    body = t.get("body")
    if body and shutil.which("fc-list"):
        primary_font = body[0]
        try:
            res = subprocess.run(
                ["fc-list", ":family"],
                capture_output=True, text=True, timeout=3,
            )
            if res.returncode == 0 and primary_font.lower() not in res.stdout.lower():
                r.warnings.append(Issue("warn", "font_missing",
                                        f"primary body font {primary_font!r} not found by fc-list — "
                                        "stack fallbacks will be used",
                                        path="typography.body[0]"))
        except (subprocess.TimeoutExpired, OSError):
            pass


def _validate_spacing(spec, r):
    s = spec.get("spacing")
    if s is None:
        return
    if not isinstance(s, dict):
        r.errors.append(Issue("error", "spacing_invalid",
                              "`spacing` must be a mapping",
                              path="spacing"))
        return
    pad = s.get("slide_padding")
    if pad is None:
        return
    for side in ("top", "right", "bottom", "left"):
        v = pad.get(side)
        if v is not None and not isinstance(v, (int, float)):
            r.errors.append(Issue("error", "spacing_value_invalid",
                                  f"`spacing.slide_padding.{side}` must be a number, got {v!r}",
                                  path=f"spacing.slide_padding.{side}"))


def _validate_logo(spec, spec_path: Path, r):
    logo = spec.get("logo")
    if logo is None:
        return
    if not isinstance(logo, dict):
        r.errors.append(Issue("error", "logo_invalid", "`logo` must be a mapping", path="logo"))
        return
    path = logo.get("path")
    if path:
        # Resolve relative to brand.yaml location, NOT cwd
        resolved = (spec_path.parent / path).resolve()
        if not resolved.exists():
            r.errors.append(Issue("error", "logo_not_found",
                                  f"`logo.path` not found at resolved path: {resolved}",
                                  path="logo.path"))
    pos = logo.get("position", "top-right")
    if pos not in {"top-right", "top-left", "bottom-right", "bottom-left", "none"}:
        r.errors.append(Issue("error", "logo_position_invalid",
                              f"`logo.position` must be one of top-right/top-left/bottom-right/bottom-left/none, got {pos!r}",
                              path="logo.position"))


def _validate_footer(spec, r):
    f = spec.get("footer")
    if f is None:
        return
    if not isinstance(f, dict):
        r.errors.append(Issue("error", "footer_invalid", "`footer` must be a mapping", path="footer"))


def _validate_variants(spec, r):
    v = spec.get("variants")
    if v is None:
        return
    if not isinstance(v, dict):
        r.errors.append(Issue("error", "variants_invalid", "`variants` must be a mapping", path="variants"))
        return
    known = {"title", "section", "two_column"}
    for key in v.keys():
        if key not in known:
            r.warnings.append(Issue("warn", "variant_unknown",
                                    f"unknown variant {key!r} (known: {sorted(known)})",
                                    path=f"variants.{key}"))


def _validate_wcag(palette: dict, r):
    text = palette.get("text")
    bg = palette.get("bg")
    if not text or not bg:
        return  # already errored above
    # Hard errors — body text contrast pairs
    for fg_path, bg_path in (
        ("palette.text", "palette.bg"),
    ):
        fg = palette.get(fg_path.split(".")[-1])
        bgv = palette.get(bg_path.split(".")[-1])
        if not fg or not bgv:
            continue
        try:
            ratio = contrast_ratio(fg, bgv)
        except ValueError:
            continue  # bad hex already errored
        if ratio < _AA_BODY:
            r.errors.append(Issue("error", "wcag_body_fail",
                                  f"{fg_path} on {bg_path} contrast {ratio:.2f}:1 is below "
                                  f"WCAG AA body-text threshold {_AA_BODY}:1",
                                  path=fg_path))
    # text on bg_alt (code blocks contain body-style text)
    bg_alt = palette.get("bg_alt")
    if bg_alt and text:
        try:
            ratio = contrast_ratio(text, bg_alt)
            if ratio < _AA_BODY:
                r.errors.append(Issue("error", "wcag_body_fail",
                                      f"palette.text on palette.bg_alt contrast {ratio:.2f}:1 is below "
                                      f"WCAG AA body-text threshold {_AA_BODY}:1",
                                      path="palette.text"))
        except ValueError:
            pass
    # inverse pair
    inverse = palette.get("inverse")
    if isinstance(inverse, dict):
        try:
            inv_text = resolve_token(inverse.get("text"), {**palette, "white": "#FFFFFF", "black": "#000000"})
            inv_bg = resolve_token(inverse.get("bg"), {**palette, "white": "#FFFFFF", "black": "#000000"})
            if inv_text and inv_bg:
                ratio = contrast_ratio(inv_text, inv_bg)
                if ratio < _AA_BODY:
                    r.errors.append(Issue("error", "wcag_body_fail",
                                          f"palette.inverse.text on palette.inverse.bg contrast "
                                          f"{ratio:.2f}:1 is below WCAG AA body-text threshold {_AA_BODY}:1",
                                          path="palette.inverse"))
        except ValueError as e:
            r.errors.append(Issue("error", "palette_inverse_unresolved",
                                  f"could not resolve palette.inverse: {e}",
                                  path="palette.inverse"))

    # Warnings — brand colors on bg (heading-style usage; AA Large is 3:1)
    for key in ("primary", "secondary", "primary_soft", "accent"):
        v = palette.get(key)
        if not v:
            continue
        try:
            ratio = contrast_ratio(v, bg)
        except ValueError:
            continue
        if ratio < _AA_BODY:
            severity_note = "below AA body 4.5:1"
            if ratio < _AA_LARGE:
                severity_note = "below AA Large 3:1"
            r.warnings.append(Issue("warn", "wcag_brand_warn",
                                    f"palette.{key} on palette.bg contrast {ratio:.2f}:1 ({severity_note}) — "
                                    "fine for decorative use, may fail accessibility for heading text",
                                    path=f"palette.{key}"))


_KNOWN_TOP_LEVEL = {"version", "brand", "palette", "typography", "spacing",
                    "logo", "footer", "variants", "overrides"}


def _warn_unknown_keys(spec, r):
    if not isinstance(spec, dict):
        return
    for k in spec.keys():
        if k not in _KNOWN_TOP_LEVEL:
            r.warnings.append(Issue("warn", "unknown_key",
                                    f"unknown top-level key {k!r} (known: {sorted(_KNOWN_TOP_LEVEL)})",
                                    path=k))


# ─── CLI entrypoint (only for direct invocation; main is via new_theme.py) ───


def _format_issue(i: Issue) -> str:
    where = f" [{i.path}]" if i.path else ""
    return f"  {i.severity}: {i.message}{where}"


if __name__ == "__main__":
    import argparse
    import yaml

    # Allow direct invocation: `python3 validate_brand.py brand.yaml`
    sys.path.insert(0, str(Path(__file__).parent))

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("brand_yaml", type=Path)
    ap.add_argument("--no-wcag", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    spec = yaml.safe_load(args.brand_yaml.read_text())
    if not isinstance(spec, dict):
        sys.exit(f"error: {args.brand_yaml} did not parse to a mapping")
    res = validate(spec, args.brand_yaml, run_wcag=not args.no_wcag)
    if args.json:
        import json
        print(json.dumps({
            "ok": res.ok,
            "errors": [vars(i) for i in res.errors],
            "warnings": [vars(i) for i in res.warnings],
        }, indent=2))
    else:
        if res.errors:
            print(f"validate_brand: {len(res.errors)} error(s):")
            for i in res.errors:
                print(_format_issue(i))
        if res.warnings:
            print(f"validate_brand: {len(res.warnings)} warning(s):")
            for i in res.warnings:
                print(_format_issue(i))
        if not res.errors and not res.warnings:
            print("validate_brand: clean")
    sys.exit(0 if res.ok else 1)
