import streamlit as st
import json
import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import plotly.express as px
import pandas as pd
from frontend.utils.ui_components import set_page_config

PROFILE_PATH = "database/profiles.json"

from frontend.utils.i18n import _t

def show_dashboard():
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        if st.button(_t("go_login")):
            st.switch_page("pages/login.py")
        return

    st.title(f"🧠 {_t('nav_dashboard')}")
    st.markdown(_t('dashboard_desc'))

    profile_data = st.session_state.get('profile_data', None)
    
    if not profile_data and os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r") as f:
                profile_data = json.load(f)
        except:
            profile_data = None
        
    if profile_data:
        # Load history for completion status
        history_file = "database/upload_history.json"
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
            if history:
                total = len(history)
                completed = sum(1 for item in history if item.get("completed", False))
                rate = completed / total
                
                st.markdown("### 🎯 Study Goal Progress")
                col_prog1, col_prog2 = st.columns([3, 1])
                with col_prog1:
                    st.progress(rate, text=f"{completed}/{total} Documents Completed")
                with col_prog2:
                    st.metric("Completion Rate", f"{int(rate*100)}%")
                st.markdown("---")

        df = pd.DataFrame(list(profile_data.items()), columns=['Topic', 'Count'])
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### 📊 {_t('topic_mastery_chart')}")
            fig = px.bar(df, x='Topic', y='Count', 
                        color='Count', 
                        color_continuous_scale='Viridis',
                        template='plotly_dark')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"### 🥧 {_t('concept_dist_chart')}")
            fig_pie = px.pie(df, values='Count', names='Topic', 
                            template='plotly_dark')
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown(f"### 📈 {_t('recent_progress_chart')}")
        st.info("💡 **Mastery Velocity**: This chart tracks how your Digital Twin's unique knowledge base is expanding day-by-day. Use this to maintain study momentum for your upcoming exams!")
        
        # Mock timeline data - Synchronized to 2026
        timeline_data = {
            'Date': pd.date_range(start='2026-03-10', periods=len(df), freq='D'),
            'Mastery': df['Count'].cumsum()
        }
        df_line = pd.DataFrame(timeline_data)
        fig_line = px.line(df_line, x='Date', y='Mastery', markers=True, template='plotly_dark')
        fig_line.update_traces(line_color='#00ffff') # Cyan for mastery
        st.plotly_chart(fig_line, use_container_width=True)
        
    else:
        st.info(_t("no_docs"))

if __name__ == "__main__":
    set_page_config(title="Dashboard - NeuroTwin AI")
    show_dashboard()
