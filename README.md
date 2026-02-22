# health-agent-skill

A safety-first health management skill for OpenClaw agents. It prioritizes rule-based guidance and flags high-risk cases for human review (need_hitl).

## Features
- User profile validation with Pydantic v2
- TCM-style descriptive assessment (non-diagnostic)
- Nutrition assessment (low-risk guidance)
- Rehab safety checks for exercise plans
- Personalized advice orchestrator
- Rule-based safety and redline handling
- Evals harness with golden dataset

## Project Structure
```
health-agent-skill/
  health_agent_skill/
    agents/
    orchestrator.py
    profile.py
    rules.py
    safety.py
    skill.py
  evals/
    critical_cases.json
    normal_cases.json
    golden_dataset.json
    eval.py
    EVAL_REPORT.md
  demo/
    app.py
  requirements.txt
```

## Quickstart

Create a virtual environment and install dependencies:
```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Run tests:
```
pytest -q
```

Run evals:
```
python evals/eval.py
python evals/generate_report.py
```

Run Streamlit demo:
```
streamlit run demo/app.py
```

## Hybrid Decision Architecture

### Design Philosophy
**Rules protect redlines, LLM handles reasoning.**

- **Rule layer**: hard-coded medical redlines, <10ms response, 100% block
- **LLM layer**: Claude 3.5 Sonnet for complex reasoning, 3-8s response
- **Fallback layer**: API errors downgrade to safe defaults

### Prompt Engineering Highlights
1. Role definition to activate domain expertise
2. Structured user profile input (medical history, constitution, constraints)
3. Task decomposition (analyze → decide → recommend)
4. JSON-only output constraints for parsing
5. Defensive instruction (uncertain → caution)
6. Temperature tuning per task

## Safety Notes
- This skill does not provide medical diagnosis.
- High-risk inputs set need_hitl=true.
- Redline rules block unsafe training and medication advice.

## API Overview
Main entrypoint: `personalized_advice_entry` in `health_agent_skill/skill.py`.

Example:
```python
from health_agent_skill.skill import personalized_advice_entry

profile = {
    "static": {"age": 24, "sex": "female"},
    "dynamic": {"goals": ["mobility"]},
    "realtime": {"pain_scale": 2},
}

result = personalized_advice_entry(profile, user_query="我想做臀桥")
print(result["advice"])
```

## License
MIT License.
