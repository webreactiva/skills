"""
Reliability tests for the Rubber Duck plumbing (scripts/rubber_duck.py).

These cover the deterministic, pure-ish parts that matter for correctness:
contrast selection, critic rotation, concrete-model freshness, family
inference, v1->v2 migration, status idempotency, and filesystem confinement.

Run from the skill root:
    python3 -m pytest tests/test_rubber_duck.py -q
"""

import json
import pathlib
import sys

# Import the script under test from ../scripts regardless of CWD.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import rubber_duck as rd  # noqa: E402


def _state(host="claude-code", session="claude-opus-4-x", installed=("claude-code",)):
    det = {"agent": host, "config_root": "/tmp/rd-test", "confidence": "high", "signals": []}
    s = rd.default_state(det)
    s["host_agent"] = host
    s["session_model"] = {"id": session, "family": rd.family_of(session, s), "updated_at": "x"}
    for k in s["agents"]:
        s["agents"][k]["installed"] = k in installed
    return s


# --- contrast selection -----------------------------------------------------
def test_contrast_never_matches_session_family():
    s = _state(installed=("claude-code", "amp"))
    pick = rd.pick_critic("claude-opus-4-x", s)  # anthropic session
    assert pick["critic_family"] != "anthropic"
    assert pick["is_independent_agent"] is True


def test_no_contrasting_agent_falls_back_to_self_critique():
    s = _state(installed=("claude-code",))  # only an anthropic single-family host
    pick = rd.pick_critic("claude-opus-4-x", s)
    assert pick["method"] == "none"


def test_single_family_host_uses_an_independent_cli():
    # Claude host (anthropic-only) + codex installed -> codex (openai) critic.
    s = _state(installed=("claude-code", "codex"))
    pick = rd.pick_critic("claude-opus-4-x", s)
    assert pick["critic_agent"] == "codex"
    assert pick["critic_family"] == "openai"
    assert pick["method"] == "subprocess"


# --- rotation across runs ---------------------------------------------------
def test_rotation_deprioritizes_last_used_agent():
    # Two equally strong critics; with no history amp wins (registry order),
    # but once amp was used last, kilo should be chosen instead.
    s = _state(installed=("claude-code", "amp", "kilo"))
    for k in ("amp", "kilo"):
        s["agents"][k]["verified"] = True
        s["agents"][k]["available_models"] = [{"id": "gpt-x", "family": "openai"}]
    first = rd.pick_critic("claude-opus-4-x", s)["critic_agent"]
    s["critic"]["last_used_agent"] = first
    second = rd.pick_critic("claude-opus-4-x", s)["critic_agent"]
    assert {first, second} == {"amp", "kilo"}
    assert first != second


# --- concrete model freshness ----------------------------------------------
def test_concrete_model_avoids_last_used_model():
    s = _state(installed=("claude-code", "kilo"))
    s["agents"]["kilo"]["available_models"] = [
        {"id": "gpt-a", "family": "openai"},
        {"id": "gpt-b", "family": "openai"},
    ]
    s["critic"]["last_used_model"] = "gpt-a"
    pick = rd.pick_critic("claude-opus-4-x", s)
    assert pick["critic_model"] == "gpt-b"
    assert pick["model_resolved"] == "concrete"


def test_family_only_when_no_concrete_model_known():
    s = _state(installed=("claude-code", "codex"))
    pick = rd.pick_critic("claude-opus-4-x", s)
    assert pick["model_resolved"] == "family-only"
    assert pick["critic_model"] is None


# --- discover path ----------------------------------------------------------
def test_tui_first_agent_uses_discover_method():
    # antigravity has no subprocess_command -> must be discovered via help.
    s = _state(host="codex", session="gpt-5.5", installed=("codex", "antigravity"))
    pick = rd.pick_critic("gpt-5.5", s)
    assert pick["critic_agent"] == "antigravity"
    assert pick["method"] == "discover"
    assert pick["invocation"]["discover_with"] == "agy --help"


# --- legacy deprioritization ------------------------------------------------
def test_legacy_agent_is_deprioritized():
    # gemini-cli (legacy, google) vs codex (openai); for an anthropic session
    # both contrast, but the non-legacy codex should win.
    s = _state(installed=("claude-code", "gemini-cli", "codex"))
    pick = rd.pick_critic("claude-opus-4-x", s)
    assert pick["critic_agent"] != "gemini-cli"


# --- family inference -------------------------------------------------------
def test_family_inference_from_id():
    s = _state()
    assert rd.family_of("claude-opus-4-x", s) == "anthropic"
    assert rd.family_of("gpt-5.5", s) == "openai"
    assert rd.family_of("gemini-3-pro", s) == "google"
    assert rd.family_of("grok-4", s) == "xai"
    assert rd.family_of(None, s) is None


# --- migration --------------------------------------------------------------
def test_v1_migration_preserves_history_and_verified_command(tmp_path):
    root = tmp_path / "host"
    p = rd.state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    v1 = {
        "version": 1,
        "host_agent": "claude-code",
        "session_model": {"id": "claude-opus-4-x", "family": "anthropic"},
        "model_switching": {
            "supported": True, "method": "subprocess",
            "subprocess_command": "claude -p --model {model} {prompt}",
            "in_session_command": "/model {model}", "verified": True,
        },
        "history": [{"at": "old", "outcome": "none"}],
    }
    p.write_text(json.dumps(v1), encoding="utf-8")
    det = {"agent": "claude-code", "config_root": str(root), "confidence": "high", "signals": []}
    state = rd.load_state(root, det)
    assert state["version"] == rd.SCHEMA_VERSION
    assert state["history"] == [{"at": "old", "outcome": "none"}]
    assert state["agents"]["claude-code"]["verified"] is True


# --- persistence: path + confinement + idempotency --------------------------
def test_memory_path_layout():
    assert rd.state_path(pathlib.Path("/x")) == pathlib.Path("/x/.webreactiva/rubber-duck/agents.json")


def test_save_writes_only_under_config_root(tmp_path):
    root = tmp_path / "host"
    before = set(tmp_path.rglob("*"))
    rd.save_state(root, rd.default_state(
        {"agent": "claude-code", "config_root": str(root), "confidence": "high", "signals": []}))
    written = set(tmp_path.rglob("*")) - before
    files = {p for p in written if p.is_file()}
    assert files == {rd.state_path(root)}


def test_status_is_idempotent_after_init(tmp_path):
    root = tmp_path / "host"
    det = {"agent": "claude-code", "config_root": str(root), "confidence": "high", "signals": []}
    rd.save_state(root, rd.load_state(root, det))
    first = rd.state_path(root).read_text(encoding="utf-8")
    rd.save_state(root, rd.load_state(root, det))  # re-read existing, re-save
    second = rd.state_path(root).read_text(encoding="utf-8")
    assert first == second
