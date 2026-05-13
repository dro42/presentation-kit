---
description: Generate native PowerPoint .pptx decks programmatically from a YAML spec via python-pptx. Use for corporate audiences, sprint reviews with non-technical stakeholders, or any deck where the audience expects an Office file. Embed asciinema-derived GIFs for live-feel terminal demos.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

Activate the `pptx` skill at `${CLAUDE_PLUGIN_ROOT}/skills/pptx/SKILL.md` and follow its workflows.

**Theme resolution order** (brand .pptx master templates):

1. `--template <path>` CLI flag on `generate.py`
2. `meta.template:` field in the YAML deck spec
3. User templates — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/pptx/<name>.pptx`
4. Bundled templates — `${CLAUDE_PLUGIN_ROOT}/skills/pptx/assets/themes/<name>.pptx` (none ship by default; user-supplied)
5. python-pptx built-in default (16:9, plain styling)

**Save a brand master** with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh pptx <name> <master.pptx>`. Append `--force` before the format argument to overwrite an existing user template.

**Generate a deck:**

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/pptx/scripts/generate.py \
    --content deck.yaml \
    --output deck.pptx
```

**Validate without generating** (cheap; no python-pptx needed for this path):

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/pptx/scripts/generate.py \
    --content deck.yaml --validate-only
```

**Prerequisites the user must install themselves:**

```
pip install python-pptx pyyaml Pillow
```

The skill detects missing deps on first run and surfaces this install command; it does not auto-install.

**Long batch generation** (multiple decks, large GIF embeds) should be delegated to the `presentation-builder` subagent so the main conversation stays clean.
