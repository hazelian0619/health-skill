# EVAL_REPORT

## Summary (LLM-enabled)
- Accuracy (overall): 0.838
- Safety (redline pass rate): 10/10
- P95 latency: 11508.54 ms
- Decision layers: rule=11, hybrid=10, llm=16, fallback=13

## Version Comparison
| Metric | v1 Rules-only | v2 LLM-enabled | Change |
|---|---:|---:|---:|
| Accuracy | 0.928 | 0.838 | -0.090 |
| Safety | 10/10 | 10/10 | = |
| P95 latency | 0.03 ms | 11508.54 ms | +11508.51 ms |
| Decision layers | rule=100% | rule/hybrid/llm/fallback | mixed |

## Notes
- LLM is now used for reasoning; rules remain as redline guardrails.
- Fallback still appears in a subset of cases; further prompt tightening can reduce it.

## Failures (count=4)
- Remaining failures are primarily due to strict must_contain matching or judge variability.
- Next steps: add few-shot examples and expand domain-specific templates.
