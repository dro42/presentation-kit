# Layouts Reference

How the YAML `layout:` field maps to python-pptx slide layouts.

## The lookup

`generate.py` reads layouts from the master template by name. Default
PowerPoint masters ship 11 layouts:

| Index | Default name (en-US) |
|---|---|
| 0 | Title Slide |
| 1 | Title and Content |
| 2 | Section Header |
| 3 | Two Content |
| 4 | Comparison |
| 5 | Title Only |
| 6 | Blank |
| 7 | Content with Caption |
| 8 | Picture with Caption |
| 9 | Title and Vertical Text |
| 10 | Vertical Title and Text |

`generate.py` maps YAML `layout:` values to these as follows (lookup is
case-insensitive and ignores spaces/dashes):

| YAML `layout:` | Preferred master layout name | Fallback index |
|---|---|---|
| `title` | "Title Slide" | 0 |
| `section` | "Section Header" | 2 |
| `bullets` | "Title and Content" | 1 |
| `image` | "Picture with Caption" | 8 |
| `two_column` | "Two Content" | 3 |
| `code` | "Title and Content" | 1 |
| `quote` | "Title and Content" | 1 |
| `end` | "Title Slide" | 0 |

If the master template renames or removes a layout, the generator falls
back to the index. If neither resolves, the generator uses
`slide_layouts[1]` (Title and Content) as a last resort and prints a
warning.

## Custom layout names in a brand template

If your `.pptx` master defines custom layouts (`Sprint Review Title`,
`Demo Slide`), reference them directly in the YAML — `generate.py`
prefers exact name matches when present:

```yaml
- layout: "Sprint Review Title"      # custom layout name from your master
  title: "Sprint 42 Review"
  subtitle: "What we shipped"
```

Spaces and punctuation are preserved in the lookup. The fallback only
kicks in when the master doesn't have a layout by the YAML name AND
doesn't have one by the canonical name in the table above.

## Inspecting a master template

```bash
python3 -c "
from pptx import Presentation
p = Presentation('master.pptx')
for i, layout in enumerate(p.slide_layouts):
    print(f'{i:2}: {layout.name!r}')
"
```

Run this once on a new master to see what's available before authoring
deck YAML against it.

## Placeholder index quirks

Within a layout, placeholders are accessed by index. python-pptx exposes
them via `slide.placeholders[idx]` where:

- `idx = 0` is usually the title
- `idx = 1` is usually the body / content
- Higher indices are layout-specific (e.g. `Two Content` has 1 and 2 for
  left and right; `Picture with Caption` has 1 for image and 2 for caption)

`generate.py` knows the canonical indices for each layout. If a brand
master uses non-standard placeholder ordering, you'll see content land in
unexpected slots. Fix in PowerPoint (rearrange placeholders in the master
view) or override in `layouts.py`.

## Adding a new layout shape

To extend `generate.py` to support a new YAML layout:

1. Add the YAML→master mapping in `layouts.py`'s `LAYOUT_MAP` dict.
2. Write a renderer function `render_<layout_name>(slide, spec)` that
   populates placeholders from the YAML spec.
3. Register it in `generate.py`'s dispatch table.
4. Document the YAML shape in `deck-yaml-spec.md`.

The existing layouts (`title`, `section`, `bullets`, `image`, `two_column`,
`code`, `quote`, `end`) are implemented this way and serve as references.
