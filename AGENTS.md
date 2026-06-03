# AGENTS.md

Guidance for agents (and humans) working **in this repository**.
(`CLAUDE.md` is a symlink to this file.)

## What this repo is

A catalog of Agent Skills by Web Reactiva, installable via [skills.sh](https://skills.sh)
(`npx skills add webreactiva/skills`). It is published to `webreactiva.com/skills`.

## Golden rules

- **Everything tracked in the repo is in English.** (Local plans under `docs/plans/*.local.md`
  are gitignored and may be in any language.)
- A skill lives at `skills/<category>/<slug>/SKILL.md`.
- **Category = parent folder. Status = top folder** (`work-in-progress/` → wip; otherwise stable).
  Categories are broad on purpose — don't create a folder per micro-topic.
- **`SKILL.md` frontmatter stays standard:** `name`, `description`, optional `argument-hint` /
  `allowed-tools`, plus the `metadata` block below. Don't add other custom top-level keys — it
  would break the agent-skill protocol and skills.sh.
- **Every skill declares its origin** in the frontmatter via the protocol-safe `metadata` block —
  required on every skill:
  ```yaml
  metadata:
    author: webreactiva.com
    namespace: webreactiva
  ```
  This is the only extra frontmatter we add; web-facing catalog data (summary, tags, …) still
  lives in `skills-catalog.json`.
- **Extra metadata lives only in `skills-catalog.json`**, keyed by `slug`: hand-edit
  `summary`, `tags`, `lang`, `featured` (and an optional `status`/`title` override). Everything
  else in that file is derived — do not hand-edit it. The one exception is `webUrl`, which is
  **synced** from the website (see below), not hand-edited and not derived from the tree.
- **`skills-catalog.json` and the README skills tables are generated.** The English `README.md`
  (grouped by category) and the briefer Spanish `README.es.md` (flat table) both hold their tables
  between `<!-- skills:start -->`/`<!-- skills:end -->` markers — edit the prose around them, never
  the table. After adding, moving, or renaming a skill, run `npm run build:catalog`. CI runs
  `npm run check` and fails on drift in either README.
- **Every `SKILL.md` frontmatter is YAML-linted.** `npm run validate` (run on its own, and first
  inside `npm run check`) checks each skill's frontmatter with a tiny zero-dependency linter: it
  flags an unquoted value containing `:` (the classic "mapping values are not allowed" break that
  the lenient catalog parser would silently accept), unterminated quotes, and a missing `name`,
  `description`, or `metadata` (author/namespace) block. Quote a tricky `description` (`"…"`) or use
  a `>-` block — see `github-profile-readme` for the block style.
- **Web page links are synced from the live site, not invented.** `npm run sync:web` is the only
  script that hits the network: it reads `https://www.webreactiva.com/skills/rss.xml`, matches
  each `<item>` to a skill by slug (`<guid>`), and writes the page URL as `webUrl` into
  `skills-catalog.json`. That URL then drives the README "Page" column. `build:catalog`/`check`
  stay offline (they only preserve the already-synced `webUrl`), so CI never depends on the site.
  Re-run `sync:web` whenever skills are published or change on the website.

## Common operations

**Add a skill**
1. Create `skills/<category>/<slug>/SKILL.md` with standard frontmatter (`name` + `description` required).
2. Add an entry to `skills-catalog.json` with at least `summary` and `tags`.
3. `npm run build:catalog`.

**Move a skill to another category**
```bash
git mv skills/<from>/<slug> skills/<to>/<slug>
npm run build:catalog
```
The catalog entry is keyed by `slug`, so nothing is re-typed — only the derived
`category`/`path`/`repoUrl` change, and the install command stays the same.

**Mark a skill as work-in-progress**
```bash
git mv skills/<category>/<slug> skills/work-in-progress/<slug>
npm run build:catalog
```

**Refresh the web page links** (after publishing/changing skills on webreactiva.com)
```bash
npm run sync:web   # reads the site's RSS feed and updates webUrl + the README "Page" column
```

**Test locally without installing from GitHub**
```bash
scripts/link-skills.sh local  # symlinks ALL skills into ./.claude/skills (this repo; gitignored)
scripts/link-skills.sh both   # or into ~/.claude/skills and ~/.agents/skills (global)
```
`.claude/` is gitignored, so the local links are a dev convenience — re-run after adding a skill.

**Install one skill (or all) into another project or your global dirs**
```bash
scripts/install-skill.sh <slug|all> <dest> [<dest> ...] [--copy]
#   dest: claude | agents | both | local | <project-dir> | <path/to/skills>
scripts/install-skill.sh politenizer both          # symlink into both user globals
scripts/install-skill.sh politenizer ~/code/myapp  # into myapp's .claude + .agents
scripts/install-skill.sh all ~/code/myapp --copy   # copy every skill into myapp (self-contained)
```
The granular companion to `link-skills.sh`: pick a single skill, choose a target project or the
global dirs, and either symlink (stays in sync with the repo) or `--copy` (a standalone snapshot).
A bare project dir gets both `.claude/skills` and `.agents/skills`; a path ending in `/skills`,
`/.claude`, or `/.agents` is honored as given.
