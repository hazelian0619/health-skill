from health_agent_skill.skill import health_init, health_query, health_stats, health_add_rule


def test_init_and_query():
    profile = {
        "static": {"age": 24, "sex": "female"},
        "dynamic": {},
        "realtime": {},
    }
    assert health_init("demo", profile)["status"] == "ok"
    resp = health_query("demo", "我想练深蹲")
    assert "advice" in resp


def test_stats_and_rules():
    health_add_rule("demo", "孕妇", "禁忌", "仰卧起坐")
    stats = health_stats()
    assert "calls" in stats
