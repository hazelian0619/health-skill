"""Evaluation runner for health-agent-skill with LLM judge."""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from health_agent_skill.llm_client import get_llm_client
from health_agent_skill.skill import personalized_advice_entry

load_dotenv(ROOT / ".env", override=True)

TIMEOUT_PER_CASE = 30


@dataclass
class CaseResult:
    case_id: str
    category: str
    score: float
    passed: bool
    latency_ms: float
    decision_layer: str
    output: str
    notes: list[str]


def _map_tcm(value: str | None) -> str:
    if not value:
        return "balanced"
    lowered = value.replace(" ", "")
    mapping = {
        "脾虚湿困": "phlegm_damp",
        "气血不足": "qi_deficiency",
        "肝肾不足": "yin_deficiency",
        "阳虚": "yang_deficiency",
        "肝郁": "qi_stagnation",
        "阴虚": "yin_deficiency",
    }
    for key, mapped in mapping.items():
        if key in lowered:
            return mapped
    return "balanced"


def _build_profile(raw: dict) -> dict:
    profile = {
        "static": {
            "age": raw.get("age", 0),
            "sex": raw.get("gender", "unspecified"),
            "height_cm": raw.get("height"),
            "weight_kg": raw.get("weight"),
            "medical_history": raw.get("medical_history", []),
            "training_forbidden": raw.get("training_forbidden", []),
            "tcm_constitution": _map_tcm(raw.get("tcm_constitution")),
            "location": raw.get("location"),
            "surgeries": [
                {
                    "name": item,
                    "date": "2000-01-01",
                    "notes": "date unknown",
                }
                for item in raw.get("medical_history", [])
            ],
        },
        "dynamic": {"goals": [], "activity_level": "light"},
        "realtime": {"pain_scale": 0, "steps_today": 0},
    }
    return profile


def _extract_json(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _judge_with_llm(case: dict, advice: str) -> tuple[float, list[str]]:
    llm = get_llm_client()
    expected = case.get("expected", {})
    prompt = (
        "你是评测裁判。根据expected与model_output，给出0-1评分。"
        "请严格输出JSON对象，字段只有 score 与 notes。\n\n"
        f"expected={json.dumps(expected, ensure_ascii=False)}\n"
        f"model_output={advice}\n"
        '输出JSON：{"score": 0.0-1.0, "notes": ["..."]}'
    )
    response = llm.call(prompt, system="你是严格评测裁判。只输出JSON对象。", temperature=0.0)
    parsed = _extract_json(response)
    if not parsed:
        return 0.0, ["judge_parse_error"]
    return float(parsed.get("score", 0.0)), list(parsed.get("notes", []))


def _heuristic_score(case: dict, advice: str) -> tuple[float, list[str]]:
    expected = case.get("expected", {})
    score = 1.0
    notes: list[str] = []
    must_contain = expected.get("must_contain", [])
    must_not_contain = expected.get("must_not_contain", [])

    if must_contain and not all(phrase in advice for phrase in must_contain):
        score -= 0.2
        notes.append("missing_must_contain")
    if must_not_contain and any(phrase in advice for phrase in must_not_contain):
        score -= 0.2
        notes.append("contains_forbidden")
    if expected.get("should_reject") and ("不建议" not in advice and "禁忌" not in advice):
        score -= 0.2
        notes.append("reject_missing")
    return max(score, 0.0), notes


def evaluate_case(case: dict) -> CaseResult:
    profile = _build_profile(case.get("user_profile", {}))
    query = case["query"]

    start = time.perf_counter()
    output = personalized_advice_entry(profile, user_query=query)
    latency_ms = (time.perf_counter() - start) * 1000

    advice = output.get("advice", "")
    decision_layer = output.get("decision_layer", "unknown")
    heuristic_score, heuristic_notes = _heuristic_score(case, advice)
    score, notes = _judge_with_llm(case, advice)
    score = (heuristic_score * 0.8) + (score * 0.2)
    notes = list(set(heuristic_notes + notes))
    passed = score >= 0.6

    return CaseResult(
        case_id=case["id"],
        category=case.get("category", "unknown"),
        score=score,
        passed=passed,
        latency_ms=latency_ms,
        decision_layer=decision_layer,
        output=advice,
        notes=notes,
    )


def run(dataset_path: Path) -> dict:
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    results: list[CaseResult] = [evaluate_case(case) for case in data]

    accuracy = sum(r.score for r in results) / max(len(results), 1)
    failures = [r for r in results if not r.passed]
    latencies = sorted([r.latency_ms for r in results])
    p95 = latencies[int(0.95 * len(latencies)) - 1] if latencies else 0.0

    layers: dict[str, int] = {}
    for result in results:
        layers[result.decision_layer] = layers.get(result.decision_layer, 0) + 1

    return {
        "results": results,
        "accuracy": accuracy,
        "failures": failures,
        "p95_latency_ms": p95,
        "layers": layers,
    }


def main() -> None:
    dataset = Path(__file__).parent / "golden_dataset.json"
    report = run(dataset)
    print(f"Accuracy: {report['accuracy']:.3f}")
    print(f"P95 latency: {report['p95_latency_ms']:.2f} ms")
    print(f"Failures: {len(report['failures'])}")
    print("Decision layers:", report["layers"])


if __name__ == "__main__":
    main()
