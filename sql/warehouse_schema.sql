DROP TABLE IF EXISTS fact_patients CASCADE;
DROP TABLE IF EXISTS dim_hospital CASCADE;
DROP TABLE IF EXISTS dim_doctor CASCADE;
DROP TABLE IF EXISTS dim_insurance CASCADE;

-- ===========================
-- Hospital Dimension
-- ===========================
CREATE TABLE dim_hospital (
    hospital_id SERIAL PRIMARY KEY,
    hospital_name VARCHAR(150) UNIQUE NOT NULL
);

-- ===========================
-- Doctor Dimension
-- ===========================
CREATE TABLE dim_doctor (
    doctor_id SERIAL PRIMARY KEY,
    doctor_name VARCHAR(120) UNIQUE NOT NULL
);

-- ===========================
-- Insurance Dimension
-- ===========================
CREATE TABLE dim_insurance (
    insurance_id SERIAL PRIMARY KEY,
    insurance_provider VARCHAR(100) UNIQUE NOT NULL
);

-- ===========================
-- Patient Fact Table
-- ===========================
CREATE TABLE fact_patients (

    patient_id SERIAL PRIMARY KEY,

    patient_name VARCHAR(150),

    age INT,

    gender VARCHAR(20),

    blood_type VARCHAR(10),

    medical_condition VARCHAR(120),

    medication VARCHAR(120),

    admission_type VARCHAR(30),

    test_results VARCHAR(30),

    admission_date DATE,

    discharge_date DATE,

    billing_amount NUMERIC(12,2),

    room_number INT,

    length_of_stay INT,

    hospital_id INT REFERENCES dim_hospital(hospital_id),

    doctor_id INT REFERENCES dim_doctor(doctor_id),

    insurance_id INT REFERENCES dim_insurance(insurance_id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patient_condition
ON fact_patients(medical_condition);

CREATE INDEX idx_patient_admission
ON fact_patients(admission_date);

CREATE INDEX idx_patient_hospital
ON fact_patients(hospital_id);