"""Rehab safety agent (rules + LLM)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from health_agent_skill.llm_client import get_llm_client
from health_agent_skill.profile import UserProfile

FORBIDDEN_KEYWORDS = {
    "深蹲": ["深蹲", "squat", "蹲起"],
    "硬拉": ["硬拉", "deadlift"],
    "跳跃": ["跳", "jump", "box jump", "跳跃"],
    "保加利亚": ["保加利亚", "bulgarian"],
    "冲刺": ["冲刺", "sprint", "变向"],
}


@dataclass
class RehabResult:
    is_safe: bool
    notes: list[str]
    contraindications: list[str]
    need_hitl: bool
    risk_level: str
    decision_layer: str


def rehab_safety_check(
    profile: UserProfile,
    plan: list[str],
    pain_scale: int | None = None,
    recent_surgery_days: int | None = None,
) -> RehabResult:
    query = " ".join(plan)
    red_line = check_red_lines(query, profile)
    if red_line:
        return red_line

    llm_result = llm_analyze(query, profile)
    risk_level = llm_result.get("risk_level", "caution")
    should_reject = llm_result.get("should_reject", False)
    recommendation = llm_result.get("recommendation", "建议咨询专业教练。")
    alternatives = llm_result.get("alternatives", [])
    notes = [recommendation]
    if alternatives:
        notes.append(f"替代动作：{'、'.join(alternatives)}")

    return RehabResult(
        is_safe=not should_reject,
        notes=notes,
        contraindications=[] if not should_reject else ["llm_flag"],
        need_hitl=should_reject,
        risk_level=risk_level,
        decision_layer=llm_result.get("decision_layer", "llm"),
    )


def check_red_lines(query: str, profile: UserProfile) -> RehabResult | None:
    if not profile.static.training_forbidden:
        return None

    query_lower = query.lower()
    for forbidden_item in profile.static.training_forbidden:
        for exercise, keywords in FORBIDDEN_KEYWORDS.items():
            if any(keyword in forbidden_item for keyword in keywords):
                if any(keyword in query_lower or keyword in query for keyword in keywords):
                    notes = [
                        f"❌ 不建议：{exercise}对您有高风险，属于医疗禁忌。",
                        f"您的医疗史包含手术史，{exercise}可能对髋关节造成过度负荷。",
                        f"替代动作：{'、'.join(get_alternatives(exercise))}",
                    ]
                    return RehabResult(
                        is_safe=False,
                        notes=notes,
                        contraindications=[exercise],
                        need_hitl=True,
                        risk_level="dangerous",
                        decision_layer="rule",
                    )
    return None


def llm_analyze(query: str, profile: UserProfile) -> dict:
    llm = get_llm_client()
    prompt = build_prompt(query, profile)
    response = llm.call(
        prompt,
        system="你是专业的运动康复顾问，擅长评估运动风险并给出安全建议。",
        temperature=0.5,
    )

    try:
        result = json.loads(response)
        result["decision_layer"] = "llm"
        return result
    except json.JSONDecodeError:
        return {
            "risk_level": "caution",
            "recommendation": "建议咨询专业教练后再执行。",
            "reasoning": "分析过程中遇到不确定因素。",
            "should_reject": True,
            "decision_layer": "fallback",
        }


def build_prompt(query: str, profile: UserProfile) -> str:
    medical_str = ", ".join(profile.static.medical_history) or "无"
    forbidden_str = ", ".join(profile.static.training_forbidden) or "无"
    return f"""# 任务：运动安全性评估

## 用户档案
- 基础信息：{profile.static.age}岁，{profile.static.sex}，{profile.static.weight_kg}kg
- 医疗史：{medical_str}
- 训练禁忌：{forbidden_str}
- 体质：{profile.static.tcm_constitution}

## 用户问题
"{query}"

***

## 评估任务

### 1. 风险分析
基于用户档案，分析此动作/计划的潜在风险：
- 对手术部位有无影响？
- 对体质有无负面作用？
- 强度是否适合当前状态？

### 2. 风险分级
- **safe**：无明显风险，可以执行
- **caution**：有一定风险，需要注意技术和强度
- **dangerous**：高风险，不建议执行

### 3. 具体建议
- 如果safe/caution：给出执行要点和注意事项
- 如果dangerous：给出替代方案

### 4. 决策依据
说明你的判断理由（基于医疗史、体质等）

***

## 输出格式（严格JSON）

```json
{{
  "risk_level": "safe|caution|dangerous",
  "should_reject": false,
  "recommendation": "具体建议（50字以内）",
  "alternatives": ["替代动作1", "替代动作2"],
  "reasoning": "判断依据（30字以内）"
}}
```

## 重要原则
- 如果用户有手术史，涉及该部位的动作必须谨慎
- 如果不确定，宁可标记为caution
- 建议必须具体可操作，不要泛泛而谈
- 如果risk_level=dangerous，should_reject必须为true

现在输出JSON："""


def get_alternatives(exercise: str) -> list[str]:
    alts = {
        "深蹲": ["臀桥", "箱式深蹲（控制深度）", "腿弯举"],
        "硬拉": ["罗马尼亚硬拉（轻重量）", "臀桥", "反向划船"],
        "跳跃": ["台阶踏步", "弹力带侧行走"],
        "保加利亚": ["弓步蹲（前腿在前）", "单腿臀桥"],
    }
    return alts.get(exercise, ["咨询专业教练"])
