#!/usr/bin/env bash
# presentation-kit SessionStart hook (v0.2)
# Detects presentation files in the current working directory and surfaces
# nudges toward the matching slash command via additionalContext.
# Always exits 0 — never aborts the session on detection failure.
#
# Marp vs Slidev disambiguation: both formats use slides.md.
#   - `marp: true` present              → Marp
#   - layout/transition/mdc/colorSchema → Slidev
#   - theme: @slidev/* | seriph | apple-basic → Slidev
#   - theme: default alone              → AMBIGUOUS (surface both)
#   - package.json with @slidev/cli     → Slidev project signal

set -uo pipefail
trap 'exit 0' ERR

msgs=()
slides_classified=0

if [[ -f slides.md ]]; then
  head -n 60 slides.md > /tmp/.pk-head.$$ 2>/dev/null || true
  if grep -qE '^marp:[[:space:]]*true' /tmp/.pk-head.$$ 2>/dev/null; then
    msgs+=("Detected Marp slides.md — /marp available")
    slides_classified=1
  elif grep -qE '^(layout|transition|mdc|colorSchema|drawings):' /tmp/.pk-head.$$ 2>/dev/null \
       || grep -qE '^theme:[[:space:]]*(@slidev/|seriph$|apple-basic$)' /tmp/.pk-head.$$ 2>/dev/null; then
    msgs+=("Detected Slidev slides.md — /slidev available")
    slides_classified=1
  else
    msgs+=("Detected slides.md (ambiguous frontmatter) — /marp or /slidev")
  fi
  rm -f /tmp/.pk-head.$$
fi

# Beamer
if compgen -G "*.tex" > /dev/null 2>&1; then
  if grep -l '\\documentclass.*{beamer}' ./*.tex 2>/dev/null | head -1 | grep -q .; then
    msgs+=("Detected a Beamer deck — /beamer available")
  fi
fi

# Slidev project (no slides.md but package.json mentions @slidev/cli)
if [[ -f package.json ]] && grep -q '"@slidev/cli"' package.json 2>/dev/null; then
  (( slides_classified )) || msgs+=("Detected Slidev project — /slidev available")
fi

# pptx (raw .pptx file or a pptx-shaped deck.yaml)
if compgen -G "*.pptx" > /dev/null 2>&1; then
  msgs+=("Detected .pptx file(s) — /pptx available")
elif [[ -f deck.yaml ]] && grep -qE '^(slides|meta|layout):' deck.yaml 2>/dev/null; then
  msgs+=("Detected deck.yaml — /pptx available")
fi

# Asciinema cast files
if compgen -G "*.cast" > /dev/null 2>&1; then
  msgs+=("Detected .cast recording(s) — /asciinema available")
fi

if ((${#msgs[@]})); then
  joined=$(IFS='; '; echo "${msgs[*]}")
  if command -v jq > /dev/null 2>&1; then
    # jq -Rs reads raw stdin and JSON-encodes (handles newlines, quotes, control chars)
    escaped=$(printf '%s' "$joined" | jq -Rs .)
  else
    # Fallback: minimal JSON escape (backslash, quotes). Safe because the
    # message strings constructed above contain neither newlines nor backslashes.
    escaped="\"$(printf '%s' "$joined" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
  fi
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$escaped"
fi

exit 0
