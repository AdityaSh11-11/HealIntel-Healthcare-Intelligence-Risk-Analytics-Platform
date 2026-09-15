<div align="center">

# HealIntel - Healthcare Intelligence Risk Analytics Platform

### End-to-End Healthcare Analytics & Business Intelligence Ecosystem

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/PostgreSQL-Data_Warehouse-336791?style=for-the-badge&logo=postgresql"/>
  <img src="https://img.shields.io/badge/Streamlit-Enterprise_App-FF4B4B?style=for-the-badge&logo=streamlit"/>
  <img src="https://img.shields.io/badge/Power_BI-Business_Intelligence-F2C811?style=for-the-badge&logo=powerbi"/>
  <img src="https://img.shields.io/badge/Machine_Learning-Random_Forest-16A34A?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Gemini_AI-Clinical_Insights-7C3AED?style=for-the-badge&logo=google"/>
</p>

<p align="center">
  <b>PostgreSQL • ETL • Machine Learning • AI • Power BI • Excel • Streamlit</b>
</p>

</div>

---

# Project Overview

Healthcare Intelligence Platform is a complete enterprise-grade healthcare analytics solution that combines **Data Engineering, Machine Learning, Artificial Intelligence, Business Intelligence, and Interactive Web Analytics** into one ecosystem.

The platform transforms raw healthcare records into actionable clinical and operational insights through automated ETL pipelines, a PostgreSQL data warehouse, interactive Streamlit dashboards, enterprise Power BI reports, Excel dashboards, AI-generated reports, and patient risk prediction models.

> **Built for Data Analyst / Business Intelligence / Healthcare Analytics Portfolio**

---

# Project Highlights

<table>
<tr>
<td width="50%">

### Business Intelligence
- Executive Healthcare Dashboard
- Patient Analytics Dashboard
- Hospital Operations Dashboard
- Medication & Insurance Dashboard
- AI Risk Intelligence Dashboard

</td>

<td width="50%">

### AI & ML
- Random Forest Risk Prediction
- AI Clinical Summary Generator
- AI Chat Assistant
- Automated PDF Reports
- Dynamic Risk Insights

</td>
</tr>
</table>

---

# Complete Tech Stack

| Category | Technologies |
|----------|--------------|
| Programming | Python 3.12 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Streamlit |
| BI Tools | Power BI Desktop, Microsoft Excel |
| Machine Learning | Scikit-learn Random Forest |
| AI Integration | Google Gemini API / OpenRouter |
| Reporting | ReportLab PDF |
| Deployment | Streamlit Cloud / Render |

---

# System Architecture

<img src="assets/architecture.png" width="100%"/>

### Workflow

```text
CSV Healthcare Dataset
        │
        ▼
 Python ETL Pipeline
        │
        ▼
 PostgreSQL Data Warehouse
        │
 ├───────────────┐
 ▼               ▼
Streamlit App    Power BI
 ▼               ▼
AI + ML      Executive Dashboards
        │
        ▼
 PDF Reports + Excel Dashboard
```

---

# Project Structure

```bash
Healthcare-Intelligence-Platform/
│
├── app.py                         # Main Streamlit Application
│
├── dashboard/                     # All Dashboard Pages
│   ├── executive.py
│   ├── patient_dashboard.py
│   ├── hospital_dashboard.py
│   ├── risk_dashboard.py
│   └── Admin_Control_Panel.py
│
├── components/
│   ├── sidebar.py
│   ├── footer.py
│   └── cards.py
│
├── services/
│   ├── ai_summary.py
│   ├── ai_chat.py
│   ├── report_generator.py
│   └── etl_runner.py
│
├── ml/
│   ├── train_model.py
│   ├── predict.py
│   ├── risk_prediction_model.pkl
│   ├── feature_importance.csv
│   └── metrics.json
│
├── database.py
│
├── sql/
│   ├── schema.sql
│   ├── views.sql
│   └── procedures.sql
│
├── powerbi/
│   └── Healthcare_Intelligence.pbix
│
├── excel/
│   └── Healthcare_Dashboard.xlsx
│
├── assets/
│   ├── logo.png
│   ├── banner.png
│   ├── architecture.png
│   └── screenshots/
│
└── README.md
```

---

# PostgreSQL Data Warehouse

### Star Schema Design

<img src="assets/screenshots/schema.png" width="100%"/>

## Fact Table

| Table | Description |
|-------|-------------|
| fact_patients | 55,000+ Patient Records |

## Dimension Tables

| Table | Description |
|-------|-------------|
| dim_hospital | Hospital Information |
| dim_doctor | Doctor Information |
| dim_insurance | Insurance Providers |

## Analytical Views

