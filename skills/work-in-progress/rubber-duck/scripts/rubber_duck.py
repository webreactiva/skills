#!/usr/bin/env python3
"""
rubber_duck.py — host detection, cross-agent discovery, persistent memory, and
contrast-model selection for the Rubber Duck skill.

Why this exists
---------------
The Rubber Duck pattern is only useful when the critic
runs on a DIFFERENT model family than the session, so it doesn't share the
session model's blind spots. The hard part in practice is reaching a different
model. Two doors:

  1. The host agent can switch models itself (subprocess like `claude -p`, or an
     in-session `/model` command).
  2. Some OTHER agent CLI is installed on the machine (opencode, codex, amp,
     kilo, pi, antigravity, copilot...). Even if the host is single-family
     (e.g. Claude Code = anthropic only), a second installed CLI is the door to
     a contrasting family.

This script discovers BOTH and remembers them in `agents.json` so the next run
doesn't have to rediscover. It also records, per agent, the `help_command` to
run so the host can confirm the exact non-interactive invocation and write the
verified command back.

Subcommands
-----------
  detect   Identify the host agent and scan for every known agent CLI installed.
  status   Read or initialize agents.json and print it.
  plan     Given the current session model, pick a contrasting critic across all
           installed agents and print the recommended (or to-be-verified)
           invocation.
  record   Log a critique outcome and update last-used critic agent/model.
  block    Mark an agent as never-to-be-used as a critic (user decision).
  unblock  Lift a previous block.

Design notes
------------
* Stdlib only, no network.
* Families drive contrast logic; concrete model IDs live in agents.json
  (`available_models`), supplied by the host agent, which knows what it can
  reach. The script never invents a model ID it can't justify.
* subprocess_command / in_session_command are best-known STARTING POINTS marked
  unverified. The host should run the agent's `help_command`, confirm the flags
  for the installed version, then set `verified: true` and the corrected command
  so future runs trust it.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
from pathlib import Path

SCHEMA_VERSION = 2
HOME = Path(os.path.expanduser("~"))

# --------------------------------------------------------------------------- #
# Agent registry
# --------------------------------------------------------------------------- #
# env       : env-var name fragments that signal this agent is the *host*
# bins       : executable names (first found wins for the recorded binary)
# dirs       : candidate config dirs under $HOME (first existing wins; first
#              entry is the default config root if none exist yet)
# families   : model families this agent can drive. >1 => multi-provider, i.e.
#              it can contrast against *any* session family by picking a model
#              from a different family.
# help_command       : how to discover the real non-interactive invocation
# subprocess_command : best-known one-shot form (preferred critic path). May
#                      contain {model} and {prompt}. None => must be discovered
#                      via help_command before use. Fill {prompt} from a file —
#                      "$(cat <file>)" or the agent's stdin/file flag — never by
#                      pasting raw prompt text into the shell (quoting breakage,
#                      ARG_MAX limits).
# in_session_command : slash command to switch the live session (host fallback)
# legacy     : deprecated; kept for detection only
# notes      : guidance carried into agents.json
AGENT_REGISTRY = {
    "claude-code": {
        "env": ["CLAUDECODE", "CLAUDE_CODE"],
        "bins": ["claude"],
        "dirs": [".claude"],
        "families": ["anthropic"],
        "help_command": "claude --help",
        "subprocess_command": "claude -p --model {model} {prompt}",
        "in_session_command": "/model {model}",
        "notes": "Single-family (anthropic). As a Claude-session HOST it cannot "
                 "contrast against itself; use another installed agent as critic.",
    },
    "copilot-cli": {
        "env": ["COPILOT_", "GH_COPILOT", "GITHUB_COPILOT"],
        "bins": ["copilot"],
        "dirs": [".config/copilot", ".copilot"],
        "families": ["openai", "anthropic"],
        "help_command": "copilot --help",
        "subprocess_command": "copilot -p {prompt} --model {model}",
        "in_session_command": "/model {model}",
        "notes": "Multi-provider; routes GPT and Claude families, so it can "
                 "contrast against either an anthropic or an openai session.",
    },
    "opencode": {
        "env": ["OPENCODE"],
        "bins": ["opencode"],
        "dirs": [".config/opencode", ".opencode"],
        "families": ["anthropic", "openai", "google", "xai", "deepseek"],
        "help_command": "opencode --help",
        "subprocess_command": "opencode run --model {model} {prompt}",
        "in_session_command": "/model {model}",
        "notes": "Provider-agnostic. Model IDs are usually provider/model form; "
                 "record each in available_models as "
                 "{\"id\": \"provider/model\", \"family\": \"...\"}.",
    },
    "codex": {
        "env": ["CODEX_"],
        "bins": ["codex"],
        "dirs": [".codex"],
        "families": ["openai"],
        "help_command": "codex --help",
        "subprocess_command": "codex exec -m {model} {prompt}",
        "in_session_command": None,
        "notes": "Use the non-interactive `exec` form. Single-family (openai).",
    },
    "antigravity": {
        "env": ["ANTIGRAVITY", "AGY_"],
        "bins": ["agy"],
        "dirs": [".antigravity", ".config/antigravity"],
        "families": ["google", "anthropic"],
        "help_command": "agy --help",
        "subprocess_command": None,  # TUI-first; confirm one-shot flags via help
        # /goal runs a prompt — it does NOT switch the model, so it must not be
        # offered as an in-session model-switch path (that would yield a
        # same-model self-review disguised as an independent opinion).
        "in_session_command": None,
        "notes": "Successor to Gemini CLI (binary `agy`). Default Gemini family, "
                 "optional Claude/OSS backends. One-shot flags evolving — run "
                 "`agy --help` to confirm, then record subprocess_command.",
    },
    "amp": {
        "env": ["AMP_API_KEY", "AMP_"],
        "bins": ["amp"],
        "dirs": [".config/amp"],
        "families": ["anthropic", "openai", "google"],
        "help_command": "amp --help",
        "subprocess_command": "amp -x {prompt}",
        "in_session_command": None,
        "notes": "Sourcegraph Amp. `amp -x` is non-interactive (consumes paid "
                 "credits; Free is interactive-only). Model is chosen via amp "
                 "settings/palette rather than a flag — pin the critic family in "
                 "~/.config/amp/settings.json or via AMP_* env, then verify.",
    },
    "kilo": {
        "env": ["KILO_", "KILOCODE"],
        "bins": ["kilo", "kilocode"],
        "dirs": [".kilo", ".config/kilo", ".config/kilocode"],
        "families": ["anthropic", "openai", "google", "xai", "deepseek", "qwen"],
        "help_command": "kilo --help",
        "subprocess_command": "kilo run --auto {prompt} --json",
        "in_session_command": None,
        "notes": "Kilo Code: 500+ models / 60+ providers, so it can contrast any "
                 "session family. Set the critic model via `kilo config`/`/connect`; "
                 "confirm the model flag with `kilo --help`.",
    },
    "pi": {
        "env": ["PI_", "PI_CODING_AGENT"],
        "bins": ["pi"],
        "dirs": [".pi", ".config/pi"],
        "families": ["anthropic", "openai", "google", "xai", "deepseek", "mistral", "groq"],
        "help_command": "pi --help",
        "subprocess_command": None,  # interactive-first; confirm one-shot via help
        "in_session_command": None,
        "notes": "earendil-works/pi. BYOK across 20+ providers, so a strong "
                 "multi-family critic. Primarily an interactive TUI — run "
                 "`pi --help` to find a one-shot/print mode, then record it.",
    },
    "cursor": {
        "env": ["CURSOR_"],
        "bins": ["cursor-agent"],
        "dirs": [".cursor"],
        "families": ["anthropic", "openai"],
        "help_command": "cursor-agent --help",
        "subprocess_command": None,
        "in_session_command": None,
        "notes": "No reliable programmatic one-shot critic path. Prefer another "
                 "installed CLI; otherwise fall back to self-critique.",
    },
    "gemini-cli": {
        "env": ["GEMINI_", "GOOGLE_GENAI"],
        "bins": ["gemini"],
        "dirs": [".gemini"],
        "families": ["google"],
        "help_command": "gemini --help",
        "subprocess_command": "gemini -m {model} -p {prompt}",
        "in_session_command": "/model {model}",
        "legacy": True,
        "notes": "DEPRECATED — being retired in favor of Antigravity (`agy`). "
                 "Still usable as a google-family critic until it disappears.",
    },
}

# Preferred contrast order per session family (critic family must differ).
CONTRAST_ORDER = {
    "anthropic": ["openai", "google", "xai", "deepseek"],
    "openai": ["anthropic", "google", "xai", "deepseek"],
    "google": ["anthropic", "openai", "xai", "deepseek"],
    "xai": ["anthropic", "openai", "google"],
    "deepseek": ["anthropic", "openai", "google"],
    "meta": ["anthropic", "openai", "google"],
    "mistral": ["anthropic", "openai", "google"],
    "qwen": ["anthropic", "openai", "google"],
    "groq": ["anthropic", "openai", "google"],
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def config_root_for(agent: str) -> Path:
    spec = AGENT_REGISTRY.get(agent)
    if spec:
        for d in spec["dirs"]:
            if (HOME / d).is_dir():
                return HOME / d
        return HOME / spec["dirs"][0]
    return HOME / ".config" / "rubber-duck"


def scan_installed() -> dict:
    """Build the per-agent registry entry for every known agent, marking which
    are installed (config dir present and/or a binary on PATH)."""
    agents: dict[str, dict] = {}
    for key, spec in AGENT_REGISTRY.items():
        binary_path = None
        binary = None
        for b in spec["bins"]:
            p = shutil.which(b)
            if p:
                binary, binary_path = b, p
                break
        dir_present = any((HOME / d).is_dir() for d in spec["dirs"])
        installed = bool(binary_path) or dir_present
        families = spec.get("families", [])
        agents[key] = {
            "installed": installed,
            "binary": binary or spec["bins"][0],
            "binary_path": binary_path,
            "config_root": str(config_root_for(key)),
            "families": families,
            "multi_provider": len([f for f in families if f]) > 1,
            "help_command": spec.get("help_command"),
            "subprocess_command": spec.get("subprocess_command"),
            "in_session_command": spec.get("in_session_command"),
            "verified": False,
            "blocked": False,
            "available_models": [],
            "legacy": spec.get("legacy", False),
            "notes": spec.get("notes", ""),
        }
    return agents


def detect_host_agent() -> dict:
    """Identify the running agent and its config root. The agents.json
    `host_agent` field, once set, overrides this guess."""
    scores: dict[str, int] = {a: 0 for a in AGENT_REGISTRY}
    signals: list[str] = []
    env_keys = list(os.environ.keys())
    for agent, spec in AGENT_REGISTRY.items():
        for frag in spec["env"]:
            if any(k.startswith(frag) or frag in k for k in env_keys):
                scores[agent] += 3
                signals.append(f"env~{frag}->{agent}")
        for d in spec["dirs"]:
            if (HOME / d).is_dir():
                scores[agent] += 2
        for b in spec["bins"]:
            if shutil.which(b):
                scores[agent] += 1
    best = max(scores, key=lambda a: scores[a])
    best_score = scores[best]
    agent = best if best_score > 0 else "unknown"
    confidence = "high" if best_score >= 4 else "medium" if best_score >= 2 else "low"
    return {
        "agent": agent,
        "config_root": str(config_root_for(agent)),
        "confidence": confidence,
        "signals": signals,
    }


def state_path(config_root: Path) -> Path:
    return Path(config_root) / ".webreactiva" / "rubber-duck" / "agents.json"


def default_state(detection: dict) -> dict:
    agent = detection["agent"]
    fam = None
    spec = AGENT_REGISTRY.get(agent)
    if spec and len(spec.get("families", [])) == 1:
        fam = spec["families"][0]
    return {
        "version": SCHEMA_VERSION,
        "host_agent": agent,
        "config_root": detection["config_root"],
        "detected_at": _now(),
        "detection_confidence": detection["confidence"],
        "session_model": {"id": None, "family": fam, "updated_at": None},
        "agents": scan_installed(),
        "critic": {
            "preferred_family": None,
            "last_used_model": None,
            "last_used_agent": None,
        },
        "history": [],
    }


def _migrate(old: dict, detection: dict) -> dict:
    """Best-effort migration from the v1 single-agent schema."""
    fresh = default_state(detection)
    fresh["history"] = old.get("history", [])
    if old.get("host_agent"):
        fresh["host_agent"] = old["host_agent"]
    if old.get("session_model"):
        fresh["session_model"] = old["session_model"]
    # carry any previously verified host command into the matching agent entry
    sw = old.get("model_switching", {})
    ha = fresh["host_agent"]
    if ha in fresh["agents"] and sw.get("verified"):
        fresh["agents"][ha].update({
            "subprocess_command": sw.get("subprocess_command") or fresh["agents"][ha]["subprocess_command"],
            "in_session_command": sw.get("in_session_command") or fresh["agents"][ha]["in_session_command"],
            "verified": True,
        })
    return fresh


def load_state(config_root: Path, detection: dict | None = None) -> dict:
    det = detection or detect_host_agent()
    p = state_path(config_root)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if data.get("version") == SCHEMA_VERSION and "agents" in data:
                return data
            return _migrate(data, det)
        except (json.JSONDecodeError, OSError):
            pass
    return default_state(det)


def save_state(config_root: Path, state: dict) -> Path:
    p = state_path(config_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


# Substring hints for inferring a model family from a model ID.
FAMILY_HINTS = {
    "anthropic": ["claude", "opus", "sonnet", "haiku"],
    "openai": ["gpt", "o1", "o3", "o4", "codex"],
    "google": ["gemini"],
    "xai": ["grok"],
    "deepseek": ["deepseek"],
    "meta": ["llama"],
    "mistral": ["mistral", "mixtral"],
    "qwen": ["qwen"],
    "groq": ["groq"],
    "moonshot": ["kimi"],
}


def _family_from_id(model_id: str) -> str | None:
    lid = model_id.lower()
    for fam, needles in FAMILY_HINTS.items():
        if any(n in lid for n in needles):
            return fam
    return None


def _normalize_models(agent_entry: dict) -> list[dict]:
    """available_models entries should be {"id", "family"} dicts, but a host
    may write bare id strings — accept both instead of crashing, and infer a
    missing family from the id."""
    out = []
    for m in agent_entry.get("available_models", []):
        if isinstance(m, str):
            m = {"id": m, "family": _family_from_id(m)}
        if isinstance(m, dict) and m.get("id"):
            if not m.get("family"):
                m = {**m, "family": _family_from_id(m["id"])}
            out.append(m)
    return out


def family_of(model_id: str | None, state: dict) -> str | None:
    if not model_id:
        return None
    for a in state.get("agents", {}).values():
        for m in _normalize_models(a):
            if m["id"] == model_id and m.get("family"):
                return m["family"]
    return _family_from_id(model_id)


def _contrast_for_agent(agent_entry: dict, session_family: str | None, last_model: str | None) -> dict | None:
    """Best contrasting (family, concrete-model-or-None) this agent can offer,
    or None if it can't contrast the session family."""
    fams = [f for f in agent_entry.get("families", []) if f]
    contrasting = [f for f in fams if f != session_family] if session_family else fams
    if not contrasting:
        return None
    order = CONTRAST_ORDER.get(session_family or "", contrasting)
    contrasting.sort(key=lambda f: order.index(f) if f in order else 99)
    target = contrasting[0]
    avail = [m["id"] for m in _normalize_models(agent_entry) if m.get("family") == target]
    fresh = [m for m in avail if m != last_model] or avail
    return {"family": target, "model": fresh[0] if fresh else None}


