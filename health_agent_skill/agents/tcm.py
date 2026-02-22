"""TCM constitution agent (LLM-driven)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from health_agent_skill.llm_client import get_llm_client
from health_agent_skill.profile import UserProfile


@dataclass
class TcmResult:
    tcm_patterns: list[str]
    notes: str
    need_hitl: bool
    risk_level: str
    decision_layer: str


def tcm_diagnosis(profile: UserProfile, symptoms: list[str], context: str | None = None) -> TcmResult:
    llm = get_llm_client()
    prompt = build_prompt("、".join(symptoms), profile, {"context": context})
    response = llm.call(
        prompt,
        system="你是岭南中医专家，精通体质辨证和地域性调理。回答必须是JSON格式。",
        temperature=0.3,
    )

    try:
        result = json.loads(response)
        patterns = [result.get("constitution", "需要更多信息")]
        notes = "；".join(result.get("recommendations", [])) or result.get("reasoning", "")
        need_hitl = bool(result.get("need_clarification", False))
        return TcmResult(
            tcm_patterns=patterns,
            notes=notes,
            need_hitl=need_hitl,
            risk_level="caution" if need_hitl else "safe",
            decision_layer="llm",
        )
    except json.JSONDecodeError:
        return TcmResult(
            tcm_patterns=["需要更多信息"],
            notes="请描述具体症状与持续时间。",
            need_hitl=True,
            risk_level="caution",
            decision_layer="fallback",
        )


def build_prompt(symptoms: str, profile: UserProfile, context: dict) -> str:
    return f"""# 任务：中医体质辨证与调理建议

## 用户信息
- {profile.static.age}岁，{profile.static.sex}
- 已知体质：{profile.static.tcm_constitution}
- 所在地：{profile.static.location}（岭南湿热地区）

## 当前症状
"{symptoms}"

## 环境因素
- 天气/季节：{context.get('weather', '未知')}

***

## 辨证任务

### 1. 体质分析
结合症状、已知体质、地域特点分析：
- 这是"本"（根本体质）还是"标"（外部诱因）？
- 是虚是实？是寒是热？

### 2. 调理建议
- 食疗方案（结合岭南地域）
- 生活作息调整
- 汤方建议（如适用）

### 3. 置信度评估
- 如果症状模糊，列出需要澄清的问题

***

## 输出格式（JSON）

```json
{{
  "constitution": "当前体质状态",
  "confidence": 0.85,
  "recommendations": [
    "食疗：陈皮红豆祛湿",
    "作息：早睡养肝血"
  ],
  "need_clarification": false,
  "clarification_questions": [],
  "reasoning": "辨证依据"
}}
```

## 重要原则
- 岭南地区湿热常态，调理需考虑祛湿
- 如果症状严重（发烧、剧痛），建议就医
- 不要下确诊性诊断，只分析可能性
- 如果症状模糊，need_clarification设为true

输出JSON："""
