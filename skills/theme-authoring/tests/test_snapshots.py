"""Token-snapshot tests for the four format generators.

These are the test gate: they catch the "tokens didn't make it through
substitution" failure mode without needing any visual rendering. Visual
verification lives in tests/smoke_render.py.

Each test runs the real CLI as a subprocess (so we exercise argparse,
exit codes, and JSON output exactly as a user would), then opens the
generated artifact and asserts the brand tokens landed in the right
slots.

Run from anywhere:
  python3 -m unittest skills.theme-authoring.tests.test_snapshots
Or:
  cd skills/theme-authoring && .venv/bin/python3 -m unittest tests/test_snapshots.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = SKILL_ROOT.parent.parent
HCW_SPEC = SKILL_ROOT / "examples" / "hcw-brand.yaml"
NEW_THEME = SKILL_ROOT / "scripts" / "new_theme.py"

# Resolve the python interpreter once. Honor a project-local venv if it
# exists (so python-pptx is on the path); else fall back to sys.executable.
_VENV_PY = PLUGIN_ROOT / ".venv" / "bin" / "python3"
PYTHON = str(_VENV_PY) if _VENV_PY.exists() else sys.executable


def run_new_theme(*args: str, expect_exit: int | None = None) -> tuple[int, str, str]:
    """Run new_theme.py as a subprocess, return (exit_code, stdout, stderr)."""
    cmd = [PYTHON, str(NEW_THEME), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if expect_exit is not None and proc.returncode != expect_exit:
        raise AssertionError(
            f"expected exit {expect_exit}, got {proc.returncode}\n"
            f"cmd: {' '.join(cmd)}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc.returncode, proc.stdout, proc.stderr


# ── Fixtures ────────────────────────────────────────────────────────────────


class _GeneratedHCW:
    """Lazy single-shot generation of all four HCW formats into a temp dir.

    Shared across tests in the class to avoid re-running the generator
    for every assertion (it's cheap, but the venv-python startup is the
    dominant cost).
    """
    _tmp: tempfile.TemporaryDirectory | None = None
    _out: Path | None = None
    _skipped: dict[str, str] = {}
    _exit: int | None = None

    @classmethod
    def get(cls) -> Path:
        if cls._out is None:
            cls._tmp = tempfile.TemporaryDirectory(prefix="theme-snapshot-")
            cls._out = Path(cls._tmp.name)
            code, stdout, _ = run_new_theme(
                str(HCW_SPEC), "--out", str(cls._out), "--json", "--no-fail-on-warn"
            )
            cls._exit = code
            cls._skipped = json.loads(stdout).get("skipped", {})
        return cls._out

    @classmethod
    def is_skipped(cls, fmt: str) -> bool:
        cls.get()  # ensure populated
        return fmt in cls._skipped


# ── Marp ────────────────────────────────────────────────────────────────────


class TestMarpSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (_GeneratedHCW.get() / "marp" / "hcw.css").read_text()

    def test_theme_header(self):
        self.assertIn("@theme hcw", self.css)

    def test_primary_brand_color(self):
        self.assertIn("--primary-color:    #36566D;", self.css)

    def test_secondary_brand_color(self):
        self.assertIn("--secondary-color:  #4B5059;", self.css)

    def test_primary_soft(self):
        self.assertIn("--primary-soft:     #7897AC;", self.css)

    def test_no_accent_when_null(self):
        # HCW's spec sets palette.accent: null — the --accent-color var must NOT appear
        self.assertNotIn("--accent-color:", self.css)

    def test_logo_background_image(self):
        self.assertIn("background-image: url('hcw-logo.svg')", self.css)

    def test_section_invert_emitted(self):
        self.assertIn("section.invert", self.css)

    def test_two_column_emitted(self):
        self.assertIn("section.two-column", self.css)

    def test_logo_file_copied_alongside(self):
        logo = _GeneratedHCW.get() / "marp" / "hcw-logo.svg"
        self.assertTrue(logo.exists(), f"logo not copied next to CSS: {logo}")


# ── Beamer ──────────────────────────────────────────────────────────────────


class TestBeamerSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sty = (_GeneratedHCW.get() / "beamer" / "beamerthemeHcw.sty").read_text()

    def test_provides_pascal_cased_package(self):
        self.assertIn(r"\ProvidesPackage{beamerthemeHcw}", self.sty)

    def test_primary_definecolor_hex_stripped(self):
        self.assertIn(r"\definecolor{BrandPrimary}{HTML}{36566D}", self.sty)

    def test_secondary_definecolor(self):
        self.assertIn(r"\definecolor{BrandSecondary}{HTML}{4B5059}", self.sty)

    def test_inverse_bg_resolves_to_primary(self):
        # palette.inverse.bg = "primary" → token-resolved to #36566D
        self.assertIn(r"\definecolor{BrandInverseBg}{HTML}{36566D}", self.sty)

    def test_no_accent_color_when_null(self):
        self.assertNotIn("BrandAccent", self.sty)

    def test_section_divider_template_emitted(self):
        self.assertIn(r"\AtBeginSection", self.sty)

    def test_logo_overlay_emitted(self):
        self.assertIn(r"\addtobeamertemplate{background canvas}", self.sty)

    def test_footer_text_resolved_with_year_and_author(self):
        # footer template "© {{year}} {{author}}" → contains the year and the author
        self.assertIn("Andreas Drozd", self.sty)
        self.assertRegex(self.sty, r"\\textcopyright\{\}\s*20\d\d")


# ── Slidev ──────────────────────────────────────────────────────────────────


class TestSlidevSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.theme_dir = _GeneratedHCW.get() / "slidev" / "slidev-theme-hcw"
        cls.css = (cls.theme_dir / "styles" / "index.css").read_text()
        cls.pkg = json.loads((cls.theme_dir / "package.json").read_text())

    def test_theme_directory_named_with_short(self):
        self.assertTrue(self.theme_dir.is_dir())

    def test_package_name(self):
        self.assertEqual(self.pkg["name"], "slidev-theme-hcw")

    def test_brand_primary_in_css(self):
        self.assertIn("--brand-primary:      #36566D;", self.css)

    def test_inverse_bg_resolves_to_primary(self):
        self.assertIn("--brand-inverse-bg:   #36566D;", self.css)

    def test_no_accent_when_null(self):
        self.assertNotIn("--brand-accent:", self.css)

    def test_layouts_copied_verbatim(self):
        # .vue files should be copied without .tmpl substitution
        cover = self.theme_dir / "layouts" / "cover.vue"
        section = self.theme_dir / "layouts" / "section.vue"
        self.assertTrue(cover.exists())
        self.assertTrue(section.exists())

    def test_logo_copied_into_theme_dir(self):
        logo = self.theme_dir / "hcw-logo.svg"
        self.assertTrue(logo.exists(), f"logo missing from theme dir: {logo}")


# ── pptx ────────────────────────────────────────────────────────────────────


class TestPptxSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if _GeneratedHCW.is_skipped("pptx"):
            raise unittest.SkipTest("pptx generator skipped (python-pptx not installed)")
        cls.master = _GeneratedHCW.get() / "pptx" / "hcw-master.pptx"
        with zipfile.ZipFile(cls.master) as zf:
            cls.theme_xml = zf.read("ppt/theme/theme1.xml").decode("utf-8")
            cls.master_xml = zf.read("ppt/slideMasters/slideMaster1.xml").decode("utf-8")
            cls.master_rels = zf.read("ppt/slideMasters/_rels/slideMaster1.xml.rels").decode("utf-8")
            cls.has_image1 = "ppt/media/image1.png" in zf.namelist()

    # ── color slots ────────────────────────────────────────────────────
    def test_dk1_is_text(self):
        self.assertIn('<a:dk1><a:srgbClr val="1A1A1A"/></a:dk1>', self.theme_xml)

    def test_lt1_is_bg(self):
        self.assertIn('<a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>', self.theme_xml)

    def test_dk2_is_inverse_bg(self):
        # palette.inverse.bg = "primary" → dk2 = #36566D
        self.assertIn('<a:dk2><a:srgbClr val="36566D"/></a:dk2>', self.theme_xml)

    def test_lt2_is_inverse_text(self):
        self.assertIn('<a:lt2><a:srgbClr val="FFFFFF"/></a:lt2>', self.theme_xml)

    def test_accent1_is_primary(self):
        self.assertIn('<a:accent1><a:srgbClr val="36566D"/></a:accent1>', self.theme_xml)

    def test_accent2_is_secondary(self):
        self.assertIn('<a:accent2><a:srgbClr val="4B5059"/></a:accent2>', self.theme_xml)

    def test_accent3_is_primary_soft(self):
        self.assertIn('<a:accent3><a:srgbClr val="7897AC"/></a:accent3>', self.theme_xml)

    def test_accent4_left_at_default_when_no_brand_accent(self):
        # HCW spec sets palette.accent: null → accent4 stays at python-pptx default
        # (8064A2 in the Office baseline). We assert the default rather than the absence,
        # because absence would mean a malformed clrScheme.
        self.assertIn('<a:accent4><a:srgbClr val="8064A2"/></a:accent4>', self.theme_xml)

    def test_hlink_is_primary(self):
        self.assertIn('<a:hlink><a:srgbClr val="36566D"/></a:hlink>', self.theme_xml)

    def test_folhlink_is_primary_soft(self):
        self.assertIn('<a:folHlink><a:srgbClr val="7897AC"/></a:folHlink>', self.theme_xml)

    # ── fonts ─────────────────────────────────────────────────────────
    def test_major_font_latin_typeface(self):
        self.assertIn('<a:majorFont><a:latin typeface="Helvetica Neue"/>', self.theme_xml)

    def test_minor_font_latin_typeface(self):
        self.assertIn('<a:minorFont><a:latin typeface="Helvetica Neue"/>', self.theme_xml)

    # ── logo ──────────────────────────────────────────────────────────
    def test_logo_pic_in_master_sptree(self):
        self.assertIn("<p:pic>", self.master_xml)
        self.assertIn('name="Brand Logo"', self.master_xml)

    def test_logo_image_part_present(self):
        self.assertTrue(self.has_image1, "image1.png missing from pptx zip")

    def test_logo_relationship_in_master_rels(self):
        self.assertIn('Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"', self.master_rels)
        self.assertIn("../media/image1.png", self.master_rels)


# ── Negative tests: validation behavior ─────────────────────────────────────


class TestValidationFailures(unittest.TestCase):
    """Exercise schema/WCAG/asset failure modes via --validate-only."""

    def _spec(self, body: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            prefix="theme-bad-", suffix=".yaml", delete=False, mode="w", encoding="utf-8"
        )
        f.write(textwrap.dedent(body).lstrip())
        f.close()
        self.addCleanup(os.unlink, f.name)
        return Path(f.name)

    def test_body_text_wcag_hard_fail(self):
        spec = self._spec("""
            version: 1
            brand: { name: Bad, short: bad }
            palette: { text: "#cccccc", bg: "#dddddd", primary: "#005fb8" }
        """)
        code, stdout, _ = run_new_theme(str(spec), "--validate-only", "--json")
        self.assertEqual(code, 1)
        report = json.loads(stdout)
        self.assertFalse(report["ok"])
        # error mentions text/bg contrast
        joined = " ".join(e["message"] for e in report["errors"])
        self.assertIn("contrast", joined.lower())

    def test_brand_color_warning_passes_with_no_fail_on_warn(self):
        spec = self._spec("""
            version: 1
            brand: { name: Soft, short: soft }
            palette: { text: "#000000", bg: "#ffffff", primary: "#aaccee" }
        """)
        # Default: warns gate exit 1
        code, _, _ = run_new_theme(str(spec), "--validate-only")
        self.assertEqual(code, 1)
        # With --no-fail-on-warn: exit 0
        code, _, _ = run_new_theme(str(spec), "--validate-only", "--no-fail-on-warn")
        self.assertEqual(code, 0)

    def test_missing_logo_path_errors(self):
        spec = self._spec("""
            version: 1
            brand: { name: NoLogo, short: nl }
            palette: { text: "#000000", bg: "#ffffff", primary: "#005fb8" }
            logo: { path: "./nonexistent.svg", width_px: 100, position: top-right, offset: { top: 0, right: 0 } }
        """)
        code, stdout, _ = run_new_theme(str(spec), "--validate-only", "--json")
        self.assertEqual(code, 1)
        joined = " ".join(e["message"] for e in json.loads(stdout)["errors"])
        self.assertIn("logo", joined.lower())

    def test_missing_version_errors(self):
        spec = self._spec("""
            brand: { name: NoVer, short: nv }
            palette: { text: "#000000", bg: "#ffffff", primary: "#005fb8" }
        """)
        code, stdout, _ = run_new_theme(str(spec), "--validate-only", "--json")
        self.assertEqual(code, 1)
        joined = " ".join(e["message"] for e in json.loads(stdout)["errors"])
        self.assertIn("version", joined.lower())


# ── Positive accent test: when palette.accent IS set ─────────────────────


class TestAccentWiring(unittest.TestCase):
    """When palette.accent is set, it must land in accent4/CSS var/etc."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="theme-accent-")
        self.addCleanup(self.tmp.cleanup)
        spec = Path(self.tmp.name) / "with-accent.yaml"
        spec.write_text(textwrap.dedent("""
            version: 1
            brand: { name: AccentTest, short: at }
            palette:
              text: "#000000"
              bg:   "#ffffff"
              primary:   "#005fb8"
              secondary: "#003e7e"
              accent:    "#FF6600"
        """).lstrip())
        self.out = Path(self.tmp.name) / "out"
        run_new_theme(str(spec), "--out", str(self.out), "--no-fail-on-warn", expect_exit=0)

    def test_marp_emits_accent_var(self):
        css = (self.out / "marp" / "at.css").read_text()
        self.assertIn("--accent-color:", css)
        self.assertIn("#FF6600", css)

    def test_beamer_defines_brand_accent(self):
        sty = (self.out / "beamer" / "beamerthemeAt.sty").read_text()
        self.assertIn(r"\definecolor{BrandAccent}{HTML}{FF6600}", sty)

    def test_pptx_accent4_patched(self):
        if _GeneratedHCW.is_skipped("pptx"):
            self.skipTest("pptx generator skipped (python-pptx not installed)")
        master = self.out / "pptx" / "at-master.pptx"
        with zipfile.ZipFile(master) as zf:
            theme = zf.read("ppt/theme/theme1.xml").decode("utf-8")
        self.assertIn('<a:accent4><a:srgbClr val="FF6600"/></a:accent4>', theme)


