"""
AI Healthcare Intelligence Service
---------------------------------
Supports:
1. Google Gemini 2.5 Flash
2. OpenRouter (Llama / GPT / Claude)

Reads LIVE PostgreSQL warehouse and generates
executive healthcare intelligence reports.
"""

import os
import json
from datetime import datetime

import pandas as pd
import requests
from sqlalchemy import text

try:
    from google import genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None

from database import get_engine

engine = get_engine()

# ==========================================================
# CONFIGURATION
# ==========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DEFAULT_MODEL = "gemini-2.5-flash"

# ==========================================================
# DATABASE SNAPSHOT
# ==========================================================

def load_database_snapshot():
    """Loads important warehouse information."""

    queries = {
        "kpi": """
        SELECT
            COUNT(*) AS total_patients,
            ROUND(SUM(billing_amount),2) AS total_revenue,
            ROUND(AVG(age),1) AS average_age,
            ROUND(AVG(length_of_stay),1) AS average_stay
        FROM fact_patients
        """,

        "disease": """
        SELECT
            medical_condition,
            COUNT(*) AS patients,
            ROUND(AVG(billing_amount),2) avg_bill
        FROM fact_patients
        GROUP BY medical_condition
        ORDER BY patients DESC
        LIMIT 15
        """,

        "hospital": """
        SELECT
            dh.hospital_name,
            COUNT(*) patients,
            ROUND(SUM(fp.billing_amount),2) revenue,
            ROUND(AVG(fp.length_of_stay),2) avg_stay
        FROM fact_patients fp
        JOIN dim_hospital dh USING(hospital_id)
        GROUP BY dh.hospital_name
        ORDER BY revenue DESC
        LIMIT 15
        """,

        "doctor": """
        SELECT
            dd.doctor_name,
            COUNT(*) patients
        FROM fact_patients fp
        JOIN dim_doctor dd USING(doctor_id)
        GROUP BY dd.doctor_name
        ORDER BY patients DESC
        LIMIT 15
        """,

        "insurance": """
        SELECT
            di.insurance_provider,
            COUNT(*) claims,
            ROUND(SUM(fp.billing_amount),2) billing
        FROM fact_patients fp
        JOIN dim_insurance di USING(insurance_id)
        GROUP BY di.insurance_provider
        ORDER BY billing DESC
        """,

        "admissions": """
        SELECT
            DATE_TRUNC('month', admission_date) month,
            COUNT(*) admissions,
            ROUND(SUM(billing_amount),2) revenue
        FROM fact_patients
        GROUP BY month
        ORDER BY month
        """,

        "medication": """
        SELECT
            medication,
            COUNT(*) prescriptions
        FROM fact_patients
        GROUP BY medication
        ORDER BY prescriptions DESC
        LIMIT 15
        """,

        "risk": """
        SELECT
            risk_category,
            COUNT(*) patients
        FROM risk_predictions
        GROUP BY risk_category
        """
    }

    snapshot = {}

    with engine.connect() as conn:
        for key, query in queries.items():
            try:
                snapshot[key] = pd.read_sql(query, conn)
            except Exception:
                snapshot[key] = pd.DataFrame()

    return snapshot


# ==========================================================
# BUILD AI PROMPT
# ==========================================================

