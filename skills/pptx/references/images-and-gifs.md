# Images and GIFs Reference

How `generate.py` handles image embedding, including asciinema-derived GIFs.

## Image layout slide

```yaml
- layout: image
  title: "Architecture"
  image: "./figures/architecture.svg"
  caption: "v2 design"            # optional
  width: 0.85                     # optional; fraction of slide width (default 0.85)
```

Path resolution:
- Absolute paths: used as-is.
- Relative paths: resolved relative to the YAML file's directory.

Supported formats (python-pptx via Pillow):
- PNG, JPEG, GIF (animated), TIFF, BMP
- SVG: python-pptx 0.6.23+ supports SVG; older versions error. Convert to
  PNG first if you hit issues: `rsvg-convert -o out.png in.svg`.

## Sizing logic

If `width` is specified, the image is sized to `width * slide_width`,
centered horizontally. Height is computed to preserve aspect ratio
(generator reads intrinsic dimensions via Pillow).

If `width` is omitted, default is `0.85` of slide width — leaves room for
the title and caption.

For a 16:9 slide (10 in × 5.625 in), `width: 0.85` produces an 8.5-inch
wide image. The height is computed; if the image's intrinsic aspect
ratio would make it overflow the content area vertically, the generator
scales down further (preserves aspect, caps height at 70 % of slide
height).

## Animated GIFs (asciinema-derived)

```yaml
- layout: image
  title: "Live deploy demo"
  image: "./demo.gif"
  caption: "Recorded with asciinema; converted via agg"
```

PowerPoint plays GIFs **in slideshow mode**, not in normal view. The
audience sees animation when you present; the editor shows the first
frame.

**Keynote shows only the first frame** even in slideshow mode. If
Keynote-on-Mac is a target, use the `slidev` skill (web-based, plays
GIFs uniformly).

**LibreOffice Impress plays GIFs** in slideshow mode similarly to
PowerPoint.

### GIF size budget

PowerPoint embeds the GIF directly in the `.pptx` (which is a zip).
A 5 MB GIF inflates the deck by 5 MB. Keep under ~10 MB per deck or the
file is unwieldy to email.

Reduce GIF size:
- Drop `agg --font-size` from 18 → 14 (smaller cells)
- Drop `agg --cols/--rows`
- Speed up with `agg --speed 1.5`

## Two-column image + bullets

```yaml
- layout: two_column
  title: "Before / After"
  left:
    image: "./before.png"
    caption: "v1 architecture"
  right:
    bullets:
      - "Latency -42 %"
      - "Error rate -3 %"
      - "Cost neutral"
```

The image goes in the left column; bullets in the right. Roles can be
flipped — `generate.py` reads `image`/`bullets`/`text` on each side
independently.

## Image-in-bullets-slide (inline)

YAML doesn't support inline images in a `bullets` layout. If you need a
bullet list with an accompanying image, use `two_column` instead.

## Charts (deferred to v0.3)

python-pptx supports chart insertion (`slide.shapes.add_chart(...)`).
v0.2's `generate.py` doesn't expose this in the YAML spec because chart
authoring is rarely the best path:

- For static charts: render to PNG via matplotlib / your tool of choice
  and embed via `layout: image`.
- For interactive charts: use the `slidev` skill (Vue components let you
  embed Plotly, Vega, etc.).

v0.3 may add a `chart:` slide type. Track issue #N if you need it sooner.

## Tables

YAML doesn't support tables in v0.2's `generate.py` either. Workaround:
render the table to PNG (via pandoc, matplotlib's `pyplot.table`, or
HTML→PNG) and embed via `layout: image`.

## Speaker notes with images

Speaker notes are plain text. To reference an image in the notes:

```yaml
- layout: image
  title: "Architecture"
  image: "./figures/architecture.svg"
  notes: |
    Walk through:
    1. Client (top-left) connects to load balancer
    2. LB shards by tenant ID
    3. Cache layer in the middle
    Skip the failure-recovery path unless asked.
```

Notes are visible in presenter view; not on the projected slide.
