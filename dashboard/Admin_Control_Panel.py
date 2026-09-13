from __future__ import annotations

import os
import subprocess
from pathlib import Path
from datetime import datetime
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
import socket
import platform
import psutil
from database import get_engine
from services.ai_chat import ask_healthcare_ai, clear_memory, executive_report
from services.report_generator import generate_pdf_report
import streamlit as st

# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================

def initialize_session_state():

    defaults = {
        "activity_logs": [],
        "sql_history": [],
        "etl_status": "Idle",
        "last_ai_report": "",
        "selected_table": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
st.session_state.setdefault("activity_logs", [])
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("generated_report", "")

st.set_page_config(
    page_title="Healthcare Admin Center",
    page_icon="",
    layout="wide"
)

engine = get_engine()

ROOT = Path(__file__).resolve().parents[1]

EXPORT_FOLDER = ROOT / "exports"
REPORT_FOLDER = ROOT / "reports"
POWERBI_FOLDER = ROOT / "powerbi"

EXPORT_FOLDER.mkdir(exist_ok=True)
REPORT_FOLDER.mkdir(exist_ok=True)


def log_activity(action: str):

    st.session_state.setdefault("activity_logs", [])

    st.session_state["activity_logs"].insert(
        0,
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": action,
        },
    )

    st.session_state["activity_logs"] = st.session_state["activity_logs"][:30]


@st.cache_data(ttl=30)
def get_database_stats():

    queries = {
        "Patients": "SELECT COUNT(*) FROM fact_patients",
        "Hospitals": "SELECT COUNT(DISTINCT hospital_id) FROM fact_patients",
        "Doctors": "SELECT COUNT(DISTINCT doctor_id) FROM fact_patients",
        "Insurance": "SELECT COUNT(DISTINCT insurance_id) FROM fact_patients",
        "Drug Events": "SELECT COUNT(*) FROM fact_drug_events",
        "Risk Predictions": "SELECT COUNT(*) FROM risk_predictions",
    }

    stats = {}

    with engine.connect() as conn:
        for key, query in queries.items():
            stats[key] = conn.execute(text(query)).scalar()

    return stats


@st.cache_data(ttl=30)
def load_patients():

    query = """
    SELECT
        fp.patient_id,
        fp.patient_name,
        fp.age,
        fp.gender,
        fp.medical_condition,
        fp.billing_amount,
        fp.length_of_stay,
        fp.admission_date,
        dh.hospital_name,
        dd.doctor_name,
        di.insurance_provider
    FROM fact_patients fp
    JOIN dim_hospital dh USING(hospital_id)
    JOIN dim_doctor dd USING(doctor_id)
    JOIN dim_insurance di USING(insurance_id)
    """

    df = pd.read_sql(query, engine)

    df["admission_date"] = pd.to_datetime(df["admission_date"])

    return df


