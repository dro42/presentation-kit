# Theme reference: writing and customizing Marp themes

Marpit themes are plain CSS files with one extra ingredient: a `@theme` declaration at the top that names the theme. Marp Core themes (default, gaia, uncover) extend the Marpit spec with extra classes and tokens. You can extend them via `@import` or write from scratch — extending is almost always the right move.

## Anatomy of a Marp theme CSS

```css
/* @theme my-theme */            /* required — the name used in `theme:` frontmatter */

@import 'gaia';                  /* optional but recommended — inherit a built-in baseline */

/* Theme-wide selectors — Marpit ships these */
section {                        /* a single slide */
  background: #fff;
  color: #222;
  font-family: 'Arial', sans-serif;
  padding: 70px;
}

h1 { color: #b21f1f; }
h2 { color: #1f3a8a; }

/* Built-in slide class — invert for dark-mode slides */
section.invert {
  background: #1a1a1a;
  color: #f0f0f0;
}

/* Built-in slide class — lead is centered hero/title slide */
section.lead {
  text-align: center;
}
section.lead h1 {
  font-size: 2.6em;
}

/* Marpit-specific pseudo-elements for header/footer/pagination */
header {
  font-size: 0.7em;
  color: #888;
}
footer {
  font-size: 0.6em;
  color: #888;
}
section::after {                 /* pagination number */
  color: #888;
}
```

The selectors you'll touch 90 % of the time: `section`, `section.lead`, `section.invert`, `h1`-`h3`, `p`, `ul`/`ol`/`li`, `code`, `pre`, `table`, `blockquote`, `header`, `footer`, `section::after`.

## Registering and using a custom theme

A theme is a file until it's *registered* with Marp. Three ways:

1. **In marp-cli**: `marp deck.md --theme-set path/to/theme.css --pdf`
2. **In `marp.config.js`**:
   ```js
   module.exports = { themeSet: ['./themes/minimal.css'] };
   ```
3. **In the Obsidian Marp Slides plugin**: drop the `.css` next to the deck — auto-discovered.

Then in the deck:

```yaml
---
marp: true
theme: minimal            # matches @theme inside the CSS, NOT the filename
---
```

## Extending gaia (the right baseline for academic talks)

Gaia is warm, has comfortable typography, and supports `lead`, `invert`, `gaia` classes out of the box. Extending it is 5 lines:

```css
/* @theme thesis */
@import 'gaia';

section {
  font-family: 'Arial', sans-serif;
  /* shift accent color from gaia's coral to a corporate navy */
  --accent-color: #1f3a8a;
}

h1 { color: var(--accent-color); }
h2 { color: var(--accent-color); }
section::after { color: var(--accent-color); }
```

## The minimal starter theme

`assets/themes/minimal.css` ships as a token-surface stub. Override the brand-specific values to match your institution, company, or personal identity. The token surface is exposed via CSS custom properties so a future re-brand is one search-and-replace:

```css
/* @theme minimal */
@import 'gaia';

:root {
  /* Brand tokens — override with your own values */
  --primary-color:   #1f3a8a;     /* override: brand primary */
  --secondary-color: #6b7280;     /* override: brand secondary */
  --accent-color:    #b21f1f;     /* override: brand accent */
  --bg-color:        #ffffff;
  --text-color:      #1a1a1a;
  --muted-color:     #6b7280;

  --font-family-headings: 'Arial', sans-serif;
  --font-family-body:     'Arial', sans-serif;

  --logo-path:       '';          /* drop your logo here */
  --footer-text:     '';          /* per-deck or per-project footer */
}
```

Save your customized copy as a personal theme via `bash scripts/save-theme.sh marp <name> ./my-theme.css` — it lands in `~/.local/share/presentation-kit/themes/marp/` and survives plugin updates.

## Iterating on a theme

The fastest loop is server mode:

```bash
marp deck.md -s .                  # opens http://localhost:8080
# Then edit the .css; the browser hot-reloads on save.
```

Don't iterate via PDF export — re-renders take 5-10 s each. Server mode is sub-second.

## Common theme pitfalls

- **`@theme` name vs filename mismatch.** The CSS declares `@theme minimal`. The frontmatter must say `theme: minimal`, regardless of whether the file is called `minimal.css` or `mytheme.css`.
- **Forgetting to register.** A theme that isn't on `themeSet`/`--theme-set`/co-located with the deck silently falls back to `default`.
- **Overriding Marpit pseudo-elements without `!important` doesn't work in some cases.** `section::after` (pagination) is one of them.
- **Custom fonts via `@font-face` don't survive PDF export.** Embed via system fonts or accept the fallback. For thesis-quality PDFs, prefer sans-serifs that are bundled with macOS/most systems (Arial, Helvetica) over web fonts.
- **`!important` cascades**: gaia uses `!important` on a few selectors. If your override isn't taking effect, that's usually why — match the specificity or use `!important` yourself.

## Two-column / advanced layouts

Marpit's CSS doesn't ship grid utilities. The community pattern is to define them in your theme:

```css
section.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
```

Then use in a slide:

```markdown
<!-- _class: two-column -->

## Left

- bullet
- bullet

---

## Right

- bullet
- bullet
```

(The second `---` inside a `two-column` slide doesn't break to a new slide — Marpit only breaks at top-level `---`.)

Actually, the cleaner pattern is HTML with `--html` enabled — see `references/authoring.md` for the `<div class="columns">` approach. Pick whichever matches your taste; both ship in real-world decks.

## Where to learn more

- **Marpit theme spec**: https://marpit.marp.app/theme-css
- **Marp Core (default/gaia/uncover) source**: https://github.com/marp-team/marp-core/tree/main/themes
- **Directives reference**: https://marpit.marp.app/directives

Reading the gaia source is the single best way to understand what's possible — it's ~200 lines of CSS that you can fork and mutate.
