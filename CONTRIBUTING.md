# Contributing

Thanks for wanting to add a skill. Keep it focused, keep it honest, keep it in English.

## Add a skill

1. **Create the folder** at `skills/<category>/<slug>/` and write `SKILL.md`.
   - `<slug>` is lowercase-kebab-case and unique across the whole repo (it's what
     `--skill <slug>` and the catalog key use).
   - Frontmatter is **standard agent-skill only**:
     ```yaml
     ---
     name: my-skill
     description: >-
       What it does and, crucially, *when* an agent should trigger it. Pack the
       trigger phrases here — this is how the skill gets discovered.
     argument-hint: "<optional> [flags]"   # optional
     ---
     ```
   - Do **not** add custom frontmatter keys.

2. **Register it** in [`skills-catalog.json`](skills-catalog.json) — add an object to
   `skills` with the hand-authored fields:
   ```json
   {
     "slug": "my-skill",
     "summary": "One short, web-facing sentence.",
     "tags": ["topic", "agent"],
     "lang": ["en"],
     "featured": false
   }
   ```
   Everything else (`name`, `description`, `category`, `status`, `path`, `repoUrl`, `install`,
   `canonicalUrl`) is filled in for you.

3. **Generate** and verify:
   ```bash
   npm run build:catalog   # fills derived fields + README table
   npm run check           # must pass (CI runs this too)
   ```

## Categories

Categories are the folders under `skills/`. They are intentionally **broad** — a little
ambiguity is fine. Reuse an existing one when you can; only add a new category (an object in
`categories` in `skills-catalog.json`, plus the folder) when several skills will share it.

## Build in public

Not finished? Put it in `skills/work-in-progress/<slug>/` and add a short `ROADMAP.md` saying
what's left. When it's ready, `git mv` it into a real category and re-run `npm run build:catalog`.

## Style

- English, conversational, no hype.
- The skill's `description` is its discovery surface: describe the job **and the triggers**.
- One skill = one job.
