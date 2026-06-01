#!/usr/bin/env bash
# Symlink every skill into your local agent skills dir(s) so you can test
# without installing from GitHub.
#
# Usage:
#   scripts/link-skills.sh [claude|agents|both|local]   # default: claude
#
#   claude -> ~/.claude/skills        (Claude Code, global)
#   agents -> ~/.agents/skills        (cross-agent convention, global)
#   both   -> link into both globals
#   local  -> ./.claude/skills        (this repo only; gitignored)
set -euo pipefail
cd "$(dirname "$0")/.."

target="${1:-claude}"
case "$target" in
  claude) dests=("$HOME/.claude/skills") ;;
  agents) dests=("$HOME/.agents/skills") ;;
  both)   dests=("$HOME/.claude/skills" "$HOME/.agents/skills") ;;
  local)  dests=("$(pwd)/.claude/skills") ;;
  *) echo "Unknown target: $target (use: claude | agents | both | local)" >&2; exit 1 ;;
esac

shopt -s nullglob
for dest in "${dests[@]}"; do
  mkdir -p "$dest"
  for skill in skills/*/*/; do
    [ -f "${skill}SKILL.md" ] || continue
    name="$(basename "$skill")"
    ln -sfn "$(pwd)/${skill%/}" "$dest/$name"
    echo "linked $name -> $dest/$name"
  done
done