def _selection_result(key: str, a: dict, contrast: dict, host: str | None,
                      sess_fam: str | None, alternatives: list[str],
                      warning: str | None = None) -> dict:
    """Build the selection payload for one chosen agent + contrast."""
    model = contrast.get("model")
    needs_discovery = not a.get("subprocess_command")
    method = "in_session" if (key == host and needs_discovery and a.get("in_session_command")) else \
             ("discover" if needs_discovery else "subprocess")

    invocation = {}
    if method == "subprocess":
        cmd = a["subprocess_command"]
        invocation["subprocess"] = (
            cmd.replace("{model}", model or "<critic-model>")
               .replace("{prompt}", '"$(cat <critique-prompt-file>)"')
        )
        if "{model}" not in cmd and model:
            invocation["model_pinning"] = (
                f"This command has no model flag; pin the critic model "
                f"'{model}' (family {contrast.get('family')}) via {key}'s own config "
                f"before running, or confirm a model flag with `{a.get('help_command')}`."
            )
    elif method == "in_session":
        invocation["in_session"] = (a.get("in_session_command") or "/model {model}").replace("{model}", model or "<critic-model>").replace("{prompt}", "<critique-prompt>")
    else:  # discover
        invocation["discover_with"] = a.get("help_command")
        invocation["instructions"] = (
            f"No verified one-shot command for '{key}' yet. Run "
            f"`{a.get('help_command')}`, find the non-interactive flag, then write "
            f"the command into agents.json (agents.{key}.subprocess_command) and set "
            f"agents.{key}.verified=true."
        )

    result = {
        "critic_agent": key,
        "is_independent_agent": key != host,
        "critic_family": contrast.get("family"),
        "critic_model": model,
        "model_resolved": "concrete" if model else "family-only",
        "session_family": sess_fam,
        "verified": a.get("verified", False),
        "method": method,
        "invocation": invocation,
        "alternatives": alternatives,
    }
    if warning:
        result["warning"] = warning
    return result


