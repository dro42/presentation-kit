# Deck YAML Spec

The contract `scripts/generate.py` consumes. Stable for v0.2; breaking
changes will bump the major version on this spec.

## Top-level structure

```yaml
meta:
  title: <DECK TITLE>            # required; sets the file metadata title
  author: <NAME>                 # optional; appears in file properties
  template: <name-or-path>       # optional; brand master template (see master-templates.md)
  aspect_ratio: "16:9"           # optional; "16:9" (default) | "4:3" | "16:10"
  language: en                   # optional; lang tag for accessibility metadata

slides:                           # required; list of slide specs
  - layout: title                 # required for each slide
    title: ...                    # layout-specific props follow
    ...
```

## Slide types (`layout:`)

The 8 layouts the generator understands. Each maps to a master-template
layout by name (`Title`, `Section`, etc.) with a `slide_layouts[1]` fallback
if the name isn't found.

### `title`

```yaml
- layout: title
  title: "Sprint 42 Review"
  subtitle: "What we shipped"        # optional
  notes: "..."                       # optional speaker note
```

### `section`

```yaml
- layout: section
  title: "Demo"                      # large centered text
  notes: "..."
```

### `bullets`

```yaml
- layout: bullets
  title: "What we shipped"
  bullets:
    - "Feature A — shipped Tuesday"
    - "Feature B — shipped Wednesday"
    - "Bugfix C — closed 3 P1 tickets"
  notes: "Spend 30s on each."
```

### `image`

```yaml
- layout: image
  title: "Architecture"
  image: "./figures/architecture.svg"  # path resolved relative to the YAML file
  caption: "v2 design"                 # optional; rendered below the image
  width: 0.85                          # optional; fraction of slide width (default 0.85)
  notes: "..."
```

For asciinema-derived GIFs: `image: ./demo.gif`. Plays in slideshow mode.

### `two_column`

```yaml
- layout: two_column
  title: "Before / After"
  left:
    image: "./before.png"              # one of: image | bullets | text
  right:
    bullets:
      - "Latency -42%"
      - "Errors -3%"
  notes: "..."
```

`left` and `right` each accept one of: `image`, `bullets` (list), or `text` (string).

### `code`

```yaml
- layout: code
  title: "The fix"
  language: python                    # for syntax-highlight metadata
  code_file: "./snippets/fix.py"      # OR `code: "..."` for inline
  highlight_lines: [3, 7]             # optional; emphasize specific lines
  notes: "..."
```

**Note:** python-pptx doesn't render syntax-highlighted code natively. The
generator emits the code as monospaced text with optional bold/color on
highlighted lines. For richer code rendering, use the `slidev` skill.

### `quote`

```yaml
- layout: quote
  text: "The best deck is the one you finish."
  cite: "Anonymous"                   # optional
  notes: "..."
```

### `end`

```yaml
- layout: end
  title: "Questions?"
  subtitle: "<EMAIL>"                 # optional
```

## Validation

```bash
python3 scripts/generate.py --content deck.yaml --validate-only
# exits 0 if the YAML matches the spec; exits 1 with diagnostics otherwise
```

The validator checks:
- Required top-level keys (`meta.title`, `slides`)
- Each slide has a `layout` field with a known value
- Layout-specific required props are present (e.g. `bullets` for `layout: bullets`)
- File paths in `image` and `code_file` exist relative to the YAML file
- No unknown top-level keys (typos surfaced)

## Reserved future keys

Don't use these names for custom data in v0.2 — they're reserved for v0.3
features:

- `meta.theme`, `meta.colors`, `meta.fonts` (theme overrides)
- `slides[].transition` (per-slide transitions)
- `slides[].animations` (incremental reveals)
- `slides[].background` (custom backgrounds)

Custom data the generator should pass through unchanged should live under
`meta.extra:` (a free-form dict the generator preserves in the file
properties metadata but doesn't otherwise interpret).
