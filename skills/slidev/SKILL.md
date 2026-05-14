---
name: slidev
description: Author Vue/Markdown presentation decks with Slidev — interactive code blocks with twoslash, built-in layouts, custom Vue components, theme packages, and PDF/PPTX/SPA export. Use this skill whenever the user wants a Slidev deck, mentions Slidev, asks for "developer-focused slides", "Vue presentation", "interactive code in slides", "slides with live demos", needs to embed asciinema casts or Mermaid diagrams that Marp/Beamer can't render natively, or wants a deck with hot-reload dev experience. Trigger eagerly when the user says "sprint review", "tech talk", or "engineering demo" — Slidev is the strongest fit for technical audiences.
---

# Slidev Skill

[Slidev](https://sli.dev) is a presentation framework built on Vue + Vite + Markdown. Compared to Marp, Slidev trades simplicity for power: interactive code blocks with `twoslash` TypeScript hints, built-in layouts (`cover`, `two-cols`, `image-right`, `iframe`, `quote`), Vue components (`<Toc/>`, `<Youtube/>`, `<Tweet/>`, `<Arrow/>`), theme packages, drawing tools, presenter mode with notes, and live remote-audience interaction.

The cost: a npm-based project (not a single markdown file) and Playwright/Chromium for PDF export.

Companion skills: `marp` (lighter Markdown decks), `beamer` (LaTeX), `pptx` (corporate output), `asciinema` (terminal-demo embeds — Slidev integrates cleanly via a custom Vue component).

## When to read what

- Scaffold a new deck → stay here, Workflow A.
- Author with layouts and code blocks → `references/authoring.md`, `references/layouts.md`.
- Custom components, addons, Monaco editor → `references/components.md`.
- Build, export to PDF/PPTX/SPA → `references/export-and-config.md`.
- Build or extend themes (npm package or local directory) → `references/themes.md`.

## Quick reference card

```markdown
---
theme: ./slidev-theme-minimal
title: <DECK TITLE>
info: |
  ## <SUBTITLE>
  Authored with Slidev.
class: text-center
transition: slide-left
mdc: true
---

# <DECK TITLE>

<SUBTITLE>

<div class="abs-br m-6 text-xl">
  <NAME> &middot; YYYY-MM-DD
</div>

---
layout: default
---

## Section heading

- Bullet 1
- Bullet 2

<!--
Speaker notes go inside an HTML comment at the END of a slide.
This appears in the presenter view.
-->

---
layout: two-cols
---

## Left column content

::right::

## Right column content
```

Slide separator is `---` with an **optional** YAML frontmatter block immediately after it (sets `layout:`, per-slide `class:`, etc.). The opening frontmatter at the top is the deck-level config.

## Workflow A: Scaffold a new deck

1. **Initialize a Slidev project:**
   ```bash
   npm init slidev@latest my-deck
   cd my-deck
   ```
   This creates `slides.md`, `package.json` with `@slidev/cli`, and a `components/` directory.

2. **Pick a template** based on context (the 8 templates mirror marp/beamer):
   - `assets/templates/basic/slides.md` — generic deck, default layouts.
   - `assets/templates/academic/slides.md` — conference/seminar shape.
   - `assets/templates/thesis-defense/slides.md` — bachelor/master defense skeleton.
   - `assets/templates/research-update/slides.md` — 5-8 frame supervisor check-in.
   - `assets/templates/sprint-review/slides.md` — agile demo with asciinema embed wiring.
   - `assets/templates/tech-talk/slides.md` — engineering talk with code-heavy slides.
   - `assets/templates/lightning-talk/slides.md` — 5-min talk, 4-6 slides max.
   - `assets/templates/kickoff/slides.md` — project kickoff with timeline/risks/decisions.
3. **Copy the template content over the scaffolded `slides.md`:**
   ```bash
   cp assets/templates/sprint-review/slides.md slides.md
   ```
4. **Install the bundled minimal theme** (a local directory theme, NOT an npm package):
   ```bash
   cp -R assets/themes/slidev-theme-minimal ./
   # frontmatter references it as: theme: ./slidev-theme-minimal
   ```
5. **Apply the slide-budget rule** (one slide per minute of talk; see `marp/SKILL.md` Workflow A for the per-format table).
6. **Run the dev server:** `npx slidev` — opens `http://localhost:3030` with hot reload.

## Workflow B: Author with layouts and components

Slidev's power lives in the built-in layouts and components. Read `references/layouts.md` for the full catalog; `references/components.md` for the components.

The five layouts you'll use 80 % of the time:

| Layout | Use case |
|---|---|
| `cover` | Title slide (deck-level frontmatter usually defaults to this) |
| `default` | Standard content slide with title + body |
| `section` | Section divider (large centered text) |
| `two-cols` | Two-column layout; content split by `::right::` marker |
| `image-right` / `image-left` | Image + body split |

Components worth knowing:

- `<Toc />` — auto-generated table of contents.
- `<Youtube id="..." />`, `<Tweet id="..." />` — embed external media.
- `<Arrow x1="..." y1="..." x2="..." y2="..." />` — annotate slides with arrows.
- `<LightOrDark>` — conditional render for light vs dark color schemes.
- `<AsciinemaPlayer src="/demo.cast" />` — bundled in templates that need terminal demos.

## Workflow C: Code blocks with line highlights and twoslash

Slidev shines on code-heavy slides. The fenced code block syntax supports per-line highlights and TypeScript "twoslash" type hints:

````markdown
```ts {2-4|6|all}
function compute(x: number): number {
  const a = x * 2;
  const b = a + 1;
  const c = b * b;
  return c;
}
compute(5);  // 121
```
````

The `{2-4|6|all}` notation creates "click steps" — lines 2-4 highlight first, click to reveal line 6 highlight, click again for all. This replaces awkward `\pause`-style overlays.

`twoslash` adds inline type information (red squiggles for type errors, hover info for inferred types):

````markdown
```ts twoslash
const arr: number[] = [1, 2, 3];
arr.foo();
//  ^? — TypeScript error inline
```
````

twoslash requires TypeScript installed in the project: `npm install -D typescript`.

## Workflow D: Embed an asciinema cast

The companion `asciinema` skill produces `.cast` files. To embed them as a live player in Slidev:

1. Install: `npm install asciinema-player`.
2. Create `components/AsciinemaPlayer.vue` — full code in `asciinema/assets/embed-snippets/slidev.md`.
3. Place `demo.cast` under `public/` (Vite serves it from `/`).
4. In any slide: `<AsciinemaPlayer src="/demo.cast" :cols="100" :rows="30" />`.

For PDF export, the live player renders as the first-frame snapshot. If you need motion in PDF, also embed the asciinema-derived GIF on the same slide and conditionally hide one with `v-if="!$slidev.nav.exportToPdf"`.

## Workflow E: Build and export

```bash
# Dev server with hot reload (recommended for authoring)
npx slidev

# Static SPA (deployable to Netlify, Vercel, GitHub Pages)
npx slidev build
# Output: dist/  (commit to gh-pages or upload)

# PDF export (uses Playwright — installs Chromium on first run)
npx slidev export --format pdf --with-clicks
# Output: slides-export.pdf

# PPTX export (experimental in Slidev; expect formatting drift)
npx slidev export --format pptx

# Speaker notes PDF
npx slidev export --format pdf --with-notes
```

Long builds delegate to the `presentation-builder` subagent so the main conversation stays clean.

`--with-clicks` expands each click step into its own PDF page (matches the live deck). `--with-toc` adds a table of contents page.

**After PDF export succeeds, invoke the `slide-overflow-check` skill on the output PDF before reporting completion.** Slidev's flexible layout components (especially `two-cols`, `image-right`, code blocks with `{1-3|4|all}` click-step expansion) are particularly prone to overflowing the canvas at export time even when the live preview looked fine. One-line invocation:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/slide-overflow-check/scripts/check_overflow.py slides-export.pdf
```

If a slide flags, common Slidev fixes: switch to a smaller built-in layout, add `class: text-sm` to the slide frontmatter, or split the click-step expansion into multiple slides.

## Workflow F: Themes

Slidev themes come in two shapes:

1. **npm package** — `theme: <package-name>` resolves to `slidev-theme-<package-name>` on npm. Built-ins: `@slidev/theme-default`, `@slidev/theme-seriph`, `@slidev/theme-apple-basic`.
2. **Local directory theme** — `theme: ./path/to/theme-dir` resolves to a local directory with a `package.json` declaring `slidev.defaults`. Works with `slidev export`, dark/light switching, and upgrades without npm publish.

This skill bundles `assets/themes/slidev-theme-minimal/` as a local directory theme. Copy it into your project root and reference via `theme: ./slidev-theme-minimal`.

### Theme resolution

User themes resolve in two locations:

1. **User themes** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/slidev/<name>/` (a directory).
2. **Bundled themes** — `assets/themes/slidev-theme-minimal/` (this skill's local directory theme).

When listing themes, prefix each with `(user)` or `(bundled)` so the active source is unambiguous. Copy the resolved directory into the user's project root before they reference it.

**Save a customized theme** (entire directory copy):

```bash
bash scripts/save-theme.sh slidev <name> ./slidev-theme-myproject
# add --force before "slidev" to overwrite an existing user theme directory
```

## Prerequisites and install commands

- **Node.js** (required) — Slidev needs ≥ 18.x. macOS: `brew install node` or use `fnm`/`nvm`.
- **Slidev** — `npm init slidev@latest <project>` bootstraps the entire toolchain.
- **Playwright + Chromium** (for `slidev export`) — automatically downloaded by `slidev export` on first run (~150 MB). To pre-download: `npx playwright install chromium`.
- **TypeScript** (for twoslash code blocks) — `npm install -D typescript`.

Surface install commands to the user. Never auto-install.

## Common pitfalls

- **`theme: minimal` without the directory** — Slidev tries to resolve `slidev-theme-minimal` on npm and fails. Either use `theme: ./slidev-theme-minimal` after copying the directory in, or omit the theme entirely (Slidev defaults to `@slidev/theme-default`).
- **PPTX export loses Vue components** — anything Vue-rendered (custom components, asciinema player, mermaid diagrams) becomes a static screenshot in the .pptx. If pptx is the target format, the `pptx` skill is a better fit.
- **`mdc: true` changes `:::` semantics** — block-level extensions parse differently. Stick to defaults unless you need MDC syntax.
- **Twoslash without TypeScript installed** — silent failure; type hints don't appear and there's no error. Add `npm install -D typescript`.
- **`public/` vs project root for static assets** — Vite serves `public/foo.png` as `/foo.png`. References must use the root-relative form (`/foo.png`), not the source-relative form (`./public/foo.png`).
- **Dark/light switching with `colorSchema: all`** — your custom CSS must define both. Test both before delivering.
- **`slidev export` blank PDF** — Playwright/Chromium not installed. Run `npx playwright install chromium` once.

## Quality checklist before delivering

- [ ] `npx slidev build` exits 0; `dist/index.html` opens cleanly in a browser.
- [ ] `npx slidev export --format pdf` produces a non-empty PDF (≥ 50 KB).
- [ ] Slide count matches the talk slot.
- [ ] Speaker notes present on every content slide (HTML comments at end).
- [ ] Theme renders both light and dark if `colorSchema: all` is declared.
- [ ] Asciinema casts (if any) placed under `public/` and referenced by root-relative paths.
- [ ] Code blocks use line highlights / twoslash where they add value, not where they don't.
- [ ] `package.json` pins `@slidev/cli` to a specific version (not `latest`).
- [ ] **`slide-overflow-check` ran clean against the exported PDF** (no footer-collision or off-canvas warnings). See the companion `slide-overflow-check` skill.
