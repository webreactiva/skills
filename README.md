<div align="center">

# Web Reactiva Skills

**Agent Skills for real developers — practical, human, no hype.**
Built in public by the [Web Reactiva](https://webreactiva.com) community.

[![Browse the catalog](https://img.shields.io/badge/browse-webreactiva.com%2Fskills-2ea44f)](https://webreactiva.com/skills)

**English** · [Español](README.es.md)

</div>

A growing, curated collection of [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
you can drop into Claude Code, OpenCode, Codex, Cursor and many other agents with a single
command. Each skill is one focused, reusable capability — the kind of thing you teach an
agent once and never explain again.

Browse the full, filterable catalog at **[webreactiva.com/skills](https://webreactiva.com/skills)**.

> [!TIP]
> 🛠️ **Using skills is great — building your own is how you really learn.**
> Learn to craft your own skills, step by step, at **[webreactiva.com/guias/crea-skills](https://webreactiva.com/guias/crea-skills)**.

## Quickstart

Install **all** the skills into the current project:

```bash
npx skills add webreactiva/skills
```

Install **one** skill by name:

```bash
npx skills add webreactiva/skills --skill politenizer
```

Add `-g` to install globally (`~/.claude/skills`) instead of in the current project.
Distribution is powered by [skills.sh](https://skills.sh), which supports 50+ agents.

## Skills

<!-- skills:start -->
### AI Workflow

| Skill | What it does | Page | Install |
| --- | --- | --- | --- |
| [`handoff-torch`](skills/ai-workflow/handoff-torch) | Generate a self-contained handoff document so any AI coding agent can resume the current task in a fresh conversation with zero prior context — code map, run/test commands, pending steps, and gotchas learned. | — | `npx skills add webreactiva/skills --skill handoff-torch` |
| [`migrate-copilot-instructions`](skills/ai-workflow/migrate-copilot-instructions) | Migrate a project's GitHub Copilot config into Claude Code, Codex, or opencode via a portable AGENTS.md — converting prompts, agents, skills, and MCP, never blind-copying. | [web ↗](https://www.webreactiva.com/skills/migrate-copilot-instructions) | `npx skills add webreactiva/skills --skill migrate-copilot-instructions` |
| [`pre-mortem`](skills/ai-workflow/pre-mortem) | Imagine the change has already shipped and broken. Surface 3-5 ranked failure modes with likelihood, blast radius, and concrete mitigations, then commit to one of: ship as-is, harden first, or split the change. | — | `npx skills add webreactiva/skills --skill pre-mortem` |

### Career

| Skill | What it does | Page | Install |
| --- | --- | --- | --- |
| [`github-profile-readme`](skills/career/github-profile-readme) | Generate a polished GitHub profile README — the special <owner>/<owner> repo — from real account data, for a person, project, or brand. | [web ↗](https://www.webreactiva.com/skills/github-profile-readme) | `npx skills add webreactiva/skills --skill github-profile-readme` |
| [`politenizer`](skills/career/politenizer) | Turn blunt, angry, or profanity-laden messages into courteous, persuasive ones — in three registers, in the user's own language. | [web ↗](https://www.webreactiva.com/skills/politenizer) | `npx skills add webreactiva/skills --skill politenizer` |

### Engineering

| Skill | What it does | Page | Install |
| --- | --- | --- | --- |
| [`ascii-flow`](skills/engineering/ascii-flow) | Draw portable ASCII / Unicode diagrams — flows, architecture, sequences, trees — that stay aligned and render anywhere with zero tooling, for code comments, READMEs and commit messages. | — | `npx skills add webreactiva/skills --skill ascii-flow` |
| [`git-commit-organizer`](skills/engineering/git-commit-organizer) | Organize pending git changes into clean, atomic Conventional Commits — proposed for your approval, never pushed. | [web ↗](https://www.webreactiva.com/skills/git-commit-organizer) | `npx skills add webreactiva/skills --skill git-commit-organizer` |
<!-- skills:end -->

### 🚧 Work in progress (build in public)

We ship in the open. Skills under [`skills/work-in-progress/`](skills/work-in-progress) are
unfinished **on purpose** — peek at them, give feedback, and watch them grow.
_(Nothing here yet — the first one is on its way.)_

## Philosophy

This is the [Web Reactiva](https://webreactiva.com) take on Agent Skills: small, sharp tools
that solve a real problem a developer actually has, written the way we'd explain them to a
colleague. We follow the *malandriner* mindset — pragmatic, human-centered, allergic to hype.
A skill earns its place by being useful on a normal Tuesday, not by being clever.

What every skill here holds to:

- **One job, done well.** A skill is a single capability, not a framework.
- **Honest by default.** No invented facts, no fake confidence. If a skill can't know
  something, it asks or says so.
- **Human on the other end.** The output is for a person — readable, kind, and still convinced.
- **Built in public.** Half-finished is fine if it's labeled — see [`work-in-progress/`](skills/work-in-progress).

The repo is in **English** so it travels, but the voice keeps the Web Reactiva warmth.

## How it's organized

- A skill lives at `skills/<category>/<slug>/SKILL.md`.
- **Category** is just the parent folder — moving a skill is a `git mv`.
- **Status** is the top folder: `work-in-progress/` means it's still cooking; everything else is stable.
- Extra metadata for the website (summary, tags, languages, featured) lives in
  [`skills-catalog.json`](skills-catalog.json), which is **generated** — run `npm run build:catalog`
  after adding or moving a skill. The `SKILL.md` frontmatter stays 100% standard.


<img width="2400" height="1200" alt="github-webreactiva-skills" src="https://github.com/user-attachments/assets/e6b60704-c4bb-4295-8ea9-3b10dbe6e49a" />


## License

[MIT](LICENSE) — use them, fork them, make them yours.
