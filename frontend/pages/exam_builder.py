import streamlit as st
import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from frontend.utils.i18n import _t

def show_exam_builder():
    set_page_config(title="Exam Builder - NeuroTwin AI", show_header=False)
    
    st.title("📝 AI Exam Builder")
    st.markdown("Generate professional-grade descriptive examination papers from your study materials.")

    if not st.session_state.get('descriptive_paper'):
        st.warning("⚠️ No exam paper found. Please upload and process a document in the 'Library' first.")
        if st.button("Go to Library"):
            st.switch_page("pages/upload_page.py")
        return

    st.success("✅ Your AI-Generated Exam Paper is ready!")
    
    # Header Info
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Subject:** {st.session_state.get('processed_filename', 'General Knowledge')}")
        st.write(f"**Level:** {st.session_state.get('doc_level', 'Intermediate')}")
    with col2:
        st.write("**Duration:** 3 Hours (Recommended)")
        st.write("**Total Marks:** 100")

    st.markdown("---")
    
    # Render Questions
    for i, item in enumerate(st.session_state.descriptive_paper):
        with st.container(border=True):
            st.markdown(f"#### Question {i+1}")
            st.markdown(f"**{item['question']}**")
            
            with st.expander("🔍 View Ideal Answer Key"):
                st.info(item['answer_key'])
            
            st.markdown("<div style='text-align: right;'><small>10 Marks</small></div>", unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Export Options
    st.subheader("📦 Export Exam")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.button("Print Paper (PDF)", use_container_width=True)
    with col_ex2:
        st.button("Share with Students", use_container_width=True)

if __name__ == "__main__":
    show_exam_builder()
