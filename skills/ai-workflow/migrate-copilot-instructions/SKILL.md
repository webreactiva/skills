---
name: migrate-copilot-instructions
description: Migrate a project's GitHub Copilot configuration — global instructions (.github/copilot-instructions.md), path-scoped instructions (.github/instructions/*.instructions.md), prompts (.github/prompts), custom agents (.github/agents), skills (.github/skills), and MCP (.vscode/mcp.json) — into a target coding agent: Claude Code (CLAUDE.md, .claude/rules, .claude/agents, .claude/commands, .claude/skills), Codex (AGENTS.md, ~/.codex), or opencode (AGENTS.md, .opencode), via a portable AGENTS.md. Use this skill whenever the user wants to migrate, port, consolidate, unify, or reconcile Copilot instructions, custom instructions, rules, prompts, agents, or skills to another coding agent, or mentions copilot-instructions.md, AGENTS.md, CLAUDE.md, moving off Copilot to Claude Code / Codex / opencode, or reconciling a .github and a .claude setup. Always detect the target from the repository FIRST; only ask the user when detection is ambiguous.
metadata:
  author: webreactiva.com
  namespace: webreactiva
---

# Migrate Copilot instructions

Migrate a project's AI coding-agent configuration **from GitHub Copilot's format** into a portable `AGENTS.md` and the target tool's ecosystem — **Claude Code**, **Codex**, or **opencode** — without losing anything and without creating a "museum of contradictory instructions for robots."

