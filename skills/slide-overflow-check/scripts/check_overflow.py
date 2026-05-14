#!/usr/bin/env python3
"""
slide-overflow-check — detect text that collides with the footer band or
runs off the page in a rendered slide PDF.

Pure-stdlib. Requires `pdftotext` (poppler-utils). Format-agnostic — works
on any PDF (Marp, Beamer, Slidev, pptx-via-LibreOffice).

See ../SKILL.md for usage and ../references/algorithm.md for tuning notes.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Iterable
from xml.etree import ElementTree as ET


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Word:
    page: int
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float

@dataclass
class Page:
    number: int
    width: float
    height: float
    words: list[Word] = field(default_factory=list)

@dataclass
class Issue:
    page: int
    severity: str             # "error" | "warn"
    kind: str                 # "footer_collision" | "page_bottom" | …
    text: str
    bbox: dict
    page_size: dict
    threshold_used: float | None


# ─── Step 1: extract bboxes via pdftotext ────────────────────────────────────

NS_STRIP = re.compile(rb' xmlns(:\w+)?="[^"]+"')

def extract_pages(pdf_path: str) -> list[Page]:
    if shutil.which("pdftotext") is None:
        sys.exit(
            "error: `pdftotext` is required but not on PATH.\n"
            "  install: brew install poppler\n"
            "  (Homebrew on macOS, ~5s; or apt-get install poppler-utils on Linux)"
        )

    proc = subprocess.run(
        ["pdftotext", "-bbox-layout", pdf_path, "-"],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        sys.exit(f"error: pdftotext failed (exit {proc.returncode}):\n{proc.stderr.decode(errors='replace')}")

    # Strip the xmlns so ElementTree XPath stays readable.
    xhtml = NS_STRIP.sub(b"", proc.stdout)
    root = ET.fromstring(xhtml)

    pages: list[Page] = []
    for i, page_el in enumerate(root.iter("page"), start=1):
        try:
            width = float(page_el.attrib["width"])
            height = float(page_el.attrib["height"])
        except (KeyError, ValueError) as e:
            sys.exit(f"error: page {i} missing width/height in pdftotext output ({e})")

        page = Page(number=i, width=width, height=height)
        for word_el in page_el.iter("word"):
            try:
                page.words.append(Word(
                    page=i,
                    text=(word_el.text or "").strip(),
                    x_min=float(word_el.attrib["xMin"]),
                    y_min=float(word_el.attrib["yMin"]),
                    x_max=float(word_el.attrib["xMax"]),
                    y_max=float(word_el.attrib["yMax"]),
                ))
            except (KeyError, ValueError):
                continue
        pages.append(page)

    # Self-test: silent false-clean is the failure mode to prevent above all else.
    if not pages:
        sys.exit(
            "error: pdftotext returned 0 pages.\n"
            "  this usually means the XHTML namespace handling broke — file a bug.\n"
            f"  raw bytes: {len(proc.stdout)}, head: {proc.stdout[:200]!r}"
        )
    return pages


# ─── Step 2: detect the recurring footer cluster ─────────────────────────────

def detect_footer(
    pages: list[Page],
    footer_band_pct: float,
    coverage_pct: float,
) -> tuple[set[Word], float | None]:
    """
    Returns (footer_words, footer_text_top).

    footer_words: every Word that belongs to a recurring footer cluster.
                  These are excluded from overflow flagging.
    footer_text_top: yMin of the topmost word in the canonical (widest-
                     coverage) cluster. None if no cluster qualified.
    """
    # Group bottom-band words across pages by quantized (x_band, y_band) position.
    # Quantize to 10pt buckets so per-page page-numbers ("1", "2", "3", …)
    # at the same screen position end up in the same cluster.
    BUCKET = 10.0

    bottom_words_by_page: dict[int, list[Word]] = defaultdict(list)
    body_positions_by_page: dict[int, set[tuple[int, int]]] = defaultdict(set)

    for p in pages:
        band_top = p.height * (1 - footer_band_pct)
        for w in p.words:
            key = (round(w.x_min / BUCKET), round(w.y_min / BUCKET))
            if w.y_min >= band_top:
                bottom_words_by_page[p.number].append(w)
            else:
                body_positions_by_page[p.number].add(key)

    # Denominator: pages that have at least one word in the bottom band
    # (i.e., paginated pages). Excludes title slides with paginate: false.
    paginated_pages = [p for p in pages if bottom_words_by_page[p.number]]
    if not paginated_pages:
        return set(), None

    # Group bottom-band words across pages by position.
    cluster_pages: dict[tuple[int, int], set[int]] = defaultdict(set)
    cluster_words: dict[tuple[int, int], list[Word]] = defaultdict(list)
    for page_num, words in bottom_words_by_page.items():
        for w in words:
            key = (round(w.x_min / BUCKET), round(w.y_min / BUCKET))
            cluster_pages[key].add(page_num)
            cluster_words[key].append(w)

    # A position is a footer cluster if:
    #   (a) it appears on ≥ coverage_pct of paginated pages, AND
    #   (b) it does NOT appear in body content (top 1-band) on any page —
    #       prevents misclassifying a repeating below-footer overflow as
    #       "the footer" and silencing it.
    threshold = max(2, int(len(paginated_pages) * coverage_pct))
    footer_keys: set[tuple[int, int]] = set()
    for key, page_set in cluster_pages.items():
        if len(page_set) < threshold:
            continue
        if any(key in body_positions_by_page[p.number] for p in pages):
            continue
        footer_keys.add(key)

    if not footer_keys:
        return set(), None

    footer_words = {w for key in footer_keys for w in cluster_words[key]}

    # Canonical footer text top = yMin of the highest word in the
    # widest-coverage cluster. (If two clusters tie, take the lower one —
    # safer for clearance.)
    canonical_key = max(footer_keys, key=lambda k: (len(cluster_pages[k]), -k[1]))
    canonical_words = cluster_words[canonical_key]
    footer_text_top = min(w.y_min for w in canonical_words)

    return footer_words, footer_text_top


# ─── Step 3: flag overflow per page ──────────────────────────────────────────

def find_issues(
    pages: list[Page],
    footer_words: set[Word],
    safe_zone_top: float | None,
    hard_boundary_pct: float,
    epsilon: float,
) -> list[Issue]:
    issues: list[Issue] = []

    for p in pages:
        # Zero-word page → warn, can't analyze.
        if not p.words:
            issues.append(Issue(
                page=p.number,
                severity="warn",
                kind="not_analyzable",
                text="<no extracted text>",
                bbox={},
                page_size={"width": p.width, "height": p.height},
                threshold_used=None,
            ))
            continue

        # Determine the effective vertical limit for this page.
        if safe_zone_top is not None:
            v_limit = safe_zone_top
            v_kind = "footer_collision"
            no_footer_warn_limit = None
        else:
            v_limit = p.height * hard_boundary_pct
            v_kind = "page_bottom"
            no_footer_warn_limit = p.height * 0.95

        for w in p.words:
            if w in footer_words:
                continue

            # Off-canvas (hard errors).
            if w.x_max > p.width + epsilon:
                issues.append(_mk_issue(p, w, "error", "off_canvas_right", p.width))
                continue
            if w.x_min < -epsilon:
                issues.append(_mk_issue(p, w, "error", "off_canvas_left", 0.0))
                continue
            if w.y_min < -epsilon:
                issues.append(_mk_issue(p, w, "error", "off_canvas_top", 0.0))
                continue
            if w.y_max > p.height + epsilon:
                issues.append(_mk_issue(p, w, "error", "off_canvas_bottom", p.height))
                continue

            # Footer-band collision (or hard-bottom in no-footer case).
            if w.y_max > v_limit + epsilon:
                issues.append(_mk_issue(p, w, "error", v_kind, v_limit))
                continue

            # Soft warn for "near edge but not crossing" when no footer was detected.
            if no_footer_warn_limit is not None and w.y_max > no_footer_warn_limit + epsilon:
                issues.append(_mk_issue(p, w, "warn", "near_page_edge", no_footer_warn_limit))

    return issues


def _mk_issue(p: Page, w: Word, severity: str, kind: str, threshold: float) -> Issue:
    return Issue(
        page=p.number,
        severity=severity,
        kind=kind,
        text=w.text,
        bbox={"xMin": w.x_min, "yMin": w.y_min, "xMax": w.x_max, "yMax": w.y_max},
        page_size={"width": p.width, "height": p.height},
        threshold_used=threshold,
    )


# ─── Step 4: report ──────────────────────────────────────────────────────────

def merge_adjacent_issues(issues: list[Issue]) -> list[Issue]:
    """Collapse word-level issues into sentence-level issues per page+kind."""
    merged: list[Issue] = []
    by_page_kind: dict[tuple[int, str, str], list[Issue]] = defaultdict(list)
    for iss in issues:
        by_page_kind[(iss.page, iss.severity, iss.kind)].append(iss)

    for (page, sev, kind), group in sorted(by_page_kind.items()):
        if not group:
            continue
        if kind == "not_analyzable":
            merged.append(group[0])
            continue
        # Sort by reading order, then merge text.
        group.sort(key=lambda i: (i.bbox.get("yMin", 0), i.bbox.get("xMin", 0)))
        text = " ".join(i.text for i in group if i.text).strip()
        # Compose a unioned bbox.
        bbox = {
            "xMin": min(i.bbox["xMin"] for i in group),
            "yMin": min(i.bbox["yMin"] for i in group),
            "xMax": max(i.bbox["xMax"] for i in group),
            "yMax": max(i.bbox["yMax"] for i in group),
        }
        merged.append(Issue(
            page=page,
            severity=sev,
            kind=kind,
            text=text,
            bbox=bbox,
            page_size=group[0].page_size,
            threshold_used=group[0].threshold_used,
        ))
    return merged


def render_text_report(
    pdf_path: str,
    pages: list[Page],
    footer_text_top: float | None,
    footer_clearance: float,
    safe_zone_top: float | None,
    issues: list[Issue],
    quiet: bool,
) -> str:
    lines = [f"slide-overflow-check: {pdf_path} — {len(pages)} pages, {len(issues)} issues"]
    if footer_text_top is not None:
        lines.append(
            f"  footer text top: y={footer_text_top:.0f}  ·  "
            f"clearance: {footer_clearance:.0f}pt  ·  "
            f"safe_zone_top: y={safe_zone_top:.0f}"
        )
    else:
        lines.append("  no recurring footer detected — using hard-boundary fallback")
    lines.append("")

    issue_pages = {i.page for i in issues}
    for iss in issues:
        ph = iss.page_size.get("height", 0)
        if iss.kind == "not_analyzable":
            lines.append(f"  Page {iss.page} — warn — not analyzable:")
            lines.append("    no extracted text (image-based or outlined-font page)")
        else:
            y_max = iss.bbox.get("yMax", 0)
            label = iss.kind.replace("_", " ")
            lines.append(f"  Page {iss.page} — {iss.severity} — {label}:")
            lines.append(
                f"    \"{iss.text}\" at yMax={y_max:.0f}/{ph:.0f} "
                f"(threshold {iss.threshold_used:.0f})"
            )
        lines.append("")

    if not quiet:
        clean = sorted(p.number for p in pages if p.number not in issue_pages)
        if clean:
            lines.append(f"  Pages {', '.join(str(n) for n in clean)}: clean")

    return "\n".join(lines).rstrip() + "\n"


def render_json_report(
    pdf_path: str,
    pages: list[Page],
    footer_text_top: float | None,
    footer_clearance: float,
    safe_zone_top: float | None,
    issues: list[Issue],
) -> str:
    payload = {
        "pdf_path": pdf_path,
        "pages_total": len(pages),
        "pages_with_issues": len({i.page for i in issues}),
        "footer_baseline": footer_text_top,
        "footer_clearance": footer_clearance,
        "safe_zone_top": safe_zone_top,
        "issues": [asdict(i) for i in issues],
    }
    return json.dumps(payload, indent=2) + "\n"


# ─── Main ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Detect text overflow / footer collisions in slide PDFs."
    )
    ap.add_argument("pdf_path", help="Path to the rendered slide PDF.")
    ap.add_argument("--footer-band-pct", type=float, default=0.15,
                    help="Fraction of page height (from bottom) to consider as footer zone (default 0.15)")
    ap.add_argument("--footer-coverage-pct", type=float, default=0.6,
                    help="Min coverage of paginated pages for a position to be a footer cluster (default 0.6)")
    ap.add_argument("--footer-clearance", type=float, default=20.0,
                    help="pt margin above footer text representing the visual band (default 20)")
    ap.add_argument("--hard-boundary-pct", type=float, default=0.97,
                    help="No-footer fallback boundary as fraction of page height (default 0.97)")
    ap.add_argument("--epsilon", type=float, default=0.5,
                    help="Float tolerance on boundary comparisons in pt (default 0.5)")
    ap.add_argument("--json", action="store_true",
                    help="Emit JSON report instead of human-readable text.")
    ap.add_argument("--no-fail-on-warn", action="store_true",
                    help="Exit 0 even when only warnings are present.")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress the trailing 'Pages …: clean' line.")
    args = ap.parse_args(argv)

    pages = extract_pages(args.pdf_path)
    footer_words, footer_text_top = detect_footer(
        pages, args.footer_band_pct, args.footer_coverage_pct
    )
    safe_zone_top = (
        footer_text_top - args.footer_clearance
        if footer_text_top is not None else None
    )
    raw_issues = find_issues(
        pages, footer_words, safe_zone_top,
        args.hard_boundary_pct, args.epsilon,
    )
    issues = merge_adjacent_issues(raw_issues)

    if args.json:
        sys.stdout.write(render_json_report(
            args.pdf_path, pages, footer_text_top,
            args.footer_clearance, safe_zone_top, issues,
        ))
    else:
        sys.stdout.write(render_text_report(
            args.pdf_path, pages, footer_text_top,
            args.footer_clearance, safe_zone_top, issues, args.quiet,
        ))

    has_error = any(i.severity == "error" for i in issues)
    has_warn = any(i.severity == "warn" for i in issues)
    if has_error:
        return 1
    if has_warn and not args.no_fail_on_warn:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
