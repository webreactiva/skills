# Migration recipes

Copy-paste-ready moves per direction, the field-by-field conversion mechanics for behavioral artifacts, plus the team-scale compiler approach and a portable repo layout. Use after Step 0 detection has chosen source and target. For exact per-tool file locations, see `tool-behaviors.md`.

## Table of contents

- Recipe: Copilot → Claude Code
- Recipe: Copilot → Codex
- Recipe: Copilot → opencode
- Converting prompts (field-by-field)
- Converting subagents/agents (field-by-field)
- Converting skills
- Skipping retired artifacts
- Team scale: compile native formats from one source
- Portable repo layout

## Recipe: Copilot → Claude Code

```txt
.github/copilot-instructions.md     → AGENTS.md + a CLAUDE.md wrapper
.github/instructions/*.md (applyTo) → .claude/rules/*.md with `paths` frontmatter
.github/prompts/*.prompt.md         → .claude/commands/*.md (or .claude/skills/*/SKILL.md)
.github/agents/*.agent.md           → .claude/agents/*.md (redo model + tools)
.github/skills/*/SKILL.md           → .claude/skills/*/SKILL.md (drop *.metadata.json)
.vscode/mcp.json (MCP)              → .mcp.json
```

Preferred `CLAUDE.md`:

```markdown
# CLAUDE.md

@AGENTS.md

## Claude Code

- Use plan mode before large refactors.
- Prefer TodoWrite for multi-step tasks.
- Run the test command before finalizing changes.
```

Thin path-rule wrapper (avoids duplicating content while Copilot stays in use):

```markdown
---
paths:
  - "src/frontend/**/*"
---

# Frontend rules

Follow the rules in ../../.github/instructions/frontend.instructions.md.
```

## Recipe: Copilot → Codex

Codex reads `AGENTS.md` natively. Two Codex specifics change the mapping: its **agents are TOML** (not markdown), and its **custom prompts are deprecated in favour of skills** — so a Copilot prompt becomes a Codex skill, not a prompt file.

```txt
.github/copilot-instructions.md     → AGENTS.md (root; ~/.codex/AGENTS.md for user-global)
.github/instructions/*.md           → AGENTS.md sections, or per-directory AGENTS.md (no glob scoping)
.github/prompts/*.prompt.md         → .agents/skills/<name>/SKILL.md   (prompts → skills; ~/.codex/prompts/ is deprecated)
.github/agents/*.agent.md           → .codex/agents/<name>.toml         (project) or ~/.codex/agents/ (personal)
.github/skills/*/SKILL.md           → .agents/skills/<name>/SKILL.md    (repo) or $HOME/.agents/skills (global)
.vscode/mcp.json (MCP)              → .codex/config.toml ([mcp_servers]) / ~/.codex/config.toml
overly long style rules             → referenced docs, not always-in-context
```

A Copilot agent (`*.agent.md` = YAML frontmatter + system-prompt body) becomes a Codex agent **TOML**. The body moves into `developer_instructions`; restrictiveness is expressed with `sandbox_mode` (Codex has no per-agent tool allowlist); external tools come from `[mcp_servers]`. Required keys: `name`, `description`, `developer_instructions`.

```toml
name = "research"
description = "Read-only codebase exploration"   # keep from the .agent.md
model = "gpt-5.4-mini"                            # normalize from the Copilot `model`
sandbox_mode = "read-only"                        # preserve a read-only agent's intent
developer_instructions = """
<the .agent.md body, verbatim>
"""

[mcp_servers.example]                             # only if the agent needs an MCP server
url = "https://..."
```

Leave the source tool's global file as a short wrapper while Copilot stays in use.

## Recipe: Copilot → opencode

opencode reads `AGENTS.md` natively (and `CLAUDE.md` for legacy compatibility), so the instruction layer often needs no new file.

```txt
.github/copilot-instructions.md     → AGENTS.md (already native to opencode)
.github/instructions/*.md           → AGENTS.md sections, or `instructions: ["...glob..."]` in opencode.json
.github/prompts/*.prompt.md         → .opencode/command/*.md   (filename → /name)
.github/agents/*.agent.md           → .opencode/agent/*.md      (filename → agent id)
.github/skills/*/SKILL.md           → .opencode/skills/*/SKILL.md (or reuse .claude/skills / .agents/skills)
.vscode/mcp.json (MCP)              → opencode.json
```

## Converting prompts (field-by-field)

The body of a prompt is usually reusable verbatim. Only the frontmatter needs work.

| Source field | Target action |
| --- | --- |
| `name` | Drop — the **filename** becomes the command name (`deploy.md` → `/deploy`). |
| `description` | Keep. |
| `model` | **Normalize** to a name the target runs; **drop** if the source pinned a model the target can't run (e.g. a GPT model when migrating to Claude Code — let it inherit). |
| `mode` / IDE fields | Drop. |
| arguments in body | Translate placeholders to the target's syntax (Claude: `$ARGUMENTS`, `$N`, `$name`; opencode: `$ARGUMENTS`, `$1`). |

> **Codex target:** custom prompts (`~/.codex/prompts/`) are deprecated — convert a Copilot prompt into a **skill** (`.agents/skills/<name>/SKILL.md`) instead, so Codex can invoke it explicitly or implicitly.

## Converting subagents/agents (field-by-field)

Reuse the system-prompt **body verbatim**; rebuild the frontmatter for the target.

