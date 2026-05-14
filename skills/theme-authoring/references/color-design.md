# Color design — WCAG, palette tips, why the body/brand split

This document covers the color model behind the brand spec: the WCAG contrast checks the validator runs, why body-text and brand-color failures get different exit-code treatment, and a few practical guardrails for designing a palette that passes (or that intentionally trades contrast for brand identity).

## WCAG 2.1 contrast in 60 seconds

The W3C accessibility model says text needs to be readable by people with low vision. The threshold is a numeric ratio of **relative luminance** between foreground and background:

| Threshold | Use case |
|---|---|
| **4.5:1** | AA "normal" body text — required for any text < 18pt regular or < 14pt bold. |
| **3:1** | AA "large" text — applies to text ≥ 18pt regular or ≥ 14pt bold (headings often qualify). |
| **7:1** | AAA "normal" — strictest level; most brands don't aim for this. |
| **4.5:1** | AAA "large" — same as AA normal. |

Relative luminance is a perceptual measurement, not just hex distance. `#FFFFFF` on `#000000` is 21:1 (the maximum). `#666666` on `#FFFFFF` is 5.74:1 (passes AA body). `#999999` on `#FFFFFF` is 2.85:1 (fails AA body, fails AA large).

The validator computes contrast via the WCAG 2.1 formula in `_generators/_common.py:contrast_ratio()` — pure stdlib, no `colormath` dependency.

## Why body-text vs brand-color split

Reading text is non-negotiable. If body-text contrast is too low, the deck is unreadable for the lowest-vision audience member, and it's also harder for everyone in bright rooms or projector-glare scenarios. So the validator gates generation on body-text pairs:

**Hard error (blocks generation, exit 1):**
- `palette.text` on `palette.bg` — main body text on slide background.
- `palette.text` on `palette.bg_alt` — body text appears in code blocks and blockquotes; same threshold applies.
- `palette.inverse.text` on `palette.inverse.bg` — section-divider slides also contain body-style text.

These three pairs must all clear AA 4.5:1. No exceptions, no warnings — exit 1 with an error.

Brand colors are different. They're often used for:

- **Headings** (h1, h2) — large text, AA Large 3:1 applies, often passes even when AA body 4.5:1 doesn't.
- **Decorative surfaces** (rules, borders, brand strips) — no text inside, no accessibility requirement.
- **Hero/lead slides** — large display text where AA Large applies.

A brand whose `primary` color is a soft sky blue (`#7897AC`) probably *intentionally* fails AA body on white but is fine for an h2 heading. Failing the build is wrong; flagging it as a warning is right.

**Warning (does not block, exit 1 unless `--no-fail-on-warn`):**
- `palette.primary` on `palette.bg`
- `palette.secondary` on `palette.bg`
- `palette.primary_soft` on `palette.bg`
- `palette.accent` on `palette.bg`

The exit-code default still surfaces the warning (a careful brand author should know about the contrast trade-off), but `--no-fail-on-warn` lets CI accept the trade as an informed decision.

```bash
# Failing body-text contrast — always exit 1
python3 scripts/new_theme.py bad-brand.yaml --validate-only
# error: palette.text on palette.bg contrast 1.27:1 is below WCAG AA body-text threshold 4.5:1

# Failing brand-color contrast — exit 1 by default, exit 0 with the flag
python3 scripts/new_theme.py soft-brand.yaml --validate-only
# warn: palette.primary on palette.bg contrast 2.91:1 (below AA body 4.5:1) — fine for decorative use, may fail accessibility for heading text

python3 scripts/new_theme.py soft-brand.yaml --validate-only --no-fail-on-warn
# exit 0
```

## How the validator computes contrast

```python
# from _generators/_common.py (verbatim)
def relative_luminance(hex_str: str) -> float:
    r, g, b = hex_to_rgb(hex_str)
    return 0.2126 * _channel_luminance(r) \
         + 0.7152 * _channel_luminance(g) \
         + 0.0722 * _channel_luminance(b)

def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    l1 = relative_luminance(fg_hex)
    l2 = relative_luminance(bg_hex)
    lighter, darker = (l1, l2) if l1 > l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)
```

Symmetric: `contrast_ratio(fg, bg) == contrast_ratio(bg, fg)`. The `+ 0.05` term is the WCAG flare offset that prevents division-by-zero and accounts for ambient screen reflection. Returns are between 1.0 (no contrast) and 21.0 (white on black).

## Palette design tips

### Pick body text and bg first; everything else follows

Body text is the constraint that gates generation. Choose `text` and `bg` first, verify contrast clears 4.5:1 (the validator does this for you), THEN pick brand colors. Trying to "make brand colors work" by tweaking body text leads to gray-on-white horrors.

Three safe body-text patterns:

| `text` | `bg` | Ratio | Notes |
|---|---|---|---|
| `#1A1A1A` | `#FFFFFF` | 17.59:1 | Default near-black on white. AAA-clean. |
| `#212529` | `#F8F9FA` | 15.05:1 | Bootstrap's defaults — slightly softer; still AAA. |
| `#FFFFFF` | `#1A1A1A` | 17.59:1 | Inverted (dark mode). |

