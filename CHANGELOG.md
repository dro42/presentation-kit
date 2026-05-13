# Changelog

All notable changes to `presentation-kit` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-14

### Added
- **Three new skills:** `asciinema` (record/narrate/embed/convert terminal
  demos), `slidev` (Vue/Markdown decks with interactive code), `pptx`
  (YAML → PowerPoint via python-pptx).
- **`/asciinema`, `/slidev`, `/pptx` slash commands** wiring the new skills.
- **Four new templates per Marp + Beamer skill** (8 templates each, mirroring
  the new slidev and pptx skills): `sprint-review`, `tech-talk`,
  `lightning-talk`, `kickoff`.
- **`scripts/build-skill-bundles.sh`** — produces self-contained
  `dist/*.skill` zips for installation into Codex CLI (`~/.codex/skills/`),
  Gemini CLI (`~/.gemini/skills/`), or cross-tool `.agents/skills/`.
  Includes a drift guard that asserts no synced `save-theme.sh` copies
  land in the source tree.
- **`dist/manifest.json`** with sha256 + size per bundle, for release
  attachment verification.
- **Per-runtime install instructions** in README for Claude Code, Codex,
  Gemini, and `.agents/skills/`.
- **`save-theme.sh`** now accepts five formats (`marp | beamer | slidev |
  pptx | asciinema`) and supports directory sources for Slidev local
  themes.
- **Asciinema embed snippets** under `skills/asciinema/assets/embed-snippets/`
  for Marp, Slidev, reveal.js, Beamer, and pptx.
- **Five bundled asciinema-player themes** (default, solarized-dark,
  solarized-light, dracula, monokai).
- **Slidev local-directory theme** (`slidev-theme-minimal/`) with
  `package.json` declaring `slidev.defaults` — works correctly with
  `slidev export --format pdf` and dark/light switching.
- **Generic `<TITLE>` / `<NAME>` / `<INSTITUTE>` placeholder tokens** in
  every template (replaces the former personal/institutional content).

### Changed
- **Bundled themes renamed:** `hcw-starter.css` → `minimal.css` (`@theme
  minimal`); `beamerthemeHCW.sty` → `beamerthemeMinimal.sty`
  (`\usetheme{Minimal}`). Pure `git mv` preserved history. Color macros
  renamed `HCWprimary` → `BrandPrimary` etc.
- **SessionStart hook** rewrite: disambiguates Marp vs Slidev `slides.md`
  via unambiguous frontmatter signals; also detects Slidev project
  `package.json`, `.pptx`, `deck.yaml`, and `.cast` files.
- **All existing templates generalized** (`thesis-defense.{md,tex}`,
  `academic.{md,tex}`, `basic.{md,tex}`, `research-update.{md,tex}`)
  with placeholder tokens.
- **`skills/beamer/references/thesis-defense-checklist.md`** rewritten
  generic (bachelor/master defense advice without institution-specific
  framing).
- **SKILL.md bodies are now AI-agnostic** — `${CLAUDE_PLUGIN_ROOT}`
  references removed from skill bodies and references. They remain in
  `commands/*.md` (those files run only under Claude Code).
- **README** rewritten with v0.2 scope (5 skills, per-runtime install
  instructions, full template inventory).

### Removed
- All FH Campus Wien-specific content (BA2 thesis examples, "Sidecar vs
  Ambient" placeholder content, `fh_vault/` paths, supervisor names,
  personal email). Plugin metadata (author = Andreas Drozd) preserved
  for correct attribution.

## [0.1.0] - 2026-05-13

### Added
- Initial release with Marp and Beamer skills.
- `/marp` and `/beamer` slash commands.
- `presentation-builder` subagent for long-running builds.
- SessionStart hook detecting `slides.md` and Beamer `.tex` files.
- HCW (FH Campus Wien) starter theme for both Marp and Beamer
  (subsequently generalized in 0.2.0).
- User-extensible theme system at
  `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/` with a
  `save-theme.sh` helper.
- Four templates per skill: `basic`, `academic`, `thesis-defense`,
  `research-update`.
