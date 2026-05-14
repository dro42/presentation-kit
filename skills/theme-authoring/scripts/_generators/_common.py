"""Shared helpers for theme generators.

Pure stdlib. Provides safe template substitution, token resolution,
WCAG luminance computation, and a TeX math protection helper for Beamer.
"""
from __future__ import annotations

import re
from pathlib import Path
from string import Template


def safe_substitute_tmpl(template_path: Path, tokens: dict[str, str]) -> str:
    """Read a .tmpl file and fill ${name} placeholders.

    Uses Template.safe_substitute so unknown ${...} markers are preserved
    rather than raising — this means a template can carry literal $price
    text without breaking, and missing tokens become visible in the output
    instead of silently exploding.
    """
    text = template_path.read_text(encoding="utf-8")
    return Template(text).safe_substitute(tokens)


_MATH_RE = re.compile(r"(\$[^$\n]+\$|\$\$.+?\$\$)", re.DOTALL)


def protect_tex_math(content: str, transform):
    """Apply `transform` to non-math regions of LaTeX content.

    Splits on inline ($...$) and display ($$...$$) math, runs transform on
    the surrounding text, leaves math regions verbatim, rejoins.

    Used by the Beamer generator so any ${...} placeholders inside math
    aren't consumed by Template substitution.
    """
    parts = _MATH_RE.split(content)
    return "".join(
        part if (i % 2 == 1) else transform(part) for i, part in enumerate(parts)
    )


_TOKEN_REF_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def resolve_token(value, palette: dict[str, str]) -> str | None:
    """Resolve a brand-spec value that may be a literal hex or a palette token name.

    Returns None when value is None (e.g. palette.accent: null).
    Raises ValueError when value is a string that's neither hex nor a known token.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"expected string or null, got {type(value).__name__}: {value!r}")
    if value.startswith("#"):
        return value
    if _TOKEN_REF_RE.match(value):
        if value not in palette:
            raise ValueError(f"token reference {value!r} not found in palette")
        ref = palette[value]
        if isinstance(ref, str) and ref.startswith("#"):
            return ref
        if ref is None:
            raise ValueError(f"token reference {value!r} resolves to null")
        return resolve_token(ref, palette)
    raise ValueError(f"unrecognized color value: {value!r}")


def normalize_palette(palette: dict) -> dict:
    """Resolve token refs and ensure canonical surface tokens have fallbacks.

    Returns a flat dict {token_name: hex_string_or_None} with these guarantees:
      - 'text', 'bg', 'primary' are present (validator already enforces this)
      - 'secondary', 'primary_soft' fall back to 'primary' if absent
      - 'bg_alt' falls back to 'bg' if absent
      - 'rule' falls back to 'primary' if absent
      - 'rule_soft' falls back to 'rule' if absent
      - 'accent' is present as None when null/absent (so callers can test truthiness)

    Subdocs like palette.inverse / palette.code are NOT included; callers
    handle those separately because their resolution depends on the
    fallback semantics (e.g. inverse.bg defaults to 'primary').
    """
    pal: dict = {}
    for k, v in palette.items():
        if isinstance(v, dict):
            continue
        pal[k] = resolve_token(v, palette)
    pal.setdefault("secondary", pal["primary"])
    pal.setdefault("primary_soft", pal["primary"])
    pal.setdefault("bg_alt", pal["bg"])
    pal.setdefault("rule", pal["primary"])
    pal.setdefault("rule_soft", pal["rule"])
    pal.setdefault("accent", None)
    return pal


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """#RRGGBB → (r, g, b) integer triple."""
    h = hex_str.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected 6-digit hex, got {hex_str!r}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _channel_luminance(c: int) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_str: str) -> float:
    """WCAG 2.1 relative luminance from sRGB hex (range 0..1)."""
    r, g, b = hex_to_rgb(hex_str)
    return 0.2126 * _channel_luminance(r) + 0.7152 * _channel_luminance(g) + 0.0722 * _channel_luminance(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """WCAG contrast ratio (1:1 worst, 21:1 best). AA body text needs 4.5:1."""
    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter, darker = (l1, l2) if l1 > l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)