- vw_dashboard_summary
- vw_revenue_trend
- vw_hospital_performance
- vw_disease_distribution

---

# ETL Pipeline

<img src="assets/screenshots/etl_pipeline.png" width="100%"/>

### Features

- CSV ingestion.
- Data Cleaning.
- Feature Engineering.
- Duplicate Handling.
- PostgreSQL Bulk Loading.
- Automated Refresh.
- Admin Center ETL Execution.

### ETL Workflow

```text
Raw CSV
   │
Cleaning & Validation
   │
Transformation
   │
Feature Engineering
   │
PostgreSQL Warehouse
```

---

# Streamlit Enterprise Application

<img src="assets/screenshots/streamlit_home.png" width="100%"/>

## Modules

### Executive Dashboard

<img src="assets/screenshots/executive_dashboard.png"/>

**Features**

- Revenue KPIs
- Patient KPIs
- LOS Analysis
- Disease Distribution
- Admission Trends
- Hospital Revenue
- Interactive Filters

---

### Patient Analytics Dashboard

<img src="assets/screenshots/patient_dashboard.png"/>

**Features**

- Demographics
- Age Analysis
- Blood Group Distribution
- Medication Trends
- Clinical Insights
- Billing Distribution

---

### Hospital Analytics Dashboard

<img src="assets/screenshots/hospital_dashboard.png"/>

**Features**

- Top Performing Hospitals
- Doctor Performance
- Revenue Contribution
- Admission Types
- LOS by Hospital

---

### AI Risk Dashboard

<img src="assets/screenshots/risk_dashboard.png"/>

**Features**

- Patient Risk Score
- Risk Gauge
- High Risk Patients
- Prediction History
- Confidence Analysis

---

### Patient Registration Portal

<img src="assets/screenshots/patient_registration.png"/>

**Features**

- Register New Patients.
- Live PostgreSQL Update.
- Dynamic Dropdowns.
- Recent Registrations.

---

### Admin Control Panel

<img src="assets/screenshots/admin_panel.png"/>

### Features

- SQL Console
- ETL Runner
- Power BI Launcher
- Excel Launcher
- AI Report Generator
- Activity Logs
- Database Monitoring

---

# Machine Learning Pipeline

<img src="assets/screenshots/ml_pipeline.png" width="100%"/>

## Model

**Random Forest Classifier**

### Features Used

| Feature | Description |
|----------|-------------|
| Age | Patient Age |
| Gender | Encoded Gender |
| Blood Type | Blood Group |
| Medical Condition | Disease |
| Admission Type | Emergency/Urgent/Elective |
| Test Results | Clinical Tests |
| Billing Amount | Financial Indicator |
| Length of Stay | Hospital Stay |

### Outputs

- Risk Category
- Risk Score (0–100)
- Prediction Confidence
- Feature Importance

---

### Model Performance

<img src="assets/screenshots/model_metrics.png" width="100%"/>

| Metric | Score |
|--------|-------|
| Accuracy | XX% |
| Weighted F1 Score | XX |
| Cross Validation Accuracy | XX |
| ROC-AUC | XX |

---

### Feature Importance

<img src="assets/screenshots/feature_importance.png"/>

Top Predictive Features

- Billing Amount
- Length of Stay
- Age
- Test Results
- Admission Type

---

# AI Integration (Gemini / OpenRouter)

<img src="assets/screenshots/ai_summary.png" width="100%"/>

### AI Features

- Healthcare Executive Summary
- Clinical Risk Analysis
- Revenue Insights
- Hospital Performance Summary
- Medication Insights
- Insurance Analysis

---

### AI Chat Assistant

<img src="assets/screenshots/ai_chat.png"/>

Ask questions like

```text
Top 5 hospitals by revenue.

Show abnormal test trends.

Which condition has highest billing?

Summarize patient admissions.
```

AI answers directly from PostgreSQL snapshot.

---

### AI PDF Report Generator

<img src="assets/screenshots/ai_report.png"/>

Automatically generates

- Executive Summary.
- Financial Summary.
- Clinical Insights.
- AI Recommendations.
- Risk Summary.

---

# Power BI Enterprise Dashboard

<img src="assets/screenshots/powerbi_cover.png" width="100%"/>

## Dashboard Pages

### Executive Command Center

<img src="assets/screenshots/powerbi_exec.png"/>

### KPIs

- Total Patients
- Revenue
- Avg Billing
- Avg LOS
- Hospitals
- Doctors
- Emergency Admissions
- Abnormal Tests

---

### Patient Analytics Dashboard

<img src="assets/screenshots/powerbi_patient.png"/>

Includes

- Population Pyramid.
- Age Distribution.
- Gender Analysis.
- Disease Heatmap.
- Medication Trends.

---

