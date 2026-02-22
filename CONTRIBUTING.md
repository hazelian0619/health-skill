# Contributing

Thanks for contributing to health-agent-skill.

## Development Setup

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```
pytest -q
```

## Running Evals

```
python evals/eval.py
python evals/generate_report.py
```

## Code Style
- Keep functions typed and documented.
- Prefer rules-first logic over model calls.
- Avoid stateful global logic.

## Safety Review
Changes that affect safety rules must include:
- Updated tests
- Updated eval cases if behavior changes
- Notes in PR describing risk impact
