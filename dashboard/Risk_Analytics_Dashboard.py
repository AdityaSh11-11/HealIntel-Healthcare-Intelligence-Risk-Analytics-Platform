import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text

from database import get_engine
from ml.predict import predict_patient_risk

engine = get_engine()


# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data(ttl=60)
def load_patients():
    query = """
    SELECT
        fp.patient_id,
        fp.patient_name,
        fp.age,
        fp.gender,
        fp.blood_type,
        fp.medical_condition,
        fp.billing_amount,
        fp.length_of_stay,
        fp.admission_type,
        fp.test_results,
        dh.hospital_name
    FROM fact_patients fp
    JOIN dim_hospital dh
        ON fp.hospital_id = dh.hospital_id
    ORDER BY fp.patient_id DESC
    """
    return pd.read_sql(query, engine)


@st.cache_data(ttl=60)
def prediction_history():
    query = """
    SELECT
        rp.prediction_date,
        fp.patient_name,
        dh.hospital_name,
        rp.risk_score,
        rp.risk_category,
        rp.prediction_confidence
    FROM risk_predictions rp
    JOIN fact_patients fp
        ON rp.patient_id = fp.patient_id
    JOIN dim_hospital dh
        ON fp.hospital_id = dh.hospital_id
    ORDER BY rp.prediction_date DESC
    LIMIT 50
    """
    return pd.read_sql(query, engine)


# ==========================================================
# RISK COLOR
# ==========================================================

def risk_color(score):
    if score >= 85:
        return "#DC2626"
    elif score >= 65:
        return "#EA580C"
    elif score >= 35:
        return "#EAB308"
    return "#16A34A"


# ==========================================================
# GAUGE CHART
# ==========================================================

def risk_gauge(score):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 34}},
            title={"text": "Patient Risk Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": risk_color(score)},
                "steps": [
                    {"range": [0, 35], "color": "#DCFCE7"},
                    {"range": [35, 65], "color": "#FEF9C3"},
                    {"range": [65, 85], "color": "#FED7AA"},
                    {"range": [85, 100], "color": "#FECACA"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "value": score,
                },
            },
        )
    )

    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    return fig


# ==========================================================
# MAIN DASHBOARD
# ==========================================================

