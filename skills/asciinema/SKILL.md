---
name: asciinema
description: Record terminal demos as .cast files, write timestamped narration scripts, and embed the result into Marp/Slidev/reveal.js as a live player or into Beamer/pptx as an animated GIF or SVG via agg. Use this skill whenever the user wants to capture a CLI demo, asks to "record my terminal", "make a screencast", "embed a terminal recording in slides", "narrate a demo", mentions asciinema, agg, svg-term, or wants a reproducible CLI walkthrough for a talk. Trigger even when the user only says "I want to show this command in my slides" — terminal demos are this skill's territory regardless of the consuming format.
---

# Asciinema Skill

`asciinema` records terminal sessions as `.cast` files (JSON event streams). The cast plays back via `asciinema play` or the web `asciinema-player`. This skill teaches you how to record clean demos, write the narration to accompany them, embed the result into Marp/Slidev/reveal.js as a live player, and convert to animated GIF/SVG for formats that can't host a JavaScript player (Beamer PDF, pptx).

The companion skills are `marp`, `beamer`, `slidev`, and `pptx`. This skill is the source of terminal-demo artifacts that those skills then *consume* via embed snippets bundled in `assets/embed-snippets/`.

## When to read what

- Record a demo cleanly → `references/recording.md` (terminal size, prompt, dotfile isolation, idle-time clamping).
- Write narration → `references/narration.md` (timestamped script format, rehearsal discipline).
- Embed into a deck → `references/embedding.md` plus the per-format snippets in `assets/embed-snippets/`.
- Convert to GIF/SVG → `references/conversion-agg-svg.md` (`agg` for GIF, `svg-term` for SVG, ffmpeg for MP4).

The reference files are small on purpose. Read the one you need.

## Quick reference card

```bash
# Record (sane defaults: 100 cols × 30 rows, 2-second idle clamp)
asciinema rec --cols 100 --rows 30 --idle-time-limit 2 \
              --title "<TITLE>" demo.cast

# Play locally
asciinema play demo.cast

# Convert to animated GIF (Beamer / pptx / GitHub README)
agg demo.cast demo.gif --theme monokai --font-size 18

# Convert to SVG (smaller, crisp in PDF; static image for Beamer print)
svg-term --in demo.cast --out demo.svg --window

# Upload (optional, public — host on asciinema.org)
asciinema upload demo.cast
```

`--idle-time-limit 2` collapses any pause longer than 2 s — keeps the cast tight when you stop to think. `--cols/--rows` make the recording terminal-size-independent.

## Workflow A: Record a clean demo

1. **Plan the demo first.** Draft `narration.md` from `assets/narration-template.md` *before* recording. Knowing what you'll say (and when) makes the recording 2-3× shorter than "press record and improvise".
2. **Set up the terminal:**
   - Fixed size: `cols=100 rows=30` is a good 16:9 default. Bigger casts force shrink-to-fit in the embed player.
   - Clean prompt: `PS1='$ '` for the recording shell. The user's normal shell prompt (powerline, git status, etc.) is visual noise.
   - Isolated dotfiles (optional but recommended): `HOME=$(mktemp -d) asciinema rec ...` runs in a pristine environment so nothing leaks (aliases, history, etc.).
3. **Use the wrapper script** for sane defaults:
   ```bash
   bash scripts/record-demo.sh "<TITLE>" demo.cast
   # adds --cols 100 --rows 30 --idle-time-limit 2 and a clean PS1
   ```
4. **Record. Stop talking at the end.** Trailing silence becomes idle-time padding; the cast is shorter and cleaner if you `exit` immediately when done.
5. **Verify the cast plays:** `asciinema play demo.cast`. If the demo is too fast/slow, re-record — post-hoc time scaling exists in some players but breaks narration sync.

## Workflow B: Write a narration script

1. **Copy the template:** `cp assets/narration-template.md narration.md`.
2. **Watch the cast once with a stopwatch.** Note the timestamp of each key moment.
3. **Write one paragraph per moment.** Two columns: `MM:SS` and what you'll say.
4. **Rehearse aloud** with the cast playing. Adjust narration density — if you finish a paragraph before the cast moves on, your narration is too short; if you can't finish before the next moment, too long.
5. **Render the script as a printable PDF** alongside the embed (so you have it on the lectern). Marp or Beamer can render it in two minutes.

## Workflow C: Embed the cast into slides

For each target format, copy the matching snippet from `assets/embed-snippets/`:

