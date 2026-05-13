---
name: beamer
description: Author LaTeX Beamer presentation decks (academic, thesis-defense, conference talks), convert existing Markdown drafts or thesis chapters into Beamer, compile to PDF via latexmk, and create or customize Beamer themes. Use this skill whenever the user wants Beamer slides, mentions Beamer or LaTeX slides, asks for a thesis-defense deck, says "compile this .tex deck", "render the slides to PDF", "make Beamer slides about X", "convert my chapter into a defense deck", "apply a custom Beamer theme", or opens a .tex file containing `\documentclass{beamer}`. Trigger eagerly even when the user only says "slides" in a thesis or academic context where Beamer is the obvious choice.
---

# Beamer Skill

LaTeX Beamer compiles `.tex` source into HTML-free, presentation-quality PDF slides. It is the standard for academic thesis defenses, conference talks, and any deck where typographic and mathematical fidelity matter. This skill teaches you how to author Beamer decks from scratch, convert existing Markdown/Obsidian drafts, compile them reliably via `latexmk`, and extend the theme system without inventing new mechanisms.

The companion skill is `marp` (Markdown-based slides via marp-cli). They share template names (`basic`, `academic`, `thesis-defense`, `research-update`) so the same content shape can be authored in either format depending on the venue — Markdown for fast iteration and live preview, Beamer for academic submission.

## When to read what

- New deck from scratch → stay in this file (Workflow A) and pick a template from `assets/templates/`.
- Convert an existing Markdown/Obsidian draft → Workflow B, then `references/authoring.md` for frame mapping.
- Build to PDF, fix compiler errors, set up continuous compilation → Workflow C, then `references/build-and-config.md`.
- Build or extend a theme (custom brand or institution) → Workflow D, then `references/authoring.md` for Beamer-specific selectors. Start from `assets/themes/beamerthemeMinimal.sty`.
- Thesis defense structure (bachelor/master defense shape — agenda, RQs, methodology, results, discussion, Q&A) → `references/thesis-defense-checklist.md`.

The reference files are small on purpose. Read the one you need; don't preload all of them.

## Quick reference card

Every Beamer deck begins with a class declaration and frontmatter-like preamble:

```latex
\documentclass[aspectratio=169,12pt]{beamer}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[ngerman,english]{babel}   % English primary, German secondary for thesis context
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{listings}
\usepackage{hyperref}

\usetheme{Minimal}                        % or default, Madrid, Berlin, Szeged, Frankfurt
% \usepackage{./preamble/common}      % when using the bundled common preamble

\title{<TITLE>}
\subtitle{Telemetry Reliability under Automated Canary Remediation}
\author{<NAME>}
\institute{<INSTITUTE>}
\date{\today}

\begin{document}

\begin{frame}
  \titlepage
\end{frame}

\begin{frame}{Section heading}
  \begin{itemize}
    \item Bullet
    \item Bullet with \textbf{emphasis}
  \end{itemize}
  \note{Speaker note for this frame.}
\end{frame}

\end{document}
```

Each `\begin{frame}{Title}` … `\end{frame}` pair is one slide. `\note{...}` blocks become presenter notes (rendered via the `beamer` `show notes` mode).

| Construct | Effect |
|---|---|
| `\begin{block}{Heading}…\end{block}` | Highlighted text block with a title |
| `\begin{alertblock}{Heading}…\end{alertblock}` | Red-toned variant for warnings/key findings |
| `\begin{exampleblock}{Heading}…\end{exampleblock}` | Green-toned variant for examples |
| `\begin{columns}\begin{column}{0.5\textwidth}…\end{column}\end{columns}` | Multi-column layout |
| `\pause` / `\onslide<2->` | Reveal content incrementally |
| `\includegraphics[width=0.7\textwidth]{figures/foo}` | Insert figure |
| `\frametitle{...}` | Set the frame title from inside the frame |

Built-in themes worth knowing: **default** (clean, minimal), **Madrid** (blue with header bar — popular for academic), **Berlin** (with navigation bullets), **Szeged** (clean horizontal nav), **Frankfurt** (vertical nav). The bundled `Minimal` theme is a token-driven extension of Madrid that matches the marp `minimal` companion theme — one source of brand truth across both formats.

## Workflow A: Author a new deck

