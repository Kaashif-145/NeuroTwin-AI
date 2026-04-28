import streamlit as st
import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from backend.services.cv_analyzer import analyze_cv_ats, get_skill_gap_scores
from backend.services.document_loader import load_document
from frontend.utils.i18n import _t
import plotly.graph_objects as go

def show_radar_chart(scores):
    categories = list(scores.keys())
    values = list(scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Profile',
        line_color='#FF416C',
        fillcolor='rgba(255, 65, 108, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#888")
            ),
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.2)",
                linecolor="rgba(255, 255, 255, 0.2)",
                tickfont=dict(color="#ccc")
            )
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=350
    )

    st.plotly_chart(fig, use_container_width=True)

def show_cv_checker():
    st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h1 style="font-family: 'Outfit'; font-weight: 900; font-size: 3rem; margin: 0; line-height: 1.1;">
                <span style="background: linear-gradient(to right, #FF4B2B, #FF416C); 
                             -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🔥 The Resume Roast
                </span>
            </h1>
            <p style="color: #888; font-size: 1.2rem; margin-top: 5px;">Brutally Honest Recruiter Analysis</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💀 Stop Guessing. Get the Hard Truth.")
    st.markdown("Most recruiters spend 6 seconds on a CV. We'll give you the harsh, unfiltered reality of what they *really* think about your profile. No sugarcoating, just the gaps you need to fix to get hired.")

    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📤 Upload Your Resume")
        uploaded_file = st.file_uploader("Upload PDF or DOCX version of your CV", type=["pdf", "docx"])
        
        if uploaded_file:
            # Save temporarily
            temp_path = os.path.join("data", f"temp_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🔥 Roast My Resume"):
                with st.spinner("Our AI recruiters are reviewing your profile..."):
                    text = load_document(temp_path)
                    result = analyze_cv_ats(text)
                    gap_scores = get_skill_gap_scores(text)
                    st.session_state.last_cv_result = result
                    st.session_state.last_cv_gap_scores = gap_scores
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

    with col2:
        st.subheader("📈 Professional Standing")
        if "last_cv_result" in st.session_state:
            res = st.session_state.last_cv_result
            st.metric("ATS Compatibility Score", f"{res['score']}%")
            st.progress(res['score'] / 100)
            
            st.markdown("### 🏢 Recommended Companies")
            for comp in res['companies']:
                st.success(f"**{comp}**")
            
            if "last_cv_gap_scores" in st.session_state:
                st.markdown("---")
                st.markdown("### 📊 Mastery Heatmap")
                show_radar_chart(st.session_state.last_cv_gap_scores)
        else:
            st.info("Upload and analyze your CV to see your score.")

    if "last_cv_result" in st.session_state:
        st.markdown("---")
        st.subheader("📑 Expert Recruiter Analysis")
        st.markdown(st.session_state.last_cv_result['analysis'])

if __name__ == "__main__":
    set_page_config(title="Career Launchpad - NeuroTwin AI")
    show_cv_checker()
