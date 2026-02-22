# health-agent-skill

医疗垂域安全智能助手（OpenClaw Skill）。规则兜底 + LLM 推理 + 降级回退。

## 1 分钟上手
```
@health-agent /health-init user_id=demo age=24 sex=female medical=髋关节手术
@health-agent /health-query user_id=demo "我想练深蹲"
```

## 安装
```
curl -sSL https://raw.githubusercontent.com/hazelian0619/health-skill/main/install.sh | bash
```

## 要求
- Python 3.11+
- 有效 API Key（无 key 时自动降级为规则模式）

## 指令（5 个）
- /health-init
- /health-query
- /health-stats
- /health-benchmark
- /health-add-rule

## 示例输出
```
{"risk_level":"dangerous","need_hitl":true,"advice":"这是禁忌动作，建议停止并咨询医生。"}
```

## 指标
- Accuracy: 0.838
- Safety: 10/10（红线拦截）
- P95 latency: 11.5s

## 开发
```
pytest -q
```

## 评测报告
- docs/EVAL_REPORT.md

## License
MIT
