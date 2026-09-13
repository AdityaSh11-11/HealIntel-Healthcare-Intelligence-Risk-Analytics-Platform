---------1. Executive KPI View
CREATE OR REPLACE VIEW vw_executive_kpis AS
SELECT
    COUNT(*) AS total_patients,
    COUNT(DISTINCT hospital_id) AS total_hospitals,
    COUNT(DISTINCT doctor_id) AS total_doctors,
    ROUND(AVG(age),2) AS average_age,
    ROUND(AVG(billing_amount),2) AS average_bill,
    ROUND(SUM(billing_amount),2) AS total_revenue,
    ROUND(AVG(length_of_stay),2) AS avg_length_of_stay
FROM fact_patients;

SELECT * FROM vw_executive_kpis;


---------2. Disease Distribution View
CREATE OR REPLACE VIEW vw_disease_distribution AS
SELECT
    medical_condition,
    COUNT(*) total_cases,
    ROUND(AVG(age),1) avg_age,
    ROUND(AVG(billing_amount),2) avg_bill
FROM fact_patients
GROUP BY medical_condition
ORDER BY total_cases DESC;

----------3. Hospital Performance View
CREATE OR REPLACE VIEW vw_hospital_performance AS
SELECT
    h.hospital_name,
    COUNT(*) patients,
    ROUND(SUM(f.billing_amount),2) revenue,
    ROUND(AVG(f.length_of_stay),2) avg_stay
FROM fact_patients f
JOIN dim_hospital h USING(hospital_id)
GROUP BY h.hospital_name
ORDER BY revenue DESC;


--------4. Doctor Performance View
CREATE OR REPLACE VIEW vw_doctor_performance AS
SELECT
    d.doctor_name,
    COUNT(*) patients_treated,
    ROUND(AVG(billing_amount),2) avg_billing,
    ROUND(AVG(length_of_stay),2) avg_stay
FROM fact_patients f
JOIN dim_doctor d USING(doctor_id)
GROUP BY d.doctor_name;


------5. Insurance Analytics View
DROP VIEW IF EXISTS vw_insurance_summary;

CREATE VIEW vw_insurance_summary AS
SELECT
    i.insurance_provider,
    COUNT(*) AS total_claims,
    ROUND(SUM(f.billing_amount),2) AS total_billing,
    ROUND(AVG(f.billing_amount),2) AS avg_claim
FROM fact_patients f
JOIN dim_insurance i ON f.insurance_id = i.insurance_id
GROUP BY i.insurance_provider;


-----6. Monthly Admissions View
DROP VIEW IF EXISTS vw_monthly_admissions;

CREATE VIEW vw_monthly_admissions AS
SELECT
    DATE_TRUNC('month', admission_date) AS month,
    COUNT(*) AS admissions,
    ROUND(SUM(billing_amount),2) AS revenue
FROM fact_patients
GROUP BY DATE_TRUNC('month', admission_date)
ORDER BY DATE_TRUNC('month', admission_date);

-------7. Age Group Analytics View
CREATE OR REPLACE VIEW vw_age_groups AS
SELECT
CASE
WHEN age < 18 THEN 'Children'
WHEN age BETWEEN 18 AND 35 THEN 'Young Adult'
WHEN age BETWEEN 36 AND 60 THEN 'Adult'
ELSE 'Senior'
END AS age_group,

COUNT(*) patients,
ROUND(AVG(billing_amount),2) avg_bill

FROM fact_patients
GROUP BY age_group;


-------8. Blood Group Analytics View
CREATE OR REPLACE VIEW vw_blood_group_summary AS
SELECT
blood_type,
COUNT(*) patients,
ROUND(AVG(age),1) avg_age
FROM fact_patients
GROUP BY blood_type
ORDER BY patients DESC;


--------9. Medication Analytics View
CREATE OR REPLACE VIEW vw_medication_summary AS
SELECT
medication,
COUNT(*) prescriptions,
ROUND(AVG(billing_amount),2) avg_bill
FROM fact_patients
GROUP BY medication
ORDER BY prescriptions DESC;

---10. Test Result Analytics View
CREATE OR REPLACE VIEW vw_test_results AS
SELECT
test_results,
COUNT(*) patients
FROM fact_patients
GROUP BY test_results;


-----11. Admission Type View
CREATE OR REPLACE VIEW vw_admission_types AS
SELECT
admission_type,
COUNT(*) patients,
ROUND(AVG(length_of_stay),2) avg_stay
FROM fact_patients
GROUP BY admission_type;


------12. Revenue Trend View
DROP VIEW IF EXISTS vw_revenue_trend;

CREATE VIEW vw_revenue_trend AS
SELECT
    DATE_TRUNC('month', admission_date) AS month,
    ROUND(SUM(billing_amount),2) AS revenue
FROM fact_patients
GROUP BY DATE_TRUNC('month', admission_date)
ORDER BY DATE_TRUNC('month', admission_date);