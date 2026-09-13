CREATE OR REPLACE VIEW vw_patient_summary AS

SELECT

state,
city,
COUNT(*) total_patients,
AVG(age) avg_age,
AVG(risk_score) avg_risk,
SUM(CASE WHEN diabetic THEN 1 ELSE 0 END) diabetic_cases,
SUM(CASE WHEN hypertension THEN 1 ELSE 0 END) hypertension_cases

FROM patients

GROUP BY state, city;


CREATE OR REPLACE VIEW vw_disease_distribution AS

SELECT
disease,
COUNT(*) total_cases,
AVG(risk_score) avg_risk
FROM patients
GROUP BY disease;


CREATE OR REPLACE VIEW vw_daily_admissions AS

SELECT
admission_date,
COUNT(*) admissions
FROM patients
GROUP BY admission_date
ORDER BY admission_date;