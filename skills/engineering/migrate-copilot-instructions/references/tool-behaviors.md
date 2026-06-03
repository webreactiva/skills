# Tool behaviors (verified against official documentation)

Use this as the source of truth for how each agent reads configuration and where every artifact lives. Claims here are confirmed by the official docs linked at the bottom. If something a user asks for contradicts this file, flag it rather than guessing.

## Table of contents

- Artifact destination matrix
- GitHub Copilot
- Claude Code
- Codex
- opencode
- MCP declaration per tool
- Official sources

## Artifact destination matrix

Where each artifact type lives in each tool. Project-level paths are shown; most tools also have a global/user equivalent (noted per tool below). "—" means the tool has no dedicated home and the content folds into another layer.

| Artifact | GitHub Copilot | Claude Code | Codex | opencode |
| --- | --- | --- | --- | --- |
| Global instructions | `.github/copilot-instructions.md` | `CLAUDE.md` (commonly `@AGENTS.md`) | `AGENTS.md` (root) | `AGENTS.md` (root; also reads `CLAUDE.md`) |
| Path-scoped rules | `.github/instructions/*.instructions.md` (`applyTo:`) | `.claude/rules/*.md` (`paths:` frontmatter) | — (sections in `AGENTS.md` / per-dir `AGENTS.md`) | — (sections in `AGENTS.md`; globs via `instructions` in `opencode.json`) |
| Prompts / commands | `.github/prompts/*.prompt.md` | `.claude/commands/*.md` **or** `.claude/skills/<name>/SKILL.md` → `/name` | `~/.codex/prompts/*.md` (**deprecated** → use skills) | `.opencode/command/*.md` → `/name` |
| Subagents / agents | `.github/agents/*.agent.md` | `.claude/agents/*.md` | `.codex/agents/*.toml` / `~/.codex/agents/*.toml` | `.opencode/agent/*.md` |
| Skills | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` → `/name` | `.agents/skills/<name>/SKILL.md` | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` |
| MCP servers | `.vscode/mcp.json` | `.mcp.json` | `.codex/config.toml` | `opencode.json` |
| Settings / hooks | VS Code settings | `.claude/settings.json` | `~/.codex/config.toml`, `.codex/config.toml` | `opencode.json` |

