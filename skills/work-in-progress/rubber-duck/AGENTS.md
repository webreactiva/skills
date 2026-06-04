# AGENTS.md — Rubber Duck skill (developer guide)

Development-level documentation for the `rubber-duck` webreactiva skill: how it is built, its
data model, its security properties, and how to audit and test it. This file is
**not** part of the skill's runtime — the skill only loads `SKILL.md`,
`scripts/`, and `references/`; this guide and the `tests/` directory are
developer/meta material.

> Note: `AGENTS.md` sits at the skill root, following the usual convention for
> a developer entry point. Don't confuse it with the runtime instructions the
> host agent follows — those live in `SKILL.md`.

## What the skill does

Rubber Duck gives a constructive second opinion on a plan, design, diff, or test
suite using a model from a **different family** than the one running the current
session, so the critic does not share the session model's blind spots. It
detects the host coding agent, discovers every other agent CLI installed on the
machine, works out which can reach a contrasting model family, and remembers all
of it so the next run is instant.

## Runtime file layout

```
rubber-duck/
├── SKILL.md                      # instructions the host agent follows
├── AGENTS.md                     # this file — developer guide, NOT loaded at runtime
├── scripts/
│   └── rubber_duck.py            # deterministic plumbing (detection, memory, selection)
├── references/
│   ├── agents.md                 # per-agent markers, config roots, invocations
│   └── critique-rubric.md        # critic prompt template + severity rubric
└── tests/                        # ← developer-only, NOT loaded at runtime
    ├── test_rubber_duck.py       # pytest for the pure functions
    └── audit.sh                  # one-command security/quality audit
```

## The two-layer architecture (read this before auditing)

The single most important thing to understand: **the script is inert; the risk
lives in the instructions.**

- **Layer 1 — `rubber_duck.py`.** Pure plumbing. It only: reads environment
  variable *names* (`os.environ.keys()`), looks up binaries on `PATH`
  (`shutil.which`), and reads/writes one JSON file under the config root. It does
  **not** execute subprocesses, open network sockets, or `eval`/`exec` anything.
  A linter can fully audit this layer.

- **Layer 2 — `SKILL.md`.** This tells the *host agent* to run other CLIs
  (`amp -x`, `kilo run --auto`, `claude -p`, …) to obtain the critique. Those
  commands are executed by the host agent with the user's permissions — not by
  the script. No linter sees this. You audit it by reading `SKILL.md`,
  `references/agents.md`, and the `subprocess_command` templates, and by
  inspecting each command before it runs.

## How `rubber_duck.py` is structured

- `AGENT_REGISTRY` — the source of truth for each known agent: env-var markers
  for host detection, candidate binaries, candidate config dirs, model
  `families`, the `help_command` used to confirm invocations, and the best-known
  `subprocess_command` / `in_session_command`. Adding support for a new agent is
  a single new entry here.
- `CONTRAST_ORDER` — preferred critic family per session family (the critic
  family must differ from the session family).
- `detect_host_agent()` — scores agents by env (3) > config dir (2) > binary (1)
  to guess the host. The `host_agent` field in `agents.json` overrides it.
- `scan_installed()` — builds a per-agent entry for every known agent, marking
  which are installed (binary on `PATH` and/or config dir present).
- `pick_critic()` — ranks installed agents and selects the best contrasting
  critic. Scoring favors: a programmatic subprocess path (+4) over a discoverable
  one (+1), an **independent** agent different from the host (+3, = a truer
  second opinion), a verified command (+3), multi-provider flexibility (+2), a
  known concrete model (+2); it penalizes legacy agents (−2) and the
  agent used last time (−1, to rotate critics). Returns `method` ∈
  {`subprocess`, `in_session`, `discover`, `none`}.
- `load_state` / `save_state` / `_migrate` — JSON persistence with automatic
  migration from the old v1 single-agent schema (v1 history and any verified host
  command are preserved).
- Subcommands: `detect`, `status`, `plan`, `record`.

## The memory file: `agents.json`

Path: `<config-root>/.webreactiva/rubber-duck/agents.json` (e.g.
`~/.claude/.webreactiva/rubber-duck/agents.json` for a Claude Code host).

Top-level fields: `version`, `host_agent`, `config_root`, `session_model`
(`id`/`family`), a `critic` block (`last_used_agent`, `last_used_model`,
`preferred_family`), and a bounded `history` (last 50 critiques). The `agents`
map has one entry per known agent: `installed`, `binary`, `binary_path`,
`config_root`, `families`, `multi_provider`, `help_command`,
`subprocess_command`, `in_session_command`, `verified`, `available_models`,
`legacy`, `notes`.

What only the host agent can fill in: concrete model IDs in `available_models`,
and `verified: true` + corrected commands after running each agent's
`help_command`.

## Security model

**Layer 1 is clean by construction** — verify with `tests/audit.sh` (runs
`py_compile`, `bandit`, `ruff`, `pip-audit`, and a dangerous-pattern grep). The
script writes only under the config root; confirm with a sandbox run:
`python3 scripts/rubber_duck.py status --config-root /tmp/rd-audit`.

**Layer 2 is where you must apply judgment:**

1. **Command injection.** `subprocess_command` templates contain `{prompt}`. The
   critique prompt may include your code or untrusted repo/PR content. The host
   agent must pass the prompt as an **argv argument, never interpolated into a
   shell string**. The script deliberately prints the command with a
   `<critique-prompt>` placeholder so it is inspected before substitution.
2. **Autonomous / over-permissioned flags.** `kilo run --auto` and Amp's
   `--dangerously-allow-all` execute without approval. Decide whether you want
   them; trim them in `agents.json` before setting `verified: true`.
3. **Prompt injection toward the critic.** The critic reads "the work in
   context," which may be untrusted. Mitigation by design: the critic is
   read-only. Still, never pass secrets into the critique.
4. **Cost / credits.** `amp -x` consumes paid credits. Review before wiring it.
5. **Trust model.** A skill runs with the host agent's permissions. Read
   `SKILL.md` fully — you are trusting what the agent would do following it.

## Reliability notes

- Treat every unverified `subprocess_command` as a **guess** until confirmed with
  the agent's `--help` (the skill surfaces this as the `discover` method).
- `agents.json` is **last-write-wins**; parallel/fleet sessions can clobber it.
- Detection can collide (e.g. both `~/.claude` and `~/.codex` present) — the
  `host_agent` override is authoritative.
- `status` is idempotent after first init; `plan`/`record` mutate state.

## Efficiency notes

The script is O(number of agents) — negligible. The real cost is the second
model call (latency + tokens/credits). The lever is the "when to invoke" gating
in `SKILL.md`; the `agents.json` cache avoids re-detecting and re-verifying each
run.

## How to audit and test

```bash
# From the skill root:
bash tests/audit.sh                       # security + quality, one command
python3 -m pytest tests/test_rubber_duck.py -q   # reliability of pure functions
```

## Extending: add a new agent

Add an entry to `AGENT_REGISTRY` in `scripts/rubber_duck.py` with its `env`
markers, `bins`, `dirs`, `families`, `help_command`, and best-known
`subprocess_command` (use `None` if it must be discovered via help). Add a
section to `references/agents.md`. Add a test case to `test_rubber_duck.py` if
the agent introduces new selection behavior (e.g. a new single-family contrast).

## Credits

Created by Daniel Primo in webreactiva.com