def pick_critic(session_model: str | None, state: dict,
                preferred_agent: str | None = None,
                preferred_model: str | None = None) -> dict:
    """Rank installed agents and pick the best contrasting critic.

    Priority favors: a programmatic (subprocess) path, an independent agent
    (different process/ecosystem than the host = a truer second opinion),
    multi-provider flexibility, a known concrete model, a verified command, and
    rotating away from the agent used last time.

    A preferred agent/model — the user's explicit choice — bypasses the
    ranking: the script only validates that the choice exists and actually
    contrasts the session family, attaching a `warning` when it can't confirm
    that. The decision still belongs to the user.
    """
    agents = state.get("agents", {})
    host = state.get("host_agent")
    sess_fam = family_of(session_model, state) or state.get("session_model", {}).get("family")
    last_model = state.get("critic", {}).get("last_used_model")
    last_agent = state.get("critic", {}).get("last_used_agent")

    if preferred_agent:
        a = agents.get(preferred_agent)
        if not a or not a.get("installed"):
            return {
                "method": "none",
                "reason": f"Preferred agent '{preferred_agent}' is not a known installed "
                          "agent. Run `status` to see what is installed, or fix the "
                          "entry in agents.json.",
                "session_family": sess_fam,
            }
        if a.get("blocked"):
            return {
                "method": "none",
                "reason": f"Agent '{preferred_agent}' is blocked as a critic in "
                          "agents.json (blocked: true) — a standing user decision that "
                          "explicit arguments do not override. Unblock it first with "
                          f"`rubber_duck.py unblock {preferred_agent}` if the user "
                          "really wants it.",
                "session_family": sess_fam,
            }
        warning = None
        if preferred_model:
            fam = family_of(preferred_model, state)
            contrast = {"family": fam, "model": preferred_model}
            if fam is None:
                warning = (f"Could not infer the family of '{preferred_model}' — confirm "
                           f"it differs from the session family ({sess_fam}) before "
                           "treating the critique as an independent second opinion.")
            elif sess_fam and fam == sess_fam:
                warning = (f"'{preferred_model}' is in the SAME family as the session "
                           f"({sess_fam}); this would be a same-family review, not a "
                           "contrasting second opinion.")
        else:
            contrast = _contrast_for_agent(a, sess_fam, last_model)
            if not contrast:
                contrast = {"family": None, "model": None}
                warning = (f"'{preferred_agent}' cannot reach a family different from "
                           f"the session ({sess_fam}); pick a concrete model from "
                           "another family or another agent.")
        return _selection_result(preferred_agent, a, contrast, host, sess_fam, [], warning)

    ranked = []
    for key, a in agents.items():
        if not a.get("installed"):
            continue
        if a.get("blocked"):
            continue  # the user ruled this agent out as a critic — never offer it
        if not a.get("subprocess_command") and not a.get("help_command"):
            continue  # no way to invoke it programmatically, even to discover
        contrast = _contrast_for_agent(a, sess_fam, last_model)
        if not contrast:
            continue
        score = 0
        if a.get("subprocess_command"):
            score += 4            # ready-to-run programmatic path
        elif a.get("help_command"):
            score += 1            # discoverable via help, but needs a step first
        if key != host:
            score += 3            # independent agent => true second opinion
        if a.get("verified"):
            score += 3
        if a.get("multi_provider"):
            score += 2
        if contrast["model"]:
            score += 2            # concrete contrasting model already known
        if a.get("legacy"):
            score -= 2
        if key == last_agent:
            score -= 1            # rotate critics across runs
        ranked.append((score, key, a, contrast))

    ranked.sort(key=lambda t: t[0], reverse=True)

    if not ranked:
        return {
            "method": "none",
            "reason": "No installed agent can reach a model family different "
                      "from the session. Fall back to self-critique and label it "
                      "as a same-model review, not an independent second opinion.",
            "session_family": sess_fam,
        }

    _, key, a, contrast = ranked[0]
    return _selection_result(key, a, contrast, host, sess_fam, [t[1] for t in ranked[1:4]])


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_detect(_args) -> int:
    det = detect_host_agent()
    out = {
        "host": det,
        "installed_agents": {
            k: {"installed": v["installed"], "binary_path": v["binary_path"],
                "config_root": v["config_root"], "families": v["families"],
                "legacy": v["legacy"]}
            for k, v in scan_installed().items()
        },
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def _resolve_root(args) -> tuple[Path, dict]:
    det = detect_host_agent()
    root = Path(args.config_root) if getattr(args, "config_root", None) else Path(det["config_root"])
    return root, det


def cmd_status(args) -> int:
    root, det = _resolve_root(args)
    state = load_state(root, det)
    if not state_path(root).exists():
        save_state(root, state)
        state["_note"] = f"Initialized memory at {state_path(root)}"
    state["_memory_path"] = str(state_path(root))
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def cmd_plan(args) -> int:
    root, det = _resolve_root(args)
    state = load_state(root, det)
    session_model = args.session_model or state.get("session_model", {}).get("id")
    if session_model and session_model != state.get("session_model", {}).get("id"):
        state["session_model"] = {
            "id": session_model,
            "family": family_of(session_model, state),
            "updated_at": _now(),
        }
        save_state(root, state)
    pick = pick_critic(session_model, state,
                       preferred_agent=args.preferred_agent,
                       preferred_model=args.preferred_model)
    print(json.dumps({
        "memory_path": str(state_path(root)),
        "host_agent": state.get("host_agent"),
        "session_model": session_model,
        "selection": pick,
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_record(args) -> int:
    root, det = _resolve_root(args)
    state = load_state(root, det)
    if args.session_model:
        state["session_model"] = {
            "id": args.session_model,
            "family": family_of(args.session_model, state),
            "updated_at": _now(),
        }
    crit = state.setdefault("critic", {})
    if args.critic_model:
        crit["last_used_model"] = args.critic_model
        crit["preferred_family"] = family_of(args.critic_model, state)
    if args.critic_agent:
        crit["last_used_agent"] = args.critic_agent
    state.setdefault("history", []).append({
        "at": _now(),
        "session_agent": state.get("host_agent"),
        "session_model": args.session_model or state.get("session_model", {}).get("id"),
        "critic_agent": args.critic_agent,
        "critic_model": args.critic_model,
        "outcome": args.outcome,
    })
    state["history"] = state["history"][-50:]
    p = save_state(root, state)
    print(json.dumps({"recorded": True, "memory_path": str(p)}, indent=2, ensure_ascii=False))
    return 0


def cmd_block(args) -> int:
    root, det = _resolve_root(args)
    state = load_state(root, det)
    key = args.agent
    if key not in state.get("agents", {}):
        print(json.dumps({
            "error": f"Unknown agent '{key}'.",
            "known_agents": sorted(state.get("agents", {})),
        }, indent=2, ensure_ascii=False))
        return 1
    state["agents"][key]["blocked"] = args.blocked
    p = save_state(root, state)
    print(json.dumps({
        "agent": key,
        "blocked": args.blocked,
        "memory_path": str(p),
    }, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rubber Duck host/cross-agent plumbing.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("detect", help="Identify host agent and scan installed agent CLIs.")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("status", help="Show (init if needed) the agents.json memory.")
    p.add_argument("--config-root", default=None)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("plan", help="Pick a contrasting critic across installed agents.")
    p.add_argument("--session-model", default=None, help="Concrete ID of the current session model.")
    p.add_argument("--preferred-agent", default=None,
                   help="User-chosen critic agent key; bypasses ranking but is still validated.")
    p.add_argument("--preferred-model", default=None,
                   help="User-chosen critic model ID (pairs with --preferred-agent).")
    p.add_argument("--config-root", default=None)
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("record", help="Log a critique outcome to history.")
    p.add_argument("--session-model", default=None)
    p.add_argument("--critic-agent", default=None)
    p.add_argument("--critic-model", default=None)
    p.add_argument("--outcome", default=None, help="blocking|non-blocking|suggestions|none")
    p.add_argument("--config-root", default=None)
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("block", help="Never use an agent as a critic (sets agents.<key>.blocked).")
    p.add_argument("agent", help="Registry key of the agent to block (e.g. claude-code).")
    p.add_argument("--config-root", default=None)
    p.set_defaults(func=cmd_block, blocked=True)

    p = sub.add_parser("unblock", help="Allow a previously blocked agent as a critic again.")
    p.add_argument("agent", help="Registry key of the agent to unblock.")
    p.add_argument("--config-root", default=None)
    p.set_defaults(func=cmd_block, blocked=False)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
