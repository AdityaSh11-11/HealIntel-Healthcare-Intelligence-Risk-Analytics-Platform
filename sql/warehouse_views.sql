-- Executive Patient Summary
CREATE OR REPLACE VIEW vw_patient_summary AS
SELECT
    gender,
    medical_condition,
    COUNT(*) AS total_patients,
    ROUND(AVG(age),2) AS avg_age,
    ROUND(AVG(billing_amount),2) AS avg_bill
FROM fact_patients
GROUP BY gender, medical_condition;

------------------------------------------------

-- Hospital Performance
CREATE OR REPLACE VIEW vw_hospital_performance AS
SELECT
    h.hospital_name,
    COUNT(*) AS patients,
    ROUND(AVG(f.billing_amount),2) AS revenue,
    ROUND(AVG(f.length_of_stay),2) AS avg_stay
FROM fact_patients f
JOIN dim_hospital h
ON f.hospital_id = h.hospital_id
GROUP BY h.hospital_name;

------------------------------------------------

-- Doctor Performance
CREATE OR REPLACE VIEW vw_doctor_performance AS
SELECT
    d.doctor_name,
    COUNT(*) patients_treated,
    ROUND(AVG(billing_amount),2) avg_billing
FROM fact_patients f
JOIN dim_doctor d
ON f.doctor_id=d.doctor_id
GROUP BY d.doctor_name;

------------------------------------------------

-- Insurance Analytics
CREATE OR REPLACE VIEW vw_insurance_summary AS
SELECT
    i.insurance_provider,
    COUNT(*) total_claims,
    ROUND(SUM(billing_amount),2) total_billing
FROM fact_patients f
JOIN dim_insurance i
ON f.insurance_id=i.insurance_id
GROUP BY i.insurance_provider;