1. **Pick a template** based on context:
   - `assets/templates/basic.tex` — generic deck, default theme, 3-5 frames for a quick talk.
   - `assets/templates/academic.tex` — conference/seminar talk shape (motivation → method → result → conclusion), Madrid theme.
   - `assets/templates/thesis-defense.tex` — full thesis-defense skeleton (intro · RQs · methodology · results · discussion · conclusion · backup). Mirrors `marp/assets/templates/thesis-defense.md` content. Use only for the defense itself.
   - `assets/templates/research-update.tex` — 5-8 frame supervisor check-in: what we tested · key result · problem/finding · next step · ask.
   - `assets/templates/sprint-review.tex` — agile sprint review/demo: goal · shipped · demo · metrics · retro · next sprint · asks.
   - `assets/templates/tech-talk.tex` — engineering talk: problem · prior art · design · implementation · live demo · results · lessons.
   - `assets/templates/lightning-talk.tex` — 5-minute talk: hook · the one point · evidence · takeaway.
   - `assets/templates/kickoff.tex` — project kickoff: problem · goals · non-goals · scope · solution · timeline · stakeholders · risks · decisions.
2. **Confirm the output path with the user before writing.** Sensible defaults — but always ask if you don't know:
   - Thesis-related decks → `<vault>/<thesis-folder>/Presentations/<YYYY-MM-DD>-<slug>/main.tex`
   - Conference/seminar submissions → wherever the project source already lives
   - Project / work decks → wherever the project source lives
   - Anything else → ask. Do not invent a path silently.
3. **Apply the slide-budget rule of thumb.** Roughly one frame per minute of speaking time:
   - Thesis defense (~15 min talk) → 12-15 content frames plus title + backup section.
   - Supervisor check-in (~5-7 min) → 5-8 frames.
   - Sprint review (~10-15 min) → 8-12 frames.
   - Tech talk (~30 min) → ~20 frames + backup.
   - Lightning talk (~3-5 min) → 3-6 frames.
   If the content forces 30+ frames for a 15-min slot, push back: suggest cutting or splitting before drafting.
4. **Write the deck.** One `\begin{frame}{Title}…\end{frame}` per slide. Use `\begin{itemize}` for bullets (3-5 per frame). Put speaker notes in `\note{...}` blocks at the end of the frame.
5. **Compile to verify.** Run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` after the first three frames are drafted — catches preamble issues before they cascade into 100 errors. See `references/build-and-config.md` for the build pipeline.

## Workflow B: Convert an existing Markdown or Obsidian draft into Beamer

1. **Read the source.** Identify H1 (title), H2 sections, prose paragraphs, lists, code blocks.
2. **Default mapping:**
   - H1 → title page (`\titlepage`)
   - H2 → new frame title (`\begin{frame}{H2 text}`)
   - Lists → `\begin{itemize}…\end{itemize}`
   - Code fences → `\begin{lstlisting}…\end{lstlisting}` (load `listings` package)
   - Block quotes → `\begin{quote}…\end{quote}` or a colored `\begin{block}`
   - Inline emphasis: `**bold**` → `\textbf{...}`, `*italic*` → `\emph{...}`, `` `code` `` → `\texttt{...}`
3. **Special characters need escaping.** `_`, `&`, `%`, `#`, `$`, `{`, `}` → `\_`, `\&`, `\%`, `\#`, `\$`, `\{`, `\}`. Backticks become straight quotes or use the `listings` package for verbatim text.
4. **Figures.** Markdown image paths (`![](./figures/foo.png)`) → `\includegraphics[width=...]{figures/foo}` (omit extension; Beamer resolves it). Keep figures under `figures/` next to the `.tex` for the bundled `.latexmkrc` discovery.
5. **Iterate.** Compile after each section is converted; LaTeX is much less forgiving than Markdown — fix as you go.

## Workflow C: Build and export

Local prereq: `latexmk` and a TeX distribution (`pdflatex`). Both are pre-installed on this system.

```bash
# One-shot compile
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

# Continuous compile + preview (delegate to presentation-builder subagent)
latexmk -pdf -pvc main.tex

# Clean intermediate files (.aux, .log, .nav, .snm, .out, .toc, .vrb)
latexmk -c

# Full clean (also removes the .pdf)
latexmk -C
```

`-interaction=nonstopmode` makes LaTeX exit on errors instead of dropping into an interactive prompt — essential for scripted compilation. `-halt-on-error` stops on the first error rather than trying to recover (which produces 80 cascading errors).

