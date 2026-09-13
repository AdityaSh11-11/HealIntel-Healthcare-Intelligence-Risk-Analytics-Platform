DROP TABLE IF EXISTS fact_drug_events CASCADE;

CREATE TABLE fact_drug_events (

    event_id SERIAL PRIMARY KEY,

    received_date DATE,

    patient_age INT,

    patient_gender VARCHAR(20),

    medicinal_product TEXT,

    reaction TEXT,

    seriousness INT,

    report_source TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE INDEX idx_drug_date
ON fact_drug_events(received_date);

CREATE INDEX idx_drug_name
ON fact_drug_events(medicinal_product);