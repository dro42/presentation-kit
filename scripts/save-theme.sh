#!/usr/bin/env bash
# Save a user-authored presentation theme into the XDG user-data directory.
# Usage: save-theme.sh [--force] <format> <name> <source-file>
#   format: marp | beamer
#   name:   destination basename (without extension)
#   source-file: existing file on disk; extension is preserved
set -euo pipefail

force=0
if [[ "${1:-}" == "--force" ]]; then
  force=1
  shift
fi

format="${1:?usage: save-theme.sh [--force] <format> <name> <source-file>}"
name="${2:?missing name}"
src="${3:?missing source file}"

case "$format" in
  marp|beamer) ;;
  *)
    echo "Unknown format '$format' (expected: marp, beamer)" >&2
    exit 2
    ;;
esac

if [[ ! -f "$src" ]]; then
  echo "Source file not found: $src" >&2
  exit 2
fi

dest_dir="${XDG_DATA_HOME:-$HOME/.local/share}/presentation-kit/themes/${format}"
mkdir -p "$dest_dir"

ext="${src##*.}"
dest="${dest_dir}/${name}.${ext}"

if [[ -e "$dest" && $force -eq 0 ]]; then
  echo "Refusing to overwrite existing theme: $dest" >&2
  echo "Re-run with --force to replace." >&2
  exit 1
fi

cp "$src" "$dest"
echo "Saved theme → $dest"
