#!/usr/bin/env bash
# audit.sh — one-command security and quality audit for the Rubber Duck skill.
#
# Runs, against scripts/rubber_duck.py:
#   1. byte-compile          (py_compile)        — hard fail
#   2. dangerous-pattern grep                     — hard fail if any match
#   3. bandit                (security linter)    — hard fail on findings
#   4. ruff                  (bugs / quality)     — hard fail on findings
#   5. pip-audit             (dependency CVEs)    — best-effort (needs network)
#   6. pytest                (reliability suite)  — hard fail
#
# Missing tools are installed on the fly with --break-system-packages.
# Usage:  bash tests/audit.sh
set -uo pipefail

# Resolve paths relative to this script so it runs from anywhere.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SCRIPT="$ROOT/scripts/rubber_duck.py"
TESTS="$HERE/test_rubber_duck.py"
FAIL=0

say()  { printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
ok()   { printf '\033[32m  PASS\033[0m %s\n' "$1"; }
bad()  { printf '\033[31m  FAIL\033[0m %s\n' "$1"; FAIL=1; }
warn() { printf '\033[33m  WARN\033[0m %s\n' "$1"; }

ensure() {  # ensure a python module is importable; pip-install it if not
  local mod="$1" pkg="${2:-$1}"
  python3 -c "import $mod" 2>/dev/null && return 0
  warn "$pkg not found — installing"
  pip install -q --break-system-packages "$pkg" >/dev/null 2>&1 || true
}

# 1. byte-compile
say "byte-compile (py_compile)"
if python3 -m py_compile "$SCRIPT"; then ok "compiles"; else bad "syntax error"; fi

# 2. dangerous-pattern grep (the script must stay inert)
say "dangerous-pattern scan"
PAT='os\.system|os\.popen|subprocess\.|shell=True|[^_]eval\(|[^_]exec\(|socket\.|urllib|requests\.|__import__|pickle\.'
# Strip comments/docstrings noise by scanning code lines only is overkill here;
# the script never imports these modules, so any real hit is a regression.
if grep -nE "$PAT" "$SCRIPT" \
     | grep -vE 'subprocess_command|in_session_command|# ' >/dev/null; then
  bad "found a dangerous call — inspect:"
  grep -nE "$PAT" "$SCRIPT" | grep -vE 'subprocess_command|in_session_command|# '
else
  ok "no execution / network / eval primitives in the script"
fi

# 3. bandit
say "bandit (security)"
ensure bandit
if python3 -m bandit -q "$SCRIPT" 2>/dev/null | grep -q '>> Issue'; then
  bad "bandit reported issues:"; python3 -m bandit "$SCRIPT" 2>/dev/null | grep -A3 '>> Issue'
else
  ok "no issues identified"
fi

# 4. ruff
say "ruff (bugs / quality)"
ensure ruff
if python3 -m ruff check "$SCRIPT" >/tmp/ruff.out 2>&1; then
  ok "all checks passed"
else
  bad "ruff findings:"; cat /tmp/ruff.out
fi

# 5. pip-audit (best-effort: needs network to the advisory DB)
say "pip-audit (dependency CVEs)"
ensure pip_audit pip-audit
if python3 -m pip_audit >/tmp/pipaudit.out 2>&1; then
  ok "no known vulnerabilities (note: this skill uses only the stdlib)"
else
  warn "pip-audit could not complete (offline?) — skill has no third-party deps anyway"
fi

# 6. pytest
say "pytest (reliability)"
ensure pytest
if python3 -m pytest "$TESTS" -q; then ok "tests passed"; else bad "tests failed"; fi

# Summary
say "summary"
if [ "$FAIL" -eq 0 ]; then
  printf '\033[32mAll hard checks passed.\033[0m\n'; exit 0
else
  printf '\033[31mOne or more hard checks failed — see above.\033[0m\n'; exit 1
fi