def risk_dashboard():

    st.title("AI Patient Risk Prediction Center")
    st.caption("Random Forest + PostgreSQL + Healthcare Intelligence Platform")

    df = load_patients()

    # -------------------------------------------------------
    # PATIENT SELECTION
    # -------------------------------------------------------

    patient = st.selectbox(
        "Select Patient",
        df["patient_name"].tolist(),
    )

    row = df[df.patient_name == patient].iloc[0]

    patient_data = {
        "age": row.age,
        "gender": row.gender,
        "blood_type": row.blood_type,
        "medical_condition": row.medical_condition,
        "billing_amount": row.billing_amount,
        "length_of_stay": row.length_of_stay,
        "admission_type": row.admission_type,
        "test_results": row.test_results,
    }

    prediction = predict_patient_risk(patient_data)

    if isinstance(prediction, dict):
        score = float(prediction.get("score", 0.0))
        category = prediction.get("category", "Low Risk")
        confidence = float(prediction.get("confidence", score))
    elif isinstance(prediction, (list, tuple)) and len(prediction) > 0:
        values = list(prediction)
        if len(values) >= 3:
            score, category, confidence = values[:3]
        elif len(values) >= 2:
            score, category = values[:2]
            confidence = score
        else:
            score = float(values[0])
            category = "Low Risk"
            confidence = float(score)
    else:
        score = 0.0
        category = "Low Risk"
        confidence = 0.0

    score = float(score)
    confidence = float(confidence)

    if score >= 85:
        category = "Critical Risk"
    elif score >= 65:
        category = "High Risk"
    elif score >= 35:
        category = "Moderate Risk"
    else:
        category = "Low Risk"

    # -------------------------------------------------------
    # KPI CARDS
    # -------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Risk Score", f"{score:.1f}%")
    c2.metric("Risk Category", category)
    c3.metric("Confidence", f"{confidence:.1f}%")
    c4.metric("Hospital", row.hospital_name)

    st.divider()

    # -------------------------------------------------------
    # GAUGE + DONUT
    # -------------------------------------------------------

    left, right = st.columns([1.2, 1])

    with left:
        st.plotly_chart(
            risk_gauge(score),
            use_container_width=True,
        )

    with right:

        donut = px.pie(
            values=[score, 100 - score],
            names=["Risk", "Safe"],
            hole=0.75,
        )

        donut.update_traces(textinfo="none")
        donut.update_layout(
            title="Risk Distribution",
            height=320,
            showlegend=True,
        )

        st.plotly_chart(donut, use_container_width=True)

    st.divider()

    # -------------------------------------------------------
    # PATIENT SUMMARY
    # -------------------------------------------------------

    st.subheader("Patient Clinical Summary")

    summary = pd.DataFrame(
        {
            "Clinical Feature": patient_data.keys(),
            "Patient Value": patient_data.values(),
        }
    )

    st.dataframe(summary, use_container_width=True, hide_index=True)

    # -------------------------------------------------------
    # CLINICAL INTERPRETATION
    # -------------------------------------------------------

    st.subheader("AI Clinical Interpretation")

    if category == "Critical Risk":
        st.error(
            "This patient shows a very high probability of severe clinical deterioration. Immediate physician review and continuous monitoring are recommended."
        )

    elif category == "High Risk":
        st.warning(
            "Patient has elevated clinical risk and should receive priority monitoring and follow-up care."
        )

    elif category == "Moderate Risk":
        st.info(
            "Patient has moderate clinical risk. Regular monitoring and preventive intervention are advised."
        )

    else:
        st.success(
            "Patient currently falls into the low-risk category with no immediate high-risk indicators."
        )

    st.divider()

    # -------------------------------------------------------
    # SAVE PREDICTION
    # -------------------------------------------------------

    st.subheader("Save Prediction to PostgreSQL")

    if st.button("Save Prediction", use_container_width=True):

        insert_query = text(
            """
            INSERT INTO risk_predictions
            (
                patient_id,
                risk_score,
                risk_category,
                prediction_confidence,
                model_version
            )
            VALUES
            (
                :patient_id,
                :risk_score,
                :risk_category,
                :prediction_confidence,
                :model_version
            )
            """
        )

        with engine.begin() as conn:
            conn.execute(
                insert_query,
                {
                    "patient_id": int(row.patient_id),
                    "risk_score": float(score),
                    "risk_category": category,
                    "prediction_confidence": float(confidence),
                    "model_version": "Random Forest v2.0",
                },
            )

        st.success("Prediction saved successfully.")

        st.cache_data.clear()

    st.divider()

    # -------------------------------------------------------
    # PREDICTION HISTORY
    # -------------------------------------------------------

    st.subheader("Recent AI Predictions")

    history = prediction_history()

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------------
    # CATEGORY DISTRIBUTION
    # -------------------------------------------------------

    st.subheader("Risk Category Distribution")

    category_chart = (
        history.groupby("risk_category")
        .size()
        .reset_index(name="Patients")
    )

    fig = px.bar(
        category_chart,
        x="risk_category",
        y="Patients",
        color="risk_category",
        text="Patients",
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------------------------------------
    # HIGH RISK PATIENTS
    # -------------------------------------------------------

    st.subheader("High & Critical Risk Patients")

    high_risk = history[
        history["risk_score"] >= 65
    ].sort_values("risk_score", ascending=False)

    st.dataframe(
        high_risk,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------------
    # DOWNLOAD CSV
    # -------------------------------------------------------

    st.download_button(
        "Download Prediction History",
        history.to_csv(index=False).encode("utf-8"),
        file_name="risk_prediction_history.csv",
        mime="text/csv",
        use_container_width=True,
    )