#!/usr/bin/env python3
"""Generate per-format presentation themes from a single brand.yaml.

Usage:
  python3 new_theme.py brand.yaml [--formats marp,beamer,slidev,pptx] [options]

Reads a brand spec, validates it (schema + WCAG contrast), then projects to
format-specific themes. Marp/Beamer/Slidev are template-substituted from
.tmpl files; pptx fills a curated baseline.pptx via python-pptx.

See SKILL.md for the brand spec schema and per-format details.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

try:
    import yaml
except ImportError:
    sys.exit("error: PyYAML is required (pip install pyyaml)")

from validate_brand import validate  # noqa: E402

ALL_FORMATS = ("marp", "beamer", "slidev", "pptx")


_EXAMPLES = """
examples:
  # Generate all four formats next to ./themes/
  python3 new_theme.py brand.yaml

  # Subset, custom out dir
  python3 new_theme.py brand.yaml --formats marp,beamer --out ./gen/

  # Validate only, don't write
  python3 new_theme.py brand.yaml --validate-only

  # Generate + persist into XDG user theme dirs (uses ../../scripts/save-theme.sh)
  python3 new_theme.py brand.yaml --save

  # JSON output for downstream tooling (e.g. CI gates)
  python3 new_theme.py brand.yaml --json --no-fail-on-warn

