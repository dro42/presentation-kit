# Export reference: marp-cli flags and marp.config.js

This file is for the export side of the workflow. The CLI is the user's most-touched surface — these are the recipes that actually work, plus the config file that turns repeated incantations into one-liners.

## Preflight (60-second sanity check)

```bash
command -v marp                       # expected: /opt/homebrew/bin/marp on this machine
marp --version                        # confirm v4.x

# If exporting with a custom theme:
ls -la <path-to-theme.css>            # confirm it resolves

# If exporting PDF/PPTX, Marp needs a browser:
ls /Applications/Google\ Chrome.app /Applications/Chromium.app 2>/dev/null
# or
command -v chromium
```

## Common export commands

Run from the deck's directory (so relative image paths resolve).

```bash
# PDF — for distribution to supervisors, archival
marp deck.md --pdf --allow-local-files

# PDF with presenter notes embedded as annotations
marp deck.md --pdf --pdf-notes --allow-local-files

# PDF with outline (clickable bookmarks per slide)
marp deck.md --pdf --pdf-outlines --allow-local-files

# PPTX — when the audience expects PowerPoint
marp deck.md --pptx --allow-local-files

# PPTX with editable text (experimental but useful for last-minute edits in PowerPoint)
marp deck.md --pptx --pptx-editable --allow-local-files

# Standalone HTML (Bespoke template by default — has on-screen controller, transitions)
marp deck.md --html

# One image per slide
marp deck.md --images png             # all slides
marp deck.md --image png              # first slide only (good for a deck thumbnail)

# Image scale (PPTX defaults to 2x; bump for retina-perfect PDF thumbnails)
marp deck.md --images png --image-scale 3

# Watch mode — re-export on every save
marp deck.md --pdf --allow-local-files -w

# Server mode — live HTML preview at http://localhost:8080
marp deck.md -s .                     # serve the directory; auto-reloads on edit

# Register custom theme(s) on the fly
marp deck.md --pdf --theme-set ../themes/hcw.css --allow-local-files

# Override the theme without changing frontmatter
marp deck.md --pdf --theme gaia --allow-local-files
```

## marp.config.js — the right way to lock in flags

For decks that always export the same way (thesis decks always need the HCW theme set and allow-local-files), drop a `marp.config.js` next to the deck and skip the flags:

```js
// marp.config.js — place next to your decks (or in the vault Presentations/ root)
module.exports = {
  // Register custom theme(s). Paths are resolved relative to this config file.
  themeSet: [
    './themes/hcw.css',
    // '../shared-themes/another.css',
  ],

  // Allow <img src="./figures/foo.png"> etc. in PDF/PPTX/image exports.
  allowLocalFiles: true,

  // Let HTML tags (raw <div>, <style>, etc.) render in slide content.
  html: true,

  // Optional: pin the output directory. Default is alongside the source.
  // output: './dist',

  // Optional: choose template. 'bespoke' (default) has transitions/controller;
  // 'bare' is minimal and faster.
  // template: 'bespoke',

  // Optional: PDF-specific settings
  // pdf: true,
  // pdfNotes: true,
  // pdfOutlines: true,

  // Optional: PPTX-specific
  // pptx: true,
  // pptxEditable: true,

  // ─── Browser path: uncomment ONE of these if PDF/PPTX export fails ───
  // Apple Silicon + Homebrew Chromium is a common edge case where auto-detect breaks.
  // browser: 'chrome',                          // force a browser kind
  // browserPath: '/opt/homebrew/bin/chromium',  // explicit binary path
};
```

After this is in place, the same exports become:

```bash
marp deck.md --pdf
marp deck.md --pptx
marp deck.md -w           # watch & re-render
```

## Browser troubles (PDF/PPTX/image export)

If PDF/PPTX export errors with "Failed to launch browser" or "Browser not found":

1. **Check what's installed**:
   ```bash
   ls /Applications/Google\ Chrome.app /Applications/Chromium.app 2>/dev/null
   command -v chromium chrome google-chrome
   ```
2. **Set `CHROME_PATH` env var** (one-shot fix):
   ```bash
   CHROME_PATH=/opt/homebrew/bin/chromium marp deck.md --pdf
   ```
3. **Or set `browserPath` in `marp.config.js`** (permanent fix).
4. **Or pass on the CLI**:
   ```bash
   marp deck.md --pdf --browser-path /opt/homebrew/bin/chromium
   ```

If only Firefox or Edge is installed, pass `--browser firefox` / `--browser edge`. Marp supports WebDriver BiDi for Firefox via `--browser-protocol webdriver-bidi`.

## Format choice cheat sheet

| Need | Format | Notes |
|---|---|---|
| Submit to supervisor / archive | PDF | Universal, prints cleanly, presenter notes embeddable |
| Live presentation with transitions, presenter view | HTML (Bespoke) | Open in browser, F for fullscreen, P for presenter view |
| Audience wants to edit later (corporate context) | PPTX | Use `--pptx-editable`; expect some style fidelity loss |
| Thumbnail / preview / social-share image | `--image png` | First slide as PNG; combine with `--image-scale 2` for retina |
| Per-slide images for a poster or handout | `--images png` | One file per slide |

## Fidelity caveats — what doesn't survive each export

- **PPTX**: CSS animations stripped; gradients sometimes flattened; custom fonts may fall back; complex layouts (CSS grid two-column hacks) can break. Test before sending.
- **PDF**: Transitions and the Bespoke on-screen controller are gone (PDF is static). Speaker notes only included with `--pdf-notes`.
- **Images**: No interactivity at all; useful for thumbnails not handouts (handouts → PDF).

## Configuration file locations marp-cli searches

In order, marp picks up the first match:

1. The path passed to `-c, --config-file`
2. `marp.config.js` / `marp.config.cjs` / `marp.config.mjs` in the working directory
3. `.marprc.yml` / `.marprc.yaml` / `.marprc.json` / `.marprc.js` in the working directory
4. `marp` key inside `package.json`

To explicitly opt out of config lookup, pass `--no-config-file`.
