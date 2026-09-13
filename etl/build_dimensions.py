import pandas as pd
from sqlalchemy import text
from database import get_engine

engine = get_engine()

df = pd.read_csv("data/raw/healthcare_dataset.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE dim_hospital RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_doctor RESTART IDENTITY CASCADE;"))
    conn.execute(text("TRUNCATE TABLE dim_insurance RESTART IDENTITY CASCADE;"))

# Hospital
hospital_df = (
    df[["hospital"]]
    .drop_duplicates()
    .rename(columns={"hospital": "hospital_name"})
)
hospital_df.to_sql("dim_hospital", engine, if_exists="append", index=False)

# Doctor
doctor_df = (
    df[["doctor"]]
    .drop_duplicates()
    .rename(columns={"doctor": "doctor_name"})
)
doctor_df.to_sql("dim_doctor", engine, if_exists="append", index=False)

# Insurance
insurance_df = (
    df[["insurance_provider"]]
    .drop_duplicates()
)
insurance_df.to_sql("dim_insurance", engine, if_exists="append", index=False)

print("Dimension tables loaded.")