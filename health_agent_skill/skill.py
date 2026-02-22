"""Skill entrypoints for OpenClaw integration."""

from __future__ import annotations

from dataclasses import asdict
from random import sample

from health_agent_skill.agents.nutrition import nutrition_assess
from health_agent_skill.agents.rehab import rehab_safety_check
from health_agent_skill.agents.tcm import tcm_diagnosis
from health_agent_skill.evals.eval import _heuristic_score
from health_agent_skill.orchestrator import personalized_advice as _personalized_advice
from health_agent_skill.profile import UserProfile, normalize_profile
from health_agent_skill.state_store import add_rule, load_profile, record_call, save_profile, stats


def user_profile_init(profile: dict, validate_only: bool = False) -> dict:
    parsed = UserProfile.model_validate(profile)
    normalized = normalize_profile(parsed)
    issues: list[str] = []
    if validate_only:
        issues.append("validated_only")
    return {
        "normalized_profile": normalized.model_dump(),
        "issues": issues,
    }


def tcm_diagnosis_entry(profile: dict, symptoms: list[str], context: str | None = None) -> dict:
    parsed = UserProfile.model_validate(profile)
    result = tcm_diagnosis(parsed, symptoms, context=context)
    return asdict(result)


def nutrition_assess_entry(profile: dict, diet_log: list[str], goal: str | None = None) -> dict:
    parsed = UserProfile.model_validate(profile)
    result = nutrition_assess(parsed, diet_log, goal=goal)
    return asdict(result)


def rehab_safety_check_entry(
    profile: dict,
    plan: list[str],
    pain_scale: int | None = None,
    recent_surgery_days: int | None = None,
) -> dict:
    parsed = UserProfile.model_validate(profile)
    if pain_scale is not None:
        parsed.realtime.pain_scale = pain_scale
    result = rehab_safety_check(parsed, plan, pain_scale=pain_scale, recent_surgery_days=recent_surgery_days)
    return asdict(result)


def personalized_advice_entry(
    profile: dict,
    user_query: str,
    diet_log: list[str] | None = None,
    plan: list[str] | None = None,
    symptoms: list[str] | None = None,
    context: str | None = None,
) -> dict:
    parsed = UserProfile.model_validate(profile)
    response = _personalized_advice(
        parsed,
        user_query=user_query,
        diet_log=diet_log,
        plan=plan,
        symptoms=symptoms,
        context=context,
    )
    record_call({"query": user_query, "risk_level": response.get("risk_level")})
    return response


# Slash-style command helpers

def health_init(user_id: str, profile: dict) -> dict:
    parsed = UserProfile.model_validate(profile)
    normalized = normalize_profile(parsed)
    save_profile(user_id, normalized.model_dump())
    return {"status": "ok", "user_id": user_id}


def health_query(user_id: str, message: str) -> dict:
    profile = load_profile(user_id)
    if not profile:
        return {"status": "error", "message": "profile not found"}
    return personalized_advice_entry(profile, user_query=message)


def health_stats() -> dict:
    return stats()


def health_add_rule(user_id: str, condition: str, tag: str, action: str) -> dict:
    add_rule(user_id, {"condition": condition, "tag": tag, "action": action})
    return {"status": "ok"}


def health_benchmark(limit: int = 10) -> dict:
    from pathlib import Path
    import json

    dataset = Path(__file__).resolve().parents[1] / "evals" / "golden_dataset.json"
    data = json.loads(dataset.read_text(encoding="utf-8"))
    subset = sample(data, min(limit, len(data)))
    scores = []
    for case in subset:
        profile = case.get("user_profile", {})
        profile = {
            "static": {
                "age": profile.get("age", 0),
                "sex": profile.get("gender", "unspecified"),
            },
            "dynamic": {},
            "realtime": {},
        }
        result = personalized_advice_entry(profile, user_query=case["query"])
        score, _ = _heuristic_score(case, result.get("advice", ""))
        scores.append(score)
    accuracy = sum(scores) / max(len(scores), 1)
    return {"accuracy": round(accuracy, 3), "cases": len(scores)}
