---
description: Author or build a LaTeX Beamer slide deck. Generates templates, applies themes, and compiles via latexmk.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `beamer` skill at `${CLAUDE_PLUGIN_ROOT}/skills/beamer/SKILL.md` and follow its workflows.

**Theme resolution order** (used in Workflow D, theme selection):

1. User themes — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/beamer/`
2. Bundled themes — `${CLAUDE_PLUGIN_ROOT}/skills/beamer/assets/themes/`

User themes shadow bundled themes when basenames match. Beamer requires the `.sty` file to be on `TEXINPUTS` — copy the resolved theme next to the `.tex` source (or symlink it) before running `latexmk`. Use `\usetheme{NameWithoutBeamerThemePrefix}` in the document (e.g. `beamerthemeMinimal.sty` → `\usetheme{Minimal}`).

**Save the current theme** with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh beamer <name> <sty-file>`. Append `--force` before the format argument to overwrite an existing user theme.

**Long-running builds** (continuous `latexmk -pvc`, multi-output batch) should be delegated to the `presentation-builder` subagent so the main conversation stays clean.
