DROP TABLE IF EXISTS patients CASCADE;

CREATE TABLE patients (

    patient_id SERIAL PRIMARY KEY,

    patient_name VARCHAR(150) NOT NULL,

    age INT CHECK (age >= 0),

    gender VARCHAR(20),

    blood_type VARCHAR(10),

    medical_condition VARCHAR(120),

    doctor VARCHAR(120),

    hospital VARCHAR(150),

    insurance_provider VARCHAR(100),

    admission_type VARCHAR(30),

    medication VARCHAR(120),

    test_results VARCHAR(30),

    admission_date DATE,

    discharge_date DATE,

    billing_amount NUMERIC(12,2),

    room_number INT,

    length_of_stay INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE INDEX idx_condition ON patients(medical_condition);
CREATE INDEX idx_hospital ON patients(hospital);
CREATE INDEX idx_admission_date ON patients(admission_date);
CREATE INDEX idx_gender ON patients(gender);