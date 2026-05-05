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

def show_deck_creator():
    set_page_config(title="Deck Creator - NeuroTwin AI", show_header=False)
    
    st.title("📊 AI Deck Creator")
    st.markdown("Transform your complex documents into beautiful, ready-to-present study decks.")

    if not st.session_state.get('last_ppt'):
        st.warning("⚠️ No presentation deck found. Please upload and process a document in the 'Library' first.")
        if st.button("Go to Library"):
            st.switch_page("pages/upload_page.py")
        return

    st.success("✨ Your Premium Presentation is ready for download!")
    
    # Preview Section
    st.markdown("""
        <div style="background: rgba(108, 92, 231, 0.1); padding: 40px; border-radius: 20px; text-align: center; border: 1px dashed rgba(108, 92, 231, 0.5);">
            <div style="font-size: 4rem;">📑</div>
            <h3>Study Deck: {filename}</h3>
            <p>15 High-Fidelity Slides Generated</p>
        </div>
    """.format(filename=st.session_state.get('processed_filename', 'Knowledge Base')), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎨 Design Features")
        st.write("✅ **Quantum Theme**: Deep space aesthetics applied.")
        st.write("✅ **Equation Support**: LaTeX formulas rendered.")
        st.write("✅ **Auto-Summary**: Slide titles and bullet points optimized.")
        st.write("✅ **Glossary**: Final slide includes key terminology.")

    with col2:
        st.markdown("### 📥 Download Options")
        ppt_path = st.session_state.last_ppt
        if os.path.exists(ppt_path):
            with open(ppt_path, "rb") as f:
                st.download_button(
                    "📥 Download PowerPoint (.pptx)",
                    f,
                    file_name=os.path.basename(ppt_path),
                    use_container_width=True,
                    type="primary"
                )
        
        st.button("🖼️ Export as Image Slides", use_container_width=True)

if __name__ == "__main__":
    show_deck_creator()
