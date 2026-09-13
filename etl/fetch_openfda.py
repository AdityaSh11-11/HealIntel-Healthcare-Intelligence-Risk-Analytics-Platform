import requests
import pandas as pd
from sqlalchemy import text

from database import get_engine

engine = get_engine()

URL = "https://api.fda.gov/drug/event.json?limit=500"

response = requests.get(URL, timeout=30)
response.raise_for_status()

results = response.json()["results"]

records = []

for item in results:

    patient = item.get("patient", {})

    drugs = patient.get("drug", [])

    reactions = patient.get("reaction", [])

    records.append(
        {
            "received_date": item.get("receiptdate"),
            "patient_age": patient.get("patientonsetage"),
            "patient_gender": patient.get("patientsex"),
            "medicinal_product": drugs[0].get("medicinalproduct")
            if drugs
            else None,
            "reaction": reactions[0].get("reactionmeddrapt")
            if reactions
            else None,
            "seriousness": item.get("serious"),
            "report_source": item.get("primarysource", {}).get("qualification"),
        }
    )

df = pd.DataFrame(records)

df["received_date"] = pd.to_datetime(
    df["received_date"], errors="coerce"
)

df["patient_age"] = pd.to_numeric(
    df["patient_age"], errors="coerce"
)

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE fact_drug_events RESTART IDENTITY"))

df.to_sql(
    "fact_drug_events",
    engine,
    if_exists="append",
    index=False,
    method="multi",
)

print(f"Loaded {len(df)} OpenFDA events.")