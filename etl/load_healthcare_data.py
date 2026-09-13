import pandas as pd
from sqlalchemy import text
from database import get_engine

engine = get_engine()

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("data/raw/healthcare_dataset.csv")

# Clean column names
df.columns = (
    df.columns.str.strip()
              .str.lower()
              .str.replace(" ", "_")
)

# Rename columns according to PostgreSQL schema
df.rename(columns={
    "name": "patient_name",
    "blood_type": "blood_type",
    "medical_condition": "medical_condition",
    "date_of_admission": "admission_date",
    "insurance_provider": "insurance_provider",
    "billing_amount": "billing_amount",
    "room_number": "room_number",
    "admission_type": "admission_type",
    "discharge_date": "discharge_date",
    "test_results": "test_results"
}, inplace=True)

# Convert dates
df["admission_date"] = pd.to_datetime(df["admission_date"])
df["discharge_date"] = pd.to_datetime(df["discharge_date"])

# Calculate Length of Stay
df["length_of_stay"] = (
    df["discharge_date"] - df["admission_date"]
).dt.days

# Clean text values
text_cols = [
    "patient_name", "gender", "blood_type", "medical_condition",
    "doctor", "hospital", "insurance_provider",
    "admission_type", "medication", "test_results"
]

for col in text_cols:
    df[col] = df[col].astype(str).str.title().str.strip()

# Remove old data so duplicates don't come
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE patients RESTART IDENTITY;"))

# Load into PostgreSQL
df.to_sql(
    "patients",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=1000
)

print(f"✅ Successfully inserted {len(df)} records into PostgreSQL.")
print(df.head())