def build_prompt(snapshot):

    kpi = snapshot["kpi"].to_dict("records")[0]

    prompt = f"""
You are a Senior Healthcare Intelligence Consultant.

You are analysing a LIVE PostgreSQL Healthcare Data Warehouse.

Today's Date:
{datetime.now().strftime("%d %B %Y")}

==============================
EXECUTIVE KPI SNAPSHOT
==============================

Total Patients: {kpi["total_patients"]}

Total Revenue: ${kpi["total_revenue"]}

Average Patient Age: {kpi["average_age"]}

Average Length of Stay: {kpi["average_stay"]} Days


==============================
DISEASE DISTRIBUTION
==============================

{snapshot["disease"].to_markdown(index=False)}

==============================
HOSPITAL PERFORMANCE
==============================

{snapshot["hospital"].to_markdown(index=False)}

==============================
DOCTOR PERFORMANCE
==============================

{snapshot["doctor"].to_markdown(index=False)}

==============================
INSURANCE SUMMARY
==============================

{snapshot["insurance"].to_markdown(index=False)}

==============================
MONTHLY ADMISSIONS
==============================

{snapshot["admissions"].to_markdown(index=False)}

==============================
MEDICATION SUMMARY
==============================

{snapshot["medication"].to_markdown(index=False)}

==============================
RISK PREDICTIONS
==============================

{snapshot["risk"].to_markdown(index=False)}

=====================================================

Generate a professional Executive Healthcare Intelligence Report.

The report MUST include:

# Executive Summary

# Financial Performance

# Clinical Insights

# Disease Trends

# Hospital Performance

# Doctor Performance

# Insurance Analytics

# Operational Risks

# AI Recommendations

# Priority Actions (5 Bullet Points)

Write in professional markdown.

Use headings, tables and bullet points.

Never mention SQL.

"""
    return prompt


# ==========================================================
# GEMINI GENERATION
# ==========================================================

from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    "gemini-3.6-flash",
    "gemini-3.6-pro",
]


def gemini_summary():
    snapshot = load_database_snapshot()
    prompt = build_prompt(snapshot)

    last_error = None

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            if response.text:
                return response.text

        except Exception as e:
            last_error = e

    raise RuntimeError(f"Gemini generation failed: {last_error}")


# ==========================================================
# OPENROUTER GENERATION
# ==========================================================

def openrouter_summary(model_name="meta-llama/llama-3.3-70b-instruct"):

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found.")

    snapshot = load_database_snapshot()

    prompt = build_prompt(snapshot)

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a healthcare analytics consultant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=90,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# ==========================================================
# MAIN PUBLIC FUNCTION
# ==========================================================

def generate_ai_report(provider="Gemini"):

    if provider == "Gemini":
        return gemini_summary()

    return openrouter_summary()


# ==========================================================
# DATABASE SUMMARY (Without AI)
# ==========================================================

def generate_local_summary():

    snapshot = load_database_snapshot()

    kpi = snapshot["kpi"].iloc[0]

    top_hospital = snapshot["hospital"].iloc[0]["hospital_name"]
    top_disease = snapshot["disease"].iloc[0]["medical_condition"]

    report = f"""
# Healthcare Intelligence Executive Summary

Generated:
{datetime.now().strftime("%d %B %Y %H:%M")}

---

## Executive KPI

| Metric | Value |
|--------|------|
| Total Patients | {kpi.total_patients} |
| Revenue | ${kpi.total_revenue:,.2f} |
| Average Age | {kpi.average_age} |
| Average Stay | {kpi.average_stay} Days |

---

## Top Disease

**{top_disease}**

---

## Highest Revenue Hospital

**{top_hospital}**

---

## Top Five Diseases

{snapshot["disease"].head().to_markdown(index=False)}

---

## Top Five Hospitals

{snapshot["hospital"].head().to_markdown(index=False)}

---

## Recommendations

- Monitor patients with abnormal test results.
- Prioritize hospitals with highest revenue.
- Reduce average length of stay.
- Review insurance providers with highest claims.
- Track medication usage monthly.
"""

    return report


# ==========================================================
# SAVE REPORT
# ==========================================================

def save_markdown_report(text_report):

    os.makedirs("reports", exist_ok=True)

    filename = (
        f"reports/Healthcare_AI_Report_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(text_report)

    return filename


# ==========================================================
# JSON SNAPSHOT FOR DASHBOARD
# ==========================================================

def get_snapshot_json():

    snapshot = load_database_snapshot()

    result = {}

    for key, value in snapshot.items():
        result[key] = value.to_dict(orient="records")

    return json.dumps(result, indent=2, default=str)