### Hospital Operations Dashboard

<img src="assets/screenshots/powerbi_hospital.png"/>

Includes

- Revenue by Hospital.
- Doctor Performance.
- LOS.
- Admission Types.
- Waterfall Revenue.

---

### Medication & Insurance Dashboard

<img src="assets/screenshots/powerbi_insurance.png"/>

Includes

- Insurance Distribution.
- Medication Frequency.
- Revenue by Provider.
- Disease vs Medication.

---

### AI Risk Intelligence Dashboard

<img src="assets/screenshots/powerbi_ai.png"/>

Includes

- Risk Gauge.
- High Risk Patients.
- Risk Scatter Plot.
- AI Narrative.
- Risk Trends.

---

# Excel Interactive Dashboard

<img src="assets/screenshots/excel_dashboard.png" width="100%"/>

### Workbook Contains

| Sheet | Description |
|-------|-------------|
| Raw Data | Imported PostgreSQL Dataset |
| Pivot Tables | Aggregated Analytics |
| Dashboard | Interactive KPIs |
| AI Risk | Risk Prediction Dashboard |

### Dashboard Features

- KPI Cards
- Pivot Charts
- Timeline Filters
- Slicers
- Conditional Formatting
- Dynamic Charts

---

# SQL Analytics

### Example Business Queries

```sql
Top Revenue Hospitals

Monthly Revenue Trend

Disease Distribution

Emergency Admission Rate

Insurance Revenue

Doctor Performance

Average Length of Stay
```

---

# Business KPIs

| KPI | Description |
|------|-------------|
| Total Patients | Overall Admissions |
| Total Revenue | Billing Revenue |
| Avg Billing | Revenue Per Patient |
| Avg LOS | Length of Stay |
| Emergency Rate | Emergency Admissions |
| Abnormal Tests | Clinical Risk |
| High Risk Patients | ML Output |
| Hospital Performance | Revenue + Patients |

---

# Key Business Insights

### Clinical Insights

- Disease prevalence.
- Abnormal Test Analysis.
- High Risk Identification.
- Admission Pattern Analysis.

### Financial Insights

- Revenue Trends.
- Hospital Revenue Ranking.
- Insurance Contribution.
- Billing Distribution.

### Operational Insights

- Hospital Utilization.
- Doctor Workload.
- Average LOS.
- Admission Categories.

---

# Security Features

- Environment Variables.
- PostgreSQL Authentication.
- SQLAlchemy Secure Connections.
- API Key Protection.
- Parameterized SQL Queries.

---

# Installation Guide

## Clone Repository

```bash
git clone https://github.com/yourusername/healthcare-intelligence-platform.git

cd healthcare-intelligence-platform
```

## Create Environment

```bash
python -m venv heal

heal\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment

Create **.env**

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password

GEMINI_API_KEY=your_api_key
OPENROUTER_API_KEY=your_api_key
```

## Run Application

```bash
streamlit run app.py
```

---

# Power BI Setup

1. Open **Healthcare_Intelligence.pbix**
2. Connect PostgreSQL.
3. Refresh Data.
4. Publish Dashboard.

---

# Excel Dashboard Setup

1. Open Healthcare_Dashboard.xlsx.
2. Refresh Pivot Tables.
3. Refresh All Charts.

---

# Deployment

### Streamlit Cloud

```bash
streamlit deploy app.py
```

### PostgreSQL

- Render PostgreSQL
- Supabase PostgreSQL

### Power BI

Publish to Power BI Service.

---

# Screenshots

<table>
<tr>
<td><img src="assets/screenshots/streamlit_home.png"/></td>
<td><img src="assets/screenshots/executive_dashboard.png"/></td>
</tr>

<tr>
<td><img src="assets/screenshots/powerbi_exec.png"/></td>
<td><img src="assets/screenshots/excel_dashboard.png"/></td>
</tr>

<tr>
<td><img src="assets/screenshots/ai_chat.png"/></td>
<td><img src="assets/screenshots/admin_panel.png"/></td>
</tr>

</table>

---

# Future Enhancements

- Real-time Streaming Data
- Appointment Prediction
- Disease Forecasting
- Hospital Occupancy Forecast
- LLM-powered Clinical Assistant
- Azure Deployment
- Microsoft Fabric Integration

---

# Author

## Aditya Kumar

**Aspiring Data Analyst | Business Intelligence Developer | AI Analytics Enthusiast**

### Skills

Python • SQL • PostgreSQL • Streamlit • Power BI • Excel • Machine Learning • AI • ETL • Data Warehousing

---

<div align="center">

### ⭐ If you like this project, don't forget to star the repository ⭐

Made with ❤️ using Python, SQL, AI & Business Intelligence.

</div>
