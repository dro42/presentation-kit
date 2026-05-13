---
description: Author Vue/Markdown slide decks with Slidev — interactive code, built-in layouts, custom components, and PDF/SPA export. Strong fit for tech talks, sprint reviews, and engineering demos.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `slidev` skill at `${CLAUDE_PLUGIN_ROOT}/skills/slidev/SKILL.md` and follow its workflows.

**Theme resolution order** (Slidev local-directory themes):

1. User themes — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/slidev/<name>/`
2. Bundled theme — `${CLAUDE_PLUGIN_ROOT}/skills/slidev/assets/themes/slidev-theme-minimal/`

Copy the resolved theme directory into the user's Slidev project root, then reference it in `slides.md` frontmatter as `theme: ./slidev-theme-<name>`. User themes shadow bundled when basenames match.

**Save the current theme** with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh slidev <name> ./slidev-theme-<name>/` (directory source). Append `--force` before the format argument to overwrite an existing user theme directory.

**Long-running builds** (`slidev build`, `slidev export --format pdf`) should be delegated to the `presentation-builder` subagent so the main conversation stays clean.

**Prerequisites the user must install themselves**: Node.js ≥ 18, then `npm init slidev@latest <project>` bootstraps Slidev. For PDF export: `npx playwright install chromium` (~150 MB).
