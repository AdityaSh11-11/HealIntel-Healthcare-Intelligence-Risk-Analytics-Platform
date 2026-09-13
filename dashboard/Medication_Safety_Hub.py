import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_engine

engine = get_engine()


@st.cache_data(ttl=60)
def load_drug_events():

    return pd.read_sql(
        "SELECT * FROM fact_drug_events",
        engine,
    )


def medication_safety_dashboard():

    st.title("Medication Safety Dashboard")
    st.caption("Live FDA Adverse Drug Events Intelligence")

    df = load_drug_events()

    df["received_date"] = pd.to_datetime(df["received_date"])

    serious = (df["seriousness"] == 1).sum()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Drug Events", len(df))
    k2.metric("Serious Cases", serious)
    k3.metric("Unique Drugs", df["medicinal_product"].nunique())
    k4.metric("Unique Reactions", df["reaction"].nunique())

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        top_drugs = (
            df.groupby("medicinal_product")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="reports")
        )

        fig = px.bar(
            top_drugs,
            x="reports",
            y="medicinal_product",
            orientation="h",
            color="reports",
            title="Top Reported Medications",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        reactions = (
            df.groupby("reaction")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="cases")
        )

        fig = px.bar(
            reactions,
            x="cases",
            y="reaction",
            orientation="h",
            color="cases",
            title="Most Common Adverse Reactions",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:

        gender = (
            df.groupby("patient_gender")
            .size()
            .reset_index(name="patients")
        )

        fig = px.pie(
            gender,
            names="patient_gender",
            values="patients",
            hole=0.55,
            title="Patient Gender Distribution",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col4:

        fig = px.histogram(
            df,
            x="patient_age",
            nbins=20,
            title="Age Distribution of Adverse Events",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    trend = (
        df.groupby(df["received_date"].dt.to_period("M"))
        .size()
        .reset_index(name="events")
    )

    trend["received_date"] = trend["received_date"].astype(str)

    fig = px.line(
        trend,
        x="received_date",
        y="events",
        markers=True,
        title="Monthly Adverse Event Trend",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Latest FDA Reports")

    st.dataframe(
        df.sort_values("received_date", ascending=False).head(20),
        use_container_width=True,
        hide_index=True,
    )

    csv = df.to_csv(index=False).encode()

    st.download_button(
        "Download Drug Events CSV",
        csv,
        "drug_events.csv",
        "text/csv",
        use_container_width=True,
    )

    if st.button("Refresh FDA Data"):

        import subprocess

        subprocess.run(["python", "-m", "etl.fetch_openfda"])

        st.cache_data.clear()

        st.success("Latest FDA data fetched.")
