import streamlit as st

def patient_form(hospitals, doctors, insurance):

    with st.form("patient_registration", clear_on_submit=True):

        st.subheader("👤 Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("Patient Name")
            age = st.number_input("Age", 0, 120, 30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood_type = st.selectbox(
                "Blood Type",
                ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
            )

        with col2:
            medical_condition = st.selectbox(
                "Medical Condition",
                [
                    "Diabetes","Cancer","Asthma",
                    "Hypertension","Arthritis","Obesity"
                ]
            )

            medication = st.text_input("Medication")

            admission_type = st.selectbox(
                "Admission Type",
                ["Emergency","Urgent","Elective"]
            )

            test_results = st.selectbox(
                "Test Results",
                ["Normal","Abnormal","Inconclusive"]
            )

        st.divider()

        st.subheader("🏥 Hospital Information")

        hospital_name = st.selectbox(
            "Hospital",
            hospitals["hospital_name"]
        )

        doctor_name = st.selectbox(
            "Doctor",
            doctors["doctor_name"]
        )

        insurance_provider = st.selectbox(
            "Insurance Provider",
            insurance["insurance_provider"]
        )

        room_number = st.number_input(
            "Room Number",
            min_value=100,
            max_value=999,
            value=201
        )

        st.divider()

        col3, col4 = st.columns(2)

        with col3:
            admission_date = st.date_input("Admission Date")

        with col4:
            discharge_date = st.date_input("Discharge Date")

        billing_amount = st.number_input(
            "Billing Amount",
            min_value=1000.0,
            value=15000.0,
            step=500.0
        )

        submitted = st.form_submit_button(
            "Register Patient",
            use_container_width=True
        )

    return {
        "submitted": submitted,
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "blood_type": blood_type,
        "medical_condition": medical_condition,
        "medication": medication,
        "admission_type": admission_type,
        "test_results": test_results,
        "hospital_name": hospital_name,
        "doctor_name": doctor_name,
        "insurance_provider": insurance_provider,
        "room_number": room_number,
        "admission_date": admission_date,
        "discharge_date": discharge_date,
        "billing_amount": billing_amount
    }