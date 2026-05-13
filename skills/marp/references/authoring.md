# Authoring reference: Marp/Marpit directives and slide patterns

This file is the lookup for *how to write* a slide — directives, image syntax, per-slide overrides. Read it when you need details beyond the SKILL.md quick reference.

## Frontmatter directives (apply to whole deck)

```yaml
---
marp: true              # required — without it the file is plain Markdown
theme: default          # default | gaia | uncover | <name registered via --theme-set>
size: 16:9              # 16:9 (default) | 4:3 | "1280x720" etc.
paginate: true          # show slide numbers from slide 2 onward
header: "<PROJECT> · <SHORT TITLE>"  # cascading header text (HTML allowed)
footer: "© 2026 <NAME>"              # cascading footer text
backgroundColor: "#fff" # default bg color for all slides
color: "#222"           # default text color
class: invert           # apply a class globally (e.g. invert = dark mode)

# Metadata for export (PDF/PPTX)
title: "<TITLE>"
author: "<NAME>"
description: "<DESCRIPTION>"
keywords: "<comma, separated, keywords>"
---
```

## Slide separator

A line containing only `---` (with blank lines around it) is a slide break. The first slide is everything between the closing frontmatter `---` and the next `---`.

```markdown
---
marp: true
---

# Slide 1

---

## Slide 2
```

## Per-slide directives (HTML comments)

Two flavors:

- `<!-- _directive: value -->` — applies to **this slide only** (the underscore scopes it).
- `<!-- directive: value -->` — applies from **this slide forward** until overridden.

| Directive | Example | Effect |
|---|---|---|
| `_class` | `<!-- _class: lead -->` | Apply CSS class. Built-ins: `lead` (centered hero), `invert` (dark mode swap). Custom themes add more. |
| `_backgroundColor` | `<!-- _backgroundColor: #102030 -->` | Slide background |
| `_backgroundImage` | `<!-- _backgroundImage: url('bg.jpg') -->` | Background image (use full url() syntax) |
| `_color` | `<!-- _color: white -->` | Foreground/text color |
| `_paginate` | `<!-- _paginate: false -->` | Hide page number on this slide |
| `_header` / `_footer` | `<!-- _footer: "" -->` | Override header/footer for one slide |

## Speaker notes

Plain HTML comments at the end of a slide become presenter notes in PDF (`--pdf-notes`) and PPTX exports. The Bespoke HTML template also shows them in presenter view:

```markdown
## Result: faster detection in sidecar

- T1 alert fired 12 s after fault injection
- vs ambient: 47 s average

<!-- Mention this is the most pronounced gap in the dataset — bridges to RQ2. -->
```

## Image syntax (Marpit-extended)

Standard Markdown `![alt](path)` works, plus *resize and layout keywords* in the alt text:

```markdown
![w:300px](figure.png)              # fixed width
![h:60%](figure.png)                # height as % of slide
![w:200 h:100](figure.png)          # both
![blur:8px brightness:1.2](bg.jpg)  # CSS filters in alt text
```

**Backgrounds** — use the `bg` keyword in the alt:

```markdown
![bg](photo.jpg)                    # full-bleed background, this slide
![bg fit](diagram.svg)              # contain (no crop)
![bg cover](photo.jpg)              # crop to cover (default)
![bg right:40%](chart.png)          # split layout — image on right 40%, content on left
![bg left:50% blur:4px](photo.jpg)  # split + filter
```

**Multiple backgrounds** on one slide stack horizontally:

```markdown
![bg](a.jpg)
![bg](b.jpg)
![bg](c.jpg)
```

`![bg vertical]` stacks vertically instead.

## Math (KaTeX)

Marp Core ships KaTeX. Inline `$E = mc^2$` and block `$$\\sum_{i=0}^n i$$` both render. No setup needed.

## Code blocks

Fenced code blocks render with syntax highlighting (Prism). Long code is fine — Marp shrinks to fit. For line highlighting:

````markdown
```python {1,3-5}
def foo():
    pass
```
````

## Diagrams

Mermaid is **not** built in. To include diagrams: pre-render to SVG/PNG and include as an image, or use a Marp engine plugin (out of scope for this skill).

## HTML in slides

By default Marp enables only a safe subset. Pass `--html` (or set `html: true` in `marp.config.js`) to allow arbitrary HTML. Useful for tables with custom styling or two-column layouts via `<div style="display:flex">`.

## Fragmented (incremental) lists

Bullets reveal one at a time using `*` instead of `-` in some themes, but the cleaner cross-theme approach is to split slides — incremental reveals only render in the HTML/Bespoke template, not in PDF or PPTX.

## Layout patterns

**Two-column (HTML, with `--html`)**:

```markdown
<div class="columns">
<div>

## Left column
- point
- point

</div>
<div>

## Right column
- point
- point

</div>
</div>

<style>
.columns { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
</style>
```

**Comparison slide (no HTML needed)** — split background image as separator:

```markdown
![bg left:50%](sidecar-arch.svg)

## Sidecar

- one sidecar per pod
- mTLS at L7
- ~120 MB RAM/pod
```

## Common authoring pitfalls

- The frontmatter `---` and slide-break `---` look identical but mean different things. The first occurrence ends the YAML; everything after is content.
- `theme:` in frontmatter must match the `@theme` name inside the CSS, not the filename.
- `class: lead` in frontmatter applies to *every* slide. Use `<!-- _class: lead -->` for just the title slide.
- Marpit doesn't inherit `theme:` across files; each deck specifies its own.
- For PDF export, fancy CSS that depends on JS (transitions, Bespoke controllers) is lost — design with the static export in mind.