The source is always Copilot's `.github/` setup. The **target** is what varies; detect it from the repo (Step 0). Examples below lean on Copilot → Claude Code because it's the most common request, but the same workflow targets Codex and opencode — the destination homes differ, the method (convert, don't copy) does not.

## Core principle (read before touching files)

The bad migration renames `copilot-instructions.md` to `CLAUDE.md` and stops. It fails, because each tool reads configuration differently and copying a filename does not copy the behavior.

The good migration moves from **"one file per tool" to "one common source with native adapters."** `AGENTS.md` is the natural shared source: Codex and opencode read it natively, and Claude Code can import it. Each tool then reads it through a thin adapter, and Copilot's tool-specific artifacts are re-interpreted into the target's native homes.

Two classes of artifact, handled differently:

1. **Instructions & rules** — plain prose. They travel cheaply via wrappers, imports, or sections. A path-scoped rule keeps its glob; only the field name changes (`applyTo` → `paths`).
2. **Prompts, agents, skills, MCP** — behavioral/executable. They must be **re-interpreted per target, never blind-copied**, because frontmatter fields, tool names, model names, and argument syntax all differ. `cp -R .github/agents .claude/agents` looks like it works until you run it.

Keep this distinction front of mind throughout.

## Step 0 — Detect the target (do this first, always)

The source is Copilot. Inspect the repository to learn which **target** ecosystem it's heading toward before asking anything.

```bash
# List the agent-config markers that exist in this repo
for p in \
  AGENTS.md AGENTS.override.md CLAUDE.md CLAUDE.local.md GEMINI.md .cursorrules \
  .github/copilot-instructions.md .github/instructions .github/prompts .github/agents .github/skills .vscode/mcp.json \
  .claude .claude/rules .claude/agents .claude/commands .claude/skills .claude/settings.json .mcp.json \
  .codex .codex/config.toml \
  .opencode .opencode/agent .opencode/command .opencode/skills opencode.json; do
  [ -e "$p" ] && echo "FOUND  $p"
done
```

Interpret the result to confirm the **SOURCE** (Copilot markers) and pick the **TARGET**:

| Target signal found | Target |
| --- | --- |
| `.claude/` or `CLAUDE.md` | **Claude Code** |
| `AGENTS.md` + `.codex/` (no `.claude/`) | **Codex** |
| `AGENTS.md` + `.opencode/` or `opencode.json` | **opencode** |
| `AGENTS.md` only | tool-agnostic — stop at `AGENTS.md`, add adapters on request |
| only Copilot markers, no target ecosystem | ambiguous → ask (Step 1.5) |

Every target produces a clean `AGENTS.md` as the common source; the target only decides which adapter layer you also generate (`CLAUDE.md` + `.claude/` for Claude, native `AGENTS.md` + `.codex/`/`.opencode/` otherwise). State the detection back in one line — e.g. "Found Copilot config and a `.claude/` directory — migrating Copilot → Claude Code." — so the user can correct a wrong guess early.

## Step 1 — Inventory the Copilot source

Copilot is not one file. Map every layer that exists, because each lands in a different place in the target. The artifact types are universal:

1. **Global instructions** — `.github/copilot-instructions.md`.
2. **Path-specific instructions** — `.github/instructions/*.instructions.md` (each with an `applyTo` glob).
3. **Reusable prompts** — `.github/prompts/*.prompt.md`.
4. **Custom agents** — `.github/agents/*.agent.md`.
5. **Skills** — `.github/skills/<name>/SKILL.md` packages.
6. **MCP servers** — declared in `.vscode/mcp.json`.

Read each file you find so you know what you are moving. Flag anything Copilot-specific (mentions of Copilot Chat, VS Code modes, IDE-only tool names) — that gets stripped or re-interpreted, not carried over. `references/tool-behaviors.md` has the exact home for each artifact in each target — **read it before writing any file.**

## Step 1.5 — Ask only when ambiguous

If Step 0 found only Copilot markers and no target ecosystem, ask one focused question and branch:

> "I don't see a target yet. Migrate Copilot toward **Claude Code** (`CLAUDE.md` + `.claude/`), **Codex** (`AGENTS.md` + `.codex/`), or **opencode** (`AGENTS.md` + `.opencode/`)? I can also produce just a shared `AGENTS.md` plus a thin adapter for each tool you keep using."

Do not ask anything else. Pick the target from their answer.

## Step 2 — Build AGENTS.md (the common source)

Convert `.github/copilot-instructions.md` into a clean, minimal, tool-agnostic `AGENTS.md`. **Convert, do not copy.** Keep only what is common and durable:

- Stack and versions; build, test, and lint commands.
- Naming conventions and folder structure; project entry points.
- Hard rules ("don't touch these directories", "update tests when logic changes").

Strip GitHub/IDE-specific language. If Copilot stays in use, leave `.github/copilot-instructions.md` as a **short wrapper** pointing at `AGENTS.md` rather than deleting it (Copilot's coding agent reads a root `AGENTS.md` too).

> Do not silently drop content. If the source had sections that don't fit the minimal common source (e.g. project-specific git policy), tell the user where they went or that they're recoverable from version control.

## Step 3 — Wire instructions and rules into the target

- **Global**: give the target its native adapter. Claude Code → a `CLAUDE.md` importing `@AGENTS.md` plus any Claude-only lines (or a symlink when there's nothing to add). Codex / opencode → `AGENTS.md` at the root is already native. Exact wrappers are in `references/migration-recipes.md`.
- **Path-scoped rules**: keep the glob, change the home. Copilot `applyTo` → Claude `.claude/rules/*.md` with `paths:` frontmatter. Codex / opencode have no native glob-scoped rule file → fold into `AGENTS.md` sections or per-directory `AGENTS.md` files (opencode can also list globs under `instructions` in `opencode.json`). A thin wrapper that points back to the Copilot rule file avoids duplicating content while Copilot is still in use.

## Step 4 — Migrate prompts, agents, and skills (convert, don't blind-copy)

This is the part the lazy migration gets wrong. Each Copilot artifact has a native home in the target and a frontmatter dialect that must be translated. The destination matrix (condensed; full version in `references/tool-behaviors.md`):

| Copilot artifact (source) | Claude Code | Codex | opencode |
| --- | --- | --- | --- |
| `.github/prompts/*.prompt.md` | `.claude/commands/*.md` **or** `.claude/skills/<n>/SKILL.md` → `/n` | skills (`~/.codex/prompts/` deprecated) | `.opencode/command/*.md` → `/n` |
| `.github/agents/*.agent.md` | `.claude/agents/*.md` | `.codex/agents/*.toml` | `.opencode/agent/*.md` |
| `.github/skills/<n>/SKILL.md` | `.claude/skills/<n>/SKILL.md` → `/n` | `.agents/skills/<n>/SKILL.md` | `.opencode/skills/` (also reads `.claude/skills/`, `.agents/skills/`) |
| `.vscode/mcp.json` | `.mcp.json` | `.codex/config.toml` | `opencode.json` |

Conversion rules (field-by-field tables and copy-paste examples are in `references/migration-recipes.md`):

- **Prompts**: the body is usually reusable as-is. Keep `description`; **normalize the `model`** to a name the target runs and drop it if Copilot pinned a model the target can't run; translate argument placeholders to the target's syntax.
- **Agents**: reuse the system-prompt body verbatim, but re-do the frontmatter. **Normalize `model`** to the target's aliases, and **re-interpret `tools`** — map Copilot's verbs (execute/read/edit/search/web/todo/runSubagent) to the target's tool names, and **drop tool references the target doesn't have**, especially IDE-only tools and MCP server ids not declared in the target's MCP file. Preserve restrictive intent (a read-only agent stays read-only).
- **Skills**: `SKILL.md` is a cross-tool open standard ([agentskills.io](https://agentskills.io)), so the format travels. Copy `SKILL.md` plus its `references/`, `assets/`, `scripts/`, but **drop Copilot sidecar files** (`*.metadata.json`) and review `allowed-tools`/`model` per target.
- **MCP**: the server is identical; only the declaration file changes (see matrix). Re-declare; don't copy the file.

**Skip what Copilot already retired.** Before carrying an artifact over, check its frontmatter or sidecar `*.metadata.json` for `deprecated`/`excluded`/`disabled` flags and don't migrate those — surface them in the summary instead. When migrating into a concrete project, also flag artifacts that target a stack the project doesn't use (they're inert until invoked, but say so).

If there are many prompts/agents/skills, tell the user this is re-interpretation work, not a copy. A small script that maps frontmatter in bulk is fine, but the model/tool re-interpretation still needs judgment.

## Step 5 — Verify before declaring done

- `AGENTS.md` exists, is minimal, and is free of Copilot-specific language.
- The target's global adapter is in place (e.g. `CLAUDE.md` with `@AGENTS.md`, or native `AGENTS.md`).
- Each path-scoped rule that needs scoping carries the target's glob field (`paths:` for Claude).
- Each migrated prompt/agent/skill sits in the correct directory with valid target frontmatter, a normalized model, and re-interpreted tools.
- No `CLAUDE.md` exceeds ~200 lines (longer files reduce adherence).
- List anything still needing hand work (MCP servers to declare, deprecated artifacts skipped, off-stack artifacts), so nothing is silently dropped.

End with a short summary table of what moved where and what still needs hand work.

## Output style

Be concrete: show the resulting file tree and the actual file contents you create or edit. Prefer surgical edits over rewrites when a file already exists. Never invent tool behavior — if a claim can't be confirmed from `references/tool-behaviors.md` or official docs, flag it instead of stating it.
