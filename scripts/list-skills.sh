#!/usr/bin/env bash
# List every skill grouped by its category folder.
set -euo pipefail
cd "$(dirname "$0")/.."

for category in skills/*/; do
  [ -d "$category" ] || continue
  echo "▸ $(basename "$category")"
  shopt -s nullglob
  for skill in "$category"*/; do
    [ -f "${skill}SKILL.md" ] || continue
    echo "    - $(basename "$skill")"
  done
  shopt -u nullglob
done
