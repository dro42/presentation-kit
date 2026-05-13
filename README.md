# presentation-kit

A Claude Code plugin for authoring and building presentation decks across
**Marp** (Markdown) and **LaTeX Beamer**. Slash-command driven, theme-extensible,
with a builder subagent that keeps long render output out of your main
conversation.

> Built for thesis-defense and academic talks at FH Campus Wien, but useful
> for any deck where you'd rather write content than fight with theming.

## Install

In a Claude Code session:

```
/plugin marketplace add dro42/presentation-kit
/plugin install presentation-kit
```

To develop or test locally:

```
/plugin marketplace add /path/to/presentation-kit
/plugin install presentation-kit
```

## What you get

| Slash command | Skill | Output formats |
|---|---|---|
| `/marp` | `marp` — Markdown decks via marp-cli | PDF, PPTX, HTML, PNG |
| `/beamer` | `beamer` — LaTeX Beamer decks via latexmk | PDF |

Plus:

- **`presentation-builder` subagent** — watch-mode and long renders run in an
  isolated context so the main conversation stays clean.
- **SessionStart hook** — when you open a directory containing `slides.md` or
  a `\documentclass{beamer}` `.tex` file, the matching slash command is
  surfaced as context.
- **Bundled templates** — `basic`, `academic`, `thesis-defense`,
  `research-update`. The thesis-defense templates (Marp and Beamer) share the
  same content shape, so you can author once and switch venues.
- **HCW theme** — a token-driven FH Campus Wien starter theme in both Marp
  CSS (`hcw-starter.css`) and Beamer `.sty` (`beamerthemeHCW.sty`). One
  source of brand truth across both formats.

## External prerequisites

These tools must be installed for the corresponding skill to build artifacts:

| Skill | Tool | Install |
|---|---|---|
| `/marp` | `marp-cli` | `npm install -g @marp-team/marp-cli` |
| `/beamer` | `latexmk` + `pdflatex` | macOS: BasicTeX / MacTeX. Linux: TeX Live. |

The plugin will detect missing tools and surface the install command before
attempting a build; nothing is installed silently.

## User themes (XDG-compliant)

Plugin-bundled themes live inside the plugin and get overwritten when the
plugin updates. Your themes live separately:

```
${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/
├── marp/        # *.css files, used via marp --theme-set
└── beamer/      # beamertheme*.sty files, copied next to your .tex
```

**Saving a theme you've iterated on:**

```bash
# Marp
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" marp <name> ./theme.css

# Beamer
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" beamer <name> ./beamerthemeFoo.sty

# Overwrite an existing user theme
bash "${CLAUDE_PLUGIN_ROOT}/scripts/save-theme.sh" --force marp dynatrace-dark ./theme.css
```

User themes shadow bundled themes when their basenames match. The skills tag
each theme as `(user)` or `(bundled)` when listing them so the active source
is unambiguous.

## How the subagent works

The four scenarios that delegate to `presentation-builder`:

- **Watch mode** — `marp --watch` or `latexmk -pvc` (continuous compile + preview).
- **Multi-format batch** — one source → PDF + PPTX + HTML in one shot.
- **Long single build** — large decks with bibliography, `minted`, many figures.
- **Anything expected to take > ~30 s.**

The subagent returns a single Markdown report listing each artifact's path,
size, build duration, and any compiler warnings. It has read access and a
narrow Bash allowlist (no `rm`); cleanup is the caller's responsibility.

## How the hook works

The `SessionStart` hook runs `hooks/detect-presentation.sh` against your
current working directory. If it finds `slides.md` or a `.tex` file
declaring `\documentclass{beamer}`, it injects a short context line like
"Detected slides.md — /marp available". Silent in directories without
presentation files. Always exits 0.

The detected-file message is JSON-encoded via `jq -Rs` (with a small `sed`
fallback if `jq` isn't installed) to ensure the injection cannot break the
hook contract.

## Repository layout

```
presentation-kit/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── commands/
│   ├── marp.md
│   └── beamer.md
├── skills/
│   ├── marp/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── assets/{templates,themes}/
│   └── beamer/
│       ├── SKILL.md
│       ├── references/
│       └── assets/{templates,preamble,themes}/
├── agents/
│   └── presentation-builder.md
├── hooks/
│   ├── hooks.json
│   └── detect-presentation.sh
└── scripts/
    └── save-theme.sh
```

## Roadmap

**v0.2 (planned):**

- `pptx` skill — direct PowerPoint generation via `python-pptx`. Deferred
  because the bundled `presentations@openai-primary-runtime` plugin already
  covers part of this surface; v0.2 will differentiate via the shared
  template shape and user-theme system.
- `asciinema` skill — record terminal demos with a synced narration script,
  embeddable in Marp decks and renderable as standalone terminal-demo decks.

## Contributing

Issues and PRs welcome at https://github.com/dro42/presentation-kit. The
bundled themes use `TODO:` markers wherever brand-specific values are
placeholders; PRs against those are the easiest way to start.

## License

MIT. See [LICENSE](./LICENSE).
