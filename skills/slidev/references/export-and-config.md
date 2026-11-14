# Slidev Export and Configuration Reference

How to build, export, and configure a Slidev project for delivery.

## Dev server

```bash
npx @slidev/cli                       # opens http://localhost:3030, hot reload
npx @slidev/cli --port 5050           # custom port
npx @slidev/cli --remote              # accept connections from network (audience interaction)
```

In `--remote` mode, Slidev prints a URL and QR code for audience devices. Audiences can draw on slides (with `--drawings`) or send messages.

## Build static SPA

```bash
npx @slidev/cli build
# Output: dist/  (a deployable static site)
```

`dist/` is a Vite-built SPA. Deploy targets:
- GitHub Pages: `npm install -D gh-pages && npx gh-pages -d dist`
- Netlify: drag-drop `dist/` or point at the repo with build command `slidev build`
- Vercel: same, `slidev build` as the build command, `dist` as the output directory

For sub-path hosting (e.g. `https://example.com/my-deck/`), pass `--base`:

```bash
npx @slidev/cli build --base /my-deck/
```

## Export to PDF

```bash
npx @slidev/cli export --format pdf
# Output: slides-export.pdf
```

PDF export uses Playwright/Chromium. On first run, downloads Chromium (~150 MB). To skip the download prompt: `npx playwright install chromium` before exporting.

Flags worth knowing:

| Flag | Effect |
|---|---|
| `--with-clicks` | Expand click steps into separate PDF pages |
| `--with-toc` | Add a table-of-contents page |
| `--with-notes` | Include speaker notes (printed after each slide) |
| `--output <PATH>` | Custom output filename |
| `--timeout <MS>` | Increase per-page render timeout (default 30000) |
| `--executable-path <PATH>` | Use a specific Chromium binary instead of Playwright's |
| `--range 1-10` | Export only a slide range |

## Export to PPTX (experimental)

```bash
npx @slidev/cli export --format pptx
```

PPTX export converts each slide to a static image and embeds it in a `.pptx`. **You lose**: Vue components, code interactivity, live links. **You keep**: visual fidelity (mostly).

If pptx is a hard target, the `pptx` skill (this plugin) is a better fit — it generates pptx natively via python-pptx from a YAML deck spec.

## Export to PNG (per-slide images)

```bash
npx @slidev/cli export --format png
# Output: slides-export/slide-1.png, slide-2.png, ...
```

Useful for social-share thumbnails or video editing pipelines.

## Configuration file

`slidev.config.ts` (optional) at the project root:

```ts
import { defineConfig } from '@slidev/cli'

export default defineConfig({
  // Override Vite config
  vite: {
    server: { port: 5050 },
  },
  // Override per-deck defaults
  defaults: {
    layout: 'default',
  },
})
```

Most config is better in the deck frontmatter (it's visible to the reader). Use `slidev.config.ts` for build-time tweaks.

## `package.json` scripts

A scaffolded Slidev project ships with these scripts:

```json
{
  "scripts": {
    "build": "slidev build",
    "dev": "slidev --open",
    "export": "slidev export"
  }
}
```

Pin `@slidev/cli` to a specific version, not `latest` — Slidev minor releases occasionally change frontmatter defaults:

```json
{
  "dependencies": {
    "@slidev/cli": "^0.50.0",
    "@slidev/theme-default": "*"
  }
}
```

## Long-running export: delegate to subagent

PDF export of a 30-slide tech-talk deck via Playwright takes 60-120 s. Delegate to the `presentation-builder` subagent so the main conversation stays clean.

## Common export failures

| Symptom | Cause | Fix |
|---|---|---|
| Blank PDF | Chromium not installed | `npx playwright install chromium` |
| `Timeout 30000ms exceeded` | Slow assets (heavy mermaid, large images) | Add `--timeout 60000` |
| Custom font missing | `@font-face` not embeddable in Playwright's Chromium | Use system fonts or embed via `<link>` in `<style>` |
| Component renders blank | SSR-incompatible component | Wrap in `<ClientOnly>` |
| PDF size huge | High-res raster images at full DPI | Pre-resize images to slide dimensions (1920×1080 max) |
