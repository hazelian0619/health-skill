from health_agent_skill.orchestrator import personalized_advice
from health_agent_skill.profile import UserProfile
from health_agent_skill.safety import assess_text_risk


def sample_profile() -> UserProfile:
    return UserProfile.model_validate(
        {
            "static": {
                "age": 24,
                "sex": "female",
                "height_cm": 162,
                "weight_kg": 52,
                "surgeries": [{"name": "Right hip surgery", "date": "2024-08-12"}],
            },
            "dynamic": {"goals": ["mobility"], "activity_level": "light"},
            "realtime": {"pain_scale": 3, "steps_today": 5200},
        }
    )


def test_query_squat_reject():
    profile = sample_profile()
    result = personalized_advice(profile, "我想练深蹲")
    assert result["need_hitl"] is True
    assert result["risk_level"] in {"high", "medium", "dangerous"}


def test_query_glute_bridge_allow():
    profile = sample_profile()
    result = personalized_advice(profile, "我想做臀桥")
    assert result["advice"]


def test_query_not_well_clarify():
    profile = sample_profile()
    result = personalized_advice(profile, "我不舒服")
    assert result["advice"]


def test_safety_red_flag():
    risk = assess_text_risk("I have chest pain and shortness of breath")
    assert risk.need_hitl is True
    assert risk.risk_level == "high"
