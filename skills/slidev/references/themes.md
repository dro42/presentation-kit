# Slidev Themes Reference

Two flavors: **npm-package themes** and **local-directory themes**. This plugin's bundled `slidev-theme-minimal/` is a local-directory theme — the right pattern for distributing a theme without publishing to npm.

## npm-package themes

Built-in themes ship as `@slidev/theme-*`:

- `@slidev/theme-default` — clean, sans-serif, neutral
- `@slidev/theme-seriph` — serif, academic-feel
- `@slidev/theme-apple-basic` — Apple-keynote-inspired

Community themes are conventional `slidev-theme-*` packages:

- `slidev-theme-shibainu` — playful
- `slidev-theme-academic` — strict academic typography
- `slidev-theme-bricks` — geometric / bold

To use: `npm install <package>` then `theme: <name>` (without the `slidev-theme-` prefix).

## Local-directory themes (recommended for unpublished themes)

A local theme is a directory at the project root containing:

```
slidev-theme-<name>/
├── package.json          required — declares { "name": "slidev-theme-<name>",
│                                   "slidev": { "defaults": { ... } } }
├── styles/
│   └── index.css         theme-wide CSS (auto-loaded by Slidev)
├── layouts/
│   ├── cover.vue         (optional) custom layouts
│   └── *.vue
├── components/
│   └── *.vue             (optional) theme-scoped components
└── README.md             (optional) installation and customization notes
```

Reference from deck frontmatter:

```yaml
---
theme: ./slidev-theme-<name>
---
```

Slidev resolves the path relative to the deck. Local themes work with:
- `npx slidev` dev server
- `npx slidev build` SPA export
- `npx slidev export --format pdf` (Playwright)
- `colorSchema: all` light/dark switching (when CSS handles it)

## The bundled `slidev-theme-minimal`

The plugin ships `assets/themes/slidev-theme-minimal/` with:

- `package.json` declaring `slidev.defaults.aspectRatio = "16/9"`, `canvasWidth = 980`, `colorSchema = "auto"`
- `styles/index.css` with brand-token CSS custom properties (`--brand-primary`, `--brand-secondary`, etc.) matching the marp `minimal.css` token surface
- `layouts/cover.vue` for the title slide
- `README.md` with customization notes

To use it in a Slidev project:

```bash
cp -R <plugin-path>/skills/slidev/assets/themes/slidev-theme-minimal ./
# slides.md frontmatter:
#   theme: ./slidev-theme-minimal
npx slidev
```

## Token-driven customization

The bundled theme exposes brand-color tokens as CSS custom properties:

```css
/* slidev-theme-minimal/styles/index.css */
:root {
  --brand-primary:   #1f3a8a;
  --brand-secondary: #6b7280;
  --brand-accent:    #b21f1f;
  --brand-bg:        #ffffff;
  --brand-text:      #1a1a1a;
}

[data-color-schema="dark"] {
  --brand-bg:   #1a1a1a;
  --brand-text: #e6e6e6;
}
```

Override the values to match your institution / company. The tokens mirror the marp `minimal.css` and the Beamer `BrandPrimary`/etc. macros — one source of brand truth across all three formats.

## Theme resolution (presentation-kit user themes)

User themes resolve in two locations:

1. **User themes** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/slidev/<name>/` (a directory)
2. **Bundled themes** — `assets/themes/slidev-theme-minimal/`

User themes shadow bundled when basenames match. Copy the resolved directory into the user's project root before referencing it via `theme: ./<theme-dir>`.

## Saving a custom theme

```bash
bash scripts/save-theme.sh slidev <name> ./slidev-theme-myproject
# --force to overwrite an existing user-data theme directory
```

The script accepts a directory source for slidev (vs file source for other formats) and copies it recursively to the XDG user-data location.

## Building your own theme

Start from the bundled `slidev-theme-minimal`:

1. Copy `assets/themes/slidev-theme-minimal/` into a new directory: `slidev-theme-myproject/`.
2. Edit `package.json` — set `"name": "slidev-theme-myproject"`.
3. Edit `styles/index.css` — override the brand tokens and any specific selectors.
4. Add/customize layouts in `layouts/` (e.g. a custom `cover.vue` with your logo).
5. Test in a scratch project: `cp -R slidev-theme-myproject /tmp/test-deck/ && cd /tmp/test-deck && npx slidev`.
6. When satisfied, save into XDG user-data: `bash scripts/save-theme.sh slidev myproject ./slidev-theme-myproject`.

For wider distribution (multiple projects, other people), publish to npm as `slidev-theme-myproject` — drops the `./` prefix in deck frontmatter.

## What's in `slidev.defaults`

The `slidev.defaults` block in `package.json` sets deck-wide defaults the theme provides:

```json
{
  "slidev": {
    "defaults": {
      "aspectRatio": "16/9",
      "canvasWidth": 980,
      "colorSchema": "auto",
      "fonts": {
        "sans": "Inter, system-ui, sans-serif",
        "serif": "Iowan Old Style, serif",
        "mono": "JetBrains Mono, ui-monospace, monospace"
      }
    }
  }
}
```

These are overridable in deck frontmatter; they're the *default* if the deck doesn't specify. Use this to bake institutional defaults into your theme.

## Common pitfalls

- **`theme: minimal` without the directory** — Slidev tries to resolve `slidev-theme-minimal` on npm. Either publish it or use the local path `./slidev-theme-minimal`.
- **Theme styles overridden by inline CSS** — Slidev loads theme styles before deck CSS, so deck-level CSS wins. To enforce, use `!important` (sparingly) or override at the theme level.
- **Custom fonts in `styles/index.css`** — `@font-face` works in dev but may not embed cleanly in PDF export. Use system fonts or `<link>` to a hosted font in deck frontmatter.
- **Dark mode rendering** — `colorSchema: all` requires the theme CSS to define both. Test both before delivering.
