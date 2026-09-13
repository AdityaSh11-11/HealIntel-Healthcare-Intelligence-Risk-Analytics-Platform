import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_engine

engine = get_engine()

# -----------------------------
# Load Hospital Data
# -----------------------------
@st.cache_data(ttl=60)
def load_hospital_data():

    query = """
    SELECT
        fp.patient_id,
        fp.patient_name,
        fp.age,
        fp.gender,
        fp.medical_condition,
        fp.billing_amount,
        fp.length_of_stay,
        fp.admission_type,
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


# -----------------------------
# Dashboard
# -----------------------------
def hospital_operations_dashboard():

    st.title("Hospital Operations Dashboard")
    st.caption("Clinical Operations • Revenue • Doctors • Insurance")

    df = load_hospital_data()

    # ---------------- KPIs ----------------

    total_revenue = df["billing_amount"].sum()
    avg_bill = df["billing_amount"].mean()
    avg_stay = df["length_of_stay"].mean()

    total_hospitals = df["hospital_name"].nunique()
    total_doctors = df["doctor_name"].nunique()
    insurance_count = df["insurance_provider"].nunique()

    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)

    k1.metric("Hospitals", total_hospitals)
    k2.metric("Doctors", total_doctors)
    k3.metric("Insurance Providers", insurance_count)

    k4.metric("Total Revenue", f"${total_revenue:,.0f}")
    k5.metric("Avg Billing", f"${avg_bill:,.0f}")
    k6.metric("Avg Stay", f"{avg_stay:.1f} Days")

    st.divider()

    # ---------------- Top Hospitals ----------------

    left, right = st.columns(2)

    with left:

        hospital = (
            df.groupby("hospital_name")
            .billing_amount.sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            hospital,
            x="billing_amount",
            y="hospital_name",
            orientation="h",
            color="billing_amount",
            title="Top 10 Hospitals by Revenue",
        )

        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

    with right:

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
            color="patients",
            title="Top Doctors by Patients Treated",
        )

        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Insurance ----------------

    left, right = st.columns(2)

    with left:

        insurance = (
            df.groupby("insurance_provider")
            .billing_amount.sum()
            .reset_index()
        )

        fig = px.pie(
            insurance,
            names="insurance_provider",
            values="billing_amount",
            hole=0.55,
            title="Revenue by Insurance Provider",
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        admission = (
            df.groupby("admission_type")
            .size()
            .reset_index(name="patients")
        )

        fig = px.bar(
            admission,
            x="admission_type",
            y="patients",
            color="patients",
            title="Admission Type Distribution",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Monthly Revenue ----------------

    monthly = (
        df.groupby(df["admission_date"].dt.to_period("M"))
        .billing_amount.sum()
        .reset_index()
    )

    monthly["admission_date"] = monthly["admission_date"].astype(str)

    fig = px.line(
        monthly,
        x="admission_date",
        y="billing_amount",
        markers=True,
        title="Monthly Revenue Trend",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Heatmap ----------------

    heat = (
        df.groupby(["medical_condition", "admission_type"])
        .size()
        .reset_index(name="patients")
    )

    fig = px.density_heatmap(
        heat,
        x="admission_type",
        y="medical_condition",
        z="patients",
        color_continuous_scale="Blues",
        title="Disease vs Admission Type Heatmap",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------- Hospital Performance Table ----------------

    st.subheader("Hospital Performance Summary")

    summary = (
        df.groupby("hospital_name")
        .agg(
            Total_Patients=("patient_id", "count"),
            Revenue=("billing_amount", "sum"),
            Avg_Bill=("billing_amount", "mean"),
            Avg_Stay=("length_of_stay", "mean"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    st.dataframe(summary, use_container_width=True, hide_index=True)

    csv = summary.to_csv(index=False).encode()

    st.download_button(
        "Download Hospital Summary",
        csv,
        "hospital_summary.csv",
        "text/csv",
        use_container_width=True,
    )
