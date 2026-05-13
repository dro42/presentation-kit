# Conversion Reference: cast → GIF/SVG/MP4

`.cast` is a JSON event stream. To embed in formats that can't host a JavaScript player (Beamer PDF, pptx, README images), convert to an image format first.

## GIF via `agg`

`agg` (asciinema gif generator) is the official tool. Written in Rust, no runtime dependencies once installed.

**Install:**
- macOS: `brew install agg`
- Linux: `cargo install --git https://github.com/asciinema/agg`
- Verify: `agg --version`

**Basic usage:**

```bash
agg demo.cast demo.gif
```

**Recommended flags for slide embeds:**

```bash
agg demo.cast demo.gif \
    --theme monokai \
    --font-size 18 \
    --cols 100 --rows 30 \
    --speed 1.0
```

| Flag | Effect |
|---|---|
| `--theme <name>` | Built-in: `asciinema`, `dracula`, `github-dark`, `github-light`, `monokai`, `nord`, `solarized-dark`, `solarized-light`, `tango` |
| `--theme <path.json>` | Use a custom theme JSON (see `assets/themes/` for the schema) |
| `--font-size <N>` | Pixel size of each character cell (default 14; 18 is comfortable for slides) |
| `--cols <N>` / `--rows <N>` | Override the cast's recorded dimensions (downscale only) |
| `--speed <N>` | Playback speed multiplier (1.0 = real time; 2.0 = double speed) |
| `--last-frame-duration <SEC>` | Hold the final frame for `SEC` seconds (default 3) |
| `--idle-time-limit <SEC>` | Clamp idle pauses (default uses what's in the cast) |
| `--font-family <NAME>` | Override font (default: Liberation Mono) |
| `--font-dir <PATH>` | Add a custom font search path |

**Size budget:**

GIFs scale linearly with `cols × rows × font-size² × frame count`. A 90-second cast at `font-size=18, cols=100, rows=30` produces ~3-5 MB. Keep under 5 MB for Beamer (PDF inflates linearly). If too big:

- Drop `--font-size` from 18 to 14 (smaller cells)
- Drop `--cols/--rows` to 80×24
- Speed up: `--speed 1.5` (audience can still follow tutorials; demos lose impact)
- Use the SVG fallback (next section)

## SVG via `svg-term-cli`

Smaller files than GIF, crisper in print, but **static** by default (snapshot of one frame). Animated SVG is possible with extra tooling but rarely worth the complexity — for animation, use GIF.

**Install:** `npm install -g svg-term-cli`. Verify: `svg-term --version`.

```bash
svg-term --in demo.cast --out demo.svg \
         --window \
         --term iterm2 --profile Dracula
```

| Flag | Effect |
|---|---|
| `--in <PATH>` | Cast file path |
| `--out <PATH>` | Output SVG path |
| `--window` | Add a window-chrome frame (traffic-light buttons, title bar) |
| `--from <SEC>` | Start time within the cast |
| `--to <SEC>` | End time within the cast |
| `--term <NAME>` | Terminal style: `iterm2` | `terminal` | etc. (chrome variants) |
| `--profile <NAME>` | Color profile (matches well-known terminal themes) |

SVG embeds cleanly in Beamer (`\includegraphics{demo.svg}` requires `dvisvgm` or the SVG-as-PDF conversion via `rsvg-convert`).

## MP4 via `agg` → `ffmpeg`

For venues that require video files (some conference platforms, Keynote embeds):

```bash
# 1. Render GIF with agg (high frame rate for smooth video)
agg demo.cast demo.gif --theme monokai --font-size 18 --speed 1.0

# 2. Convert GIF to MP4 with ffmpeg
ffmpeg -i demo.gif \
       -movflags faststart -pix_fmt yuv420p \
       -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
       demo.mp4
```

The `scale=trunc(iw/2)*2:trunc(ih/2)*2` filter ensures even pixel dimensions (required by `yuv420p`). `faststart` lets the video stream-start without downloading the full file first.

**Note:** v0.2 doesn't bundle MP4 conversion as a first-class workflow. Document this path for users who ask; v0.3 will add a `record-demo.sh` `--format mp4` mode.

## Choosing between formats

| Constraint | Choice |
|---|---|
| Web (Marp HTML, Slidev, reveal.js, README) | Live cast — `asciinema-player` |
| PDF, print, Keynote | Static GIF (or SVG if size matters) |
| pptx | Animated GIF — plays in slideshow mode |
| Conference video uploads | MP4 |
| Print-only handout | First-frame PNG (`agg demo.cast demo.gif && convert demo.gif[0] demo.png`) |

## Reproducibility

When converting in CI:

- Pin `agg` version (`cargo install --version 1.4.3 ...`) — themes and defaults shift across releases.
- Pin `svg-term-cli` (`npm install -g svg-term-cli@2.1.1`) — same reason.
- Pin `ffmpeg` (`brew install ffmpeg@7` or a specific Docker image).
- Commit a `Makefile` with the exact commands so the artifacts rebuild deterministically.
