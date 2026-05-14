---
name: marp
description: Author Marp/Marpit presentation decks (Markdown-driven slides), convert existing Obsidian notes into decks, export to PDF/PPTX/HTML/PNG via marp-cli, and create or customize Marp themes. Use this skill whenever the user wants to make slides, build a presentation, prepare a talk or supervisor meeting, draft a thesis defense, prepare a sprint review or tech talk, turn a note into a deck, render or export a deck, apply or update a theme, or mentions Marp, Marpit, marp-cli, "deck", or the Obsidian Marp Slides plugin. Trigger even when the user says things like "make me slides about X", "presentation for Friday's meeting", "convert this note to a deck", "render this as PDF", "export the slides", "outline to slides", "create a Marp theme", or "the deck needs an institutional look".
---

# Marp Skill

Marp turns Markdown into HTML/PDF/PPTX slide decks. The user runs marp-cli locally and previews decks live in Obsidian via the `marp-slides` plugin. This skill teaches you how to author decks that work in both contexts, convert existing notes into decks, export to the format the user actually needs, and extend the theme system without inventing new mechanisms.

## When to read what

- New deck from scratch → stay in this file (Workflow A) and pick a template from `assets/templates/`.
- Convert an existing note → Workflow B, then `references/obsidian-and-conversion.md`.
- Export to PDF/PPTX/HTML/PNG → Workflow C, then `references/export-and-config.md` for flags and `marp.config.js`.
- Build or extend a theme (custom brand or institution) → Workflow D, then `references/themes.md`. Start from `assets/themes/minimal.css`.
- Directive lookup / image syntax / per-slide overrides → `references/authoring.md`.

The reference files are small on purpose. Read the one you need; don't preload all of them.

## Quick reference card

Every Marp deck begins with frontmatter:

```markdown
---
marp: true
theme: default          # or gaia, uncover, or a custom theme name registered via --theme-set
paginate: true          # show slide numbers
size: 16:9              # or 4:3
title: "My Deck"        # metadata for PDF/PPTX
author: "<NAME>"
---

# Title slide

---

## Second slide

- Bullet
- Bullet

<!-- Speaker note: this becomes a presenter note in PDF/PPTX. -->
```

Slide separator is a line containing only `---`. Per-slide directives go in HTML comments prefixed with `_` (scoped to the current slide) or without `_` (cascading from this point on):

| Directive | Effect |
|---|---|
| `<!-- _class: lead -->` | Center-aligned hero slide (built-in classes: `lead`, `invert`) |
| `<!-- _backgroundColor: #102030 -->` | Background color, this slide only |
| `<!-- _color: white -->` | Text color, this slide only |
| `<!-- header: "RQ1" -->` | Header text from here onward |
| `<!-- footer: "<PROJECT> · <SHORT URL>" -->` | Footer from here onward |

Built-in themes: **default** (white, clean), **gaia** (warm, larger type — good for academic talks), **uncover** (minimal, dark-friendly). For more directives and image patterns (split backgrounds, multi-image layouts) see `references/authoring.md`.

## Workflow A: Author a new deck

1. **Pick a template** based on context:
   - `assets/templates/basic.md` — generic deck, default theme, ~3-5 slides for any quick talk.
   - `assets/templates/academic.md` — gaia theme, conference/seminar talk shape (motivation → method → result → conclusion).
   - `assets/templates/thesis-defense.md` — full thesis-defense skeleton (intro · RQs · methodology · results · discussion · conclusion · backup). Use only for the defense itself.
   - `assets/templates/research-update.md` — 5-8 slide supervisor check-in or experiment progress update: what we tested · key result with metric · problem/finding · next step · ask.
   - `assets/templates/sprint-review.md` — agile sprint review/demo: goal · shipped · demo · metrics · retro · next sprint · asks.
   - `assets/templates/tech-talk.md` — engineering talk: problem · prior art · design · implementation · live demo · results · lessons.
   - `assets/templates/lightning-talk.md` — 5-minute talk: hook · the one point · evidence · takeaway.
   - `assets/templates/kickoff.md` — project kickoff: problem · goals · non-goals · scope · solution · timeline · stakeholders · risks · decisions.
2. **Confirm the output path with the user before writing.** Sensible defaults depending on context — but always ask if you don't know:
   - Thesis-related decks → `<vault>/<thesis-folder>/Presentations/<YYYY-MM-DD>-<slug>.md`
   - Research-session decks → next to the source notes
   - Project / work decks → wherever the project source lives
   - Anything else → ask. Do not invent a path silently.
