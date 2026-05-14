"""Smoke render: build each format's canonical fixture deck → PDF.

This is the visual eyeball / overflow-gated verification described in the
plan §B. Distinct from tests/test_snapshots.py which only checks token
substitution: this actually drives the format's renderer end-to-end and,
if available, runs slide-overflow-check on the produced PDF.

Per-format render is SKIPPED (not failed) when the renderer isn't on
PATH. Exit code:
  0 — every attempted format produced a clean PDF (overflow-check OK)
  1 — at least one attempted render failed OR overflow-check fired

Usage:
  python3 -m tests.smoke_render               # all formats it can render
  python3 -m tests.smoke_render --formats marp,beamer
  python3 -m tests.smoke_render --keep        # leave the work dir
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SKILL_ROOT.parent.parent
HCW_SPEC = SKILL_ROOT / "examples" / "hcw-brand.yaml"
NEW_THEME = SKILL_ROOT / "scripts" / "new_theme.py"
FIXTURES = SKILL_ROOT / "fixtures"
OVERFLOW_CHECK = PLUGIN_ROOT / "skills" / "slide-overflow-check" / "scripts" / "check_overflow.py"

_VENV_PY = PLUGIN_ROOT / ".venv" / "bin" / "python3"
PYTHON = str(_VENV_PY) if _VENV_PY.exists() else sys.executable

ALL_FORMATS = ("marp", "beamer", "slidev", "pptx")


def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def _check_overflow(pdf: Path) -> tuple[bool, str]:
    """Run slide-overflow-check; return (ok, summary). Soft-skip if pdftotext missing.

    A negative exit code means pdftotext was killed by a signal — most
    commonly SIGABRT from a known poppler 26.04 regression on certain
    PDFs. We treat that as a *warning*, not a render failure, because
    the PDF itself rendered correctly; the downstream tool crashed.
    """
    if not OVERFLOW_CHECK.exists():
        return True, "(slide-overflow-check not installed)"
    if not _have("pdftotext"):
        return True, "(pdftotext not on PATH — skipping overflow check)"
    code, stdout, stderr = _run([sys.executable, str(OVERFLOW_CHECK), str(pdf)])
    summary = (stdout + stderr).strip().splitlines()
    headline = summary[0] if summary else ""
    if "pdftotext failed" in headline and "exit -" in headline:
        return True, f"warn: poppler crash on this PDF (downstream issue, render itself OK): {headline}"
    return code == 0, headline


# ── Per-format renderers ───────────────────────────────────────────────────


def render_marp(work: Path, generated: Path) -> tuple[str, str]:
    """Returns (status, detail). status in {'ok', 'skip', 'fail'}."""
    if not _have("marp"):
        return "skip", "marp CLI not on PATH (npm i -g @marp-team/marp-cli)"
    fixture = FIXTURES / "canonical-deck-marp.md"
    deck = work / "marp-deck.md"
    shutil.copy2(fixture, deck)
    css = generated / "marp" / "hcw.css"
    pdf = work / "marp.pdf"
    code, _, err = _run([
        "marp", str(deck),
        "--theme-set", str(css),
        "--allow-local-files",
        "--pdf", "-o", str(pdf),
    ])
    if code != 0:
        return "fail", f"marp render exit {code}: {err.strip()[:200]}"
    ok, summary = _check_overflow(pdf)
    return ("ok" if ok else "fail"), f"{pdf.name} ({pdf.stat().st_size}B); overflow: {summary}"


def render_beamer(work: Path, generated: Path) -> tuple[str, str]:
    if not _have("latexmk"):
        return "skip", "latexmk not on PATH (install MacTeX or TeX Live)"
    src_fixture = FIXTURES / "canonical-deck-beamer.tex"
    deck_dir = work / "beamer"
    deck_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_fixture, deck_dir / src_fixture.name)
    # Copy the generated .sty + logo (raster sibling required for pdfLaTeX)
    for f in (generated / "beamer").iterdir():
        shutil.copy2(f, deck_dir / f.name)
    # If the logo is SVG, ensure a raster sibling lives alongside.
    svg = deck_dir / "hcw-logo.svg"
    png = deck_dir / "hcw-logo.png"
    if svg.exists() and not png.exists():
        # Try the same fallback we ship in examples/
        examples_png = SKILL_ROOT / "examples" / "hcw-logo.png"
        if examples_png.exists():
            shutil.copy2(examples_png, png)
    code, out, err = _run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", src_fixture.name],
        cwd=deck_dir,
    )
    pdf = deck_dir / "canonical-deck-beamer.pdf"
    if code != 0 or not pdf.exists():
        # Surface last 6 lines of stderr/stdout as the most useful diagnostic
        tail = "\n".join((err or out).strip().splitlines()[-6:])
        return "fail", f"latexmk exit {code}; tail:\n{tail}"
    ok, summary = _check_overflow(pdf)
    return ("ok" if ok else "fail"), f"{pdf.name} ({pdf.stat().st_size}B); overflow: {summary}"


def render_slidev(work: Path, generated: Path) -> tuple[str, str]:
    if not _have("npx"):
        return "skip", "npx not on PATH (install Node.js)"
    deck_dir = work / "slidev"
    deck_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURES / "canonical-deck-slidev.md", deck_dir / "slides.md")
    src_theme = generated / "slidev" / "slidev-theme-hcw"
    shutil.copytree(src_theme, deck_dir / "slidev-theme-hcw")
    pdf = deck_dir / "slides-export.pdf"
    # The Slidev CLI ships as `@slidev/cli`, not bare `slidev` — `npx --yes
    # -p @slidev/cli slidev export ...` aliases the binary. The export
    # command also needs `playwright-chromium`; first invocation will offer
    # to install (~150MB). In a non-interactive context, that prompt fails
    # the run, which we surface as-is.
    code, out, err = _run(
        ["npx", "--yes", "-p", "@slidev/cli", "slidev", "export", "slides.md",
         "--output", str(pdf), "--format", "pdf"],
        cwd=deck_dir,
    )
    if code != 0 or not pdf.exists():
        combined = (err or "") + (out or "")
        if "playwright" in combined.lower():
            return "skip", "playwright-chromium not installed (npx playwright install chromium, ~150MB)"
        tail = "\n".join(combined.strip().splitlines()[-6:])
        return "fail", f"slidev export exit {code}; tail:\n{tail}"
    ok, summary = _check_overflow(pdf)
    return ("ok" if ok else "fail"), f"{pdf.name} ({pdf.stat().st_size}B); overflow: {summary}"


def render_pptx(work: Path, generated: Path) -> tuple[str, str]:
    """pptx 'render' = build the deck via skills/pptx/generate.py, then optionally
    convert to PDF for overflow-check via LibreOffice's headless soffice."""
    pptx_gen = PLUGIN_ROOT / "skills" / "pptx" / "scripts" / "generate.py"
    if not pptx_gen.exists():
        return "skip", "skills/pptx/scripts/generate.py not found"
    master = generated / "pptx" / "hcw-master.pptx"
    if not master.exists():
        return "skip", "pptx generator was skipped upstream (no master)"
    out_pptx = work / "canonical-deck.pptx"
    code, out, err = _run([
        PYTHON, str(pptx_gen),
        "--content", str(FIXTURES / "canonical-deck-pptx.yaml"),
        "--template", str(master),
        "--output", str(out_pptx),
    ])
    if code != 0 or not out_pptx.exists():
        return "fail", f"pptx generate exit {code}: {(err or out).strip()[:200]}"
    if not _have("soffice"):
        return "ok", f"{out_pptx.name} ({out_pptx.stat().st_size}B); PDF skip: soffice not on PATH"
    code, out, err = _run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(out_pptx)],
    )
    pdf = work / out_pptx.with_suffix(".pdf").name
    if code != 0 or not pdf.exists():
        return "fail", f"soffice convert exit {code}; tail: {(err or out).strip()[:200]}"
    ok, summary = _check_overflow(pdf)
    return ("ok" if ok else "fail"), f"{pdf.name} ({pdf.stat().st_size}B); overflow: {summary}"


