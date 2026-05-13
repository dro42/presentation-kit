#!/usr/bin/env bash
# Wrapper around `asciinema rec` with sane slide-embed defaults.
# Usage: record-demo.sh [--dry-run] [--cols N] [--rows N] [--idle-time-limit SEC] <TITLE> <OUTPUT.cast>
#
# Defaults:
#   --cols 100 --rows 30 --idle-time-limit 2
#
# --dry-run prints the asciinema invocation without recording. Useful for CI/lint
# checks of this skill's prerequisites.
set -euo pipefail

dry_run=0
cols=100
rows=30
idle=2

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1; shift ;;
    --cols)    cols="${2:?--cols requires N}"; shift 2 ;;
    --rows)    rows="${2:?--rows requires N}"; shift 2 ;;
    --idle-time-limit) idle="${2:?--idle-time-limit requires SEC}"; shift 2 ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    --) shift; break ;;
    -*) echo "Unknown flag: $1" >&2; exit 2 ;;
    *)  break ;;
  esac
done

title="${1:?usage: record-demo.sh [flags] <TITLE> <OUTPUT.cast>}"
output="${2:?missing OUTPUT.cast}"

if ! command -v asciinema > /dev/null 2>&1; then
  echo "asciinema not installed." >&2
  echo "  macOS:        brew install asciinema" >&2
  echo "  Cross-platform: pip install asciinema" >&2
  exit 127
fi

cmd=(asciinema rec
     --cols "$cols"
     --rows "$rows"
     --idle-time-limit "$idle"
     --title "$title"
     "$output")

if (( dry_run )); then
  echo "Would run: ${cmd[*]}"
  exit 0
fi

echo "Recording to $output (cols=$cols rows=$rows idle-limit=${idle}s)"
echo "Use a clean prompt: export PS1='$ ' before starting your demo."
echo "Press Ctrl-D or type 'exit' when done."
echo
exec "${cmd[@]}"
