---
name: pptx
description: Generate PowerPoint .pptx decks programmatically from a YAML spec via python-pptx, with optional brand .pptx master templates. Use this skill whenever the user wants a PowerPoint deck without opening PowerPoint, asks to "make a pptx", "generate slides from YAML", "use our corporate template", "convert YAML to PowerPoint", "build a deck script-driven", or needs to embed asciinema-derived GIFs into pptx output. Trigger eagerly when the user mentions PowerPoint, .pptx, Keynote-compatible decks, or corporate sprint-review formats where the audience expects native Office files.
---

# pptx Skill

Generate native `.pptx` decks from a YAML deck specification using `python-pptx`. Optional `.pptx` master templates carry brand layouts (logos, color palettes, fonts) that the generator merges with the deck content.

Companion skills: `marp` and `beamer` produce decks via marp-cli / latexmk; this skill is the answer when the audience expects PowerPoint or Keynote files (corporate sprint reviews, non-technical stakeholders, venues that won't accept HTML/PDF). `asciinema` is the integration story for terminal demos — convert casts to animated GIFs and embed via the `image` layout.

## When to read what

- The YAML deck spec format → `references/deck-yaml-spec.md`.
- Layouts and slide types → `references/layouts.md`.
- Brand templates (`.pptx` masters) → `references/master-templates.md`.
- Embedding images, charts, asciinema GIFs → `references/images-and-gifs.md`.

## Quick reference card

```bash
# Generate a deck from a YAML spec
python3 scripts/generate.py \
    --content deck.yaml \
    --output deck.pptx

# With a brand master template
python3 scripts/generate.py \
    --content deck.yaml \
    --template ./brand-master.pptx \
    --output deck.pptx

# Validate the YAML spec without generating
python3 scripts/generate.py --content deck.yaml --validate-only
```

Prerequisites: `python3 -c "import pptx, yaml" || pip install python-pptx pyyaml Pillow`. The skill surfaces this command on demand — it does not auto-install.

## Workflow A: Scaffold a deck from a template

1. **Pick a template** from `assets/templates/` (the 8-slot inventory mirrors marp/beamer/slidev):
   - `basic.yaml`, `academic.yaml`, `thesis-defense.yaml`, `research-update.yaml`
   - `sprint-review.yaml`, `tech-talk.yaml`, `lightning-talk.yaml`, `kickoff.yaml`
2. **Copy the YAML into your project:** `cp assets/templates/sprint-review.yaml ./deck.yaml`.
3. **Edit the YAML.** Replace `<TITLE>`, `<NAME>`, etc. with real values. See `references/deck-yaml-spec.md` for the full schema.
4. **Generate:** `python3 scripts/generate.py --content deck.yaml --output deck.pptx`.
5. **Verify:** Open in PowerPoint, Keynote, or LibreOffice. For headless verification: `unzip -t deck.pptx` confirms the file isn't corrupt.

## Workflow B: Use a brand master template

A "master template" is a `.pptx` file with empty slide layouts that python-pptx clones for each generated slide. Standard PowerPoint masters define 11 default layouts (Title Slide, Title and Content, Section Header, Two Content, Comparison, Title Only, Blank, Content with Caption, Picture with Caption, Title and Vertical Text, Vertical Title and Text).

> **For brand-consistent masters across multiple formats**, use the `theme-authoring` skill (`/new-theme <brand.yaml>`) to generate `<short>-master.pptx` from a single `brand.yaml` — it patches the theme XML colors (`accent1`-`accent4`, dark/light text and bg slots), the major/minor fonts, the logo placeholder on every layout, and the footer. The same brand.yaml also produces the matching Marp/Beamer/Slidev artifacts. Use this skill's hand-built `.pptx` master path below when the brand requires PowerPoint-specific affordances (custom layouts, master diagrams) the `theme-authoring` curated baseline doesn't model.

A brand master inherits these but applies:
- Brand colors via the master color scheme
- Brand fonts via the theme XML
- Brand logo as a placeholder on every layout
- Custom layouts named for your deck shapes (`Sprint Review Title`, `Demo Slide`, etc.)

To use your own:

```bash
python3 scripts/generate.py --content deck.yaml --template ./brand-master.pptx --output deck.pptx
```

If no `--template` is passed, `generate.py` uses python-pptx's built-in default (16:9, plain styling). For brand work, build a master in PowerPoint (or by editing the OOXML directly) and pass it explicitly.

### Theme resolution

Brand templates resolve in two locations:

1. **User templates** — `${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/pptx/*.pptx`
2. **Bundled templates** — `assets/themes/*.pptx` (none ship by default; user-supplied)

User templates shadow bundled when basenames match. Pass the resolved path verbatim to `--template`.

**Save a brand master:**

```bash
bash scripts/save-theme.sh pptx <name> ./brand-master.pptx
# add --force to overwrite an existing user template
```

## Workflow C: Embed asciinema GIFs

PowerPoint plays GIFs in slideshow mode (not in the editor). To embed an asciinema demo:

1. Convert the cast to GIF via the `asciinema` skill: `agg demo.cast demo.gif --theme monokai --font-size 18`.
2. In your YAML spec, use an `image` layout slide:
   ```yaml
   - layout: image
     title: "Terminal demo"
     image: ./demo.gif
     caption: "Recorded with asciinema; converted via agg"
   ```
3. Generate. Open in PowerPoint and run the slideshow — the GIF plays.

See `references/images-and-gifs.md` for sizing, aspect ratio, and Keynote compatibility notes.

## Workflow D: Verify the output

```bash
# Structural sanity (zip integrity)
unzip -t deck.pptx

# Count slides
unzip -l deck.pptx | grep -c "slides/slide.*xml"

# Open in PowerPoint / Keynote / LibreOffice
open deck.pptx          # macOS — opens default app
soffice --headless --convert-to pdf deck.pptx   # convert to PDF for review

# Re-roundtrip through python-pptx to check for parse errors
python3 -c "from pptx import Presentation; p = Presentation('deck.pptx'); print(f'{len(p.slides)} slides')"
```

**Geometry-level overflow check.** After generating the deck, convert it to PDF and run the `slide-overflow-check` skill to catch text running off the canvas — the python-pptx generator places text into placeholder boxes whose dimensions come from the master template, so a verbose bullet list can silently overflow even when the YAML validates fine:

```bash
soffice --headless --convert-to pdf deck.pptx     # requires LibreOffice; install: brew install --cask libreoffice
python3 ${CLAUDE_PLUGIN_ROOT}/skills/slide-overflow-check/scripts/check_overflow.py deck.pdf
```

If LibreOffice isn't installed, surface the install command and skip this step (visual review in PowerPoint is the manual fallback). Don't auto-install the cask.

## Common pitfalls

- **Layout name mismatch.** If the YAML references a layout name not in the master template, `generate.py` falls back to `slide_layouts[1]` (Title and Content). Verify the master template's layout names via `python3 -c "from pptx import Presentation; p = Presentation('master.pptx'); [print(l.name) for l in p.slide_layouts]"`.
- **GIF playback in Keynote.** Keynote shows only the first frame of GIFs; full playback works in PowerPoint slideshow mode only. Set audience expectations.
- **GIF playback in PowerPoint normal view.** Static first-frame in the editor. Audience sees animation only during slideshow. The "stuck" appearance during editing is normal — don't re-export.
- **Aspect ratio mismatch.** The master template's slide dimensions win. If you set `aspect_ratio: 16:9` in YAML meta but the master is 4:3, slides are letterboxed.
- **Image sizing inconsistency.** Without explicit `width`/`height` props, `generate.py` uses Pillow to read intrinsic image dimensions and fit to the content area. Pre-resize large images to ~1920×1080 to keep the .pptx small.
- **Speaker notes invisible.** python-pptx writes notes to the notes pane, but PowerPoint sometimes hides the notes-pane by default. View → Notes.
- **`pip install python-pptx` not in your venv.** A common cause of "ModuleNotFoundError: No module named 'pptx'". Use `python3 -m pip install python-pptx pyyaml Pillow` inside your project's venv.

## Quality checklist before delivering

- [ ] `python3 scripts/generate.py --content deck.yaml --validate-only` exits 0 (YAML is schema-valid).
- [ ] Generated `.pptx` opens cleanly in PowerPoint AND Keynote AND LibreOffice (test all three if your audience may use any of them).
- [ ] Slide count matches the talk slot.
- [ ] Speaker notes present on every content slide (visible via View → Notes in PowerPoint).
- [ ] All image paths resolve (no broken-image placeholders).
- [ ] Aspect ratio matches the venue's projector (16:9 standard; 4:3 for older rooms).
- [ ] If using a brand master: logo on every layout, brand colors in titles, brand fonts inherited.
- [ ] For asciinema GIFs: tested in slideshow mode (not just editor) — GIFs animate.
- [ ] **`slide-overflow-check` ran clean against a PDF export of the deck** (LibreOffice headless conversion + `slide-overflow-check`; skip if LibreOffice not installed and rely on manual visual review). See the companion `slide-overflow-check` skill.
