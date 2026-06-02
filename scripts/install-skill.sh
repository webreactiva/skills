#!/usr/bin/env bash
# Place a skill (or all of them) into another project or your global skills dir(s),
# by symlink (default) or by copy. Symlinks keep the destination in sync with the repo;
# copies are self-contained snapshots (use --copy when sharing outside this checkout).
#
# Usage:
#   scripts/install-skill.sh <slug|all> <dest> [<dest> ...] [--copy]
#
# <slug>   a single skill's folder name (e.g. politenizer), or "all"
# <dest>   one or more destinations:
#            claude              ~/.claude/skills              (global, Claude Code)
#            agents              ~/.agents/skills              (global, cross-agent)
#            both                both of the globals above
#            local               ./.claude/skills              (this repo; gitignored)
#            <project-dir>       <dir>/.claude/skills AND <dir>/.agents/skills
#            <path>/.claude      ->  <path>/.claude/skills
#            <path>/.agents      ->  <path>/.agents/skills
#            <path>/skills       used as-is
# --copy    copy the files instead of symlinking (default: symlink)
#
# Examples:
#   scripts/install-skill.sh politenizer both          # symlink into both user globals
#   scripts/install-skill.sh politenizer ~/code/myapp  # into myapp's .claude + .agents
#   scripts/install-skill.sh all ~/code/myapp --copy   # copy every skill into myapp
set -euo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."
repo="$(pwd)"

mode="symlink"
slug=""
dest_tokens=()
for arg in "$@"; do
  case "$arg" in
    --copy)            mode="copy" ;;
    --symlink|--link)  mode="symlink" ;;
    -*) echo "Unknown flag: $arg" >&2; exit 1 ;;
    *)  if [ -z "$slug" ]; then slug="$arg"; else dest_tokens+=("$arg"); fi ;;
  esac
done

if [ -z "$slug" ] || [ "${#dest_tokens[@]}" -eq 0 ]; then
  echo "Usage: scripts/install-skill.sh <slug|all> <dest> [<dest> ...] [--copy]" >&2
  echo "  dest: claude | agents | both | local | <project-dir> | <path/to/skills>" >&2
  exit 1
fi

# Resolve which skill folder(s) to place.
srcs=()
if [ "$slug" = "all" ]; then
  for d in skills/*/*/; do [ -f "${d}SKILL.md" ] && srcs+=("${d%/}"); done
else
  for d in skills/*/"$slug"/; do [ -f "${d}SKILL.md" ] && srcs+=("${d%/}"); done
  if [ "${#srcs[@]}" -eq 0 ]; then
    echo "No skill named '$slug' found under skills/*/. Available:" >&2
    for d in skills/*/*/; do [ -f "${d}SKILL.md" ] && echo "  - $(basename "$d")" >&2; done
    exit 1
  fi
fi

# Resolve a single dest token into one or more absolute skills directories.
resolve_dest() {
  local t="${1%/}"
  case "$t" in
    claude) printf '%s\n' "$HOME/.claude/skills" ;;
    agents) printf '%s\n' "$HOME/.agents/skills" ;;
    both)   printf '%s\n' "$HOME/.claude/skills" "$HOME/.agents/skills" ;;
    local)  printf '%s\n' "$repo/.claude/skills" ;;
    */skills)             printf '%s\n' "$t" ;;
    */.claude|*/.agents)  printf '%s\n' "$t/skills" ;;
    *)                    printf '%s\n' "$t/.claude/skills" "$t/.agents/skills" ;;
  esac
}

# Expand + de-duplicate destination dirs.
dests=()
for t in "${dest_tokens[@]}"; do
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    seen=""
    for e in ${dests[@]+"${dests[@]}"}; do [ "$e" = "$d" ] && seen=1; done
    [ -z "$seen" ] && dests+=("$d")
  done < <(resolve_dest "$t")
done

for dest in "${dests[@]}"; do
  mkdir -p "$dest"
  for src in "${srcs[@]}"; do
    name="$(basename "$src")"
    target="$dest/$name"
    if [ "$mode" = "copy" ]; then
      rm -rf -- "$target"
      cp -R "$repo/$src" "$target"
      echo "copied  $name -> $target"
    else
      ln -sfn "$repo/$src" "$target"
      echo "linked  $name -> $target"
    fi
  done
done
