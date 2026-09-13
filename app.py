import streamlit as st

from components.sidebar import render_sidebar
from dashboard.Medication_Safety_Hub import medication_safety_dashboard
from dashboard.Patient_Registration_Page import patient_registration_dashboard
from dashboard.Patient_Analytics_Dashboard import patient_analytics_dashboard
from dashboard.Hospital_Operations_System import hospital_operations_dashboard
from dashboard.Risk_Analytics_Dashboard import risk_dashboard
from dashboard.Executive_Command_Center import executive_command_center
from dashboard.Admin_Control_Panel import admin_center
from components.footer import render_footer

st.set_page_config(
    page_title="Healthcare Intelligence Platform",
    page_icon="🏥",
    layout="wide",
)

with open("assets/styles.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

page, year, gender, condition = render_sidebar()

st.title("Healthcare Intelligence & Risk Analytics Platform")
st.caption("PostgreSQL • Streamlit • Plotly • Machine Learning")

if page == "Executive Command Center":
    executive_command_center()

elif page == "Patient_Registration_Page":
    patient_registration_dashboard()
elif page == "Patient_Analytics_Dashboard":
    patient_analytics_dashboard()

elif page == "Hospital_Operations_System":
    hospital_operations_dashboard()

elif page == "Medication_Safety_Hub":
    medication_safety_dashboard()

elif page == "Risk_Analytics_Dashboard":
    risk_dashboard()

elif page == "Admin Control Panel":
    admin_center()

else:
    st.info("This dashboard will be added in the next phase.")

render_footer()