For multi-output batch builds (PDF for distribution + handout-mode PDF + speaker-notes PDF), see `references/build-and-config.md`.

## Workflow D: Create or customize a theme

Beamer themes are LaTeX style packages (`.sty` files) named `beamertheme<Name>.sty`. The bundled `assets/themes/beamerthemeMinimal.sty` is a token-surface extension of Madrid: colors, font choices, and footer text are defined as macros at the top of the file so brand-specific values can be confirmed once and propagate to every deck that uses `\usetheme{Minimal}`.

1. **Start from `assets/themes/beamerthemeMinimal.sty`** — it's a commented stub. Override the brand-specific values (BrandPrimary, BrandSecondary, BrandAccent, footer text) with your own.
2. **Register the theme.** Beamer requires the `.sty` file on `TEXINPUTS`. Three ways:
   - Copy it next to the `.tex` source (simplest, recommended for self-contained decks).
   - Put it in `~/texmf/tex/latex/local/` and run `texhash`.
   - Set `TEXINPUTS=./themes:$TEXINPUTS` before invoking `latexmk`.
3. **Reference it from the deck.** `\usetheme{Minimal}` (the suffix after `beamertheme`, NOT the filename).
4. **Iterate.** Edit the `.sty`, rerun `latexmk -pdf main.tex`. With `latexmk -pvc` the rebuild is automatic.

### Theme resolution

Themes resolve in two locations, in order:

1. **User themes** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/beamer/beamertheme*.sty`. Survives plugin updates.
2. **Bundled themes** — `assets/themes/beamertheme*.sty` relative to this skill (e.g. `beamerthemeMinimal.sty`).

User themes shadow bundled ones when the basename matches. When listing themes to the user, prefix each with `(user)` or `(bundled)` so the active source is unambiguous. **Copy** the resolved file next to the `.tex` source before compiling — Beamer needs to find it on `TEXINPUTS`, and the user's project directory is the safest place.

**Save the current working theme** as a reusable user theme:

```bash
bash scripts/save-theme.sh beamer <name> ./beamerthemeFoo.sty
# add --force before "beamer" to overwrite an existing user theme
```

Full per-package selector reference (`\setbeamercolor`, `\setbeamerfont`, `\setbeamertemplate`) lives in `references/authoring.md` under "Theme internals".

## Common pitfalls

- **Unescaped underscores in identifiers, URLs, or filenames** — `\_` everywhere or wrap in `\texttt{}`.
- **Forgetting `[fragile]` on frames with `lstlisting`** — `\begin{frame}[fragile]{Title}` is required when the frame contains verbatim content.
- **`\usetheme{...}` mismatch with the `.sty` filename** — the argument is the suffix after `beamertheme`, not the file name. `beamerthemeMinimal.sty` → `\usetheme{Minimal}`.
- **`latexmk` not detecting a re-run** — when you add a `\label` referenced before its definition, run twice or rely on `latexmk` which handles it automatically.
- **Aspect ratio mismatch with a venue's projector** — declare it in `\documentclass[aspectratio=169]{beamer}` (or `43` for 4:3). Mixing breaks template layouts.
- **Trying to use Markdown-style inline formatting** — `**bold**` is literal in LaTeX. Use `\textbf{...}`.
- **Missing fonts for non-default themes** — themes like Madrid use the default Computer Modern; the bundled Minimal theme inherits Madrid's fonts. If a custom theme references a font you don't have installed, LaTeX falls back silently and the deck looks wrong.

## Quality checklist before delivering

- [ ] Title page renders correctly (`\title`, `\author`, `\institute`, `\date` all populated)
- [ ] Page numbers / pagination visible on content frames (theme-dependent — verify visually)
- [ ] All figures resolve (no `LaTeX Warning: File \`...\' not found` in the log)
- [ ] No `LaTeX Warning: Reference \`...\' on page ... undefined` (run `latexmk` twice or once with `-pvc` to settle)
- [ ] No `Overfull \hbox` warnings on critical text frames (content runs off-slide)
- [ ] Speaker notes present in `\note{...}` blocks for every content frame (skip title/section dividers)
- [ ] Aspect ratio matches the venue's projector
- [ ] Backup section present for thesis defense (Q&A material parked there, not in the main flow)
