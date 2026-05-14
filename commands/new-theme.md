---
description: Generate per-format presentation themes (Marp CSS, Beamer .sty, Slidev directory theme, pptx master) from a single brand.yaml spec. Keeps colors, fonts, logo, and footer in sync across all four formats.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `theme-authoring` skill at `${CLAUDE_PLUGIN_ROOT}/skills/theme-authoring/SKILL.md` and follow its workflows.

**Usage from Claude Code prompts:**

- `/new-theme path/to/brand.yaml` — generate all four formats into `./themes/`
- `/new-theme path/to/brand.yaml --formats marp,beamer` — subset
- `/new-theme path/to/brand.yaml --save` — also persist into XDG user theme dirs
- `/new-theme path/to/brand.yaml --validate-only` — schema + WCAG check; write nothing

If the user provides only a description ("create a theme using these colors: …"), draft a minimal `brand.yaml` first, confirm with the user, then run the generator. The skill's `examples/hcw-brand.yaml` is the structural template.

**Direct CLI invocation:**

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/theme-authoring/scripts/new_theme.py <brand.yaml> [options]
```

**Persisted themes** land under `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/{marp,beamer,slidev,pptx}/` when `--save` is passed. The format skills' theme-resolution logic discovers them automatically.

**Verification gates** (skill quality checklist enforces both):

1. Token snapshot: `python3 -m unittest tests.test_snapshots` (47 assertions, no rendering)
2. Smoke render: `python3 -m tests.smoke_render` (renders canonical fixture; gracefully skips formats whose renderer isn't installed)

**Optional dependencies** for the pptx generator: `python-pptx`, `pyyaml`, `Pillow`. The skill detects missing deps and surfaces install commands; never auto-installs.
