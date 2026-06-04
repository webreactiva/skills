---
name: rubber-duck
description: >-
  Get a constructive second opinion on a plan, design, diff, or test suite from
  a DIFFERENT AI model than the one running the current session. Use this skill
  whenever the user says "rubber duck this", "/rubber-duck", "poke holes in
  this", "get a critique", "second opinion", "review my plan before I build it",
  "is this approach sound", or when you are about to commit to a non-trivial
  design, multi-file change, or architectural decision and want an independent
  reviewer that does not share your blind spots. Also use it reactively after
  repeated failed attempts at the same problem. The skill detects the host
  coding agent AND every other agent CLI installed on the machine, works out
  which can reach a contrasting model family (the host's own model switch, or a
  second installed CLI like opencode / codex / copilot / amp / kilo / pi /
  antigravity), and remembers all of it in an agents.json memory file so the
  next run is instant.
argument-hint: "[agent-cli] [model]"
metadata:
  author: webreactiva.com
  namespace: webreactiva
---

# Rubber Duck

A constructive critic that gives a second opinion on work-in-progress using a
model from a **different family** than the session model. It looks for blind
spots, design defects, and substantive problems — not style, naming, or
formatting — and reports back with concrete, prioritized findings. It reviews;
it never edits files or runs mutating commands itself.

## The one principle that makes this work

The value comes from the critic running on a **different model family** than the
session. A model is least likely to catch its own blind spots, so asking the
same model to review its own work mostly produces agreement. A Claude session
should be critiqued by a GPT or Gemini model; a GPT session by Claude; and so
on. If you cannot reach a genuinely different model, say so plainly rather than
pretending a same-model self-review is an independent second opinion.

## Two doors to a different model

Reaching a contrasting model is the hard part, and there are two ways:

1. **The host agent switches models itself** — via a subprocess (`claude -p`,
   `copilot -p`, `opencode run`, `codex exec`, …) or an in-session `/model`
   command. A single-family host (e.g. Claude Code is anthropic-only) cannot
   contrast against itself this way.
2. **A second agent CLI installed on the machine** — even if you're running
   Claude Code, the user may also have `opencode`, `codex`, `copilot`, `amp`,
   `kilo`, `pi`, or `antigravity` (`agy`) installed. That second CLI is the door
   to a different family, and using a separate process gives a genuinely
   independent opinion.

The skill discovers both, remembers them, and prefers an independent installed
agent when one is available.

## When to invoke

Mirror the moments where a critique has the highest leverage:

- **After planning a non-trivial change, before implementing it.** Course
  corrections are cheapest here.
- **Mid-implementation** on complex work, to surface blind spots early.
- **After writing tests**, to check coverage and whether the behavior actually
  satisfies the original request.
- **Reactively**, after repeated errors or unexpected results.

Skip it for small, well-understood changes. A critique costs latency and extra
model usage; spend it where a missed defect would be expensive.

## Workflow

Run the bundled script for the deterministic parts (detection, discovery,
memory, contrast selection); do the judgment parts yourself.

**Narrate the phases.** Detection, memory initialization, command discovery,
and the smoke test are *setup*, not the critique. Tell the user when you are
configuring the critic and when the critique itself is running — a slow
configuration step with no narration looks like a stalled review from the
outside.

### Arguments (both optional)

`/rubber-duck [agent-cli] [model]`

- `agent-cli` — registry key of the installed agent to use as the critic
  (`opencode`, `codex`, `copilot-cli`, `gemini-cli`, `antigravity`, `amp`,
  `kilo`, `pi`).
- `model` — concrete model ID for the critic, in that agent's own format
  (e.g. opencode uses `provider/model` ids like `openai/gpt-5.5`).

When provided, they are the user's decision: skip the selection question in
step 3 — run `plan` with `--preferred-agent`/`--preferred-model` so the script
validates the choice and returns the ready invocation (surface any `warning` it
attaches), then go straight to the smoke test. When absent, ask the user in
step 3 before running anything expensive.

### 1. Detect the host and discover installed agents

```bash
python3 scripts/rubber_duck.py status
```

This identifies the host agent, **scans for every known agent CLI installed on
the machine** (binary on `PATH` and/or config dir present), and reads — or
initializes — the memory file at `<config-root>/.webreactiva/rubber-duck/agents.json`. Each
agent gets an entry recording its families, whether it's installed, its config
root, the `help_command` to confirm its invocation, and the best-known
`subprocess_command`. If host detection is wrong or `unknown`, set `host_agent`
and `config_root` in the JSON yourself and treat those as authoritative.

### 2. Establish the session model

You know the current session model better than the script does — write it into
`session_model.id`. Re-running `plan` with `--session-model` also updates it.
The script infers the family from the ID; correct it if needed.

### 3. Pick the contrasting critic — with the user

```bash
python3 scripts/rubber_duck.py plan --session-model "<current-model-id>"
```

This ranks installed agents and returns the best critic — preferring a
programmatic (subprocess) path, an **independent** agent (different process than
the host = a truer second opinion), multi-provider flexibility, a known concrete
model, a verified command, and rotating away from the critic used last time.

**The ranking is a recommendation; the user decides.** The user may prefer a
different agent for reasons the script can't see (cost, quotas, trust, taste):

- If the skill was invoked with arguments, those ARE the decision — pass them
  as `--preferred-agent <agent-cli> --preferred-model <model>` so the script
  validates the contrast and builds the invocation. It attaches a `warning`
  when the choice is same-family or its family is unknown; report that to the
  user instead of silently proceeding.
