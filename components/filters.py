import streamlit as st
import pandas as pd

def dashboard_filters(df: pd.DataFrame):

    st.sidebar.markdown("## 🎯 Patient Filters")

    gender = st.sidebar.multiselect(
        "Gender",
        sorted(df["gender"].dropna().unique()),
    )

    condition = st.sidebar.multiselect(
        "Medical Condition",
        sorted(df["medical_condition"].dropna().unique()),
    )

    blood = st.sidebar.multiselect(
        "Blood Type",
        sorted(df["blood_type"].dropna().unique()),
    )

    age = st.sidebar.slider(
        "Age Range",
        int(df["age"].min()),
        int(df["age"].max()),
        (
            int(df["age"].min()),
            int(df["age"].max())
        )
    )

    if gender:
        df = df[df.gender.isin(gender)]

    if condition:
        df = df[df.medical_condition.isin(condition)]

    if blood:
        df = df[df.blood_type.isin(blood)]

    df = df[
        (df.age >= age[0]) &
        (df.age <= age[1])
    ]

    return df