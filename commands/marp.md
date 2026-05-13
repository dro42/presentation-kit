---
description: Author or build a Marp (Markdown) slide deck. Generates, themes, and exports HTML/PDF/PPTX/PNG via marp-cli.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `marp` skill at `${CLAUDE_PLUGIN_ROOT}/skills/marp/SKILL.md` and follow its workflows.

**Theme resolution order** (used in Workflow D, theme selection):

1. User themes — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/marp/`
2. Bundled themes — `${CLAUDE_PLUGIN_ROOT}/skills/marp/assets/themes/`

User themes shadow bundled themes when basenames match. Pass the resolved absolute path verbatim to `marp --theme`.

**Save the current theme** with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh marp <name> <css-file>`. Append `--force` before the format argument to overwrite an existing user theme.

**Long-running builds** (watch mode, multi-format batch export) should be delegated to the `presentation-builder` subagent so the main conversation stays clean.
