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
  else in that file is derived — do not hand-edit it.
- **`skills-catalog.json` and the README skills table are generated.** After adding, moving, or
  renaming a skill, run `npm run build:catalog`. CI runs `npm run check` and fails on drift.

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

**Test locally without installing from GitHub**
```bash
scripts/link-skills.sh local  # symlinks into ./.claude/skills (this repo only; gitignored)
scripts/link-skills.sh both   # or into ~/.claude/skills and ~/.agents/skills (global)
```
`.claude/` is gitignored, so the local links are a dev convenience — re-run after adding a skill.
