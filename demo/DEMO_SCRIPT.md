# Demo Script

## Goal
Show an end-to-end flow: profile creation → safe query → redline rejection → clarification.

## Steps
1) Start the app:
```
streamlit run demo/app.py
```

2) Profile setup:
- Age: 24
- Sex: female
- Surgery name: Right hip surgery
- Pain scale: 3

3) Query 1 (safe):
- Input: 我想做臀桥
- Expected: advice says 臀桥安全/适合

4) Query 2 (redline):
- Input: 我今天想练大重量深蹲
- Expected: 禁忌、不建议、风险提示、need_hitl=true

5) Query 3 (ambiguous):
- Input: 我不舒服
- Expected: clarifying questions

## Notes
- Point out the decision trace section.
- Highlight need_hitl and risk_level flags.
