"""Simple JSON state store for session persistence."""

from __future__ import annotations

import json
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent / "state.json"


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"user_profiles": {}, "call_history": [], "custom_rules": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def save_profile(user_id: str, profile: dict) -> None:
    state = _load_state()
    state["user_profiles"][user_id] = profile
    _save_state(state)


def load_profile(user_id: str) -> dict | None:
    state = _load_state()
    return state["user_profiles"].get(user_id)


def add_rule(user_id: str, rule: dict) -> None:
    state = _load_state()
    state["custom_rules"].setdefault(user_id, []).append(rule)
    _save_state(state)


def list_rules(user_id: str) -> list[dict]:
    state = _load_state()
    return state["custom_rules"].get(user_id, [])


def record_call(entry: dict) -> None:
    state = _load_state()
    state["call_history"].append(entry)
    _save_state(state)


def stats() -> dict:
    state = _load_state()
    return {
        "profiles": len(state.get("user_profiles", {})),
        "calls": len(state.get("call_history", [])),
        "rules": sum(len(v) for v in state.get("custom_rules", {}).values()),
    }
