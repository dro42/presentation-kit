# presentation-kit

A Claude Code plugin for authoring and building presentation decks across
five formats: **Marp** (Markdown), **LaTeX Beamer**, **Slidev** (Vue/Markdown),
**PowerPoint** (via python-pptx), and **asciinema** terminal demos.

Slash-command driven, theme-extensible, with a builder subagent that keeps
long renders out of your main conversation. The same skills run unchanged
under Claude Code, Codex CLI, and Gemini CLI — install the whole plugin in
Claude Code, or just the per-skill `.skill` bundles elsewhere.

Useful for school, university, conferences, sprint reviews, tech talks,
kickoffs, and thesis defenses.

## Install

### Claude Code (full plugin)

```
/plugin marketplace add dro42/presentation-kit
/plugin install presentation-kit
```

To develop or test locally:

```
/plugin marketplace add /path/to/presentation-kit
/plugin install presentation-kit
```

### Codex CLI (per-skill bundles)

Codex reads skills from `~/.codex/skills/` (also `.agents/skills/` in a
project root). Install one skill, or all five:

```bash
mkdir -p ~/.codex/skills
for s in marp beamer asciinema slidev pptx; do
  curl -L -o /tmp/$s.skill \
    https://github.com/dro42/presentation-kit/releases/latest/download/$s.skill
  unzip -q /tmp/$s.skill -d ~/.codex/skills/
done
```

### Gemini CLI (per-skill bundles)

Gemini reads skills from `~/.gemini/skills/` (also `.agents/skills/` in a
project root):

```bash
mkdir -p ~/.gemini/skills
for s in marp beamer asciinema slidev pptx; do
  curl -L -o /tmp/$s.skill \
    https://github.com/dro42/presentation-kit/releases/latest/download/$s.skill
  unzip -q /tmp/$s.skill -d ~/.gemini/skills/
done
```

### Cross-tool project-local (`.agents/skills/`)

Both Codex and Gemini also discover skills from a project-local
`.agents/skills/` directory. Drop the unzipped skills there once and they
work for both runtimes:

```bash
mkdir -p .agents/skills
for s in marp beamer asciinema slidev pptx; do
  curl -L -o /tmp/$s.skill \
    https://github.com/dro42/presentation-kit/releases/latest/download/$s.skill
  unzip -q /tmp/$s.skill -d .agents/skills/
done
```

Codex and Gemini ignore `commands/`, `agents/`, `hooks/`, and
`.claude-plugin/`. The portable surface is the per-skill `.skill` zip
(SKILL.md + references/ + assets/ + scripts/).

## What you get

| Slash command | Skill | Output |
|---|---|---|
| `/marp` | `marp` — Markdown decks via marp-cli | PDF, PPTX, HTML, PNG |
| `/beamer` | `beamer` — LaTeX Beamer decks via latexmk | PDF |
| `/slidev` | `slidev` — Vue/Markdown decks with interactive code | HTML SPA, PDF, PPTX |
| `/pptx` | `pptx` — YAML → .pptx via python-pptx | PowerPoint .pptx |
| `/asciinema` | `asciinema` — Terminal demos (record, narrate, embed) | .cast, GIF, SVG |

Plus:

- **`presentation-builder` subagent** — watch-mode and long renders run in
  an isolated context so the main conversation stays clean.
- **SessionStart hook** — when you open a directory containing `slides.md`,
  a Beamer `.tex` file, `.pptx`, `deck.yaml`, or `.cast`, the matching
  slash command surfaces. Marp vs Slidev `slides.md` disambiguated by
  frontmatter signal.
- **Eight bundled templates per format** — `basic`, `academic`,
  `thesis-defense`, `research-update`, `sprint-review`, `tech-talk`,
  `lightning-talk`, `kickoff`. Same content shape across all four
  slide-producing skills, so the same outline serves any venue.
- **Asciinema integration** — record terminal demos with the bundled
  wrapper, write timestamped narration scripts, embed as a live player
  (Marp HTML, Slidev, reveal.js) or convert to GIF via `agg` for Beamer
  and pptx.
- **AI-agnostic skill bodies** — SKILL.md files use relative paths only,
  so the same skill works under Claude Code, Codex CLI, and Gemini CLI.
  Claude-specific `${CLAUDE_PLUGIN_ROOT}` paths live only in the
  `commands/*.md` slash-command files.

## External prerequisites

These tools must be installed for the corresponding skill to build artifacts:

| Skill | Tool | Install |
|---|---|---|
| `/marp` | `marp-cli` | `npm install -g @marp-team/marp-cli` |
| `/beamer` | `latexmk` + `pdflatex` | macOS: BasicTeX / MacTeX. Linux: TeX Live. |
| `/slidev` | Node.js ≥ 18 | `brew install node` or `nvm`/`fnm`. PDF export: `npx playwright install chromium`. |
| `/pptx` | python-pptx | `pip install python-pptx pyyaml Pillow` |
| `/asciinema` | `asciinema` | `brew install asciinema` (macOS) or `pip install asciinema`. For GIF: `brew install agg`. |

