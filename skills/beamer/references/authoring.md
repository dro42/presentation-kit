# Beamer Authoring Reference

Frame patterns, layout idioms, and theme-internals for `beamer` decks.

## Frame anatomy

```latex
\begin{frame}{Frame title}
  Content goes here.
  \note{Speaker note for this frame.}
\end{frame}

% With a subtitle:
\begin{frame}{Title}{Subtitle}
  ...
\end{frame}

% Verbatim content (lstlisting, verbatim, minted) requires [fragile]:
\begin{frame}[fragile]{Code example}
  \begin{lstlisting}[language=Python]
def hello():
    print("hello")
  \end{lstlisting}
\end{frame}
```

A frame title is the H2-equivalent. Avoid putting it inside the body via `\frametitle{}` unless you genuinely need a dynamic title — `\begin{frame}{Title}` is the idiomatic form.

## Blocks (visual emphasis containers)

```latex
\begin{block}{Standard block}
  Highlighted content.
\end{block}

\begin{alertblock}{Warning / key finding}
  Red-toned. Use sparingly — overuse defeats the emphasis.
\end{alertblock}

\begin{exampleblock}{Example / illustration}
  Green-toned. Good for worked examples or success cases.
\end{exampleblock}
```

Blocks pick their colors from the active theme. With `beamerthemeMinimal`, `alertblock` uses the brand accent (red by default) and `exampleblock` uses the secondary tone.

## Two-column layout

```latex
\begin{frame}{Two columns}
  \begin{columns}[T]                  % T = align tops; c = center; b = bottom
    \begin{column}{0.55\textwidth}
      \begin{itemize}
        \item Left content
      \end{itemize}
    \end{column}
    \begin{column}{0.4\textwidth}
      \includegraphics[width=\textwidth]{figures/diagram}
    \end{column}
  \end{columns}
\end{frame}
```

`\textwidth` is the *current container width*. Inside a `column` of width `0.4\textwidth`, `\includegraphics[width=\textwidth]` scales to that column, not the full slide. Sum of column widths should be ≤ 1.0; use `\hspace{0.05\textwidth}` between columns for breathing room.

## Overlays (revealing content incrementally)

```latex
\begin{frame}{Incremental reveal}
  \begin{itemize}
    \item<1-> First bullet (visible from slide 1)
    \item<2-> Second bullet (appears on slide 2)
    \item<3-> Third (appears on slide 3)
  \end{itemize}

  % Or use \pause for the simple cumulative case:
  \begin{itemize}
    \item First
    \pause
    \item Second
    \pause
    \item Third
  \end{itemize}
\end{frame}
```

`\onslide<2->{...}` reveals content; `\only<2>{...}` shows it only on slide 2; `\alt<2>{this}{otherwise that}` switches between two variants. For a thesis defense, `\pause` is usually enough — heavy `<n->` overlays cost readability.

## Figures

```latex
\includegraphics[width=0.7\textwidth]{figures/architecture}
% Beamer auto-detects extension (.pdf, .png, .jpg). Omit it.

% Centered with a caption:
\begin{figure}
  \centering
  \includegraphics[width=0.6\textwidth]{figures/results-plot}
  \caption{RQ2: remediation latency (n=10 per condition)}
\end{figure}
```

For background images (full-bleed), wrap the frame with a `tikz` backdrop or use the `\setbeamertemplate{background}` macro — see "Theme internals" below.

## Tables

Use `booktabs` rules, not vertical lines.

```latex
\usepackage{booktabs}

\begin{tabular}{lrr}
  \toprule
  Mode & False positives & False negatives \\
  \midrule
  Sidecar & 3 & 7 \\
  Ambient & 5 & 4 \\
  \bottomrule
\end{tabular}
```

For wider tables on a slide, scale down: `\resizebox{\textwidth}{!}{...}` or `\small`/`\footnotesize` font sizes.

## Code listings

```latex
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{blue!60!black}\bfseries,
  commentstyle=\color{gray},
  stringstyle=\color{red!60!black},
  showstringspaces=false,
  breaklines=true,
  frame=single,
  framerule=0.5pt,
  framesep=4pt
}

\begin{frame}[fragile]{YAML example}
  \begin{lstlisting}[language=yaml]
apiVersion: v1
kind: Service
metadata:
  name: example
  \end{lstlisting}
\end{frame}
```

`minted` (with the `-shell-escape` flag to `latexmk`) gives prettier highlighting but requires Python's Pygments. Stick with `listings` unless you need the extra polish.

## Math

```latex
% Inline:   p < 0,05 says $\alpha = 0{,}05$
% Display:
\[
  \mathrm{FPR} = \frac{\mathrm{FP}}{\mathrm{FP} + \mathrm{TN}}
\]
% Numbered:
\begin{equation}
  T_5 - T_0 = \tau_\text{detect} + \tau_\text{decide} + \tau_\text{remediate}
\end{equation}
```

For academic/Austrian contexts use `0{,}05` (comma decimal) — the `{,}` group prevents LaTeX from adding spacing after the comma as if it were punctuation.

## Theme internals

The visual identity of a Beamer deck is layered:

- `\setbeamercolor{<element>}{fg=..., bg=...}` — colors. Common elements: `palette primary`, `palette secondary`, `palette tertiary`, `structure`, `frametitle`, `title`, `block title`, `block body`, `alerted text`.
- `\setbeamerfont{<element>}{size=..., series=..., family=...}` — fonts.
- `\setbeamertemplate{<element>}{<content>}` — templates (background, footline, headline, sidebar, navigation symbols, frame title rendering).

Example: hide the navigation symbols (the small bullets bottom-right that no one uses) —

```latex
\setbeamertemplate{navigation symbols}{}
```

Example: custom footline showing author + page count —

```latex
\setbeamertemplate{footline}{%
  \hbox{%
    \hspace{1em}\insertshortauthor\hfill\insertframenumber/\inserttotalframenumber\hspace{1em}%
  }\vspace{0.4em}%
}
```

The bundled `beamerthemeMinimal.sty` uses this pattern throughout; read it as the worked example.

## Title page customization

`\titlepage` produces a default-ish title slide. For more control:

```latex
\begin{frame}[plain]
  \vspace*{1.5cm}
  {\Huge\bfseries\inserttitle\par}
  \vspace{0.5cm}
  {\Large\insertsubtitle\par}
  \vfill
  \insertauthor\\
  \insertinstitute\\
  \insertdate
\end{frame}
```

`[plain]` strips the header/footer for the title slide. The bundled `Minimal` theme styles `\titlepage` directly so you can use the default title-frame pattern instead of hand-rolling one.

## Backup sections (Q&A material)

Convention for thesis defenses:

```latex
\appendix    % everything past here numbered separately

\section*{Backup}

\begin{frame}{Backup: detailed methodology}
  ...
\end{frame}
```

`\appendix` resets the frame counter and tells the audience "we're done with the main talk." Some themes also drop the section from the navigation outline at this point.