Avoid `#666` on `#fff` (5.74:1 — passes AA but fails AAA, often looks washed out at small sizes on projectors).

### Brand primary: heading-readable preferred

If `palette.primary` is used for h1 and h2 (the default), aim for AA Large (3:1) at minimum on bg. Below 3:1, even large text is hard to read in the back of a lecture hall.

| `primary` on `#FFFFFF` | Ratio | Verdict |
|---|---|---|
| `#005FB8` (Microsoft blue) | 6.50:1 | AA body — comfortable for h1/h2/h3/links. |
| `#36566D` (HCW petrol) | 8.69:1 | AA body — generous. |
| `#7897AC` (HCW soft tint) | 2.91:1 | Fails AA Large — decorative use only, not for headings. |

The HCW spec uses `#36566D` as primary (h1, h2 base) and `#7897AC` as `primary_soft` (h3, subtitles where the lower contrast is intentional and acceptable). This is the standard pattern: pick a solid primary for headings, derive a soft variant for subtitles/de-emphasis.

### Inverse pair: same threshold

Section-divider slides ("invert" in Marp, `\section{}` in Beamer) contain real text that someone has to read. The `palette.inverse.text` on `palette.inverse.bg` pair gets the same 4.5:1 hard-error treatment as body text.

The default `inverse: { text: "white", bg: "primary" }` works as long as your `primary` is dark enough. `#36566D` on `#FFFFFF` is fine. `#7897AC` on `#FFFFFF` would fail.

### Decorative-only colors don't have a threshold

`palette.rule`, `palette.rule_soft`, `palette.bg_alt` (when used purely as a background tint with no text on it) have no WCAG requirement. The validator doesn't check them. You're free to make `rule_soft` a barely-visible `#DDE3E8` tint.

Body text *on* `bg_alt` is checked because code blocks contain real text. If `bg_alt` is too dark for your text color, the validator catches it.

### Monochromatic identities

Some brands intentionally have no accent color — HCW is one (the HCW visual guidelines use only petrol-blue + slate-grey, deliberately no yellow). Set `palette.accent: null` to signal this. The marp generator omits the `--accent-color` CSS rule entirely; the Beamer generator omits the `BrandAccent` macro; the Slidev generator omits the variable. The pptx generator falls back to PowerPoint's Office default for accent4 (a soft purple), which is unobtrusive but technically present — see `references/per-format-notes.md`.

### Brand "soft" variants — the 0.5× luminance rule of thumb

A common pattern: `primary` for h1/h2 + brand surfaces, `primary_soft` for h3/subtitles. The soft variant should be ~0.5× the luminance of the primary at the same hue (lighter than primary, but darker than `bg`). HCW's `#36566D` → `#7897AC` is exactly this — same hue family, ~50 % more luminance. The result is a clear visual hierarchy (h1 strongest, h2 same family, h3 noticeably softer) without introducing a third color.

If you're choosing freehand: `primary_soft` should be perceptibly different from `primary`, never so similar they read as the same color, but in the same hue family so the brand stays coherent.

### Accent: the dangerous one

`palette.accent` is the most-likely-to-clash color. It exists for the deliberate "spot of the brand secondary" use — call-to-action button, important callout link, etc. The risk is using it for body text or backgrounds, which it almost certainly fails.

If your accent is bright (`#FF6600`, `#E63946`, etc.), it works as a decorative spot but fails AA on bg for normal text. The warning is informative; pass `--no-fail-on-warn` only when you've consciously confined accent to decorative use.

If you don't have an accent — set `accent: null`. Don't pick a "filler" color just to fill the slot.

## Tools for picking colors

External, no plugin dependency:

- **WebAIM Contrast Checker** — https://webaim.org/resources/contrastchecker/ — paste hex pairs, see the AA/AAA verdict.
- **Coolors** — https://coolors.co — palette generator with built-in contrast warnings.
- **Adobe Color** — https://color.adobe.com/create/color-accessibility — accessibility view for arbitrary palettes.

These give you the same numeric contrast ratio the validator computes; you can pre-check a brand spec before running it through `new_theme.py --validate-only`.

## When you intentionally need to skip WCAG

```bash
python3 scripts/new_theme.py brand.yaml --no-wcag
```

Skips both layers (body and brand). Reserve for cases where the deck is being generated for a non-projected medium (PDF reader, archived deck on a website with adjustable contrast modes). For any deck shown in a room, body-text WCAG should be honored.

## A note on perceptual color

WCAG 2.1 luminance is a 1990s-era model. It overpenalizes some color combinations (red/green) and underpenalizes others. WCAG 3.0's APCA model is more accurate but not standardized. We use 2.1 because:

1. It's the legal compliance bar in most jurisdictions.
2. The math is portable (10 lines of Python, stdlib only).
3. APCA isn't ratified yet; most checkers and design tools still use 2.1.

If you have an APCA-savvy designer who insists their palette is fine despite a 2.1 warning, trust the human and use `--no-fail-on-warn`.
