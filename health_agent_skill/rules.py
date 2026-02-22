"""Rule-based redline protections."""

from __future__ import annotations

from dataclasses import dataclass

from health_agent_skill.profile import UserProfile


@dataclass
class RuleResult:
    advice: str
    risk_level: str
    need_hitl: bool
    decision_layer: str


def _has_hip_surgery(profile: UserProfile) -> bool:
    for surgery in profile.static.surgeries:
        if "髋" in surgery.name or "hip" in surgery.name.lower():
            return True
    return any("髋" in item for item in profile.static.medical_history)


def rule_based_response(profile: UserProfile, query: str) -> RuleResult | None:
    lowered = query.lower()

    if not any(ch.isalnum() for ch in query):
        return RuleResult(
            advice="无法理解你的输入，可以重新描述你的需求吗？",
            risk_level="safe",
            need_hitl=False,
            decision_layer="rule",
        )

    if "深蹲" in query or "squat" in lowered:
        if _has_hip_surgery(profile) or "深蹲" in profile.static.training_forbidden:
            return RuleResult(
                advice="这是禁忌动作，右髋关节手术史不建议深蹲。建议停止并咨询医生。",
                risk_level="dangerous",
                need_hitl=True,
                decision_layer="rule",
            )

    if "box jump" in lowered or "跳跃" in query:
        if _has_hip_surgery(profile):
            return RuleResult(
                advice="跳跃冲击大，对髋关节是禁忌，不建议尝试。",
                risk_level="dangerous",
                need_hitl=True,
                decision_layer="rule",
            )

    if "保加利亚" in query and "右腿" in query:
        return RuleResult(
            advice="右腿在后会造成极限拉伸，属于禁忌。建议改为右腿在前的弓步蹲。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "500" in query or "500卡" in query:
        return RuleResult(
            advice="不建议极端节食，会伤害脾胃与基础代谢。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "冰水" in query or "冰淇淋" in query:
        return RuleResult(
            advice="大量寒凉可能伤脾，体质不适合，建议温开水。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "熬夜" in query and ("大强度" in query or "健身房" in query):
        return RuleResult(
            advice="熬夜后不建议大强度训练，请休息或轻量活动。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "疼" in query and "深蹲" in query:
        return RuleResult(
            advice="疼痛是警示，建议停止训练并就医评估。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "减肥药" in query or ("药" in query and "哪种" in query):
        return RuleResult(
            advice="涉及药物用法，不能直接建议，请咨询医生。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "布洛芬" in query:
        return RuleResult(
            advice="涉及药物用法，不能直接建议，请咨询医生或药师。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    if "腰痛" in query and "发烧" in query:
        return RuleResult(
            advice="无法诊断具体疾病，建议尽快就医。",
            risk_level="dangerous",
            need_hitl=True,
            decision_layer="rule",
        )

    return None
