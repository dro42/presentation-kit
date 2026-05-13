# Slidev Layouts Reference

Built-in layouts and when to use each. Layouts are specified in per-slide frontmatter:

```markdown
---
layout: two-cols
---
```

## Built-in layouts

| Layout | When to use | Notable props |
|---|---|---|
| `cover` | First slide of the deck. Centered hero. | `background:` URL for cover image |
| `center` | Centered single-statement slide (quotes, transitions) | — |
| `default` | Standard title + body slide | — |
| `end` | Last slide (Thank-you / Q&A) | — |
| `fact` | Big-number highlight | — |
| `image` | Full-slide image background | `image:` URL, `backgroundSize:` `cover`/`contain` |
| `image-left` / `image-right` | Image on one side, body on the other | `image:` URL |
| `iframe` | Embed external page | `url:` URL |
| `iframe-left` / `iframe-right` | Same, split layout | `url:` URL |
| `intro` | Speaker introduction (your photo + bio) | — |
| `none` | No layout chrome — raw Markdown rendering | — |
| `quote` | Large quote with attribution | — |
| `section` | Section divider (large centered title) | — |
| `statement` | Single bold statement, centered | — |
| `two-cols` | Two-column body (split by `::right::`) | — |
| `two-cols-header` | Title across full width, two cols below | — |

## Two-column syntax

The `two-cols` layout splits content by a `::right::` marker:

```markdown
---
layout: two-cols
---

# Left column content

- Bullet A
- Bullet B

::right::

# Right column content

- Bullet C
- Bullet D
```

Optional `::default::` marker is implicit at the top.

## `two-cols-header` variant

```markdown
---
layout: two-cols-header
---

# Title across both columns

::left::

Left content.

::right::

Right content.
```

## Image-side layouts

```markdown
---
layout: image-right
image: ./figures/diagram.png
backgroundSize: contain
---

# Body content on the left

- The image fills the right ~40 % of the slide.
- `backgroundSize: contain` preserves aspect ratio.
- Use `cover` to fill (crops to fit).
```

## Custom layouts

A layout is a `.vue` file under `layouts/` (in the project root, NOT in the theme). The minimal layout:

```vue
<!-- layouts/big-quote.vue -->
<template>
  <div class="slidev-layout big-quote">
    <slot />
  </div>
</template>

<style scoped>
.big-quote {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-style: italic;
}
</style>
```

Then in a slide:

```markdown
---
layout: big-quote
---

"The best deck is the one you finish."
```

For theme-distributed layouts, put them in `<theme-dir>/layouts/`. The bundled `slidev-theme-minimal/layouts/cover.vue` is the example.