| Source field | Target action |
| --- | --- |
| `name` | Keep (identity in Claude/Copilot comes from `name`; in opencode from the filename). |
| `description` | Keep — it drives delegation. |
| `model` | **Normalize** to the target's aliases. Map by family, not exact version. |
| `tools` | **Re-interpret**, see below. |

**Model normalization** (map by family; pick the target's current alias):

| Source model contains | Claude Code | Codex / opencode |
| --- | --- | --- |
| "opus" | `opus` | nearest large model |
| "sonnet" | `sonnet` | nearest mid model |
| "haiku" | `haiku` | nearest small model |
| a model the target can't run (e.g. GPT in Claude) | `inherit` (or omit) | the target's default |

**Tool re-interpretation** — source tool names rarely match the target's. Map the generic verbs and **drop anything the target doesn't have**:

| Generic / Copilot tool | Claude Code tools |
| --- | --- |
| `execute` / run shell | `Bash` |
| `read` | `Read` |
| `edit` / write | `Edit`, `Write` |
| `search` / grep | `Grep`, `Glob` |
| `web` / websearch | `WebSearch`, `WebFetch` |
| `todo` | `TodoWrite` |
| `runSubagent` | `Agent` |
| IDE-only (`vscode`, editor APIs) | drop |
| MCP tool ids (`server/tool`, `com.x/...`) | drop unless that MCP server is declared in the target's MCP file |

Preserve **restrictive intent**: if the source agent omits write/execute tools (a read-only researcher), the migrated agent must stay read-only — don't widen it by omitting the `tools` field (which inherits everything in Claude Code).

**Per-target frontmatter shape:**

| Target | File | Identity | Body field | Model | Restrict tools via |
| --- | --- | --- | --- | --- | --- |
| Claude Code | `.claude/agents/<name>.md` | `name` frontmatter | markdown body | `model:` alias | `tools:` allowlist |
| Codex | `.codex/agents/<name>.toml` | `name` key | `developer_instructions` | `model` key | `sandbox_mode` (no tool allowlist); MCP via `[mcp_servers]` |
| opencode | `.opencode/agent/<name>.md` | filename | markdown body | `model:` frontmatter | `permission`/`tools` frontmatter |

## Converting skills

`SKILL.md` is the cross-tool [Agent Skills](https://agentskills.io) standard, so skills are the most portable artifact.

- Copy the whole skill folder: `SKILL.md` + `references/` + `assets/` + `scripts/`.
- **Drop tool-specific sidecar files** that aren't part of the standard (e.g. Copilot's `*.metadata.json`).
- Review `allowed-tools`/`model` in the frontmatter against the target.
- opencode can read `.claude/skills/` and `.agents/skills/` directly, so a copy may be unnecessary there.

## Skipping retired artifacts

Don't migrate what the source already turned off. Before carrying each prompt/agent/skill over, check its frontmatter or sidecar metadata for retirement flags and skip the ones marked, e.g.:

```bash
# example: skip agents whose sidecar metadata marks them deprecated
grep -l '"deprecated"[[:space:]]*:[[:space:]]*true' .github/agents/*.metadata.json
```

Common flags seen in the wild: `deprecated`, `excluded`, `disabled`. Surface skipped artifacts in the final summary instead of dropping them silently. When migrating into a concrete project, also flag artifacts whose stack the project doesn't use — they're inert until invoked, but the user should know they came along.

## Team scale: compile native formats from one source

For teams with several repos and tools, compile instead of hand-syncing. The "write once, emit many" approach keeps one intermediate source and generates the native files:

| Destination | Generated artifact | Transform |
| --- | --- | --- |
| Copilot | `.github/instructions/*.instructions.md` | preserve `applyTo` |
| Claude Code | `.claude/rules/*.md` | `applyTo` → `paths` |
| Cursor | `.cursor/rules/*.mdc` | `applyTo` → Cursor rule format |
| Codex / opencode | `AGENTS.md` | flatten to single guide |

One source of truth, native adapters generated, no drift.

## Portable repo layout

```txt
repo/
├── AGENTS.md                         # common source, minimal (Codex/opencode read natively)
├── CLAUDE.md                         # wrapper: @AGENTS.md + Claude layer
├── .github/
│   ├── copilot-instructions.md       # short wrapper while Copilot is used
│   ├── instructions/*.instructions.md # path rules (applyTo)
│   ├── prompts/*.prompt.md
│   ├── agents/*.agent.md
│   └── skills/*/SKILL.md
├── .claude/
│   ├── rules/*.md                    # path rules (paths frontmatter)
│   ├── commands/*.md                 # prompts → /name
│   ├── agents/*.md                   # subagents
│   └── skills/*/SKILL.md
├── .opencode/                        # agent/, command/, skills/ (or reuse .claude/.agents)
└── .codex/
    └── config.toml                   # Codex MCP + settings
```

Governing rules:

- `AGENTS.md` = common source. Everything universal lives here.
- `CLAUDE.md` / `.github/copilot-instructions.md` = wrapper or tool-specific layer, never a full copy.
- Path rules stay in the source format if that tool is still used, replicated as thin wrappers in the target.
- Skills = reusable workflows, not global rules — never inside `AGENTS.md`.
- Agents = roles, not repo documentation; re-interpret model + tools per tool.
- MCP, settings, and hooks = native per tool.