# ── Save-flow integration ──────────────────────────────────────────────────


class TestSaveFlow(unittest.TestCase):
    """--save delegates to scripts/save-theme.sh and lands in XDG_DATA_HOME."""

    def test_save_writes_into_xdg_data_home(self):
        with tempfile.TemporaryDirectory(prefix="xdg-fake-") as fake_xdg:
            env = os.environ.copy()
            env["XDG_DATA_HOME"] = fake_xdg
            with tempfile.TemporaryDirectory(prefix="theme-save-out-") as out_dir:
                cmd = [
                    PYTHON, str(NEW_THEME), str(HCW_SPEC),
                    "--out", out_dir, "--save", "--no-fail-on-warn",
                ]
                proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
                self.assertEqual(
                    proc.returncode, 0,
                    f"save failed: stdout={proc.stdout}\nstderr={proc.stderr}"
                )
            base = Path(fake_xdg) / "presentation-kit" / "themes"
            self.assertTrue((base / "marp" / "hcw.css").exists(),
                            "marp theme not saved to XDG dir")
            self.assertTrue((base / "beamer" / "beamerthemeHcw.sty").exists(),
                            "beamer theme not saved")
            self.assertTrue((base / "slidev" / "slidev-theme-hcw").is_dir(),
                            "slidev theme dir not saved")
            if not _GeneratedHCW.is_skipped("pptx"):
                self.assertTrue((base / "pptx" / "hcw-master.pptx").exists(),
                                "pptx master not saved")


if __name__ == "__main__":
    unittest.main()
