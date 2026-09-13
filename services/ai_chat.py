"""
Healthcare Intelligence Platform
AI Database Chat Service (Complete File)

Ask questions like:
- Top 5 hospitals by revenue.
- Which disease has highest admissions?
- Summarize today's healthcare data.
- Highest billing patients.
- Insurance providers with most claims.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Dict

import pandas as pd
from google import genai
from sqlalchemy import text

from database import get_engine

# ============================================================
# CONFIG
# ============================================================

engine = get_engine()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.6-flash"

# ============================================================
# DATABASE HELPERS
# ============================================================


def sql_dataframe(query: str) -> pd.DataFrame:
    """Run SELECT query safely."""

    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def get_database_context() -> str:
    """
    Collect warehouse snapshot for Gemini.
    """

    queries = {
        "Executive KPI": """
            SELECT
                COUNT(*) total_patients,
                ROUND(SUM(billing_amount),2) revenue,
                ROUND(AVG(age),1) avg_age,
                ROUND(AVG(length_of_stay),1) avg_stay
            FROM fact_patients
        """,

        "Disease Distribution": """
            SELECT
                medical_condition,
                COUNT(*) patients
            FROM fact_patients
            GROUP BY medical_condition
            ORDER BY patients DESC
            LIMIT 10
        """,

        "Hospital Revenue": """
            SELECT
                dh.hospital_name,
                ROUND(SUM(fp.billing_amount),2) revenue
            FROM fact_patients fp
            JOIN dim_hospital dh USING(hospital_id)
            GROUP BY dh.hospital_name
            ORDER BY revenue DESC
            LIMIT 10
        """,

        "Doctor Performance": """
            SELECT
                dd.doctor_name,
                COUNT(*) patients
            FROM fact_patients fp
            JOIN dim_doctor dd USING(doctor_id)
            GROUP BY dd.doctor_name
            ORDER BY patients DESC
            LIMIT 10
        """,

        "Insurance Providers": """
            SELECT
                di.insurance_provider,
                ROUND(SUM(fp.billing_amount),2) billing
            FROM fact_patients fp
            JOIN dim_insurance di USING(insurance_id)
            GROUP BY di.insurance_provider
            ORDER BY billing DESC
        """,

        "Latest Patients": """
            SELECT
                patient_name,
                medical_condition,
                billing_amount,
                admission_date
            FROM fact_patients
            ORDER BY admission_date DESC
            LIMIT 10
        """,

        "Risk Predictions": """
            SELECT
                risk_category,
                COUNT(*) patients
            FROM risk_predictions
            GROUP BY risk_category
        """
    }

    sections = []

    for title, query in queries.items():
        try:
            df = sql_dataframe(query)
            formatted = df.copy()

            for col in formatted.select_dtypes(include=["float", "int"]).columns:
                formatted[col] = formatted[col].map(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else ""
                )

            markdown = formatted.to_markdown(index=False)
            sections.append(f"## {title}\n{markdown}")
        except Exception:
            continue

    return "\n\n".join(sections)


# ============================================================
# CHAT MEMORY
# ============================================================

class AIChatMemory:

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str | None):
        safe_content = content if content is not None else ""
        self.messages.append(
            {
                "role": role,
                "content": safe_content
            }
        )

        self.messages = self.messages[-6:]

    def history(self):

        history = []

        for m in self.messages:
            history.append(
                f"{m['role'].upper()}:\n{m['content']}"
            )

        return "\n\n".join(history)


memory = AIChatMemory()

# ============================================================
# PROMPT BUILDER
# ============================================================


def build_prompt(question: str):

    context = get_database_context()

    history = memory.history()

    prompt = f"""
You are an Enterprise Healthcare Intelligence Analyst.

Current Date:
{datetime.now().strftime("%d %B %Y")}

Database Snapshot:

{context}

Conversation History:

{history}

User Question:

{question}

Instructions:

1. Answer ONLY using the healthcare warehouse.
2. Be concise but insightful.
3. Use Markdown.
4. Include bullet points.
5. Mention important trends if relevant.
6. Give recommendations when appropriate.
7. Never invent numbers.

Formatting Rules:

- Currency must always be like $1,084,200.
- Percentages with one decimal place.
- Never use scientific notation.
- Use markdown headings and tables.
- Give 3–5 actionable recommendations.
- Highlight anomalies and trends if data supports them."""
    return prompt


# ============================================================
# GEMINI CHAT
# ============================================================


def ask_healthcare_ai(question: str):
    prompt = build_prompt(question)

    chat = client.chats.create(
        model="gemini-3.6-flash",
        history=[]
    )

    response = chat.send_message(prompt)

    answer = response.text

    memory.add("user", question)
    memory.add("assistant", answer)

    return answer
# ============================================================
# EXECUTIVE REPORT
# ============================================================


def executive_report():

    return ask_healthcare_ai(
        """
Generate a complete executive healthcare intelligence report.

Include:

1. Executive Summary.
2. Financial Performance.
3. Disease Trends.
4. Hospital Rankings.
5. Insurance Analysis.
6. Doctor Performance.
7. Operational Risks.
8. AI Recommendations.
"""
    )


# ============================================================
# TREND REPORT
# ============================================================


def daily_trend_report():

    return ask_healthcare_ai(
        """
Summarize today's healthcare warehouse.

Mention:
- admissions,
- revenue,
- disease trends,
- billing insights,
- operational risks,
- recommendations.
"""
    )


# ============================================================
# KPI EXPLAINER
# ============================================================


def explain_kpis():

    return ask_healthcare_ai(
        """
Explain every KPI in the healthcare dashboard in business language.

Explain:
Patients,
Revenue,
Average Stay,
Average Billing,
Hospital Performance,
Doctor Performance,
Insurance,
Risk Predictions.
"""
    )


# ============================================================
# RESET CHAT
# ============================================================


def clear_memory():
    memory.messages.clear()


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Healthcare AI Chat")
    print("=" * 60)

    while True:

        question = input("\nAsk AI > ")

        if question.lower() in ["exit", "quit"]:
            break

        try:
            answer = ask_healthcare_ai(question)
            print("\n")
            print(answer)
            print("\n")

        except Exception as e:
            print(e)