`SKILL.md` follows the cross-tool [Agent Skills](https://agentskills.io) open standard, which is why skills are the most portable artifact — Claude Code, Codex, and opencode all read a `SKILL.md` (opencode even reads `.claude/skills/` and `.agents/skills/` directly).

## GitHub Copilot

Copilot stores configuration in repository layers that coexist; when global and path-specific instructions both match, Copilot uses both:

1. **Global instructions** — `.github/copilot-instructions.md`, applies to the whole repo.
2. **Path-specific instructions** — `.github/instructions/*.instructions.md`, each with an `applyTo` field (glob patterns) defining which files it applies to.
3. **Prompt files** — `.github/prompts/*.prompt.md`, reusable prompts for a single interaction.
4. **Custom agents** — `.github/agents/*.agent.md`.
5. **Skills** — `.github/skills/<name>/SKILL.md` packages.
6. **Agent file** — Copilot's coding agent also reads a root `AGENTS.md` (and accepts `CLAUDE.md`/`GEMINI.md`).
7. **MCP** — declared in `.vscode/mcp.json`.

Cost note: Copilot sends instructions **with every message**, so GitHub recommends keeping them brief and self-contained.

## Claude Code

**Claude Code reads `CLAUDE.md`, not `AGENTS.md`.** To share instructions without duplication, create a `CLAUDE.md` that imports the other file with `@AGENTS.md`, optionally adding Claude-specific lines below. A symlink also works when no Claude-specific content is needed (`ln -s AGENTS.md CLAUDE.md`); on Windows symlinks need admin/Developer Mode, so prefer the `@AGENTS.md` import there.

**Memory load scopes** (concatenated, broadest to most specific): managed policy → user (`~/.claude/CLAUDE.md`) → project (`./CLAUDE.md` or `./.claude/CLAUDE.md`) → local (`./CLAUDE.local.md`, gitignored). Files above the working directory load in full at launch; files in subdirectories load on demand.

- **Size**: target under 200 lines per `CLAUDE.md`; longer files reduce adherence. Block-level HTML comments (`<!-- ... -->`) are stripped before injection, so they cost no context.
- **Imports**: `@path/to/import`, relative or absolute, recursive up to **four hops**. Imports expand into context at launch and do not reduce context usage.

**Path-scoped rules** — `.claude/rules/*.md`. Each file covers one topic and can carry a `paths` frontmatter field with glob patterns, so it only enters context when Claude works with matching files. Rules without a `paths` field load at launch.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API rules
- All endpoints validate input.
```

**Subagents** — `.claude/agents/*.md` (project) and `~/.claude/agents/` (user); both scanned recursively (subfolders don't affect identity). Identity comes only from the `name` frontmatter field, which must be unique per scope. Frontmatter: `name` and `description` (required), `tools` (optional, comma-separated; omit to inherit all), `model` (optional — `sonnet`/`opus`/`haiku`/`inherit` or a full id). The body is the system prompt.

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a senior code reviewer...
```

**Skills & commands** — Claude Code merged custom commands into skills: a file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy`. Skills are recommended (they allow supporting files, invocation control, and auto-loading). Locations: project `.claude/skills/<name>/SKILL.md`, user `~/.claude/skills/<name>/SKILL.md`. Frontmatter: `description` (required), plus optional `argument-hint`, `arguments`, `allowed-tools`, `disallowed-tools`. Argument placeholders in the body: `$ARGUMENTS`, `$ARGUMENTS[N]`, the `$N` shorthand, and `$name` for named `arguments`.

```markdown
---
description: Fix a GitHub issue
argument-hint: [issue-number]
allowed-tools: Bash(gh *)
---

Fix GitHub issue $ARGUMENTS following our coding standards.
```

**MCP** — `.mcp.json`. **`/init`** generates a starting `CLAUDE.md`, and in a repo that already has `AGENTS.md` it folds in the relevant parts (also reads `.cursorrules`/`.windsurfrules`).

## Codex

Codex uses `AGENTS.md` as its persistent-instruction mechanism: project `AGENTS.md` (root or nested per-directory; files closer to the working directory take precedence), global `~/.codex/AGENTS.md`, and `AGENTS.override.md` for temporary overrides. Keep it small: build/test commands, review expectations, repo conventions, per-directory notes. There is no native glob-scoped rule file — scope by placing `AGENTS.md` in subdirectories.

- **Agents / subagents** — `.codex/agents/<name>.toml` (project) and `~/.codex/agents/<name>.toml` (personal). One **TOML** file per agent; required keys `name`, `description`, `developer_instructions`; optional `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`, `nickname_candidates` (omitted keys inherit from the session). Global agent settings live under `[agents]` in the config.

  ```toml
  name = "my_explorer"
  description = "Read-only codebase exploration agent"
  model = "gpt-5.4-mini"
  sandbox_mode = "read-only"
  developer_instructions = """
  Map the codebase structure. Cite specific files.
  """
  ```

- **Prompts** — `~/.codex/prompts/*.md` (top-level only; markdown + YAML frontmatter `description`/`argument-hint`, args `$1`–`$9`, `$NAME` as `KEY=value`, `$ARGUMENTS`; invoked `/prompts:name`). **Deprecated** — the docs recommend using skills for reusable instructions Codex can invoke explicitly or implicitly.
- **Skills** — `.agents/skills/<name>/SKILL.md` (repo) and `$HOME/.agents/skills/<name>/SKILL.md` (global); standard `SKILL.md` + optional `scripts/`, `references/`, `assets/`. Skill dependencies can be declared in `.agents/openai.yaml`.
- **Config / MCP / settings** — `~/.codex/config.toml` (user) and `.codex/config.toml` (repo).

## opencode

opencode reads `AGENTS.md` for instructions (project root and `~/.config/opencode/AGENTS.md` global), and for **legacy compatibility also reads `CLAUDE.md`** (project) / `~/.claude/CLAUDE.md` (global). The first matching file wins per category — if both `AGENTS.md` and `CLAUDE.md` exist, only `AGENTS.md` is used. Extra instruction paths (with glob/remote-URL support) can be listed under `instructions` in `opencode.json`, e.g. `"instructions": ["CONTRIBUTING.md", ".cursor/rules/*.md"]`.

- **Agents** — `.opencode/agent/*.md` (project) and `~/.config/opencode/agents/` (global). The filename is the agent id; markdown frontmatter (`description`, `mode`, `model`, permissions, …) followed by the system-prompt body.
- **Commands** — `.opencode/command/*.md` (project) and `~/.config/opencode/commands/` (global); filename → `/name`. Frontmatter `description`/`agent`/`model`; body is the prompt template. Arguments: `$ARGUMENTS`, `$1`/`$2`/…; templates also support `` !`cmd` `` shell injection and `@path` file references. Commands can alternatively live under the `command` key in `opencode.jsonc`.
- **Skills** — discovered from `.opencode/skills/<name>/SKILL.md`, `.claude/skills/<name>/SKILL.md`, and `.agents/skills/<name>/SKILL.md` (plus the `~/.config/opencode/`, `~/.claude/`, `~/.agents/` global equivalents). `SKILL.md` requires `name` and `description`; optional `license`, `compatibility`, `metadata`. Loaded on demand via the native `skill` tool.
- **Config / MCP** — `opencode.json`.

## MCP declaration per tool

The MCP server is identical; only the declaration changes:

| Tool | MCP declaration file |
| --- | --- |
| Claude Code | `.mcp.json` |
| GitHub Copilot | `.vscode/mcp.json` |
| Codex | `.codex/config.toml` |
| opencode | `opencode.json` |

When migrating an agent that references MCP tools by id, those tools only work if the same server is declared in the target's MCP file. If it isn't, drop the MCP tool references from the migrated agent and note that the server must be declared to restore them.

## Official sources

- How Claude remembers your project — Claude Code Docs: https://code.claude.com/docs/en/memory
- Create custom subagents — Claude Code Docs: https://code.claude.com/docs/en/sub-agents
- Extend Claude with skills (commands merged into skills) — Claude Code Docs: https://code.claude.com/docs/en/skills
- Adding repository custom instructions for GitHub Copilot — GitHub Docs: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- Customization (AGENTS.md, prompts, skills) — Codex / OpenAI Developers: https://developers.openai.com/codex/concepts/customization
- Custom instructions with AGENTS.md — Codex / OpenAI Developers: https://developers.openai.com/codex/guides/agents-md
- Subagents / custom agents (`.codex/agents/*.toml`) — Codex / OpenAI Developers: https://developers.openai.com/codex/subagents
- Custom prompts (deprecated → skills) — Codex / OpenAI Developers: https://developers.openai.com/codex/custom-prompts
- Agents, Commands, Rules, Skills — opencode Docs: https://opencode.ai/docs/agents/ , https://opencode.ai/docs/commands/ , https://opencode.ai/docs/rules/ , https://opencode.ai/docs/skills/
- Agent Skills open standard: https://agentskills.io
