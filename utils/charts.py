import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ==========================================================
# ENTERPRISE HEALTHCARE PLOTLY THEME
# ==========================================================

PRIMARY = "#2563EB"
SECONDARY = "#06B6D4"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
DANGER = "#DC2626"
PURPLE = "#7C3AED"

CHART_COLORS = [
    PRIMARY,
    SECONDARY,
    SUCCESS,
    WARNING,
    DANGER,
    PURPLE,
    "#0EA5E9",
    "#14B8A6",
]

PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"


def apply_theme(fig, title=""):

    fig.update_layout(
        title=dict(
            text=title,
            x=0.02,
            font=dict(size=20, color="white"),
        ),
        font=dict(
            family="Inter",
            color="white"
        ),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        colorway=CHART_COLORS,
        margin=dict(l=20, r=20, t=55, b=20),
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=13,
            font_family="Inter"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        color="#CBD5E1"
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.08)",
        zeroline=False,
        color="#CBD5E1"
    )

    return fig


# ==========================================================
# 1. REVENUE TREND AREA CHART
# ==========================================================

def revenue_trend_chart(df):

    trend = (
        df.groupby("admission_month", as_index=False)["billing_amount"]
        .sum()
        .sort_values("admission_month")
    )

    fig = px.area(
        trend,
        x="admission_month",
        y="billing_amount",
        markers=True,
    )

    fig.update_traces(
        line=dict(width=3),
        fill="tozeroy",
    )

    return apply_theme(fig, "Monthly Revenue Trend")


# ==========================================================
# 2. GENDER DONUT CHART
# ==========================================================

def gender_donut(df):

    gender = (
        df.groupby("gender", as_index=False)
        .size()
        .rename(columns={"size": "patients"})
    )

    fig = px.pie(
        gender,
        names="gender",
        values="patients",
        hole=0.68,
    )

    fig.update_traces(
        textinfo="percent+label",
        pull=[0.03, 0.03],
    )

    return apply_theme(fig, "Gender Distribution")


# ==========================================================
# 3. DISEASE BAR CHART
# ==========================================================

def disease_bar(df):

    disease = (
        df.groupby("medical_condition", as_index=False)
        .size()
        .rename(columns={"size": "patients"})
        .sort_values("patients", ascending=False)
    )

    fig = px.bar(
        disease,
        x="patients",
        y="medical_condition",
        orientation="h",
        text="patients",
        color="patients",
        color_continuous_scale="Blues",
    )

    fig.update_layout(coloraxis_showscale=False)

    return apply_theme(fig, "Top Medical Conditions")


# ==========================================================
# 4. BILLING DISTRIBUTION HISTOGRAM
# ==========================================================

def billing_distribution(df):

    fig = px.histogram(
        df,
        x="billing_amount",
        nbins=30,
        opacity=.9,
    )

    fig.update_traces(marker_line_width=0)

    return apply_theme(fig, "Billing Amount Distribution")


# ==========================================================
# 5. ADMISSION TYPE DONUT
# ==========================================================

def admission_donut(df):

    admission = (
        df.groupby("admission_type", as_index=False)
        .size()
        .rename(columns={"size": "patients"})
    )

    fig = px.pie(
        admission,
        names="admission_type",
        values="patients",
        hole=.65,
    )

    fig.update_traces(textinfo="percent+label")

    return apply_theme(fig, "Admission Type Distribution")


# ==========================================================
# 6. LENGTH OF STAY BOXPLOT
# ==========================================================

def stay_boxplot(df):

    fig = px.box(
        df,
        x="medical_condition",
        y="length_of_stay",
        color="medical_condition",
        points="outliers",
    )

    fig.update_layout(showlegend=False)

    return apply_theme(fig, "Length of Stay by Medical Condition")