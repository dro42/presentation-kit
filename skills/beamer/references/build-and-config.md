# Beamer Build and Configuration Reference

How to compile Beamer decks reliably, configure `latexmk`, read errors, and produce multi-output PDFs (presentation + handout + notes).

## One-shot compile

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Flag-by-flag:

- `-pdf` — produce PDF via `pdflatex`. (Alternatives: `-lualatex`, `-xelatex`. Pick one and stay with it for the whole deck; switching mid-project produces flag warnings.)
- `-interaction=nonstopmode` — never drop into the interactive `?` prompt on errors; print and continue (or exit on `-halt-on-error`). Essential for scripted invocation.
- `-halt-on-error` — stop on the first error rather than producing 80 cascading errors. Pair with `-interaction=nonstopmode` to fail fast and informatively.

For decks that use `bibtex` or `biber` for references, `latexmk` figures out the right number of passes automatically — no manual `pdflatex && bibtex && pdflatex && pdflatex` chain needed.

## Continuous build with preview

```bash
latexmk -pdf -pvc main.tex
```

- `-pvc` (preview-continuous) — watches the source, rebuilds on change, refreshes the configured PDF viewer.
- Add `-view=none` if you want to suppress the viewer launch and tail the log instead.

Delegate this to the `presentation-builder` subagent so the main Claude conversation stays free.

## Cleaning intermediate files

```bash
latexmk -c    # remove .aux, .log, .nav, .out, .snm, .toc, .vrb, .fls, .fdb_latexmk (keep .pdf)
latexmk -C    # full clean: also removes the .pdf
```

Add the intermediates to your `.gitignore` — the bundled `.gitignore` in `presentation-kit` already does this. Don't commit `.aux` files; they're regenerated on every build.

## `.latexmkrc` for project-level configuration

Place a `.latexmkrc` next to `main.tex` to set defaults without command-line flags:

```perl
# .latexmkrc — settings inherited by every latexmk invocation in this directory
$pdf_mode = 1;                              # always build PDF (equivalent to -pdf)
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';
$pvc_view_file_via_temporary = 0;           # update the viewer in place on -pvc
$clean_ext = 'synctex.gz nav snm vrb';      # add to the default clean list

# macOS Skim as the PDF previewer (Preview.app does not auto-reload):
# $pdf_previewer = 'open -a Skim';
```

Settings persist across rebuilds, are shared with collaborators via git, and override the defaults `latexmk` ships with.

## Reading the log

`latexmk` is verbose. The errors you care about live in the `.log` file alongside `main.tex`. The grep patterns to know:

```bash
grep -E "^! |LaTeX Error|LaTeX Warning: Reference|Overfull|Underfull|File \\`.*' not found" main.log
```

- `! LaTeX Error: ...` — hard error. Halts compilation. Read the line that follows for the cause.
- `LaTeX Warning: Reference \`xxx' on page N undefined on input line M` — `\ref`/`\cite` to an undefined label. Fix the typo or define the label; `latexmk` will re-run automatically.
- `LaTeX Warning: There were undefined references` — same root cause, summary at end of run.
- `Overfull \hbox (X pt too wide) in paragraph at lines M--N` — content overflows the slide horizontally. Shrink an image, drop a word, or `\small` the surrounding text.
- `Underfull \hbox (badness Y) in paragraph at lines M--N` — text stretched to fill (usually harmless; cosmetic).
- `File \`figures/foo' not found` — missing graphic. Check path and extension.

The cascade rule: when `pdflatex` reports 30+ errors, look at the *first* one. Subsequent errors are almost always artifacts of the first.

## Common error patterns and fixes

| Error | Cause | Fix |
|---|---|---|
| `! LaTeX Error: File \`beamertheme<X>.sty' not found.` | `.sty` not on `TEXINPUTS` | Copy the theme `.sty` next to `main.tex` |
| `! Undefined control sequence. l.42 \pause` | `pause` used inside non-pausable block | Use `\onslide<2->{...}` or restructure |
| `! Use of \@hangfrom doesn't match its definition.` | Stale `.aux` after class change | `latexmk -C && latexmk -pdf main.tex` |
| `! LaTeX Error: Missing \begin{document}.` | Encoding mismatch (BOM in source, wrong `inputenc`) | Save as UTF-8 without BOM; `\usepackage[utf8]{inputenc}` |
| Frame containing `lstlisting` produces gibberish | Frame is not `[fragile]` | `\begin{frame}[fragile]{Title}` |
| Bibliography missing entries | Forgot `\bibliography{...}` or wrong backend | Use `biblatex` + `biber` consistently |

## Multi-output builds

A polished thesis defense often ships three artifacts: the live deck, a print handout (no overlays), and a speaker-notes PDF.

**Handout mode** (single PDF without overlays — every `\pause` collapsed):

```latex
\documentclass[aspectratio=169,handout]{beamer}
```

For dual-output without source duplication, conditional on a macro:

```latex
% main.tex
\providecommand{\BEAMERMODE}{presentation}   % overridden via -usepretex
\documentclass[aspectratio=169,\BEAMERMODE]{beamer}
```

Build both modes from the command line:

```bash
latexmk -pdf -jobname=main-presentation -usepretex='\def\BEAMERMODE{}' main.tex
latexmk -pdf -jobname=main-handout      -usepretex='\def\BEAMERMODE{handout}' main.tex
```

**Speaker notes mode** (PDF showing only the notes — useful for printing):

```latex
\usepackage{pgfpages}
\setbeameroption{show only notes}      % or "show notes on second screen=right" for dual-display talks
```

Toggle this in a small wrapper `.tex` file that includes the main source, or via a `\providecommand` flag like above.

For dual-display rendering during the actual talk (audience sees slides, you see notes + next-slide preview), use [pdfpc](https://pdfpc.github.io/):

```bash
brew install pdfpc
pdfpc main.pdf
```

## Pre-flight: how to know the build will succeed

Before claiming a Beamer deck is "done":

1. `latexmk -C && latexmk -pdf main.tex` — full clean rebuild from scratch. Catches stale-`.aux` issues that don't surface in incremental builds.
2. `grep -E "Warning|! " main.log | head` — scan the warning surface. Aim for zero `LaTeX Warning: Reference`, zero `Overfull \hbox` on content frames.
3. Open the PDF, page through every frame. LaTeX compiles many things that look wrong (cut-off text, missing figures, broken overlays).
4. If the deck uses overlays (`\pause`, `\onslide`), check the *total page count* of the PDF — each overlay step adds a page. A 12-frame deck with three `\pause`d frames produces ~15-18 PDF pages.

## Reproducibility note

Pin your TeX distribution version in any thesis-grade deck. Beamer themes occasionally change subtly between TeX Live releases; if a reviewer rebuilds from source two years later with a different distribution, the layout can shift. Document the build environment in the project's `README.md`:

```
Built with TeX Live 2025 (pdflatex 3.141592653-2.6-1.40.27).
Required packages: beamer, booktabs, listings, hyperref, graphicx.
```
