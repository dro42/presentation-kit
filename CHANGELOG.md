# Changelog

All notable changes to `presentation-kit` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-13

### Added
- Initial release.
- `marp` skill (Markdown slide decks via marp-cli) with bundled templates
  (`basic`, `academic`, `thesis-defense`, `research-update`) and an HCW
  starter theme.
- `beamer` skill (LaTeX Beamer decks via latexmk) with bundled templates and
  an HCW-styled Beamer theme.
- `/marp` and `/beamer` slash commands.
- `presentation-builder` subagent for long-running and watch-mode builds.
- SessionStart hook that detects presentation files in the current
  directory and surfaces the matching slash command.
- User-extensible theme system at
  `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/` with a
  `save-theme.sh` helper.
