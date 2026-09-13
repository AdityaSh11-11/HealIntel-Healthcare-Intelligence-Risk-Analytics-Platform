import pandas as pd
from sqlalchemy import text
from database import get_engine

engine = get_engine()

df = pd.read_csv("data/raw/healthcare_dataset.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df.rename(columns={
    "name": "patient_name",
    "date_of_admission": "admission_date"
}, inplace=True)

df["admission_date"] = pd.to_datetime(df["admission_date"])
df["discharge_date"] = pd.to_datetime(df["discharge_date"])
df["length_of_stay"] = (
    df["discharge_date"] - df["admission_date"]
).dt.days

# Lookup IDs
hospital = pd.read_sql("SELECT hospital_id, hospital_name FROM dim_hospital", engine)
doctor = pd.read_sql("SELECT doctor_id, doctor_name FROM dim_doctor", engine)
insurance = pd.read_sql("SELECT insurance_id, insurance_provider FROM dim_insurance", engine)

df = df.merge(hospital, left_on="hospital", right_on="hospital_name")
df = df.merge(doctor, left_on="doctor", right_on="doctor_name")
df = df.merge(insurance, on="insurance_provider")

fact = df[
    [
        "patient_name","age","gender","blood_type","medical_condition",
        "medication","admission_type","test_results","admission_date",
        "discharge_date","billing_amount","room_number","length_of_stay",
        "hospital_id","doctor_id","insurance_id"
    ]
]

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE fact_patients RESTART IDENTITY;"))

fact.to_sql(
    "fact_patients",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print(f"Inserted {len(fact)} rows into fact_patients.")