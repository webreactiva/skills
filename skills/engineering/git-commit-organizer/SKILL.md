---
name: git-commit-organizer
description: Organize pending git changes into logical, well-structured commits that follow the Conventional Commits specification, in English. Use this skill whenever the user wants to commit work, "organize my commits", "split my changes into logical commits", "commit what we have", "save these changes to git", "tidy up my history before a PR", or invokes /commit — including partial asks like "commit the auth stuff" or "just commit the config". It reads git status and diffs, groups related changes into atomic commits, proposes the messages, and only commits after explicit approval. Optionally it adds gitmoji prefixes, an issue reference (auto-detected from the branch when present), and folder exclusions. It never pushes. Do not trigger for writing code, resolving merge conflicts, or opening pull/merge requests — only for turning pending changes into commits.
argument-hint: "[#issue] [gitmoji] [exclude <folders>]"
metadata:
  author: webreactiva.com
  namespace: webreactiva
---

# Git Commit Organizer

Turn a messy working tree into a clean, readable history. A good commit history is a tool for everyone who comes after you: atomic commits that each make sense on their own are easy to review, revert, and cherry-pick. This skill does exactly that — and it never commits or pushes behind your back. You always approve first.

## What you can pass (all optional)

Recognize these from natural language, in any language; act on the intent, not the exact word.

| Option | Default | How a user might say it |
| --- | --- | --- |
| `gitmoji` | off | "with gitmoji", "add emojis" |
| `issue` | auto-detect from branch | "#412", "for issue 412", "no issue" |
| `exclude` | nothing | "leave out the docs folder", "skip vendor/" |

## Workflow

### 1. See what actually changed

```bash
git status
git diff --stat
git diff --cached --stat
```

Then read the real diffs for the files that matter (`git diff <file>` and `git diff --cached <file>`). Filenames alone don't tell you whether a change is a feature, a fix, or a refactor — the diff does. You're grouping by *intent*, so you need to understand the intent.

### 2. Detect an issue reference (optional)

Run `git branch --show-current` at the start — never assume the branch from earlier in the conversation, since the user may have switched. If the branch clearly embeds an identifier (common shapes: `feature/412`, `412-add-search`, `fix/PROJ-42`), offer to include it as `#412` / `PROJ-42`. Only attach an issue when the user asked for one or the branch obviously carries one. Never invent an issue number; if the user mentions one you can't find, ask.

### 3. Apply exclusions

By default, commit everything git already considers (tracked changes and new files); `.gitignore` is the source of truth for what to ignore. Only skip a path when the user asks — then leave those files unstaged rather than deleting or touching them.

### 4. Group changes into atomic commits

One logical change per commit. The aim is a history where each commit stands on its own and doesn't break the build. Useful groupings:

- A change and the tests that cover it belong together.
- An unrelated bug fix and a new feature belong in separate commits.
- Config, build, and dependency changes group naturally.
- Pure formatting (whitespace, import order) stays out of behavior-changing commits.
- Large renames or moves are usually their own commit, separate from edits.

If everything is genuinely one cohesive change, a single commit is the right answer — don't over-split for its own sake. When you plan more than one commit, or the grouping is at all ambiguous, show your proposed grouping and confirm before doing anything.

### 5. Pick the type and scope

| Type | When |
| --- | --- |
| `feat` | A new capability |
| `fix` | A bug fix |
| `refactor` | Restructuring with no behavior change |
| `perf` | A performance improvement |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `style` | Formatting only, no logic change |
| `build` | Build system or dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance that doesn't fit elsewhere |
| `revert` | Reverting a previous commit |

Scope is optional: the area touched (a feature, module, or directory), short and lowercase.

### 6. Write the message

Format: `type(scope): [#issue] short description`

- **Header** — imperative mood ("add", not "added"), capitalized first word, no trailing period, kept under ~72 characters when you can.
- **Body** (optional, but include it when the *why* isn't obvious from the diff) — a blank line, then `- ` bullet sentences describing what changed and why. Skip noise like "updated imports".
- **gitmoji** (only when enabled) — prefix the header using this map: `feat` ✨ · `fix` 🐛 · `refactor` ♻️ · `perf` ⚡ · `test` ✅ · `docs` 📝 · `style` 🎨 · `build` 📦 · `ci` 👷 · `chore` 🔧 · `revert` ⏪

### 7. Propose, then wait for approval

**Always show the plan before committing — and wait for an explicit yes.** For each planned commit, present the message and the exact files it will stage. Surprise commits are annoying to unwind and erode trust, so this gate is the one rule that never bends.

### 8. Stage and commit

Stage only the files for that group, then commit. For multi-line messages, use a heredoc so the body's formatting survives intact:

```bash
git add <specific files for this commit>
git commit -m "$(cat <<'EOF'
type(scope): #412 Short description

- What changed and why.
- Another meaningful detail.
EOF
)"
```

Show `git log -1` after each commit so the user can see the result.

### 9. Confirm the result

After all commits, run `git log --oneline -n <number of commits>` so the new history is visible at a glance.

## Hard rules

- **Never push.** Pushing is the user's decision, always. Don't run `git push` under any circumstances.
- **Never commit without explicit approval** (see step 7).
- **No AI or tool attribution.** Commits represent the project's human authors. Never add a `Co-authored-by`, `Signed-off-by`, or any trailer, footer, or text referencing an AI tool.
- English, imperative, atomic.

## Examples

Scopes here (`search`, `parser`, `http`, `readme`) are generic on purpose — use whatever the repository actually calls its areas.

**Example 1 — a single feature (a web app), no options**

Changes: a search component plus its test.

```
feat(search): add fuzzy matching to the product search box

- Match results by approximate spelling so small typos still return hits.
- Cover the ranking edge cases with unit tests.
```

**Example 2 — splitting unrelated work into two commits (a CLI tool)**

Working tree has a bug fix and a dependency bump.

```
fix(parser): stop crashing on an empty config file

- Treat a missing or empty config as the defaults instead of throwing.
```

```
chore(deps): upgrade the HTTP client to 4.2.0
```

**Example 3 — gitmoji + issue auto-detected from branch `412-retry-logic` (a library)**

```
♻️ refactor(http): #412 extract retry handling into its own module

- Move the backoff logic out of the client so it can be unit-tested in isolation.
```

**Example 4 — documentation only**

```
docs(readme): document the new --watch flag
```

## When not to use this

- Writing or changing code (that's the work; this skill commits it afterwards).
- Resolving merge conflicts.
- Creating or describing pull/merge requests.
- Any remote operation — pushing, in particular, is never this skill's job.
