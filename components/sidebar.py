import streamlit as st

def render_sidebar():

    st.sidebar.markdown(
        """
        # 🏥 HealthIntel Platform

        Enterprise Healthcare Analytics
        """
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Executive Command Center",
            "Patient_Registration_Page",
            "Patient_Analytics_Dashboard",
            "Hospital_Operations_System",
            "Medication_Safety_Hub",
            "Risk_Analytics_Dashboard",
            "Admin Control Panel"
        ],
    )

    st.sidebar.divider()

    st.sidebar.markdown("### Dashboard Filters")

    year = st.sidebar.selectbox(
        "Admission Year",
        ["All", "2019", "2020", "2021", "2022", "2023", "2024"],
    )

    gender = st.sidebar.multiselect(
        "Gender",
        ["Male", "Female", "Other"],
    )

    condition = st.sidebar.multiselect(
        "Medical Condition",
        [
            "Diabetes",
            "Cancer",
            "Asthma",
            "Hypertension",
            "Arthritis",
            "Obesity",
        ],
    )

    return page, year, gender, condition