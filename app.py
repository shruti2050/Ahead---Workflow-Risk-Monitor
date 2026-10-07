import streamlit as st
import pandas as pd
import joblib


# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Ahead | Workflow Risk Monitor",
    page_icon="⚠",
    layout="wide"
)


# ==============================
# LOAD DATA + MODEL
# ==============================

@st.cache_data
def load_data():
    return pd.read_csv("data/tasks_with_risk.csv")


@st.cache_resource
def load_model():
    return joblib.load("models/risk_model.pkl")


df = load_data()
model = load_model()


# ==============================
# HEADER
# ==============================

st.title("Ahead")
st.caption("AI-Based Workflow Risk Monitor")

st.markdown(
    "Identify rising workflow risks before they turn into missed deadlines."
)

st.divider()


# ==============================
# TOP METRICS
# ==============================

total_tasks = len(df)

at_risk = len(
    df[df["risk_label"].isin(["Emerging Risk", "Critical"])]
)

critical = len(
    df[df["risk_label"] == "Critical"]
)

average_risk = df["risk_score"].mean()


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Tasks",
        total_tasks
    )

with col2:
    st.metric(
        "Average Risk",
        f"{average_risk:.0f}%"
    )

with col3:
    st.metric(
        "At-Risk Tasks",
        at_risk
    )

with col4:
    st.metric(
        "Critical Tasks",
        critical
    )


st.divider()


# ==============================
# TASK SELECTION
# ==============================

st.subheader("Task Risk Assessment")

task_id = st.selectbox(
    "Select a task",
    df["task_id"].tolist()
)

task = df[
    df["task_id"] == task_id
].iloc[0]


# ==============================
# RISK STATUS
# ==============================

risk_score = task["risk_score"]
risk_label = task["risk_label"]


if risk_label == "Critical":

    st.error(
        f"🔴 CRITICAL RISK — {risk_score:.0f}%"
    )

elif risk_label == "Emerging Risk":

    st.warning(
        f"🟠 EMERGING RISK — {risk_score:.0f}%"
    )

elif risk_label == "Watch":

    st.info(
        f"🟡 WATCH — {risk_score:.0f}%"
    )

else:

    st.success(
        f"🟢 NORMAL — {risk_score:.0f}%"
    )


# ==============================
# TASK DETAILS
# ==============================

st.subheader("Task Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Days Remaining",
        int(task["days_left"])
    )

with col2:
    st.metric(
        "Current Progress",
        f"{task['progress']:.0f}%"
    )

with col3:
    st.metric(
        "Expected Progress",
        f"{task['expected_progress']:.0f}%"
    )

with col4:
    st.metric(
        "Progress Gap",
        f"{task['progress_gap']:.0f}%"
    )


st.divider()


# ==============================
# RISK SIGNALS
# ==============================

st.subheader("Risk Signals")

col1, col2 = st.columns(2)


with col1:

    st.write("**Progress Gap**")

    st.progress(
        min(task["progress_gap"] / 50, 1.0)
    )

    st.caption(
        f"{task['progress_gap']:.1f}% behind expected progress"
    )


    st.write("**Team Workload**")

    st.progress(
        float(task["team_workload"])
    )

    st.caption(
        f"{task['team_workload'] * 100:.0f}% workload"
    )


with col2:

    st.write("**Dependencies**")

    st.progress(
        min(task["dependencies"] / 4, 1.0)
    )

    st.caption(
        f"{int(task['dependencies'])} dependencies"
    )


    st.write("**Previous Delays**")

    st.progress(
        min(task["previous_delays"] / 4, 1.0)
    )

    st.caption(
        f"{int(task['previous_delays'])} previous delays"
    )


# ==============================
# WHY IS THIS RISKY?
# ==============================

st.divider()

st.subheader("Why is this task at risk?")

reasons = []


if task["progress_gap"] > 40:

    reasons.append(
        "Progress is significantly behind the expected schedule."
    )

elif task["progress_gap"] > 20:

    reasons.append(
        "Progress is noticeably behind the expected schedule."
    )

elif task["progress_gap"] > 10:

    reasons.append(
        "Progress is slightly behind the expected schedule."
    )


if task["days_left"] <= 2:

    reasons.append(
        "The deadline is approaching rapidly."
    )

elif task["days_left"] <= 5:

    reasons.append(
        "Limited time remains to complete the task."
    )


if task["team_workload"] > 0.8:

    reasons.append(
        "Team workload is currently high."
    )

elif task["team_workload"] > 0.6:

    reasons.append(
        "Team workload is moderately high."
    )


if task["dependencies"] >= 3:

    reasons.append(
        "Multiple dependencies may create bottlenecks."
    )


if task["previous_delays"] >= 3:

    reasons.append(
        "The task has experienced repeated delays."
    )


if len(reasons) == 0:

    st.success(
        "No major risk signals detected."
    )

else:

    for reason in reasons:

        st.write(
            f"• {reason}"
        )


# ==============================
# RECOMMENDATION
# ==============================

st.subheader("Recommended Action")


if risk_label == "Critical":

    recommendation = (
        "Prioritize this task immediately. "
        "Resolve blocking dependencies and "
        "consider redistributing workload."
    )

elif risk_label == "Emerging Risk":

    recommendation = (
        "Review this task before the risk increases. "
        "Address dependencies and redistribute "
        "lower-priority work if necessary."
    )

elif risk_label == "Watch":

    recommendation = (
        "Monitor this task closely and review "
        "its progress at the next checkpoint."
    )

else:

    recommendation = (
        "The task is currently progressing within "
        "an acceptable risk range."
    )


st.info(recommendation)