RENDERERS = {
    "marp": render_marp,
    "beamer": render_beamer,
    "slidev": render_slidev,
    "pptx": render_pptx,
}


# ── Driver ────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--formats", default=",".join(ALL_FORMATS),
                    help=f"Comma-separated list (default: {','.join(ALL_FORMATS)})")
    ap.add_argument("--keep", action="store_true",
                    help="Leave the work dir behind (default: deleted on exit)")
    args = ap.parse_args(argv)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    unknown = [f for f in formats if f not in RENDERERS]
    if unknown:
        print(f"smoke_render: error: unknown format(s): {unknown}", file=sys.stderr)
        return 2

    tmp = tempfile.mkdtemp(prefix="theme-smoke-")
    work = Path(tmp)
    print(f"smoke_render: work dir = {work}")

    # Step 1: generate all four formats from HCW spec.
    print("smoke_render: generating themes from hcw-brand.yaml …")
    code, out, err = _run([
        PYTHON, str(NEW_THEME), str(HCW_SPEC),
        "--out", str(work / "generated"),
        "--no-fail-on-warn", "--quiet",
    ])
    if code != 0:
        print(f"smoke_render: theme generation failed (exit {code})", file=sys.stderr)
        print(out, file=sys.stderr)
        print(err, file=sys.stderr)
        return 1

    # Step 2: per-format render + overflow check.
    results: dict[str, tuple[str, str]] = {}
    for fmt in formats:
        print(f"smoke_render: rendering {fmt} …")
        try:
            results[fmt] = RENDERERS[fmt](work, work / "generated")
        except Exception as e:
            results[fmt] = ("fail", f"renderer raised: {e!r}")

    # Step 3: report.
    print()
    print("smoke_render: results")
    print("─" * 72)
    n_ok = n_fail = n_skip = 0
    for fmt in formats:
        status, detail = results[fmt]
        marker = {"ok": "✓", "skip": "·", "fail": "✗"}[status]
        print(f"  {marker} {fmt:8s} {status:5s}  {detail}")
        n_ok += status == "ok"
        n_fail += status == "fail"
        n_skip += status == "skip"
    print("─" * 72)
    print(f"  {n_ok} ok, {n_skip} skipped, {n_fail} failed")

    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
        print(f"smoke_render: cleaned {work}")
    else:
        print(f"smoke_render: --keep → leaving {work}")

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
