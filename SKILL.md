---
user-invocable: true
disable-model-invocation: false
category: Healthcare
description: "医疗安全AI Agent - 规则兜底 + LLM推理 + 社区扩展"
version: 2.0.0
author: hazelian0619
dependencies: ["openai>=2.21.0", "pydantic>=2.0", "python-dotenv>=1.0"]
install-command: "./install.sh"
---

# Health Agent Skill v2.0

医疗垂域安全智能助手。混合决策架构：规则兜底 + LLM推理 + 降级回退。

## 1分钟上手
```
@health-agent /health-init user_id=demo age=24 sex=female medical=髋关节手术
@health-agent /health-query user_id=demo "我想练深蹲"
```

## 标准指令（5个）

### /health-init
初始化用户健康档案。

### /health-query
智能健康咨询（规则+LLM）。

### /health-stats
查看使用统计。

### /health-benchmark
快速评测（10个 cases）。

### /health-add-rule
添加自定义规则。

示例：
```
/health-add-rule user_id=demo condition=孕妇 tag=禁忌 action=仰卧起坐
```

## 安装
```
curl -sSL https://raw.githubusercontent.com/hazelian0619/health-skill/main/install.sh | bash
```

## License
MIT
