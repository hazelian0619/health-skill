# health-agent-skill

医疗垂域安全智能助手（OpenClaw Skill）。混合决策架构：规则兜底 + LLM 推理 + 降级回退。

## 1 分钟上手
```
@health-agent /health-init user_id=demo age=24 sex=female medical=髋关节手术
@health-agent /health-query user_id=demo "我想练深蹲"
```

## 指标（最新）
- Accuracy: 0.838
- Safety: 10/10（红线拦截）
- P95 latency: 11.5s

## 核心能力
- 红线规则兜底（医疗禁忌 100% 拦截）
- LLM 推理（复杂场景智能建议）
- 降级回退（API 异常仍可用）
- 评测闭环（LLM judge + heuristic）

## 目录结构
```
health-agent-skill/
  SKILL.md
  install.sh
  requirements.txt
  health_agent_skill/
  docs/
  evals/
  tests/
```

## 标准指令（5 个）
- /health-init
- /health-query
- /health-stats
- /health-benchmark
- /health-add-rule

## 安装
```
curl -sSL https://raw.githubusercontent.com/hazelian0619/health-skill/main/install.sh | bash
```

## 文档
- docs/COMMUNITY_GUIDE.md
- docs/PROMPT_DESIGN.md
- docs/EVAL_REPORT.md

## License
MIT
