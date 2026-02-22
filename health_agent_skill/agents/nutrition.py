"""Nutrition assessment agent (hybrid)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from health_agent_skill.llm_client import get_llm_client
from health_agent_skill.profile import UserProfile


@dataclass
class NutritionResult:
    summary: str
    suggestions: list[str]
    nutrient_gaps: list[str]
    need_hitl: bool
    risk_level: str
    decision_layer: str


def nutrition_assess(profile: UserProfile, diet_log: list[str], goal: str | None = None) -> NutritionResult:
    query = " ".join(diet_log)
    tdee = calculate_tdee(profile)
    target = calculate_target(tdee, goal or "")

    llm = get_llm_client()
    prompt = build_prompt(query, profile, tdee, target)
    response = llm.call(
        prompt,
        system="你是注册营养师，擅长运动营养和体成分管理。输出JSON格式。",
        temperature=0.5,
    )

    try:
        result = json.loads(response)
        summary = result.get("recommendation", "营养建议已生成。")
        suggestions = result.get("meal_suggestions", [])
        precautions = result.get("precautions", [])
        if precautions:
            suggestions.extend(precautions)
        return NutritionResult(
            summary=summary,
            suggestions=suggestions,
            nutrient_gaps=[],
            need_hitl=False,
            risk_level="safe",
            decision_layer="hybrid",
        )
    except json.JSONDecodeError:
        return NutritionResult(
            summary="建议咨询专业营养师。",
            suggestions=[],
            nutrient_gaps=[],
            need_hitl=True,
            risk_level="caution",
            decision_layer="fallback",
        )


def calculate_tdee(profile: UserProfile) -> int:
    if profile.static.sex == "female":
        bmr = (
            447.593
            + (9.247 * (profile.static.weight_kg or 0))
            + (3.098 * (profile.static.height_cm or 0))
            - (4.330 * profile.static.age)
        )
    else:
        bmr = (
            88.362
            + (13.397 * (profile.static.weight_kg or 0))
            + (4.799 * (profile.static.height_cm or 0))
            - (5.677 * profile.static.age)
        )
    return int(bmr * 1.55)


def calculate_target(tdee: int, goal: str) -> dict:
    if "减脂" in goal:
        deficit = 300
        p, c, f = 0.3, 0.4, 0.3
    elif "增肌" in goal:
        deficit = -200
        p, c, f = 0.35, 0.45, 0.20
    else:
        deficit = 0
        p, c, f = 0.3, 0.4, 0.3

    target = tdee - deficit
    return {
        "calories": target,
        "protein_g": int(target * p / 4),
        "carb_g": int(target * c / 4),
        "fat_g": int(target * f / 9),
    }


def build_prompt(query: str, profile: UserProfile, tdee: int, target: dict) -> str:
    return f"""# 任务：营养评估与饮食建议

## 用户信息
- {profile.static.age}岁，{profile.static.sex}，{profile.static.weight_kg}kg
- 体质：{profile.static.tcm_constitution}
- TDEE：{tdee} kcal/天

## 目标营养
- 热量：{target['calories']} kcal
- 蛋白质：{target['protein_g']}g
- 碳水：{target['carb_g']}g
- 脂肪：{target['fat_g']}g

## 用户问题
"{query}"

***

## 任务

### 1. 需求分析
分析用户的营养需求和当前问题

### 2. 饮食建议
给出具体的饮食建议（结合中医体质）

### 3. 注意事项
特殊体质需要注意的事项

***

## 输出格式（JSON）

```json
{{
  "recommendation": "核心建议（50字以内）",
  "meal_suggestions": ["早餐：...", "午餐：...", "晚餐：..."],
  "precautions": ["注意事项1", "..."],
  "reasoning": "建议依据"
}}
```

## 重要原则
- 如果是脾虚体质，需要温补，避免生冷
- 建议要具体可操作
- 考虑中医饮食宜忌

输出JSON："""
