import streamlit as st


def render_footer():

    html = """
    <div class="footer-wrapper">

        <div class="footer">

            <div class="footer-title">
                Healthcare Intelligence & Risk Analytics Platform
            </div>

            <div class="footer-desc">
                Enterprise Healthcare Analytics • PostgreSQL • Machine Learning • AI Insights • Streamlit • Power BI
            </div>

            <div class="footer-divider"></div>

            <div class="footer-bottom">

                <div class="footer-copy">
                    © 2026 Healthcare Intelligence Platform • Built by Aditya Sharma
                </div>

                <div class="footer-badge">
                    Version 2.0 Enterprise Edition
                </div>

            </div>

        </div>

    </div>
    """

    # ✅ Streamlit 1.49+ HTML renderer
    st.html(html)