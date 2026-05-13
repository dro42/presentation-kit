# slidev-theme-minimal

A minimal starter theme for Slidev. Token-driven brand colors — override the
CSS custom properties in `styles/index.css` to match your institution or
company. The token names mirror the Marp `minimal.css` and Beamer
`beamerthemeMinimal.sty` companions so all three formats share one source of
brand truth.

## Install (local-directory theme)

This theme is **not published to npm**. Copy the directory into your Slidev
project and reference it via a relative path:

```bash
cp -R <path-to-presentation-kit>/skills/slidev/assets/themes/slidev-theme-minimal ./
```

In your `slides.md` frontmatter:

```yaml
---
theme: ./slidev-theme-minimal
---
```

This works with `npx slidev`, `npx slidev build`, and `npx slidev export --format pdf`.

## Customize

Override brand tokens in `styles/index.css`:

```css
:root {
  --brand-primary:   #YOUR-PRIMARY;
  --brand-secondary: #YOUR-SECONDARY;
  --brand-accent:    #YOUR-ACCENT;
}
```

Add custom layouts under `layouts/` (`.vue` files); add components under
`components/`. Slidev auto-imports both.

## Save your customized theme

Once tuned, save the directory into your XDG user-data location so it
survives plugin updates:

```bash
bash scripts/save-theme.sh slidev myproject ./slidev-theme-minimal
# Stored at: ${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/slidev/myproject/
```

Reference future projects via the saved directory:

```bash
cp -R ~/.local/share/presentation-kit/themes/slidev/myproject ./
```
