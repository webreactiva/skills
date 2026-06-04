# Host agents: detection, discovery, config roots, and model switching

Two questions matter for each agent: (1) is it the **host** running this
session, and (2) is it **installed** at all (so it can serve as an independent
critic even when it isn't the host). The script answers both. Detection of the
host uses env vars first, then config dir, then a binary on `PATH`. Discovery of
installed agents uses binary-on-`PATH` and/or config-dir presence.

Whatever the script guesses, the `host_agent` / `config_root` fields in
`agents.json` win once you set them. An agent with `blocked: true` in
`agents.json` is never used as a critic — not by ranking, not by explicit
arguments — until it's unblocked (`rubber_duck.py block|unblock <agent>`).

## Verifying invocations

The `subprocess_command` values below are **starting points, not guarantees** —
flags change across versions and BYOK setups. Each agent has a `help_command`.
Before relying on a one-shot command, run the help command, confirm the
non-interactive flag for the installed version, then write the corrected command
into `agents.<key>.subprocess_command` and set `agents.<key>.verified: true`.
That cost is paid once per agent and remembered thereafter.

`{model}` → the critic model ID; `{prompt}` → the critique prompt, **filled
from a file** (`"$(cat <file>)"`, or the agent's stdin/file flag) — never raw
text pasted into the shell, which breaks on quoting and `ARG_MAX` with real
critique payloads. Some agents have no model *flag* (they pick the model from
their own config); for those, pin the critic model in the agent's config and
leave the command model-free.

## Contents

- Claude Code
- GitHub Copilot CLI
- OpenCode
- Codex CLI
- Antigravity (`agy`) — successor to Gemini CLI
- Amp (Sourcegraph)
- Kilo Code
- pi
- Cursor
- Gemini CLI (deprecated)
- Unknown hosts

---

## Claude Code

- **Env:** `CLAUDECODE`, `CLAUDE_CODE*` — **Binary:** `claude` — **Config:** `~/.claude`
- **Families:** anthropic (single)
- **Help:** `claude --help`
- **Subprocess:** `claude -p --model {model} {prompt}`
- **In-session:** `/model {model}`
- **Notes:** As a *host*, a Claude session is anthropic-only and cannot contrast
  against itself — use a second installed CLI (codex/amp/kilo/pi/opencode/
  antigravity) as the critic. As a *critic* for a non-Claude session, it's an
  excellent anthropic-family contrast.

## GitHub Copilot CLI

- **Env:** `COPILOT_*`, `GH_COPILOT*` — **Binary:** `copilot` — **Config:** `~/.config/copilot` (fallback `~/.copilot`)
- **Families:** openai, anthropic (multi-provider)
- **Help:** `copilot --help`
- **Subprocess:** `copilot -p {prompt} --model {model}`
- **In-session:** `/model {model}`
- **Notes:** Multi-provider — routes both GPT and Claude families, so it can
  contrast against either an anthropic or an openai session.

## OpenCode

- **Env:** `OPENCODE*` — **Binary:** `opencode` — **Config:** `~/.config/opencode` (fallback `~/.opencode`)
- **Families:** anthropic, openai, google, xai, deepseek (multi-provider)
- **Help:** `opencode --help`
- **Subprocess:** `opencode run --model {model} {prompt}`
- **In-session:** `/model {model}`
- **Notes:** Model IDs are usually `provider/model` form — record each in
  `available_models` as `{"id": "provider/model", "family": "…"}`.
  Provider-agnostic, so a flexible critic for any session.

## Codex CLI

- **Env:** `CODEX_*` — **Binary:** `codex` — **Config:** `~/.codex`
- **Families:** openai (single)
- **Help:** `codex --help`
- **Subprocess:** `codex exec -m {model} {prompt}`
- **Notes:** Use the non-interactive `exec` form. A clean openai-family contrast
  for a Claude or Gemini session.

## Antigravity (`agy`) — successor to Gemini CLI

- **Env:** `ANTIGRAVITY*`, `AGY_*` — **Binary:** `agy` — **Config:** `~/.antigravity` (fallback `~/.config/antigravity`)
- **Families:** google, anthropic (multi-provider; default Gemini, optional Claude/OSS)
- **Help:** `agy --help` (also `agy help`, `agy -h`)
- **Subprocess:** *unverified* — TUI-first. Confirm the one-shot flag via help,
  then record it. The TUI uses `/goal <prompt>` for an autonomous run and
  `/grill-me` for clarifying questions first — neither switches the model, so
  there is no in-session model-switch path for this agent.
- **Notes:** Google's replacement for Gemini CLI (binary is `agy`, not
  `antigravity`; installer drops it in `~/.local/bin`). Shares the Antigravity
  2.0 agent harness. Prefer this over Gemini CLI going forward.

## Amp (Sourcegraph)

- **Env:** `AMP_API_KEY`, `AMP_*` — **Binary:** `amp` — **Config:** `~/.config/amp/settings.json`
- **Families:** anthropic, openai, google (multi-provider / multi-frontier)
- **Help:** `amp --help`
- **Subprocess:** `amp -x {prompt}` (also `--execute`; `--stream-json` for JSON output)
- **Notes:** `amp -x` is non-interactive but consumes **paid** credits (Amp Free
  is interactive-only). Model is chosen via settings/command palette rather than
  a flag — pin the critic family in `~/.config/amp/settings.json` (or via `AMP_*`
  env) before running. Isolated mode uses an Anthropic key; connected mode routes
  multiple frontier models.

## Kilo Code

- **Env:** `KILO_*`, `KILOCODE*` — **Binary:** `kilo` (also `kilocode`) — **Config:** `~/.kilo` (verify; also `~/.config/kilo`)
- **Families:** 500+ models across 60+ providers (anthropic, openai, google, xai, deepseek, qwen, …) — contrasts any session family
- **Help:** `kilo --help`
- **Subprocess:** `kilo run --auto {prompt} --json` (autonomous; `--json` for structured output; also `kilocode --auto`)
- **Notes:** Set the critic model via `kilo config` / `/connect`; confirm the
  model flag with the help command. Has a Memory Bank feature of its own. Free
  unlimited tier via MiniMax with no card.

## pi

- **Env:** `PI_*` — **Binary:** `pi` — **Config:** `~/.pi` (verify; also `~/.config/pi`)
- **Families:** BYOK across 20+ providers (anthropic, openai, google, xai, deepseek, mistral, groq, …) — contrasts any session family
- **Help:** `pi --help`
- **Subprocess:** *unverified* — interactive-first TUI. Confirm a one-shot/print
  mode via help, then record it. (npm: `@earendil-works/pi-coding-agent`.)
- **Notes:** Minimal four-tool core (read/write/edit/bash), self-extending via
  TypeScript. Auth via provider API-key env vars or `/login` for Claude
  Pro/ChatGPT Plus/Copilot subscriptions.

## Cursor

- **Env:** `CURSOR_*` — **Binary:** `cursor-agent` — **Config:** `~/.cursor`
- **Families:** anthropic, openai
- **Help:** `cursor-agent --help`
- **Subprocess:** none reliable.
- **Notes:** No dependable programmatic one-shot critic path. Prefer another
  installed CLI; otherwise self-critique. If `claude`/`codex`/etc. happen to be
  on `PATH`, use one of those as the critic and record it.

## Gemini CLI (deprecated)

- **Env:** `GEMINI_*` — **Binary:** `gemini` — **Config:** `~/.gemini`
- **Families:** google
- **Help:** `gemini --help`
- **Subprocess:** `gemini -m {model} -p {prompt}`
- **In-session:** `/model {model}`
- **Notes:** **Being retired in favor of Antigravity (`agy`).** The script
  deprioritizes it but still allows it as a google-family critic while it exists.
  Prefer Antigravity for new setups.

## Unknown hosts

If detection returns `unknown`, memory defaults to
`~/.config/rubber-duck/.webreactiva/rubber-duck/agents.json`. Identify the host yourself, set
`host_agent` and `config_root` (point it at the host's real config dir), then
proceed. The installed-agent scan still runs, so even an unrecognized host can
borrow any installed CLI as a contrasting critic.
