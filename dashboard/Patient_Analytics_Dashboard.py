import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_engine
from components.filters import dashboard_filters

engine = get_engine()


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
        fp.medication,
        fp.billing_amount,
        fp.length_of_stay,
        fp.admission_type,
        fp.test_results,
        fp.admission_date,
        dh.hospital_name,
        dd.doctor_name,
        di.insurance_provider
    FROM fact_patients fp
    JOIN dim_hospital dh USING(hospital_id)
    JOIN dim_doctor dd USING(doctor_id)
    JOIN dim_insurance di USING(insurance_id)
    """

    return pd.read_sql(query, engine)


def patient_analytics_dashboard():

    st.title("Patient Analytics Dashboard")

    df = load_patients()

    df = dashboard_filters(df)

    # ---------------- KPI Cards ----------------

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Patients", f"{len(df):,}")

    k2.metric("Average Age", round(df.age.mean(), 1))

    k3.metric("Average Bill", f"${df.billing_amount.mean():,.0f}")

    k4.metric("Average Stay", f"{df.length_of_stay.mean():.1f} Days")

    st.divider()

    # ---------------- Search ----------------

    search = st.text_input("🔍 Search Patient")

    if search:

        df = df[
            df.patient_name.str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # ---------------- Charts ----------------

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            df,
            x="age",
            nbins=20,
            title="Age Distribution",
            color="gender"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        gender = (
            df.groupby("gender")
            .size()
            .reset_index(name="patients")
        )

        fig = px.pie(
            gender,
            names="gender",
            values="patients",
            hole=0.6,
            title="Gender Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:

        disease = (
            df.groupby("medical_condition")
            .size()
            .reset_index(name="patients")
        )

        fig = px.bar(
            disease,
            x="medical_condition",
            y="patients",
            color="patients",
            title="Medical Condition Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col4:

        blood = (
            df.groupby("blood_type")
            .size()
            .reset_index(name="patients")
        )

        fig = px.pie(
            blood,
            names="blood_type",
            values="patients",
            title="Blood Type Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)

    with col5:

        fig = px.box(
            df,
            x="medical_condition",
            y="billing_amount",
            color="medical_condition",
            title="Billing Amount by Disease"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col6:

        fig = px.violin(
            df,
            x="admission_type",
            y="length_of_stay",
            color="admission_type",
            box=True,
            title="Length of Stay by Admission Type"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Revenue by Hospital ----------------

    revenue = (
        df.groupby("hospital_name")
        .billing_amount.sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        revenue,
        x="billing_amount",
        y="hospital_name",
        orientation="h",
        title="Top 10 Hospitals by Revenue",
        color="billing_amount"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Admission Trend ----------------

    df["admission_date"] = pd.to_datetime(df["admission_date"])

    trend = (
        df.groupby(df["admission_date"].dt.to_period("M"))
        .size()
        .reset_index(name="patients")
    )

    trend["admission_date"] = trend["admission_date"].astype(str)

    fig = px.line(
        trend,
        x="admission_date",
        y="patients",
        markers=True,
        title="Monthly Admission Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Patient Table ----------------

    st.subheader("Patient Records")

    st.dataframe(
        df.sort_values("admission_date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False).encode()

    st.download_button(
        "Export Filtered Patient Data",
        csv,
        "patient_analytics.csv",
        "text/csv",
        use_container_width=True,
    )
