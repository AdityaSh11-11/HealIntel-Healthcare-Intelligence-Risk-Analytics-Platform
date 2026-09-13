DROP TABLE IF EXISTS risk_predictions CASCADE;

CREATE TABLE risk_predictions (

    prediction_id SERIAL PRIMARY KEY,

    patient_id INT REFERENCES fact_patients(patient_id),

    risk_score NUMERIC(5,2),

    risk_category VARCHAR(20),

    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE INDEX idx_patient_risk
ON risk_predictions(patient_id);