exit codes:
  0  clean — all generators succeeded; warnings only when --no-fail-on-warn
  1  schema/asset error, body-text WCAG hard fail, write error, OR warnings
     (use --no-fail-on-warn to downgrade warnings)
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, epilog=_EXAMPLES,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brand_yaml", type=Path, help="Brand spec YAML file")
    ap.add_argument("--formats", default=",".join(ALL_FORMATS),
                    help=f"Comma-separated list (default: {','.join(ALL_FORMATS)})")
    ap.add_argument("--out", type=Path, default=Path("./themes"),
                    help="Output directory (default: ./themes)")
    ap.add_argument("--save", action="store_true",
                    help="Also save into XDG user theme dirs via save-theme.sh")
    ap.add_argument("--validate-only", action="store_true",
                    help="Validate only; write nothing")
    ap.add_argument("--no-wcag", action="store_true",
                    help="Skip WCAG contrast checks entirely")
    ap.add_argument("--no-fail-on-warn", action="store_true",
                    help="Exit 0 even if warnings fire (errors still fail)")
    ap.add_argument("--json", action="store_true",
                    help="Machine-readable JSON output")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress per-format success lines")
    args = ap.parse_args()

    if not args.brand_yaml.exists():
        return _fail(args.json, f"brand spec not found: {args.brand_yaml}")

    spec = yaml.safe_load(args.brand_yaml.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        return _fail(args.json, f"{args.brand_yaml} did not parse to a mapping")

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    unknown = [f for f in formats if f not in ALL_FORMATS]
    if unknown:
        return _fail(args.json,
                     f"unknown format(s): {unknown}; valid: {list(ALL_FORMATS)}")

    # Validate
    res = validate(spec, args.brand_yaml, run_wcag=not args.no_wcag)

    out_paths: dict[str, str] = {}
    saved_paths: dict[str, str] = {}
    skipped: dict[str, str] = {}
    write_failures: list[str] = []

    if res.ok and not args.validate_only:
        for fmt in formats:
            try:
                path = _generate_one(fmt, spec, args.brand_yaml, args.out)
                if path is None:
                    skipped[fmt] = "generator returned no path"
                else:
                    out_paths[fmt] = str(path)
                    if args.save:
                        saved_paths[fmt] = _save_theme(fmt, spec["brand"]["short"], path)
            except _GeneratorSkip as e:
                skipped[fmt] = str(e)
            except Exception as e:
                write_failures.append(f"{fmt}: {e}")

    # Determine exit code
    has_errors = bool(res.errors) or bool(write_failures)
    has_warns = bool(res.warnings)
    if args.no_fail_on_warn:
        exit_code = 1 if has_errors else 0
    else:
        exit_code = 1 if (has_errors or has_warns) else 0

    # Report
    if args.json:
        print(json.dumps({
            "ok": res.ok and not write_failures,
            "errors": [vars(i) for i in res.errors] + [{"severity": "error", "message": m} for m in write_failures],
            "warnings": [vars(i) for i in res.warnings],
            "outputs": out_paths,
            "saved": saved_paths,
            "skipped": skipped,
        }, indent=2))
    else:
        _print_human(res, out_paths, saved_paths, skipped, write_failures, args)

    return exit_code


def _generate_one(fmt: str, spec: dict, spec_path: Path, out_root: Path) -> Path | None:
    """Dispatch to the per-format generator. Returns the produced primary path."""
    out_dir = out_root / fmt
    if fmt == "marp":
        from _generators import marp
        return marp.generate(spec, spec_path, out_dir, SKILL_ROOT)
    if fmt == "beamer":
        from _generators import beamer
        return beamer.generate(spec, spec_path, out_dir, SKILL_ROOT)
    if fmt == "slidev":
        from _generators import slidev
        return slidev.generate(spec, spec_path, out_dir, SKILL_ROOT)
    if fmt == "pptx":
        from _generators import pptx as pptx_gen
        try:
            return pptx_gen.generate(spec, spec_path, out_dir, SKILL_ROOT)
        except pptx_gen.GeneratorSkip as e:
            raise _GeneratorSkip(str(e)) from e
    raise _GeneratorSkip(f"unknown format: {fmt}")


def _save_theme(fmt: str, short: str, generated_path: Path) -> str:
    """Invoke scripts/save-theme.sh from the plugin root for this generated theme.

    The destination basename comes from the *source artifact* — not from
    `short` — because three of the four formats need a specific name to
    be discoverable by their respective tools:

      - beamer: file MUST be `beamertheme<Pascal>.sty` for \\usetheme{...}
      - slidev: directory MUST be `slidev-theme-<short>` for theme: ./..
      - pptx:   file is `<short>-master.pptx`, surfaces in --template lookup
      - marp:   file is `<short>.css`; using basename keeps it consistent

    save-theme.sh appends the file extension itself, so we strip it here
    for files and pass the directory name as-is for slidev.

    Returns the destination path that save-theme.sh wrote to.
    """
    plugin_root = SKILL_ROOT.parent.parent  # presentation-kit/
    save_script = plugin_root / "scripts" / "save-theme.sh"
    if not save_script.exists():
        raise _GeneratorSkip(f"save-theme.sh not found at {save_script}")
    name = generated_path.name if generated_path.is_dir() else generated_path.stem
    proc = subprocess.run(
        ["bash", str(save_script), "--force", fmt, name, str(generated_path)],
        check=True, capture_output=True, text=True,
    )
    # save-theme.sh prints "Saved theme → <dest>" or "Saved theme directory → <dest>"
    last = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return last.split("→", 1)[1].strip() if "→" in last else ""


class _GeneratorSkip(Exception):
    """Raised by a generator when it cannot run (missing optional dep, etc.)."""


def _fail(json_out: bool, msg: str) -> int:
    if json_out:
        print(json.dumps({"ok": False, "errors": [{"severity": "error", "message": msg}]}))
    else:
        print(f"new_theme: error: {msg}", file=sys.stderr)
    return 1


def _print_human(res, out_paths: dict, saved_paths: dict, skipped: dict,
                 write_failures: list, args) -> None:
    label = "validate-only" if args.validate_only else "generate"
    n_err = len(res.errors) + len(write_failures)
    n_warn = len(res.warnings)
    print(f"new_theme [{label}] — {n_err} error(s), {n_warn} warning(s)")
    for i in res.errors:
        _print_issue(i)
    for m in write_failures:
        print(f"  error: {m}")
    for i in res.warnings:
        _print_issue(i)
    if not args.quiet:
        for fmt, path in out_paths.items():
            saved = saved_paths.get(fmt)
            if saved:
                print(f"  ✓ {fmt}: {path}\n         → saved to {saved}")
            else:
                print(f"  ✓ {fmt}: {path}")
        for fmt, why in skipped.items():
            print(f"  · {fmt}: skipped — {why}")
    if not res.errors and not res.warnings and not write_failures and out_paths:
        print("  (clean)")


def _print_issue(i) -> None:
    where = f" [{i.path}]" if i.path else ""
    print(f"  {i.severity}: {i.message}{where}")


if __name__ == "__main__":
    sys.exit(main())
