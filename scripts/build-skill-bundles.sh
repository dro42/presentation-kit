#!/usr/bin/env bash
# Build self-contained .skill bundles for distribution outside Claude Code
# (Codex CLI, Gemini CLI, .agents/skills/). Each .skill is a zip of the
# skill directory with scripts/save-theme.sh copied in so the bundle is
# self-contained.
#
# Output: dist/<skill>.skill + dist/manifest.json (gitignored).
# Staging:  dist/staging/<skill>/ (gitignored; rebuilt each run).
#
# Drift guard: this script NEVER writes save-theme.sh back into the
# skills/ source tree. The synced copy lives only in dist/staging/<name>/
# and the resulting .skill zip — verifiable via `git status` post-build.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="${ROOT}/dist"
STAGING="${DIST}/staging"
CANONICAL_SAVE="${ROOT}/scripts/save-theme.sh"
SKILLS=(marp beamer asciinema slidev pptx)

if [[ ! -f "$CANONICAL_SAVE" ]]; then
  echo "Canonical save-theme.sh not found at $CANONICAL_SAVE" >&2
  exit 1
fi

mkdir -p "$DIST"
rm -rf "$STAGING"
mkdir -p "$STAGING"
rm -f "$DIST"/*.skill "$DIST"/manifest.json

manifest_entries=()
overall_ok=1

for s in "${SKILLS[@]}"; do
  src="${ROOT}/skills/${s}"
  [[ -d "$src" ]] || { echo "missing skill dir: $src" >&2; overall_ok=0; continue; }
  [[ -f "$src/SKILL.md" ]] || { echo "missing SKILL.md in $s" >&2; overall_ok=0; continue; }

  # Validate YAML frontmatter (must open with --- and contain name: + description:)
  awk '
    NR==1 && $0!="---" { print "SKILL.md must start with --- frontmatter fence" > "/dev/stderr"; exit 1 }
    /^---/ { c++ }
    c==1 && /^name:/ { n=1 }
    c==1 && /^description:/ { d=1 }
    END { exit !(n && d) }
  ' "$src/SKILL.md" \
    || { echo "frontmatter invalid in $s/SKILL.md (need both name: and description:)" >&2; overall_ok=0; continue; }

  # Stage the skill into dist/staging/<name>/
  stage="${STAGING}/${s}"
  cp -R "$src" "$stage"

  # Drop a copy of save-theme.sh into the staged skill, with a clear header
  mkdir -p "$stage/scripts"
  {
    echo "#!/usr/bin/env bash"
    echo "# --------------------------------------------------------------------"
    echo "# Synced from presentation-kit/scripts/save-theme.sh by"
    echo "# scripts/build-skill-bundles.sh — DO NOT EDIT IN A SKILL ZIP."
    echo "# Authoritative copy: https://github.com/dro42/presentation-kit"
    echo "# --------------------------------------------------------------------"
    tail -n +2 "$CANONICAL_SAVE"   # drop the canonical's shebang; we added our own + header
  } > "$stage/scripts/save-theme.sh"
  chmod +x "$stage/scripts/save-theme.sh"

  # Strip OS noise before zipping
  find "$stage" -name '.DS_Store' -delete
  find "$stage" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

  # Zip: archive root inside the .skill is the skill name (e.g. marp/SKILL.md)
  out="${DIST}/${s}.skill"
  ( cd "$STAGING" && zip -qr "$out" "$s" )

  size=$(stat -f%z "$out" 2>/dev/null || stat -c%s "$out")
  sha=$(shasum -a 256 "$out" | awk '{print $1}')
  manifest_entries+=("{\"name\":\"$s\",\"file\":\"${s}.skill\",\"size\":$size,\"sha256\":\"$sha\"}")
  echo "built $out ($size bytes)"
done

# Compose manifest.json
{
  printf '{\n  "version": "0.2.0",\n  "built_at": "%s",\n  "skills": [\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  first=1
  for entry in "${manifest_entries[@]}"; do
    if (( first )); then
      printf '    %s' "$entry"
      first=0
    else
      printf ',\n    %s' "$entry"
    fi
  done
  printf '\n  ]\n}\n'
} | (command -v jq > /dev/null && jq . || cat) > "$DIST/manifest.json"

echo "manifest -> $DIST/manifest.json"

# Drift guard: confirm we didn't accidentally write save-theme.sh into skills/
if find "$ROOT/skills" -path '*/scripts/save-theme.sh' | grep -q .; then
  echo "ERROR: skills/*/scripts/save-theme.sh exists in source tree — drift detected!" >&2
  find "$ROOT/skills" -path '*/scripts/save-theme.sh' >&2
  exit 1
fi

(( overall_ok )) || { echo "Some skills failed to bundle." >&2; exit 1; }
echo "OK: 5/5 bundles built; source tree clean."