def run_module(module_name):

    result = subprocess.run(
        ["python", "-m", module_name],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        log_activity(f"Executed {module_name}")

    return result.returncode, result.stdout, result.stderr


def dataframe_to_excel(df: pd.DataFrame):

    excel = BytesIO()

    with pd.ExcelWriter(excel, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    return excel.getvalue()


def page_header():

    left, right = st.columns([5,1])

    with left:
        st.title("Healthcare Admin Control Center")
        st.caption(
            "Enterprise Healthcare Intelligence Platform • PostgreSQL • AI • ETL • Power BI"
        )

    with right:
        st.metric(
            "Today's Date",
            datetime.now().strftime("%d %b %Y")
        )

# =====================================================
# KPI ROW
# =====================================================

def system_kpis():

    stats = get_database_stats()

    c1,c2,c3,c4,c5,c6 = st.columns(6)

    c1.metric("Patients", f"{stats['Patients']:,}")
    c2.metric("Hospitals", stats["Hospitals"])
    c3.metric("Doctors", stats["Doctors"])
    c4.metric("Insurance", stats["Insurance"])
    c5.metric("Drug Events", stats["Drug Events"])
    c6.metric("Risk Predictions", stats["Risk Predictions"])

# =====================================================
# TAB 1 : DASHBOARD LAUNCHER
# =====================================================

def dashboard_launcher():

    st.subheader("Dashboard Launcher")

    pbix = POWERBI_FOLDER / "dashboard.pbix"

    excel = EXPORT_FOLDER / "healthcare_dashboard.xlsx"

    pdf_reports = sorted(REPORT_FOLDER.glob("*.pdf"))

    c1,c2 = st.columns(2)

    with c1:

        st.info("### Power BI Dashboard")

        if pbix.exists():

            st.download_button(
                "Download PBIX Dashboard",
                pbix.read_bytes(),
                file_name="Healthcare_Intelligence.pbix",
                use_container_width=True,
            )

        else:
            st.warning("Power BI dashboard not found.")

    with c2:

        st.info("### Excel Dashboard")

        if excel.exists():

            st.download_button(
                "Download Excel Report",
                excel.read_bytes(),
                file_name="healthcare_dashboard.xlsx",
                use_container_width=True,
            )

        else:
            st.warning("Excel export unavailable.")

    st.divider()

    logs = st.session_state.get("activity_logs", [])

    if logs:
        st.dataframe(
            pd.DataFrame(logs),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No recent admin activity available.")


# =====================================================
# SQL EXECUTOR
# =====================================================

def execute_sql(query):

    query = query.strip()

    if not query:
        return None

    with engine.begin() as conn:

        if query.lower().startswith("select"):
            return pd.read_sql(query, conn)

        conn.execute(text(query))

        log_activity("Executed SQL Query")

        st.cache_data.clear()

        return "Query executed successfully."


# =====================================================
# TABLE LIST
# =====================================================

@st.cache_data(ttl=120)
def get_tables():

    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    ORDER BY table_name
    """

    return pd.read_sql(sql, engine)


@st.cache_data(ttl=120)
def table_preview(table_name):

    query = f"""
    SELECT *
    FROM {table_name}
    LIMIT 15
    """

    return pd.read_sql(query, engine)


# =====================================================
# TAB 3 : SQL CONSOLE
# =====================================================

def sql_console():

    st.subheader("PostgreSQL SQL Console")

    examples = [
        "SELECT * FROM fact_patients LIMIT 20;",
        "SELECT * FROM vw_hospital_performance;",
        "SELECT * FROM vw_disease_distribution;",
        "SELECT COUNT(*) FROM fact_drug_events;",
        "SELECT * FROM risk_predictions ORDER BY prediction_date DESC LIMIT 20;",
    ]

    selected = st.selectbox(
        "SQL Template",
        ["Custom Query"] + examples,
    )

    if selected == "Custom Query":
        default_query = ""
    else:
        default_query = selected

    query = st.text_area(
        "SQL Editor",
        value=default_query,
        height=220,
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        if st.button(
            "Execute SQL",
            use_container_width=True,
            key="run_sql",
        ):

            try:

                result = execute_sql(query)

                if isinstance(result, pd.DataFrame):

                    st.success(f"{len(result)} rows returned.")

                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True,
                    )

                    csv = result.to_csv(index=False).encode()

                    st.download_button(
                        "Export Result CSV",
                        csv,
                        "query_result.csv",
                        use_container_width=True,
                    )

                elif result:
                    st.success(result)

            except Exception as error:
                st.error(error)

    with col2:

        if st.button(
            "Clear SQL",
            use_container_width=True,
            key="clear_sql",
        ):
            st.rerun()

    st.divider()

    # ---------------- QUERY HISTORY ----------------

    st.subheader("Recent Admin Activity")

    if st.session_state.activity_logs:

        st.dataframe(
            pd.DataFrame(st.session_state.activity_logs),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No SQL activity available.")


# =====================================================
# DATABASE EXPLORER
# =====================================================

def database_explorer():

    st.subheader("Database Explorer")

    tables = get_tables()

    table_name = st.selectbox(
        "Choose PostgreSQL Table",
        tables["table_name"],
    )

    preview = table_preview(table_name)

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows Previewed", len(preview))
    col2.metric("Columns", preview.shape[1])
    col3.metric("Table Name", table_name)

    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True,
    )

    csv = preview.to_csv(index=False).encode()

    st.download_button(
        "Download Preview CSV",
        csv,
        f"{table_name}.csv",
        use_container_width=True,
    )

    st.divider()

    st.subheader("Column Metadata")

    metadata = pd.read_sql(
        f"""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name='{table_name}'
        ORDER BY ordinal_position
        """,
        engine,
    )

    st.dataframe(
        metadata,
        use_container_width=True,
        hide_index=True,
    )

@st.cache_data(ttl=60)
def ai_snapshot():

    queries = {
        "kpi": """
        SELECT
            COUNT(*) total_patients,
            ROUND(SUM(billing_amount),2) revenue,
            ROUND(AVG(length_of_stay),1) avg_stay
        FROM fact_patients
        """,

        "disease": """
        SELECT medical_condition, COUNT(*) patients
        FROM fact_patients
        GROUP BY medical_condition
        ORDER BY patients DESC
        LIMIT 5
        """,

        "hospital": """
        SELECT
            dh.hospital_name,
            ROUND(SUM(fp.billing_amount),2) revenue
        FROM fact_patients fp
        JOIN dim_hospital dh USING(hospital_id)
        GROUP BY dh.hospital_name
        ORDER BY revenue DESC
        LIMIT 5
        """,

        "insurance": """
        SELECT
            di.insurance_provider,
            ROUND(SUM(fp.billing_amount),2) billing
        FROM fact_patients fp
        JOIN dim_insurance di USING(insurance_id)
        GROUP BY di.insurance_provider
        ORDER BY billing DESC
        LIMIT 5
        """
    }

    result = {}

    with engine.connect() as conn:
        for name, sql in queries.items():
            result[name] = pd.read_sql(sql, conn)

    return result

def ai_insight_cards():

    snap = ai_snapshot()

    kpi = snap["kpi"].iloc[0]

    disease = snap["disease"].iloc[0]

    hospital = snap["hospital"].iloc[0]

    insurance = snap["insurance"].iloc[0]

    st.subheader("Live AI Insights")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Top Disease",
        disease["medical_condition"],
        f"{disease['patients']} Patients"
    )

    c2.metric(
        "Top Hospital",
        hospital["hospital_name"],
        f"${hospital['revenue']:,.0f}"
    )

    c3.metric(
        "Top Insurance",
        insurance["insurance_provider"],
        f"${insurance['billing']:,.0f}"
    )

    c4.metric(
        "Average Stay",
        f"{kpi['avg_stay']} Days"
    )


# =====================================================
# EXECUTIVE REPORT GENERATOR
# =====================================================

def executive_ai_report_panel():

    st.subheader("AI Executive Healthcare Report")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Generate AI Report",
            use_container_width=True,
            key="generate_ai_report"
        ):

            with st.spinner("Gemini is analysing your healthcare warehouse..."):

                report = executive_report()

            st.session_state.generated_report = report

            log_activity("Generated AI Executive Report")

            st.success("AI Report Generated Successfully.")

    with col2:

        if st.button(
            "Generate PDF Report",
            use_container_width=True,
            key="generate_pdf_report"
        ):

            with st.spinner("Building enterprise PDF report..."):

                pdf_file = generate_pdf_report()

            log_activity("Generated Executive PDF Report")

            st.success("PDF Report Created.")

            with open(pdf_file, "rb") as f:
                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name=Path(pdf_file).name,
                    use_container_width=True,
                )

    st.divider()

    if "generated_report" in st.session_state:

        report_text = st.session_state.generated_report

        if isinstance(report_text, str) and report_text:
            st.markdown(report_text)

            st.download_button(
                "⬇ Download Markdown Report",
                data=report_text,
                file_name="Healthcare_AI_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info("Generate an AI report to preview and download it.")

def report_history_panel():

    st.subheader("Report History")

    reports = sorted(REPORT_FOLDER.glob("*"))

    if len(reports) == 0:
        st.info("No reports generated yet.")
        return

    history = []

    for file in reports[::-1]:

        history.append({
            "Report": file.name,
            "Created": datetime.fromtimestamp(
                file.stat().st_mtime
            ).strftime("%d %b %Y %H:%M")
        })

    st.dataframe(
        pd.DataFrame(history),
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    selected = st.selectbox(
        "Download Existing Report",
        [f.name for f in reports[::-1]]
    )

    chosen = REPORT_FOLDER / selected

    with open(chosen, "rb") as f:
        st.download_button(
            "Download Selected Report",
            f,
            file_name=chosen.name,
            use_container_width=True
        )

def export_chat_markdown():

    if len(st.session_state.chat_history) == 0:
        return None

    lines = [
        "# Healthcare AI Conversation",
        "",
        f"Generated: {datetime.now()}",
        ""
    ]

    for chat in st.session_state.chat_history:

        lines.append(f"## User")
        lines.append(chat["question"])
        lines.append("")
        lines.append("## AI")
        lines.append(chat["answer"])
        lines.append("")
        lines.append("---")

    return "\n".join(lines)


def ai_chat_panel():

    st.subheader("Ask AI About Your Healthcare Database")

    st.caption(
        "Powered by Gemini 3.6 Flash"
    )

    question = st.text_input(
        "",
        placeholder="Example: Which hospitals generated the highest revenue?"
    )

    col1, col2 = st.columns([1,1])

    with col1:

        if st.button(
            "Ask AI",
            use_container_width=True,
            key="ask_ai_button"
        ):

            if question.strip() == "":
                st.warning("Please enter a question.")

            else:

                with st.spinner("AI is analysing PostgreSQL warehouse..."):

                    answer = ask_healthcare_ai(question)

                st.session_state.chat_history.insert(
                    0,
                    {
                        "question": question,
                        "answer": answer,
                        "time": datetime.now().strftime("%H:%M"),
                    }
                )

                st.session_state.chat_history = (
                    st.session_state.chat_history[:20]
                )

                log_activity("Asked AI Assistant")

    with col2:

        if st.button(
            "Clear Conversation",
            use_container_width=True,
            key="clear_ai_chat"
        ):

            clear_memory()

            st.session_state.chat_history = []

            log_activity("Cleared AI Conversation")

            st.success("Conversation Cleared.")

    st.divider()

    if len(st.session_state.chat_history) == 0:

        st.info("Start asking AI questions about your healthcare warehouse.")

    else:

        for chat in st.session_state.chat_history:

            with st.container(border=True):

                left, right = st.columns([5,1])

                with left:
                    st.markdown(f"### {chat['question']}")

                with right:
                    st.caption(chat["time"])

                st.markdown(chat["answer"])

    st.divider()

    chat_md = export_chat_markdown()

    if chat_md:

        st.download_button(
            "⬇ Export Conversation",
            chat_md,
            file_name="Healthcare_AI_Chat.md",
            use_container_width=True,
        )


def ai_control_center():

    ai_insight_cards()

    st.divider()

    executive_ai_report_panel()

    st.divider()

    ai_chat_panel()

    st.divider()

    report_history_panel()

# =====================================================
# DATABASE STATUS
# =====================================================

@st.cache_data(ttl=30)
def database_status():
    """Check PostgreSQL connection and database information."""

    info = {}

    try:
        with engine.connect() as conn:

            info["connected"] = True

            info["database"] = conn.execute(
                text("SELECT current_database()")
            ).scalar()

            info["version"] = conn.execute(
                text("SELECT version()")
            ).scalar()

            info["current_time"] = conn.execute(
                text("SELECT NOW()")
            ).scalar()

            info["tables"] = conn.execute(
                text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema='public'
                """)
            ).scalar()

    except Exception as e:

        info["connected"] = False
        info["error"] = str(e)

    return info


@st.cache_data(ttl=60)
def warehouse_table_counts():

    query = """
    SELECT
        table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    ORDER BY table_name
    """

    tables = pd.read_sql(query, engine)

    records = []

    with engine.connect() as conn:

        for table in tables.table_name:

            try:
                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()

            except Exception:
                count = 0

            records.append(
                {
                    "Table": table,
                    "Rows": count
                }
            )

    return pd.DataFrame(records)


# =====================================================
# DATABASE SIZE
# =====================================================

@st.cache_data(ttl=300)
def database_storage():

    sql = """
    SELECT
        pg_size_pretty(pg_database_size(current_database()))
            AS database_size
    """

    return pd.read_sql(sql, engine)


# =====================================================
# SERVER HEALTH
# =====================================================

def server_health():

    return {
        "Hostname": socket.gethostname(),
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Python Version": platform.python_version(),
        "CPU Usage": psutil.cpu_percent(),
        "Memory Usage": psutil.virtual_memory().percent,
        "Disk Usage": psutil.disk_usage("/").percent,
    }


# =====================================================
# API STATUS
# =====================================================

def api_status():

    services = {
        "PostgreSQL": True,
        "Gemini AI": bool(os.getenv("GEMINI_API_KEY")),
        "OpenRouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "OpenFDA API": True,
        "Machine Learning": Path(ROOT / "ml").exists(),
    }

    rows = []

    for name, status in services.items():

        rows.append(
            {
                "Service": name,
                "Status": "🟢 Connected" if status else "🔴 Missing"
            }
        )

    return pd.DataFrame(rows)


# =====================================================
# ETL STATUS
# =====================================================

@st.cache_data(ttl=30)
def etl_status():

    pipelines = [
        "Healthcare Dataset ETL",
        "Dimension Builder",
        "Fact Loader",
        "OpenFDA API Sync",
        "SQL View Builder",
        "Risk Prediction Model",
    ]

    return pd.DataFrame(
        {
            "Pipeline": pipelines,
            "Status": ["Ready"] * len(pipelines),
            "Last Run": [
                datetime.now().strftime("%d-%b %H:%M")
            ] * len(pipelines),
        }
    )

# =====================================================
# ACTIVITY DATA
# =====================================================

@st.cache_data(ttl=30)
def recent_activity():

    patients = pd.read_sql(
        """
        SELECT
            patient_name,
            admission_date,
            medical_condition,
            billing_amount
        FROM fact_patients
        ORDER BY admission_date DESC
        LIMIT 20
        """,
        engine
    )

    return patients


@st.cache_data(ttl=30)
def monthly_activity():

    query = """
    SELECT
        DATE_TRUNC('month', admission_date) AS month,
        COUNT(*) admissions,
        ROUND(SUM(billing_amount),2) revenue
    FROM fact_patients
    GROUP BY month
    ORDER BY month
    """

    return pd.read_sql(query, engine)


@st.cache_data(ttl=30)
def disease_activity():

    query = """
    SELECT
        medical_condition,
        COUNT(*) patients
    FROM fact_patients
    GROUP BY medical_condition
    ORDER BY patients DESC
    """

    return pd.read_sql(query, engine)


# =====================================================
# ACTIVITY DASHBOARD
# =====================================================

def activity_dashboard():

    st.subheader("Healthcare Activity Dashboard")

    monthly = monthly_activity()

    monthly["month"] = pd.to_datetime(monthly["month"])

    c1, c2 = st.columns(2)

    with c1:

        fig = px.line(
            monthly,
            x="month",
            y="admissions",
            markers=True,
            title="Monthly Patient Admissions"
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:

        fig = px.bar(
            monthly,
            x="month",
            y="revenue",
            title="Monthly Hospital Revenue"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    disease = disease_activity()

    c3, c4 = st.columns(2)

    with c3:

        fig = px.pie(
            disease,
            values="patients",
            names="medical_condition",
            title="Disease Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    with c4:

        fig = px.bar(
            disease.head(10),
            x="patients",
            y="medical_condition",
            orientation="h",
            title="Top Medical Conditions"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Latest Patient Registrations")

    st.dataframe(
        recent_activity(),
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# EXPORT CENTER
# =====================================================

def export_center():

    st.subheader("Enterprise Export Center")

    df = load_patients()

    col1, col2, col3 = st.columns(3)

    # ---------------- CSV ----------------

    with col1:

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Export CSV",
            csv,
            "healthcare_patients.csv",
            "text/csv",
            use_container_width=True,
        )

    # ---------------- EXCEL ----------------

    with col2:

        excel_data = dataframe_to_excel(df)

        st.download_button(
            "Export Excel",
            excel_data,
            "healthcare_dashboard.xlsx",
            use_container_width=True,
        )

    # ---------------- PDF ----------------

    with col3:

        if st.button(
            "Generate PDF",
            use_container_width=True
        ):

            with st.spinner("Creating Executive PDF..."):

                pdf_file = generate_pdf_report()

            st.success("PDF Generated Successfully.")

            with open(pdf_file, "rb") as f:

                st.download_button(
                    "⬇ Download PDF",
                    f,
                    file_name=Path(pdf_file).name,
                    use_container_width=True,
                )

    st.divider()


# =====================================================
# REFRESH CENTER
# =====================================================

def refresh_center():

    st.subheader("Refresh & Cache Management")

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "Refresh Dashboard Data",
            use_container_width=True
        ):

            st.cache_data.clear()
            log_activity("Dashboard Cache Cleared")

            st.success("Dashboard refreshed.")

    with c2:

        if st.button(
            "Refresh AI Snapshot",
            use_container_width=True
        ):

            st.cache_data.clear()
            log_activity("AI Snapshot Refreshed")

            st.success("AI snapshot updated.")

    with c3:

        if st.button(
            "Reload Entire Admin Center",
            use_container_width=True
        ):

            st.cache_data.clear()
            st.rerun()

    st.divider()

    st.info(
        "Use these buttons whenever ETL updates PostgreSQL so dashboards and AI immediately reflect new data."
    )

    # =====================================================
# ADMIN SIDEBAR
# =====================================================

def admin_sidebar():

    with st.sidebar:

        st.title("Admin Center")

        st.caption("Healthcare Intelligence Platform")

        st.divider()

        auto_refresh = st.toggle(
            "Auto Refresh Dashboard",
            value=False
        )

        refresh_seconds = st.selectbox(
            "Refresh Every",
            [30, 60, 120, 300],
            index=1
        )

        st.divider()

        st.markdown("### Quick Tools")

        if st.button("Clear Cache", use_container_width=True):
            st.cache_data.clear()
            log_activity("Manual Cache Cleared")
            st.success("Cache Cleared")

        if st.button("Clear AI Chat", use_container_width=True):
            clear_memory()
            st.session_state.chat_history = []
            log_activity("AI Chat Cleared")
            st.success("AI Chat Cleared")

        st.divider()

        st.markdown("### Platform Info")

        stats = get_database_stats()

        st.metric("Patients", f"{stats['Patients']:,}")
        st.metric("Hospitals", stats["Hospitals"])

        st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}")

    return auto_refresh, refresh_seconds



# =====================================================
# MAIN ADMIN CENTER
# =====================================================
def admin_center():
    initialize_session_state()
    auto_refresh, refresh_seconds = admin_sidebar()

    page_header()

    system_kpis()

    st.divider()

    tabs = st.tabs(
        [
            "Dashboard Launcher",
            "SQL Console Center",
            "AI Chatbot Center",
            "",
            "Activity & Export Center",
        ]
    )

    # ---------------- TAB 1 ----------------

    with tabs[0]:
        dashboard_launcher()

    # ---------------- TAB 2 ----------------

    with tabs[1]:
        sql_console()
        st.divider()
        database_explorer()

    # ---------------- TAB 3 ----------------

    with tabs[2]:
        ai_control_center()

    # ---------------- TAB 5 ----------------

    with tabs[4]:
        activity_dashboard()
        st.divider()
        export_center()
        st.divider()
        refresh_center()

    # AUTO REFRESH

    if auto_refresh:

        import time

        holder = st.empty()

        for sec in range(refresh_seconds, 0, -1):
            holder.info(f"Refreshing Admin Center in {sec} seconds...")
            time.sleep(1)

        st.cache_data.clear()
        st.rerun()

# =====================================================
# STANDALONE TEST
# =====================================================

if __name__ == "__main__":

    admin_center()