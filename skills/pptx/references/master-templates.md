# Master Templates Reference

How to use, create, and customize `.pptx` master templates for branded output.

## What a master template is

A `.pptx` master template is a normal PowerPoint file that contains:

- **Slide master** — the top-level layout (logos, page numbers, footer text)
- **Slide layouts** — individual slide types (Title, Section, Two Content, etc.)
- **Theme** — color scheme, fonts, effects
- **Default placeholder content** — boilerplate text shown in empty placeholders

`generate.py` clones one of the master's layouts for each slide it creates,
then fills the placeholders with content from the YAML spec.

## Using a master template

```bash
python3 scripts/generate.py \
    --content deck.yaml \
    --template ./brand-master.pptx \
    --output deck.pptx
```

If `meta.template:` is set in the YAML, the generator uses that path
(resolved relative to the YAML file). The CLI `--template` flag overrides.

Resolution order (highest priority first):

1. `--template <path>` CLI flag
2. `meta.template:` in the YAML
3. `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/pptx/<name>.pptx`
4. `assets/themes/<name>.pptx` (bundled — none ship in v0.2; user-supplied)
5. python-pptx default (16:9, plain styling)

## Creating a brand master in PowerPoint

The fastest path:

1. Open PowerPoint → File → New → Blank Presentation.
2. View → Slide Master.
3. On the top-level master (the largest thumbnail):
   - Change the theme colors (Slide Master → Colors → Customize Colors). Set Primary, Accent 1-6 to your brand palette.
   - Change the theme fonts (Slide Master → Fonts → Customize Fonts). Set Heading and Body fonts.
   - Drop your logo in a corner (Insert → Picture, place on the master so it appears on every layout).
4. Customize each layout if needed — most defaults are fine.
5. Close Master View → File → Save As → "PowerPoint Template" (`.pptx` works; `.potx` is also fine).

The resulting `.pptx` is now a master template. Test it:

```bash
python3 -c "
from pptx import Presentation
p = Presentation('brand-master.pptx')
print(f'{len(p.slide_layouts)} layouts:')
for i, l in enumerate(p.slide_layouts):
    print(f'  {i}: {l.name!r}')
"
```

## Saving and reusing brand masters

```bash
# Save into the XDG user-data location so it survives plugin updates
bash scripts/save-theme.sh pptx <name> ./brand-master.pptx
# Stored at: ${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/pptx/<name>.pptx
```

Then reference by name in the YAML:

```yaml
meta:
  title: "Sprint 42 Review"
  template: <name>           # resolves to ~/.local/share/.../themes/pptx/<name>.pptx
```

## Editing the master OOXML directly

`.pptx` is a zip of XML files. For programmatic master edits (e.g. CI
that bakes the current quarter's color palette into the template):

```bash
# Extract
unzip brand-master.pptx -d master-src/

# Edit ppt/theme/theme1.xml (color scheme) or ppt/slideMasters/slideMaster1.xml

# Repack (preserving structure — order matters for some readers)
cd master-src && zip -r ../brand-master.pptx . && cd ..
```

This is fragile but necessary if you can't open PowerPoint (CI / Linux
servers). For most authoring, edit in PowerPoint and commit the resulting
`.pptx` to git (git-lfs recommended for binary masters > 1 MB).

## Master template vs slide-by-slide overrides

The master sets the *default* visual identity. Each generated slide
inherits from the master but can override:

- Font sizes / colors on specific text
- Custom positioning of placeholders
- Per-slide background images

`generate.py` doesn't expose every override in the YAML spec — for
fine-grained per-slide customization, either edit the generated `.pptx`
in PowerPoint manually, or extend `layouts.py` with custom-render
functions.

## Master template not shipping in v0.2

This skill does **not** ship a bundled `minimal.pptx` master. Reasons:

- Binary files in git bloat the repo (especially after multiple updates).
- The python-pptx default master is already minimal and works without
  configuration.
- Users with brand requirements ship their own; users without don't need
  one.

If you want a bundled minimal master in v0.3, generate it once via:

```python
from pptx import Presentation
p = Presentation()        # default master
p.save('assets/themes/minimal.pptx')
```

Track it with git-lfs to keep the repo trim.
