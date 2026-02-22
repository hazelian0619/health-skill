# Health Agent 社区指南

## 1分钟上手
1. `@health-agent /health-init user_id=demo age=24 sex=female`
2. `@health-agent /health-query user_id=demo "我想练深蹲"`

## 自定义规则
```
/health-add-rule user_id=demo condition=孕妇 tag=禁忌 action=仰卧起坐
```

## 贡献指南
1. 编辑 `health_agent_skill/rules.py`
2. 运行 `pytest`
3. 提交 PR（格式：feat: add rule）

## 常见问题
- 没有 API key？系统会降级到规则模式。
- 如何查看统计？使用 `/health-stats`。
