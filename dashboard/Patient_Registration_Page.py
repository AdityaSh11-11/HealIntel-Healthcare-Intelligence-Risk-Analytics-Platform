import streamlit as st
import pandas as pd
from sqlalchemy import text

from database import get_engine
from dashboard.utils import clear_cache
from components.patient_form import patient_form

engine = get_engine()

@st.cache_data(ttl=60)
def load_dropdowns():

    hospitals = pd.read_sql(
        "SELECT hospital_id, hospital_name FROM dim_hospital ORDER BY hospital_name",
        engine,
    )

    doctors = pd.read_sql(
        "SELECT doctor_id, doctor_name FROM dim_doctor ORDER BY doctor_name",
        engine,
    )

    insurance = pd.read_sql(
        "SELECT insurance_id, insurance_provider FROM dim_insurance ORDER BY insurance_provider",
        engine,
    )

    return hospitals, doctors, insurance


# -----------------------------
# Dashboard
# -----------------------------
def patient_registration_dashboard():

    st.title("Patient Registration Center")
    st.caption(
        "Register a patient into the Healthcare Intelligence PostgreSQL Warehouse."
    )

    hospitals, doctors, insurance = load_dropdowns()

    # ---------- Top Summary ----------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Hospitals Available", len(hospitals))

    with col2:
        st.metric("Doctors Available", len(doctors))

    with col3:
        st.metric("Insurance Providers", len(insurance))

    st.divider()

    # ---------- Registration Form ----------
    form_data = patient_form(hospitals, doctors, insurance)

    if form_data["submitted"]:

        # Validation
        if form_data["patient_name"].strip() == "":
            st.error("Patient Name is required.")
            st.stop()

        if form_data["discharge_date"] < form_data["admission_date"]:
            st.error("Discharge Date cannot be before Admission Date.")
            st.stop()

        length_of_stay = (
            form_data["discharge_date"] - form_data["admission_date"]
        ).days

        # Lookup IDs
        hospital_match = hospitals["hospital_name"] == form_data["hospital_name"]
        doctor_match = doctors["doctor_name"] == form_data["doctor_name"]
        insurance_match = (
            insurance["insurance_provider"] == form_data["insurance_provider"]
        )

        hospital_ids = pd.Series(hospitals.loc[hospital_match, "hospital_id"])
        doctor_ids = pd.Series(doctors.loc[doctor_match, "doctor_id"])
        insurance_ids = pd.Series(insurance.loc[insurance_match, "insurance_id"])

        if hospital_ids.empty or doctor_ids.empty or insurance_ids.empty:
            st.error(
                "Selected hospital, doctor, or insurance provider could not be found."
            )
            st.stop()

        hospital_id = int(hospital_ids.iloc[0])
        doctor_id = int(doctor_ids.iloc[0])
        insurance_id = int(insurance_ids.iloc[0])

        insert_query = text(
            """
            INSERT INTO fact_patients (
                patient_name,
                age,
                gender,
                blood_type,
                medical_condition,
                medication,
                admission_type,
                test_results,
                admission_date,
                discharge_date,
                billing_amount,
                room_number,
                length_of_stay,
                hospital_id,
                doctor_id,
                insurance_id
            )
            VALUES (
                :patient_name,
                :age,
                :gender,
                :blood_type,
                :medical_condition,
                :medication,
                :admission_type,
                :test_results,
                :admission_date,
                :discharge_date,
                :billing_amount,
                :room_number,
                :length_of_stay,
                :hospital_id,
                :doctor_id,
                :insurance_id
            )
            """
        )

        with engine.begin() as conn:
            conn.execute(
                insert_query,
                {
                    "patient_name": form_data["patient_name"].title(),
                    "age": int(form_data["age"]),
                    "gender": form_data["gender"],
                    "blood_type": form_data["blood_type"],
                    "medical_condition": form_data["medical_condition"],
                    "medication": form_data["medication"].title(),
                    "admission_type": form_data["admission_type"],
                    "test_results": form_data["test_results"],
                    "admission_date": form_data["admission_date"],
                    "discharge_date": form_data["discharge_date"],
                    "billing_amount": float(form_data["billing_amount"]),
                    "room_number": int(form_data["room_number"]),
                    "length_of_stay": length_of_stay,
                    "hospital_id": hospital_id,
                    "doctor_id": doctor_id,
                    "insurance_id": insurance_id,
                },
            )

        clear_cache()

        st.success("Patient Registered Successfully!")
        st.balloons()

    st.divider()

    # ---------- Recent Patients ----------
    st.subheader("Recently Registered Patients")

    recent_query = """
        SELECT
            fp.patient_id,
            fp.patient_name,
            fp.age,
            fp.gender,
            fp.medical_condition,
            dh.hospital_name,
            dd.doctor_name,
            fp.admission_date,
            fp.billing_amount
        FROM fact_patients fp
        JOIN dim_hospital dh
            ON fp.hospital_id = dh.hospital_id
        JOIN dim_doctor dd
            ON fp.doctor_id = dd.doctor_id
        ORDER BY fp.patient_id DESC
        LIMIT 10;
    """

    recent_patients = pd.read_sql(recent_query, engine)

    st.dataframe(
        recent_patients,
        use_container_width=True,
        hide_index=True,
    )

    # ---------- Download ----------
    csv = recent_patients.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Recent Patients CSV",
        csv,
        "recent_patients.csv",
        "text/csv",
        use_container_width=True,
    )