- Otherwise, ask the user: present the plan's pick and its `alternatives`
  (installed agents that can contrast the session family) and let them choose
  the agent — and the concrete model too. If the chosen agent can enumerate
  real model IDs (e.g. `opencode models`), list those instead of guessing;
  a contrasting family matters more than any particular model within it.
  Agents with `blocked: true` in the memory never appear in this question —
  the user already ruled them out (see "Blocked agents" below).

The result's `method` is one of:

- **subprocess** — a ready command. If it carries a `model_pinning` note, the
  agent selects its model via its own config rather than a flag, so pin the
  critic model there first.
- **in_session** — switch the live session with `/model` (host fallback); switch
  back afterwards.
- **discover** — no verified one-shot command for the chosen agent yet. The
  result includes `discover_with` (e.g. `agy --help`) and instructions: run that
  help command, find the non-interactive flag, write it into
  `agents.<key>.subprocess_command`, set `agents.<key>.verified: true`, then
  re-run `plan`. This is a one-time cost per agent — once verified, future runs
  use it directly.
- **none** — nothing installed can contrast. Fall back to self-critique and
  label it as such.

If `model_resolved` is `family-only`, no concrete contrasting model is recorded
for that agent yet — pick a real model from `critic_family`, add it to that
agent's `available_models`, and re-run.

### 4. Smoke-test the critic before the real critique

Setup failures are cheap to catch with a tiny message and expensive to discover
after composing a full critique prompt: an auth problem, a missing payment
method, an unknown model ID, or a wrong flag all fail the same way on a
one-line prompt as on the real one. Announce to the user that you are
verifying the critic setup, then send a trivial prompt through the **exact**
command you intend to use for the critique:

```bash
# example for opencode
opencode run --model <critic-model> "Reply with the single word OK."
```

- **It responds** → the door works. Record it in `agents.json`: set
  `agents.<key>.verified: true` and add the model (with its family) to that
  agent's `available_models`, so future runs skip discovery and trust this
  invocation.
- **It fails** → report the actual error to the user, then either fix the
  invocation (re-check flags with the agent's `help_command`) or go back to
  step 3 and ask the user to pick another agent or model. Do not silently
  switch critics — the choice belongs to the user.

### 5. Run the critique

Hand the critic the **work in context** (plan, diff, design notes, tests) plus
the original goal, and ask for a critique using `references/critique-rubric.md`.
The critic finds problems and recommends fixes; it does not edit.

**Deliver the prompt from a file.** Write the full critique prompt to a temp
file and fill `{prompt}` with `"$(cat <file>)"` — or the agent's stdin/file
flag if it has one — never by pasting the raw text into the command line. A
critique payload is thousands of tokens of diff and notes: inlined, it breaks
on shell quoting and `ARG_MAX` limits, while a quoted `$(cat …)` keeps the
content from ever being parsed as shell. Clean up the temp file afterwards.

If the chosen path is **discover** or **family-only**, do that resolution step
first (run the help command, confirm the flag and a concrete model, record
them). If the method is **none**, re-read your own work adversarially through the
rubric and state clearly it's a same-model self-review, not an independent
second opinion.

### 6. Classify and report

Summarize the critique for the user — don't paste it verbatim. Group findings by
severity: **Blocking** (must fix), **Non-blocking** (should fix), **Suggestions**
(lower-priority but real). If nothing substantive was found, say so. You own the
final decision about what to act on; the critic only advises.

### 7. Record what happened

```bash
python3 scripts/rubber_duck.py record \
  --session-model "<current-model-id>" \
  --critic-agent "<critic-agent-key>" \
  --critic-model "<critic-model-id>" \
  --outcome "blocking|non-blocking|suggestions|none"
```

This updates the last-used critic agent and model and appends to history, so the
next critique rotates critics, remembers which model you were on (including
across a mid-session `/model` switch), and reuses the verified invocations
you've already confirmed.

## The memory file: agents.json

`<config-root>/.webreactiva/rubber-duck/agents.json` holds **multiple agent configs**, not
just one. Top-level: `host_agent`, `config_root`, `session_model`, a `critic`
block (`last_used_agent`, `last_used_model`, `preferred_family`), and `history`.
The `agents` map has one entry per known agent with: `installed`, `binary`,
`binary_path`, `config_root`, `families`, `multi_provider`, `help_command`,
`subprocess_command`, `in_session_command`, `verified`, `blocked`,
`available_models`, and `notes`. Entries in `available_models` are dicts —
`{"id": "<model-id>", "family": "<family>"}` — so the script can match a
contrasting family; bare id strings are tolerated (family inferred from the
id), but write the dict form.

**Blocked agents.** `blocked: true` records a standing user decision: never
use that agent as a critic. The ranking skips it, it is never offered in the
step-3 question, and even explicit arguments are refused until it's unblocked
— a stored "don't use claude for critiques" should survive a forgetful later
invocation. Blocking only affects the *critic* role; a blocked agent can still
be the host. When the user says to stop (or resume) using an agent, run:

```bash
python3 scripts/rubber_duck.py block claude-code    # or: unblock claude-code
```

The host agent fills in what only it can know — concrete model IDs in
`available_models`, and verified commands after running each agent's
`help_command`. If a host has its own model config or memory, prefer reading
concrete model IDs from there and mirroring them into `available_models`.

## Reference files

- `references/agents.md` — per-agent detection markers, binaries, config roots,
  families, and known (unverified) invocations, including how to verify each via
  its help command.
- `references/critique-rubric.md` — the critic prompt template and severity
  classification to apply.
