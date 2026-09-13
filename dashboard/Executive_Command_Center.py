import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_engine

engine = get_engine()


@st.cache_data(ttl=60)
def load_data():
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
    df = pd.read_sql(query, engine)
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    return df


def executive_command_center():
    st.title("Executive Command Center")
    st.caption("Real-Time Healthcare Intelligence Dashboard")

    df = load_data()

    # ---------------- Sidebar Filters ----------------
    st.sidebar.subheader("Executive Filters")

    hospitals = st.sidebar.multiselect(
        "Hospital", sorted(df["hospital_name"].unique())
    )

    diseases = st.sidebar.multiselect(
        "Medical Condition", sorted(df["medical_condition"].unique())
    )

    genders = st.sidebar.multiselect(
        "Gender", sorted(df["gender"].unique())
    )

    if hospitals:
        df = df[df["hospital_name"].isin(hospitals)]

    if diseases:
        df = df[df["medical_condition"].isin(diseases)]

    if genders:
        df = df[df["gender"].isin(genders)]

    # ---------------- KPI Cards ----------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Patients", f"{len(df):,}")
    c2.metric("Revenue", f"${df['billing_amount'].sum():,.0f}")
    c3.metric("Hospitals", df["hospital_name"].nunique())
    c4.metric("Doctors", df["doctor_name"].nunique())

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Avg Billing", f"${df['billing_amount'].mean():,.0f}")
    c6.metric("Avg Age", round(df["age"].mean(), 1))
    c7.metric("Avg Stay", f"{df['length_of_stay'].mean():.1f} Days")
    c8.metric("Insurance Providers", df["insurance_provider"].nunique())

    st.divider()

    # ---------------- Revenue Trend ----------------
    monthly = (
        df.groupby(df["admission_date"].dt.to_period("M"))["billing_amount"]
        .sum()
        .reset_index()
    )
    monthly["admission_date"] = monthly["admission_date"].astype(str)

    fig = px.area(
        monthly,
        x="admission_date",
        y="billing_amount",
        title="Monthly Revenue Trend",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- Disease Distribution ----------------
    col1, col2 = st.columns(2)

    with col1:
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
            title="Disease Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            disease,
            names="medical_condition",
            values="patients",
            hole=0.55,
            title="Disease Share",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Top Hospitals ----------------
    col3, col4 = st.columns(2)

    with col3:
        hospital = (
            df.groupby("hospital_name")["billing_amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            hospital,
            x="billing_amount",
            y="hospital_name",
            orientation="h",
            title="Top Hospitals by Revenue",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        doctor = (
            df.groupby("doctor_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="patients")
        )

        fig = px.bar(
            doctor,
            x="patients",
            y="doctor_name",
            orientation="h",
            title="Top Doctors by Patients",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    
    # ---------------- Executive Insights ----------------
    st.subheader("Executive Insights")

    top_hospital = (
        df.groupby("hospital_name")["billing_amount"]
        .sum()
        .idxmax()
    )

    top_disease = df["medical_condition"].mode()[0]

    highest_patient = df.loc[
        df["billing_amount"].idxmax(), "patient_name"
    ]

    i1, i2, i3 = st.columns(3)

    i1.success(f"Highest Revenue Hospital\n\n**{top_hospital}**")
    i2.info(f"Most Common Disease\n\n**{top_disease}**")
    i3.warning(f"Highest Billing Patient\n\n**{highest_patient}**")

    st.divider()

    # ---------------- Patient Table ----------------
    st.subheader("Latest Patient Records")

    st.dataframe(
        df.sort_values("admission_date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False).encode()

    st.download_button(
        "Export Dashboard CSV",
        csv,
        "executive_dashboard.csv",
        "text/csv",
        use_container_width=True,
    )
