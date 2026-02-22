"""Safety checks and escalation rules."""

from __future__ import annotations

from dataclasses import dataclass


RED_FLAG_KEYWORDS = {
    "chest pain",
    "shortness of breath",
    "fainting",
    "severe bleeding",
    "suicidal",
    "stroke",
    "heart attack",
    "uncontrolled pain",
    "sudden weakness",
    "loss of consciousness",
    "severe headache",
}


@dataclass
class RiskAssessment:
    risk_level: str
    need_hitl: bool
    reasons: list[str]


def assess_text_risk(text: str) -> RiskAssessment:
    lowered = text.lower()
    hits = [kw for kw in RED_FLAG_KEYWORDS if kw in lowered]
    if hits:
        return RiskAssessment(risk_level="high", need_hitl=True, reasons=hits)
    if not text.strip():
        return RiskAssessment(risk_level="high", need_hitl=True, reasons=["empty_input"])
    return RiskAssessment(risk_level="low", need_hitl=False, reasons=[])
