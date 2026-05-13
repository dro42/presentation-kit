---
description: Record terminal demos with asciinema, write narration scripts, embed casts into Marp/Slidev/reveal.js as a live player, or convert to GIF/SVG/MP4 for Beamer/pptx.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `asciinema` skill at `${CLAUDE_PLUGIN_ROOT}/skills/asciinema/SKILL.md` and follow its workflows.

**Theme resolution order:**

1. User themes — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/asciinema/`
2. Bundled themes — `${CLAUDE_PLUGIN_ROOT}/skills/asciinema/assets/themes/` (default, solarized-dark, solarized-light, dracula, monokai)

User themes shadow bundled themes when basenames match. Pass the resolved absolute path to `agg --theme <path>` or wire into the asciinema-player config via `theme-url=<path>` for Marp/Slidev/reveal.js embeds.

**Save the current theme** with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh asciinema <name> <theme.json>`. Append `--force` before the format argument to overwrite an existing user theme.

**Embed snippets** for each consuming format live in `${CLAUDE_PLUGIN_ROOT}/skills/asciinema/assets/embed-snippets/` — copy the matching file into the deck source.

**Long conversions** (multi-cast batch render to GIF, MP4 via ffmpeg) should be delegated to the `presentation-builder` subagent so the main conversation stays clean.