3. **Apply the slide-budget rule of thumb.** Roughly one slide per minute of speaking time:
   - Thesis defense (~15 min talk) → 12-15 content slides plus title + thank-you.
   - Supervisor check-in (~5-7 min) → 5-8 slides.
   - Sprint review (~10-15 min) → 8-12 slides.
   - Tech talk (~30 min) → ~20 slides.
   - Lightning talk (~3-5 min) → 3-6 slides.
   If the user's content forces 30+ slides for a 15-min slot, push back: suggest cutting or splitting before drafting.
4. **Write the deck.** Use H1 for the title slide, H2 for each section, 3-5 bullets per slide. Speaker notes go in `<!-- ... -->` comments below the slide content.
5. **Preview live in Obsidian.** The `marp-slides` plugin renders the deck in a side pane as the user edits — no rebuild needed. See `references/obsidian-and-conversion.md` for plugin-specific gotchas (image paths, theme overrides).

## Workflow B: Convert an existing Obsidian note into a deck

1. **Read the source note.** Identify its structure: H1 title, H2 sections, prose paragraphs, lists, code blocks, callouts.
2. **Map to slide structure.** Default mapping:
   - H1 → title slide (`<!-- _class: lead -->`)
   - Each H2 → one slide (H2 becomes the slide title)
   - Long H2 sections with multiple subtopics → split across multiple slides, repeating or rephrasing the title
   - Long prose → distil to 3-5 bullets; keep the original prose as a speaker note
3. **Strip what doesn't render or distracts.**
   - Wikilinks `[[note name]]` don't render inside Marp HTML — convert to plain text or footnote-style references, unless the deck is only previewed inside Obsidian (then they're fine).
   - Obsidian callouts (`> [!note]`) become quote blocks in Marp; keep if the meaning carries.
   - Tags and metadata properties from frontmatter belong in the title slide footer or get removed.
4. **Add a deck frontmatter block at the top.** Don't reuse the note's frontmatter; Marp expects its own keys (`marp`, `theme`, `paginate`).
5. **Run the slide-budget check from Workflow A.** Most notes overshoot. See `references/obsidian-and-conversion.md` for cut-vs-keep heuristics.
6. **Save to a new file.** Don't overwrite the source note; the user wants the prose note preserved.

## Workflow C: Export via marp-cli

Preflight before exporting (5 seconds, prevents surprises):

- Verify `marp` is on PATH: `command -v marp`. Expected `/opt/homebrew/bin/marp` on this machine.
- If exporting with a custom theme, confirm the CSS path resolves and is passed via `--theme-set` or in `marp.config.js`.
- **PDF/PPTX require Chrome or Chromium.** marp-cli auto-detects, but on Apple Silicon with only Homebrew Chromium installed it sometimes fails. Set `chromePath` in `marp.config.js` or `CHROME_PATH` env var. See `references/export-and-config.md`.
- **PPTX has fidelity limits**: no CSS animations, limited gradient/layout support. If the deck relies on heavy CSS, prefer PDF.