The plugin detects missing tools and surfaces the install command before
attempting a build; nothing is installed silently.

## User themes (XDG-compliant)

Plugin-bundled themes live inside the plugin and get overwritten when the
plugin updates. Your themes live separately:

```
${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/
├── marp/        # *.css files, used via marp --theme-set
├── beamer/      # beamertheme*.sty files, copied next to your .tex
├── slidev/      # slidev-theme-<name>/ directories (local-dir themes)
├── pptx/        # *.pptx master templates
└── asciinema/   # *.json terminal color presets
```

**Saving a theme you've iterated on:**

```bash
# File-based formats
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" marp <name> ./theme.css
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" beamer <name> ./beamerthemeFoo.sty
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" pptx <name> ./brand-master.pptx
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" asciinema <name> ./theme.json

# Directory-based: Slidev local themes
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" slidev <name> ./slidev-theme-<name>/

# Overwrite an existing user theme
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" --force marp dynatrace-dark ./theme.css
```

(Outside Claude Code, run the bundled `scripts/save-theme.sh` inside each
`.skill` package — `bash scripts/save-theme.sh ...` from the skill directory.)

User themes shadow bundled themes when their basenames match. The skills
tag each theme as `(user)` or `(bundled)` when listing them so the active
source is unambiguous.

## How the subagent works

The scenarios that delegate to `presentation-builder`:

- **Watch mode** — `marp --watch`, `latexmk -pvc`, `slidev` dev server.
- **Multi-format batch** — one source → PDF + PPTX + HTML in one shot.
- **Long single build** — large decks, biblatex, Playwright PDF export.
- **Anything expected to take > ~30 s.**

The subagent returns a single Markdown report listing each artifact's
path, size, build duration, and any compiler warnings. It has a narrow
Bash allowlist (no `rm`); cleanup is the caller's responsibility.

## How the hook works

The `SessionStart` hook runs `hooks/detect-presentation.sh` against your
current working directory. It surfaces a context line for each detected
format:

- `slides.md` with `marp: true` → `/marp`
- `slides.md` with `layout/transition/mdc/colorSchema` or
  `theme: @slidev/*|seriph|apple-basic` → `/slidev`
- `slides.md` with `theme: default` alone → ambiguous (surface both)
- `*.tex` with `\documentclass{beamer}` → `/beamer`
- `package.json` with `@slidev/cli` → `/slidev`
- `*.pptx` or `deck.yaml` with `slides:/meta:/layout:` → `/pptx`
- `*.cast` → `/asciinema`

Silent in directories without presentation files. Always exits 0. The
detected-file message is JSON-encoded via `jq -Rs` (with a `sed` fallback
when `jq` isn't installed) to ensure the injection can't break the hook
contract.

## Repository layout

```
presentation-kit/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── commands/
│   ├── marp.md   beamer.md   slidev.md   pptx.md   asciinema.md
├── skills/
│   ├── marp/       SKILL.md + references/ + assets/{templates,themes}/
│   ├── beamer/     SKILL.md + references/ + assets/{templates,themes,preamble}/
│   ├── slidev/     SKILL.md + references/ + assets/{templates,themes/slidev-theme-minimal}/
│   ├── pptx/       SKILL.md + references/ + scripts/{generate.py,layouts.py} + assets/templates/
│   └── asciinema/  SKILL.md + references/ + scripts/record-demo.sh + assets/{themes,embed-snippets,narration-template.md}
├── agents/
│   └── presentation-builder.md
├── hooks/
│   ├── hooks.json
│   └── detect-presentation.sh
└── scripts/
    ├── save-theme.sh           single source of truth
    └── build-skill-bundles.sh  produces dist/*.skill for Codex / Gemini
```

Build output (gitignored): `dist/{marp,beamer,asciinema,slidev,pptx}.skill`
+ `dist/manifest.json`. Built on demand via `bash
scripts/build-skill-bundles.sh`; attached to GitHub Releases.

## Roadmap (v0.3+)

- `reveal.js` skill — HTML/JS framework with the chalkboard/notes/pdf plugin ecosystem
- `quarto` skill — Pandoc-based reproducible slides with R/Python/Julia code execution
- Slidev theme as a proper npm package (`slidev-theme-presentation-kit-minimal`)
- Asciinema → MP4 via `agg | ffmpeg` for venues that require video uploads
- Optional listing in `claude-plugins-official/external_plugins/` via upstream PR

## Contributing

Issues and PRs welcome at https://github.com/dro42/presentation-kit. The
bundled themes use `<NAME>` / `<TITLE>` / `<INSTITUTE>` placeholders
throughout — PRs against documentation, additional templates, or new
output formats are the easiest way to start.

## License

MIT. See [LICENSE](./LICENSE).
