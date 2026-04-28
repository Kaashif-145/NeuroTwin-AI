import streamlit as st
import os
import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from frontend.utils.export_manager import create_project_zip
from frontend.utils.i18n import _t

def show_export_page():
    set_page_config(title="Download Website - NeuroTwin AI")
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                    padding: 40px; border-radius: 20px; color: white; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem;">📦 Download Full Website</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">Export your entire project as a compressed ZIP file.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("This will package the source code, frontend, and backend assets into a single ZIP file for backup or deployment.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/fluency/144/archive.png", width=120)
        
    with col2:
        st.markdown("### Package Details")
        st.markdown("""
        - **Source Code**: Included
        - **Frontend Components**: Included
        - **Backend Services**: Included
        - **Dependencies**: Included (requirements.txt)
        - **Personal Data**: Excluded (.env)
        """)
        
        if st.button("🔍 Prepare Package", type="primary", use_container_width=True):
            with st.spinner("Compressing project files..."):
                zip_data = create_project_zip(project_root)
                st.session_state.zip_data = zip_data
                st.success("✅ Package ready for download!")
        
        if 'zip_data' in st.session_state:
            st.download_button(
                label="📥 Download ZIP Now",
                data=st.session_state.zip_data,
                file_name="NeuroTwin-AI-Full-Project.zip",
                mime="application/zip",
                use_container_width=True
            )

if __name__ == "__main__":
    show_export_page()
