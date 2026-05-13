# Obsidian + note-to-deck conversion reference

This file covers two related concerns: how Marp decks behave inside the Obsidian vault (with the `marp-slides` plugin), and how to convert an existing Obsidian note into a usable deck.

## The Obsidian Marp Slides plugin (Samuele Cozzi)

The vault at `/Users/andi/Documents/FH/ba2/fh_vault/.obsidian/plugins/marp-slides` runs version 0.46.x. It renders Marp markdown in a side pane while editing — no need to run marp-cli for live preview.

**What works the same as marp-cli**:
- Frontmatter (`marp: true`, `theme:`, `paginate:`, etc.)
- Slide separators (`---`)
- All per-slide directives (`<!-- _class: lead -->`, etc.)
- Image syntax (`![bg right:40%](path.png)`, resize keywords, filters)
- Built-in themes (default, gaia, uncover)
- Speaker-note comments

**Obsidian-specific behavior**:
- **Image paths** must resolve from the **deck file's location**, not from vault root. Use `./figures/foo.png` rather than `/figures/foo.png`. Obsidian's wikilink-style image embedding (`![[image.png]]`) is **not** Marp-compatible — convert to standard `![](path)` syntax.
- **Custom themes** in the same folder as the deck are auto-discovered by the plugin (no `--theme-set` needed inside Obsidian — only for marp-cli exports).
- **Wikilinks** (`[[note title]]`) render as literal text inside slide previews, not as clickable links. For decks that live only in the vault, this is acceptable; for export, replace with plain text or footnotes.
- **Dataview/Templater/other plugins** don't run inside Marp slides — only the Marp Slides plugin is in the rendering chain.
- The plugin has its own export command but it shells out to marp-cli under the hood. Result is identical to running `marp deck.md --pdf` from the terminal.

**Live preview shortcut**: the plugin adds a "Marp: Open Preview" command. Bind to a hotkey (e.g. `Cmd+Shift+M`) for fast iteration while editing a deck.

## Vault path conventions for decks

The user decides the deck location per call. Sensible defaults to *suggest* (but confirm before writing):

| Context | Suggested path |
|---|---|
| Thesis-related deck (defense, supervisor update, status) | `fh_vault/6_Sem/BA2/Presentations/YYYY-MM-DD-<slug>.md` |
| Deck derived from a research-session note | Same folder as the source — `fh_vault/6_Sem/BA2/Research/<session>/slides.md` |
| Deck derived from an experiment results note | Same folder as the source — `fh_vault/6_Sem/BA2/Experiment/results/<date>/slides.md` |
| Generic / unsure | Ask the user |

The Presentations folder doesn't pre-exist; create it on first use.

## Converting an existing note into a deck

Most Obsidian notes are prose-heavy and slide-hostile. The conversion isn't mechanical; it's editorial.

### Source-note shape → deck mapping

| Source element | Deck mapping |
|---|---|
| H1 (title) | Title slide with `<!-- _class: lead -->` |
| H2 (section header) | New slide; H2 becomes slide title |
| H3 (subsection) | Either a new slide (if substantial) or a sub-heading inside the current slide |
| Prose paragraph (3-5 sentences) | Distil to 3-5 bullets; keep original prose as `<!-- speaker note -->` |
| Prose paragraph (>5 sentences) | Usually means the section needs splitting across multiple slides |
| Bulleted list | Often already slide-shaped — copy as-is, cap at 5-6 bullets per slide |
| Numbered list (process) | Often translates to one slide per step, or one slide with all steps |
| Code block | Stays as code block (Marp handles syntax highlighting) — but trim to essentials |
| Figure / image | Use `![bg right:40%](path)` split layout to pair image with bullets |
| Callout `> [!note]` | Quote block; if it's a key point, promote to a dedicated slide |
| Wikilinks `[[X]]` | Plaintext (for export) or keep (for vault-only viewing) |
| Frontmatter properties | Strip — replace with Marp frontmatter |

### Decision heuristics — what to cut

Most notes have 2-3x more content than a deck can carry. Cut aggressively:

- **Detailed methodology paragraphs** → one bullet "Used X method (see notes)" + speaker note
- **Background context** → mention in 1-2 bullets, not a slide
- **Edge-case discussion** → cut entirely or move to backup slides at the end
- **Long quotations** → paraphrase to one bullet
- **Tables with >5 rows** → either summarize to top-3 rows or split across slides
- **Anything the user knows the audience already knows** → ask, then cut

### Decision heuristics — what to keep

- **The headline result / claim** of each section — this is the slide's reason to exist
- **Concrete numbers and citations** — these are what audiences remember
- **One figure per section** if available
- **The narrative arc** — intro → core point → implication; don't lose this in the transcription

### Slide-budget check

After the rough conversion, count slides and divide by talk duration:

- Defense (15 min) → 12-15 content slides + title + thank-you
- Supervisor meeting (5-7 min) → 5-8 slides
- Lightning talk (3 min) → 3-4 slides

If overshooting by more than ~30 %, push back to the user: "This note would produce 24 slides for a 15-min slot. I can either compress more aggressively (suggest cuts) or split into two decks (e.g. methodology + results separately)."

### Preserve the source note

Always write the deck to a **new file** (e.g. `<source>-slides.md` next to the source, or in the Presentations folder). The source note carries reference value beyond the deck; don't overwrite it.

### Worked example — research note → deck

Source note: `fh_vault/6_Sem/BA2/Research/2026-04-12 - canary remediation/summary.md` with H1 title, four H2 sections (Background, Method, Findings, Open Questions), each 3-5 paragraphs of prose plus one figure.

Conversion (~8 slides):

1. Title slide (`_class: lead`) — title + author + date
2. Background → 1 slide, 3 bullets distilling the paragraphs
3. Method → 1 slide with the figure on the right (`![bg right:40%]`) and 3 bullets on the left
4. Findings → 2 slides (one per top finding, with the metric front-and-centre)
5. Open Questions → 1 slide, ≤4 bullets phrased as questions
6. Thank-you / discussion slide

Speaker notes carry the original prose verbatim so the presenter has context. Deck frontmatter sets `theme: gaia`, `paginate: true`, and pulls `author` from the user's name.