Common commands (run from the deck's directory):

```bash
marp deck.md --pdf --allow-local-files            # PDF — needs --allow-local-files for any local image
marp deck.md --pptx                               # PowerPoint
marp deck.md --pptx --pptx-editable               # editable text in PPTX (experimental but useful)
marp deck.md --html                               # standalone HTML (Bespoke template by default)
marp deck.md --images png                         # one PNG per slide
marp deck.md -w                                   # watch mode — re-export on save
marp deck.md -s .                                 # server mode — http://localhost:8080 preview
marp deck.md --theme-set themes/minimal.css       # register a custom theme so `theme: minimal` in frontmatter resolves
```

For recurring workflows (e.g. all decks in a project should auto-register the same theme set and allow local files), check in a `marp.config.js` next to the decks — see `references/export-and-config.md` for the exact shape.

**After export succeeds, invoke the `slide-overflow-check` skill on the output PDF before reporting completion.** It catches text that collides with the footer band or runs off the page edge — the most common "looked fine in preview, looks broken in the PDF" failure mode in Marp decks (especially with custom themes that introduce a thicker footer band). One-line invocation:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/slide-overflow-check/scripts/check_overflow.py deck.pdf
```

Exit 0 = clean, exit 1 = overflow detected (re-render won't help; either tighten the slide content or relax the theme's footer area). See the `slide-overflow-check` SKILL.md for tuning flags.

## Workflow D: Create or customize a theme

Themes are CSS files with a `@theme` declaration at the top. Marp ships **default**, **gaia**, **uncover** — prefer extending one of these via `@import` rather than starting from scratch.

> **For brand-consistent themes across multiple formats**, use the `theme-authoring` skill (`/new-theme <brand.yaml>`) instead of editing this minimal starter directly. It generates the Marp CSS, Beamer .sty, Slidev directory theme, and pptx master from a single `brand.yaml`, keeping colors, fonts, logo, and footer in sync as the brand evolves. The minimal starter is still the right entry point if you only need Marp.

1. **Start from `assets/themes/minimal.css`** — it's a commented stub showing the token surface (primary color, secondary color, font family, logo path, footer text). Override the brand-specific values with your own.
2. **Register the theme.** Either pass `--theme-set path/to/theme.css` on the marp-cli invocation, or add it to `marp.config.js`, or place it next to the deck and let the Obsidian Marp Slides plugin pick it up (plugin scans the same directory).
3. **Reference it from the deck.** Set `theme: minimal` (or your renamed `@theme` value) in the deck frontmatter — the value must match the `@theme` name declared in the CSS, not the file name.
4. **Iterate visually.** Use `marp deck.md -s .` and edit the CSS — server mode hot-reloads.

### Theme resolution

Themes resolve in two locations, in order:

1. **User themes** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/marp/*.css`. Survives plugin updates; this is where user-authored themes live.
2. **Bundled themes** — `assets/themes/*.css` relative to this skill (e.g. `minimal.css`).

User themes shadow bundled ones when the basename matches. When listing themes to the user, prefix each with `(user)` or `(bundled)` so the active source is unambiguous. Pass the resolved *absolute path* verbatim to `marp --theme-set` (or `--theme` for marp-cli >= 4.x).

**Save the current working theme** as a reusable user theme:

```bash
bash scripts/save-theme.sh marp <name> ./theme.css
# add --force before "marp" to overwrite an existing user theme
```

Full directive reference, Marpit-specific selectors (`section`, `header`, `footer`, `section.lead`), and a complete extending-gaia example are in `references/themes.md`.

## Obsidian + Marp integration in this vault

The vault has the `marp-slides` plugin (Samuele Cozzi, v0.46.x). It uses standard Marp syntax — anything that works in marp-cli works in the plugin. Two things to keep in mind:

- **Image paths** in the deck must resolve from the deck file's location (relative paths), not from the vault root. Use `![](./figures/foo.png)` or absolute paths under the vault. For exports, `--allow-local-files` is still required regardless of how Obsidian renders them.
- **Custom themes** placed in the same folder as the deck are auto-discovered by the plugin. For exports, you still need `--theme-set` unless registered in `marp.config.js`.

Full plugin notes (live preview pane, export-from-plugin caveats) live in `references/obsidian-and-conversion.md`.

## Common pitfalls

- Forgetting `marp: true` in frontmatter — the file renders as ordinary Markdown.
- Omitting `--allow-local-files` for PDF/PPTX with local images — the images silently render as broken links.
- Mixing the slide separator `---` with the frontmatter `---` block. Frontmatter is at the top with `marp: true` inside; subsequent `---` lines are slide breaks.
- Setting `theme: <custom-name>` without registering the CSS via `--theme-set` or config — falls back to default silently.
- Heavy reliance on Obsidian-specific syntax (wikilinks, callouts, dataview) in a deck intended for export.
- Trying to use HTML/CSS animations in PPTX export — they're stripped.

## Quality checklist before delivering

- [ ] Frontmatter has `marp: true` and a theme that exists (built-in or registered).
- [ ] Slide count matches the talk duration (see budget rule in Workflow A).
- [ ] Title slide uses `<!-- _class: lead -->` or equivalent — don't bury the title.
- [ ] Speaker notes live in `<!-- ... -->` below slide content, not in the body bullets.
- [ ] Images use relative paths from the deck file; `--allow-local-files` flagged when exporting.
- [ ] Output file path was confirmed with the user, not invented.
- [ ] For thesis or institutional decks: theme is gaia, minimal, or your branded user theme — not the generic Marp default.
- [ ] **`slide-overflow-check` ran clean against the output PDF** (no footer-collision or off-canvas warnings). See the companion `slide-overflow-check` skill.
