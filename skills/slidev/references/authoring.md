# Slidev Authoring Reference

Frontmatter, slide separators, per-slide config, code blocks, and the writing patterns that pay off.

## Deck-level frontmatter

```yaml
---
theme: ./slidev-theme-minimal     # local dir theme, npm package, or '@slidev/theme-default'
title: <DECK TITLE>                # used in window title + export filename
info: |
  ## <SUBTITLE>
  Optional long-form description (Markdown allowed).
class: text-center                 # default class applied to every slide
transition: slide-left             # default transition between slides
mdc: true                          # enable MDC (Markdown Components) syntax
colorSchema: auto                  # auto | light | dark | all
drawings:
  persist: false                   # save drawings to source on quit
seoMeta:
  ogTitle: ...                     # social-share metadata for SPA build
  ogDescription: ...
download: true                     # show download-PDF button in UI
exportFilename: <name>             # base name for `slidev export` output
---
```

Only `title` is strictly required; everything else has sensible defaults.

## Slide separator

A `---` line on its own marks a new slide. **Immediately after** the `---`, you can optionally include per-slide frontmatter:

```markdown
---

# Standard slide

---
layout: two-cols
class: bg-blue-50
---

## Two-column slide
```

The per-slide frontmatter has no `---` opening fence (only a closing one). It accepts `layout:`, `class:`, `clicks:`, `transition:`, and any layout-specific props.

## Speaker notes

Speaker notes live in an HTML comment at the **end** of a slide:

```markdown
## Slide content

- Bullet 1
- Bullet 2

<!--
Speaker note. Shown in presenter view (press 'p' to toggle).
Supports Markdown.
-->
```

Slidev parses the comment as Markdown — bullets, bold, links all work.

## Click steps (overlays)

To reveal content incrementally:

```markdown
- Item A
- Item B <span v-click>(revealed on click)</span>
- Item C <span v-click="2">(revealed on click 2)</span>
- Item D <span v-after>(revealed alongside the previous v-click)</span>
```

`v-click="N"` jumps to a specific click; `v-after` reveals with the previous step.

For code blocks, line-highlight syntax is more concise:

````markdown
```ts {2-4|6|all}
const x = 1;
const y = 2;
const z = 3;
const sum = x + y + z;
// click step 2 reveals line 6
console.log(sum);
```
````

`{2-4|6|all}` means: first highlight lines 2-4, then line 6, then all lines. Each `|` is a click step.

## Code block features

```ts twoslash
// twoslash adds inline TypeScript type info
const x: number = 'hello';
//      ^? — error: Type 'string' is not assignable to type 'number'.

const arr: number[] = [1, 2, 3];
arr.filter(x => x > 1);
//   ^? — hover info on the method
```

Other code-block options:

- ` ```ts {monaco}` — embed a live Monaco editor in the slide (interactive code editing).
- ` ```ts {monaco-run}` — embed Monaco + a Run button that executes the code.
- ` ```ts {diff}` — show as a diff (use `+` and `-` line prefixes).

## Embedded media

- `<Youtube id="abcDEF12" />`
- `<Tweet id="1234567890" />`
- `<SlidevVideo controls autoplay>` for `<video>` elements.
- Standard Markdown images: `![alt](./figures/x.png)` (place files under `public/` or referenced via relative path from `slides.md`).

## Inline HTML and Vue

Slidev parses Markdown via vue-loader, so inline `<div>`, `<span>`, Vue components, and even Vue directives (`v-if`, `v-for`) all work:

```markdown
<div v-click class="grid grid-cols-2 gap-4 pt-4">
  <div>Column A</div>
  <div>Column B</div>
</div>
```

Use this when a built-in layout doesn't quite fit but you want to stay declarative.

## Conditional rendering for PDF export

```markdown
<AsciinemaPlayer v-if="!$slidev.nav.exportToPdf" src="/demo.cast" />
<img v-else src="/demo.gif" alt="demo" />
```

Renders the live player in dev/SPA, a static GIF in PDF export.

## Writing discipline

- **One claim per slide.** Same rule as Marp and Beamer; Slidev's animation tools tempt you to cram more, resist.
- **Click steps add cognitive load.** Use them where the build *teaches* something (e.g. revealing a bug, then a fix). Avoid `v-click` on every bullet just because you can.
- **Slidev makes code beautiful; that's a trap.** A talk that shows beautiful code for 30 slides has no narrative. Use code slides as evidence, not as content.
- **Test PDF export early.** Vue components that work in dev sometimes break in Playwright capture. Don't discover this the night before the talk.
