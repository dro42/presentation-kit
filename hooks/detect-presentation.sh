#!/usr/bin/env bash
# presentation-kit SessionStart hook
# Detects presentation files in the current working directory and surfaces a
# nudge toward the matching slash command via additionalContext.
# Always exits 0 — never aborts the session on detection failure.
set -uo pipefail
trap 'exit 0' ERR

msgs=()

if [[ -f slides.md ]]; then
  msgs+=("Detected slides.md — /marp available")
fi

# Look for any .tex file declaring \documentclass{beamer}
if compgen -G "*.tex" > /dev/null 2>&1; then
  if grep -l '\\documentclass.*{beamer}' ./*.tex 2>/dev/null | head -1 | grep -q .; then
    msgs+=("Detected a Beamer deck — /beamer available")
  fi
fi

if ((${#msgs[@]})); then
  joined=$(IFS='; '; echo "${msgs[*]}")
  if command -v jq > /dev/null 2>&1; then
    # jq -Rs reads raw stdin and JSON-encodes (handles newlines, quotes, control chars)
    escaped=$(printf '%s' "$joined" | jq -Rs .)
  else
    # Fallback: minimal JSON escape (backslash, quotes). Acceptable because
    # the message strings we build above contain neither newlines nor backslashes.
    escaped="\"$(printf '%s' "$joined" | sed 's/\\/\\\\/g; s/"/\\"/g')\""
  fi
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}\n' "$escaped"
fi

exit 0
