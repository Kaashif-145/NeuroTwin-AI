import streamlit as st
import pandas as pd
import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import plotly.express as px
from frontend.utils.ui_components import set_page_config
from frontend.utils.i18n import _t

def show_progress():
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        if st.button(_t("go_login")):
            st.switch_page("pages/login.py")
        return

    st.title(f"📈 {_t('nav_progress')}")
    st.markdown("Deep dive into your educational development timeline.")

    # Mock historical data - Updated to 2026 range
    data = {
        'Date': pd.date_range(start='2026-03-20', periods=30, freq='D'),
        'Mastery Level': [20, 35, 45, 60, 80, 85, 90, 110, 115, 120, 135, 150, 155, 160, 175, 190, 195, 200, 215, 230, 245, 260, 265, 275, 280, 295, 310, 320, 335, 350],
        'Concepts Mastered': [5, 8, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 60, 62, 65, 68, 70, 72, 75, 78, 80]
    }
    df = pd.DataFrame(data)

    st.markdown("### 🕒 Mastery Velocity Curve")
    fig_study = px.line(df, x='Date', y='Mastery Level', title="Knowledge Mastery Trend (2026)", template='plotly_dark')
    fig_study.update_traces(line_color='#00ffff') # Cyan theme
    st.plotly_chart(fig_study, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏅 Achievements")
        st.success("🔥 7-Day Study Streak!")
        st.info("🎓 50 Concepts Mastered!")
        st.warning("⏰ 100+ Hours Spent Researching!")

    with col2:
        st.markdown("### 🎯 Weekly Goals")
        st.write("Complete NLP Module: [====================] 100%")
        st.write("Process 5 New Papers: [============--------] 60%")
        st.write("Update Digital Twin: [==================--] 90%")

if __name__ == "__main__":
    set_page_config(title="Progress - NeuroTwin AI")
    show_progress()
