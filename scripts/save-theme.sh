#!/usr/bin/env bash
# Save a user-authored presentation theme into the XDG user-data directory.
# Usage: save-theme.sh [--force] <format> <name> <source>
#   format: marp | beamer | slidev | pptx | asciinema
#   name:   destination basename (without extension, or for slidev: directory name)
#   source: existing file on disk (or directory for slidev local themes); extension is preserved
#
# Destination: ${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/<format>/
#
# slidev themes are local-directory themes (a directory with package.json,
# styles/, layouts/, etc.). When format=slidev and source is a directory,
# the entire directory is copied recursively to themes/slidev/<name>/.
set -euo pipefail

force=0
if [[ "${1:-}" == "--force" ]]; then
  force=1
  shift
fi

format="${1:?usage: save-theme.sh [--force] <format> <name> <source>}"
name="${2:?missing name}"
src="${3:?missing source}"

case "$format" in
  marp|beamer|slidev|pptx|asciinema) ;;
  *)
    echo "Unknown format '$format' (expected: marp, beamer, slidev, pptx, asciinema)" >&2
    exit 2
    ;;
esac

dest_dir="${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/${format}"
mkdir -p "$dest_dir"

if [[ -d "$src" ]]; then
  # Directory source — only valid for slidev local-directory themes
  if [[ "$format" != "slidev" ]]; then
    echo "Directory sources are only supported for format=slidev (got: $format)" >&2
    exit 2
  fi
  dest="${dest_dir}/${name}"
  if [[ -e "$dest" && $force -eq 0 ]]; then
    echo "Refusing to overwrite existing theme directory: $dest" >&2
    echo "Re-run with --force to replace." >&2
    exit 1
  fi
  rm -rf "$dest"
  cp -R "$src" "$dest"
  echo "Saved theme directory → $dest"
elif [[ -f "$src" ]]; then
  # File source
  ext="${src##*.}"
  dest="${dest_dir}/${name}.${ext}"
  if [[ -e "$dest" && $force -eq 0 ]]; then
    echo "Refusing to overwrite existing theme: $dest" >&2
    echo "Re-run with --force to replace." >&2
    exit 1
  fi
  cp "$src" "$dest"
  echo "Saved theme → $dest"
else
  echo "Source not found (file or directory): $src" >&2
  exit 2
fi