| Format | Snippet | Mechanism |
|---|---|---|
| Marp | `embed-snippets/marp.md` | HTML `<asciinema-player>` web component + CDN script tag |
| Slidev | `embed-snippets/slidev.md` | `<AsciinemaPlayer>` Vue component (skill assumes the component is registered) |
| reveal.js | `embed-snippets/revealjs.html` | `<asciinema-player>` web component in a slide section |
| Beamer | `embed-snippets/beamer-gif.tex` | `\includegraphics{demo.gif}` (use `animate` package for true playback in Acrobat) |
| pptx | `embed-snippets/pptx.py` | `python-pptx` `shapes.add_picture('demo.gif', ...)`; PowerPoint plays GIFs in slideshow mode |

The Beamer and pptx paths require a GIF conversion first — see Workflow D.

## Workflow D: Convert to GIF (Beamer / pptx / README)

The cast is a JSON event stream; PDF and pptx can't render it interactively. Convert to GIF with `agg`:

```bash
# Default theme — readable on white slide backgrounds
agg demo.cast demo.gif --theme monokai --font-size 18 --cols 100 --rows 30

# With one of the bundled theme presets
agg demo.cast demo.gif --theme assets/themes/solarized-dark.json
```

`agg` (asciinema gif generator) is the official tool. Install on macOS: `brew install agg`. If `agg` isn't available, the skill should surface the install command and **not** attempt to render automatically.

GIF sizing rule of thumb: keep under 5 MB for Beamer (LaTeX embeds the file in the PDF). If too big, lower `--font-size` or drop `--cols`/`--rows`.

## Workflow E: SVG fallback (when GIF is too big)

`svg-term` (a Node CLI) produces a scalable SVG of the terminal session. Crisper than GIF in print, much smaller, but **static** by default — set `--window` to add a window chrome frame. Install: `npm install -g svg-term-cli`. Skip if not installed; document the prerequisite, don't auto-install.

```bash
svg-term --in demo.cast --out demo.svg --window --term iterm2 --profile Dracula
```

## Workflow F: Themes

`assets/themes/*.json` are asciinema-player theme presets (background, foreground, 16-color palette). Theme resolution:

1. **User themes** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/asciinema/*.json`
2. **Bundled themes** — `assets/themes/*.json` (`default`, `solarized-dark`, `solarized-light`, `dracula`, `monokai`)

User themes shadow bundled when basenames match. Pass the resolved path to `agg --theme <path.json>` or wire into the asciinema-player config via `theme-url=<path>` (Marp/Slidev/reveal.js embeds).

**Save a custom theme:**

```bash
bash scripts/save-theme.sh asciinema <name> ./my-theme.json
# add --force before "asciinema" to overwrite an existing user theme
```

## Prerequisites and install commands

- **asciinema** (required) — `brew install asciinema` (macOS) or `pip install asciinema` (cross-platform). Verify: `asciinema --version`.
- **agg** (soft, needed for GIF) — `brew install agg` (macOS) or `cargo install --git https://github.com/asciinema/agg` (cross-platform).
- **svg-term-cli** (soft, needed for SVG) — `npm install -g svg-term-cli`.
- **ffmpeg** (soft, needed for MP4 — out of scope here, used in v0.3) — `brew install ffmpeg`.

Surface install commands to the user. Never auto-install.

## Common pitfalls

- **Recording terminal size != playback size.** The cast embeds the terminal dimensions; players use them. Always pass `--cols/--rows` explicitly or the recorder uses the current TTY size (often 80×24 on inherited shells).
- **ANSI escape sequences from powerline prompts.** Inflate the cast and produce visual noise. Use the clean `PS1='$ '` in the recording shell.
- **Long idle pauses.** Without `--idle-time-limit`, "thinking time" becomes silent padding in playback. Clamp at 2 s for tutorials, 0.5 s for short demos.
- **GIF playback in PowerPoint.** Plays in *slideshow mode only*, not in Normal view. Audiences see static first-frame in the editor and assume it's broken. Set expectations.
- **GIF playback in Beamer/PDF.** Standard PDF viewers show only the first frame. Use the `animate` LaTeX package (`\animategraphics`) for true playback in Adobe Acrobat, or accept first-frame-as-thumbnail with a `[Live demo: <URL>]` link beneath.
- **Recording with secrets.** asciinema captures everything, including pasted passwords. Use a throwaway shell (`HOME=$(mktemp -d)`) and verify `cat demo.cast | jq` for sensitive strings before sharing.

## Quality checklist before delivering

- [ ] Cast duration matches the talk slot (or the section the demo lives in).
- [ ] Narration script timestamps align with cast events to within ±2 s.
- [ ] Terminal dimensions explicit (`--cols/--rows` set; not relying on TTY default).
- [ ] Prompt is clean (`PS1='$ '` or equivalent; no powerline, no git status).
- [ ] No secrets in the cast (`grep -i 'password\|token\|secret' demo.cast` returns nothing).
- [ ] GIF/SVG conversion succeeded if the target format isn't web (Beamer, pptx).
- [ ] Theme matches the consuming deck's color palette (light demo on dark slide is jarring).
