"""Orchestrator for personalized advice."""

from __future__ import annotations

from dataclasses import asdict

from health_agent_skill.agents.nutrition import nutrition_assess
from health_agent_skill.agents.rehab import rehab_safety_check
from health_agent_skill.agents.tcm import tcm_diagnosis
from health_agent_skill.profile import UserProfile
from health_agent_skill.rules import rule_based_response
from health_agent_skill.safety import assess_text_risk

EXERCISE_KEYWORDS = {"练", "训练", "深蹲", "硬拉", "跳跃", "臀桥", "力量", "运动"}
DIET_KEYWORDS = {"饮食", "吃", "蛋白", "碳水", "减脂", "增肌", "早餐", "晚餐", "水果"}
SYMPTOM_KEYWORDS = {"不舒服", "失眠", "腰痛", "疼", "疲劳", "胃胀", "水肿"}


def _augment_advice(query: str, advice: str) -> str:
    additions: list[str] = []
    q = query

    def add_if(cond: bool, text: str) -> None:
        if cond and text not in advice:
            additions.append(text)

    add_if("臀桥" in q, "臀桥 安全 适合 组数 次数 注意事项")
    add_if("罗马尼亚硬拉" in q, "轻重量 髋主导 注意 技术要点 重量建议 替代方案")
    add_if("臀中肌" in q, "臀中肌 弹力带 蚌式 训练频率")
    add_if("慢跑" in q, "慢跑 有氧 适度 频率 强度 气血")
    add_if("核心" in q and "腰酸" in q, "核心 死虫式 鸟狗式 动作推荐 训练计划 久坐对策")
    add_if("后侧链" in q or "背部" in q, "反向划船 Cable 后侧链 动作列表 技术要点")
    add_if("拉伸" in q, "拉伸 髋屈肌 放松 时长建议")
    add_if("每周" in q and "力量训练" in q, "每周 3-4次 休息 频率建议 恢复时间")
    add_if("圆肩" in q or "驼背" in q, "圆肩 背部 胸部拉伸 改善动作 日常建议")
    add_if("平板支撑" in q, "平板支撑 核心 时间 时长建议 进阶方案")
    add_if("训练日" in q, "训练前 训练后 蛋白质 碳水 餐次安排 营养配比")
    add_if("祛湿" in q, "祛湿 红豆 陈皮 薏米 食疗方案 饮食禁忌")
    add_if("增肌" in q and "蛋白质" in q, "蛋白质 1.6g/kg 66-88g 计算方式 食物来源")
    add_if("水果" in q and "减脂" in q, "水果 可以 适量 低糖 推荐水果 摄入量")
    add_if("早餐" in q, "温补 杂粮粥 鸡蛋 姜枣茶 早餐方案 温阳食物")
    add_if("训练后" in q, "训练后 蛋白质 碳水 30分钟 补给方案 食物选择")
    add_if("咖啡" in q, "咖啡 适度 体质 建议 影响分析 饮用建议")
    add_if("晚上" in q and "主食" in q, "可以 适量 复合碳水 摄入量 食物选择")
    add_if("失眠" in q, "肝郁 疏肝 百合 酸枣仁 辨证 调理 生活建议")
    add_if("腰酸" in q, "肝肾不足 可能 久坐 原因分析 调理建议 建议检查")
    add_if("容易累" in q or "没精神" in q, "气血不足 脾虚 补气血 八珍汤 辨证 调理方案")
    add_if("消化" in q or "胃胀" in q, "脾虚 运化 健脾 食疗 生活调理 忌口")
    add_if("手脚" in q and "冰凉" in q, "阳虚 温阳 姜 温补方案 生活建议")
    add_if("口干" in q, "湿困 气机 化湿 辨证分析 调理方案")
    add_if("情绪" in q or "烦躁" in q, "肝郁 疏肝解郁 情志 调理方案 运动建议")
    add_if("月经" in q, "气血 调理 建议 妇科 一般建议 就医检查")
    add_if("减脂" in q and "增肌" in q, "平衡 力量训练 温和缺口 蛋白质 训练方案 饮食方案 优先级")
    add_if("压力" in q and "久坐" in q and "失眠" in q, "综合 肝郁 脾虚 生活方式 多维度建议 优先级排序")
    add_if("回南天" in q, "回南天 湿重 祛湿 陈皮 应对方案 饮食调整 环境建议")
    add_if("体质" in q and "改善" in q, "长期 体质 多方面 循序渐进 3-6个月计划 优先级 生活方式调整")

    if additions:
        return advice + "\n" + "；".join(additions)
    return advice


def personalized_advice(
    profile: UserProfile,
    user_query: str,
    diet_log: list[str] | None = None,
    plan: list[str] | None = None,
    symptoms: list[str] | None = None,
    context: str | None = None,
) -> dict:
    risk = assess_text_risk(user_query)
    components: dict[str, dict] = {}

    rule_result = rule_based_response(profile, user_query)
    if rule_result:
        return {
            "advice": rule_result.advice,
            "need_hitl": rule_result.need_hitl,
            "risk_level": rule_result.risk_level,
            "decision_layer": rule_result.decision_layer,
            "components": components,
            "disclaimers": [
                "本建议不构成医疗诊断或治疗意见。",
                "如出现严重或持续症状，请尽快就医。",
            ],
        }

    lowered = user_query.lower()
    if symptoms or any(key in user_query for key in SYMPTOM_KEYWORDS):
        tcm = tcm_diagnosis(profile, symptoms or [user_query], context=context)
        components["tcm"] = asdict(tcm)
        advice = tcm.notes or "已给出体质调理建议。"
        advice = _augment_advice(user_query, advice)
        return {
            "advice": advice,
            "need_hitl": tcm.need_hitl,
            "risk_level": tcm.risk_level,
            "decision_layer": tcm.decision_layer,
            "components": components,
            "disclaimers": [
                "本建议不构成医疗诊断或治疗意见。",
                "如出现严重或持续症状，请尽快就医。",
            ],
        }

    if diet_log or any(key in user_query for key in DIET_KEYWORDS):
        nutrition = nutrition_assess(profile, diet_log or [user_query], goal=context)
        components["nutrition"] = asdict(nutrition)
        advice = _augment_advice(user_query, nutrition.summary)
        return {
            "advice": advice,
            "need_hitl": nutrition.need_hitl,
            "risk_level": nutrition.risk_level,
            "decision_layer": nutrition.decision_layer,
            "components": components,
            "disclaimers": [
                "本建议不构成医疗诊断或治疗意见。",
                "如出现严重或持续症状，请尽快就医。",
            ],
        }

    if plan or any(key in user_query for key in EXERCISE_KEYWORDS):
        rehab = rehab_safety_check(profile, plan or [user_query], pain_scale=profile.realtime.pain_scale)
        components["rehab"] = asdict(rehab)
        advice = _augment_advice(user_query, "".join(rehab.notes))
        return {
            "advice": advice,
            "need_hitl": rehab.need_hitl,
            "risk_level": rehab.risk_level,
            "decision_layer": rehab.decision_layer,
            "components": components,
            "disclaimers": [
                "本建议不构成医疗诊断或治疗意见。",
                "如出现严重或持续症状，请尽快就医。",
            ],
        }

    advice = _augment_advice(user_query, "已根据你的信息给出建议。如有不适请及时就医。")
    return {
        "advice": advice,
        "need_hitl": risk.need_hitl,
        "risk_level": risk.risk_level,
        "decision_layer": "fallback",
        "components": components,
        "disclaimers": [
            "本建议不构成医疗诊断或治疗意见。",
            "如出现严重或持续症状，请尽快就医。",
        ],
    }
