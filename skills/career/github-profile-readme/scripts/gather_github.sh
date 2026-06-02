#!/usr/bin/env bash
# gather_github.sh <owner>
#
# Collects PUBLIC profile data for a GitHub user or organization so an agent can
# seed a profile README. Everything printed here is raw material — verify every
# link before putting it in the README.
#
# Requires: gh (authenticated), jq.

set -uo pipefail

OWNER="${1:-}"
if [[ -z "$OWNER" ]]; then
  echo "usage: gather_github.sh <github-username-or-org>" >&2
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install from https://cli.github.com/ then run 'gh auth login'." >&2
  exit 3
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not found. Install jq (e.g. 'brew install jq')." >&2
  exit 3
fi

section() { printf '\n## %s\n' "$1"; }

# --- Account type & core profile -------------------------------------------
PROFILE="$(gh api "users/${OWNER}" 2>/dev/null || true)"
if [[ -z "$PROFILE" ]]; then
  echo "ERROR: could not fetch users/${OWNER}. Check the name exists and that 'gh auth status' is OK." >&2
  exit 4
fi

TYPE="$(jq -r '.type // "User"' <<<"$PROFILE")"

echo "# GitHub profile data for ${OWNER}"
echo "_Account type: ${TYPE}_"

section "Profile"
jq -r '
  "Name: \(.name // "—")",
  "Bio: \(.bio // "—")",
  "Company: \(.company // "—")",
  "Location: \(.location // "—")",
  "Website/blog: \(.blog // "—")",
  "X/Twitter: \(if .twitter_username then "@\(.twitter_username)" else "—" end)",
  "Public repos: \(.public_repos // 0)",
  "Followers: \(.followers // 0)",
  "Profile URL: \(.html_url)"
' <<<"$PROFILE"

# --- Verified social accounts the owner set on their profile ----------------
section "Verified social accounts"
gh api "users/${OWNER}/social_accounts" 2>/dev/null \
  | jq -r 'if length>0 then (.[] | "- \(.provider): \(.url)") else "—" end' 2>/dev/null \
  || echo "—"

# --- Profile README repo existence ------------------------------------------
section "Profile README repo"
if [[ "$TYPE" == "Organization" ]]; then
  README_REPO="${OWNER}/.github"
  README_PATH="profile/README.md"
else
  README_REPO="${OWNER}/${OWNER}"
  README_PATH="README.md"
fi
echo "Expected repo: ${README_REPO} (file: ${README_PATH})"
if gh api "repos/${README_REPO}" >/dev/null 2>&1; then
  echo "Status: EXISTS"
  echo
  echo "Current ${README_PATH} content:"
  echo '----- BEGIN CURRENT README -----'
  gh api "repos/${README_REPO}/contents/${README_PATH}" \
    -H "Accept: application/vnd.github.raw" 2>/dev/null \
    || echo "(repo exists but ${README_PATH} not found yet)"
  echo '----- END CURRENT README -----'
else
  echo "Status: DOES NOT EXIST — see SKILL.md 'Create the profile repo' for instructions."
fi

# --- Top repositories (own, non-fork, by stars) -----------------------------
section "Top repositories (own, non-fork, by stars)"
gh repo list "$OWNER" --no-archived --source --limit 100 \
  --json name,description,primaryLanguage,stargazerCount,url,repositoryTopics 2>/dev/null \
  | jq -r 'sort_by(-.stargazerCount) | .[:12][] |
      "- \(.name) [\(.primaryLanguage.name // "—"), ★\(.stargazerCount)] — \(.description // "no description")"' \
  2>/dev/null || echo "—"

# --- Language distribution across those repos -------------------------------
section "Languages (by primary-language repo count)"
gh repo list "$OWNER" --no-archived --source --limit 100 \
  --json primaryLanguage 2>/dev/null \
  | jq -r '[.[].primaryLanguage.name // empty] | group_by(.)
      | map({lang: .[0], n: length}) | sort_by(-.n) | .[]
      | "- \(.lang): \(.n)"' 2>/dev/null || echo "—"

# --- Pinned repositories (GraphQL; users only) ------------------------------
section "Pinned repositories"
gh api graphql -f query='
  query($login:String!){
    user(login:$login){
      pinnedItems(first:6, types:[REPOSITORY]){
        nodes{ ... on Repository { name description primaryLanguage{name} stargazerCount url } }
      }
    }
  }' -F login="$OWNER" 2>/dev/null \
  | jq -r '.data.user.pinnedItems.nodes[]?
      | "- \(.name) [\(.primaryLanguage.name // "—"), ★\(.stargazerCount)] — \(.description // "no description")"' \
  2>/dev/null || echo "— (none, or this is an organization)"

echo
echo "_Done. This is raw material. Verify every link/handle before using it; do not invent any._"
