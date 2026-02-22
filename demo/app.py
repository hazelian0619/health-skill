import streamlit as st

from health_agent_skill.skill import personalized_advice_entry, user_profile_init

st.set_page_config(page_title="Health Agent Skill Demo", layout="wide")

st.title("Health Agent Skill Demo")

st.sidebar.header("User Profile")

age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=24)
sex = st.sidebar.selectbox("Sex", ["female", "male", "other", "unspecified"], index=0)
height = st.sidebar.number_input("Height (cm)", min_value=40, max_value=250, value=162)
weight = st.sidebar.number_input("Weight (kg)", min_value=2, max_value=300, value=52)

st.sidebar.subheader("Recent Surgery")
surgery_name = st.sidebar.text_input("Surgery name", "Right hip surgery")
surgery_date = st.sidebar.date_input("Surgery date")

st.sidebar.subheader("Real-time Signals")
pain_scale = st.sidebar.slider("Pain scale", min_value=0, max_value=10, value=0)
steps_today = st.sidebar.number_input("Steps today", min_value=0, value=0)

profile = {
    "static": {
        "age": age,
        "sex": sex,
        "height_cm": height,
        "weight_kg": weight,
        "surgeries": [{"name": surgery_name, "date": surgery_date.isoformat()}] if surgery_name else [],
    },
    "dynamic": {"goals": [], "activity_level": "light"},
    "realtime": {"pain_scale": pain_scale, "steps_today": steps_today},
}

st.sidebar.markdown("---")
st.sidebar.write("Profile Preview")
st.sidebar.json(profile)

st.header("Ask for advice")

user_query = st.text_input("Your question", "我想做臀桥")

col1, col2 = st.columns(2)

with col1:
    symptoms_input = st.text_area("Symptoms (one per line)", "")
with col2:
    diet_input = st.text_area("Diet log (one per line)", "")

plan_input = st.text_area("Rehab plan (one per line)", "")

symptoms = [line.strip() for line in symptoms_input.splitlines() if line.strip()]
diet_log = [line.strip() for line in diet_input.splitlines() if line.strip()]
plan = [line.strip() for line in plan_input.splitlines() if line.strip()]

if st.button("Get Advice"):
    user_profile_init(profile)
    result = personalized_advice_entry(
        profile,
        user_query=user_query,
        symptoms=symptoms or None,
        diet_log=diet_log or None,
        plan=plan or None,
        context="streamlit-demo",
    )

    st.subheader("Advice")
    st.write(result["advice"])

    st.subheader("Flags")
    st.json(
        {
            "need_hitl": result["need_hitl"],
            "risk_level": result["risk_level"],
            "decision_layer": result.get("decision_layer"),
        }
    )

    st.subheader("Decision Trace")
    st.json(result["components"])

    st.subheader("Disclaimers")
    st.json(result["disclaimers"])
