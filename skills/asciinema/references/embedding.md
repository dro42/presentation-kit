# Embedding Reference

How to embed a `.cast` recording into each consuming format. The per-format snippets live in `assets/embed-snippets/`; this file explains the underlying mechanism and what to do when things don't work.

## Live web embed (Marp HTML, Slidev, reveal.js)

These three formats can host a JavaScript player at runtime. The player is `asciinema-player` (npm package; also CDN-distributed).

**Marp** ships HTML straight to the browser, so the standard web-component embed works. Marp HTML export is required (PDF/PPTX strip JS):

```html
<!-- in a Marp slide body, with `html: true` in marp.config.js -->
<script src="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.1/dist/bundle/asciinema-player.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/asciinema-player@3.7.1/dist/bundle/asciinema-player.css" />

<asciinema-player src="demo.cast" cols="100" rows="30"></asciinema-player>
```

**Slidev** runs Vue. Wrap `asciinema-player` in a Vue component (`components/AsciinemaPlayer.vue`) and use it inline:

```vue
<AsciinemaPlayer src="/demo.cast" :cols="100" :rows="30" />
```

The component must be registered (Slidev auto-imports anything under `components/`). The bundled `slidev` skill ships this component.

**reveal.js** uses the same web component approach as Marp HTML:

```html
<section>
  <asciinema-player src="demo.cast" cols="100" rows="30"></asciinema-player>
</section>
```

Add `<script>` and `<link>` to the reveal.js theme root once; the component then works in every slide section.

## Static embed (Beamer PDF, pptx, GitHub README)

PDF and pptx can't host JS. Convert the cast to an animated GIF first (see `conversion-agg-svg.md`), then embed the GIF:

**Beamer:** `\includegraphics{demo.gif}` shows only the first frame in most PDF viewers. For true playback in Adobe Acrobat, use the `animate` package:

```latex
\usepackage{animate}
% ... later ...
\animategraphics[loop,autoplay,width=0.85\textwidth]{12}{demo-frames/frame-}{0}{N-1}
```

`animategraphics` requires pre-extracted frames (`demo-frames/frame-0.png`, ..., `frame-N-1.png`). Use `ffmpeg` or a frames-export from `agg` to produce them. This is the only path to true playback in PDF; many audiences will see static GIFs in Preview/Skim regardless.

**pptx:** `python-pptx` adds a GIF via `slide.shapes.add_picture('demo.gif', x, y)`. PowerPoint plays GIFs in *slideshow mode* (not in the editing view). The bundled `pptx` skill's `generate.py` supports `image: ./demo.gif` in any `layout: image` slide spec.

**GitHub README / web:** `![demo](demo.gif)` works directly. No conversion needed if your cast is already a GIF.

## Sizing and aspect ratio

`asciinema-player` honors the cast's recorded dimensions, scaled to fit the container. Override with `cols`/`rows` props if you want a different scale (e.g. force `cols=120` for a 100-col cast — characters appear smaller).

For static GIF embeds, the `agg` output dimensions are `font-size × cols` wide and `font-size × line-height × rows` tall. A `font-size=18` 100×30 cast produces a ~1800×630 GIF.

Slide content area is usually ~9 inches wide on a 16:9 deck. A 1800-pixel GIF scales down cleanly. Anything wider gets squished or cropped.

## When live embed fails

Common failure modes and fixes:

| Symptom | Cause | Fix |
|---|---|---|
| Player loads but cast doesn't | Wrong path or 404 | Check browser devtools; `src` is relative to the HTML, not the markdown |
| Player invisible / 0×0 | Marp PDF export | Marp PDF strips JS. Export HTML, or convert to GIF for PDF |
| Slidev export `--format pdf` blank | Same — Playwright renders the live page, but PDF capture skips JS animations | Embed the cast *and* a static GIF; show GIF in PDF, player in HTML |
| Garbled characters | Cast `width`/`height` mismatch with player config | Re-record with `--cols/--rows` matching what you set in the player |
| Looks fine in dev, broken in prod | CDN URL changed | Pin the asciinema-player version: `asciinema-player@3.7.1` not `latest` |

## Cast hosting

The `.cast` file needs to be reachable by the browser at runtime:

- **Marp HTML export:** place `demo.cast` next to `slides.html` (relative path).
- **Slidev:** place `demo.cast` under `public/` (Vite serves `public/*` from `/`); reference as `src="/demo.cast"`.
- **reveal.js:** place next to the deck or under a `media/` folder.
- **Public hosting:** upload to asciinema.org (`asciinema upload`) and use the returned URL.

For private demos, host on internal infrastructure or inline the cast as base64 in the HTML (large but self-contained).
