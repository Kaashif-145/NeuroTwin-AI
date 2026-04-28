import streamlit as st
import sys
import os
import time

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from model_training.topic_classifier_training import train_local_model
from model_training.difficulty_model_training import train_difficulty_model
from frontend.utils.i18n import _t

def show_train_ui():
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        if st.button(_t("go_login")):
            st.switch_page("pages/login.py")
        return

    st.title(f"🔋 {_t('nav_optimize')}")
    st.markdown(_t("train_description"))

    st.write("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/wired/128/artificial-intelligence.png", width=100)
        
    with col2:
        st.markdown("""
        ### Why train your Twin?
        - **Personalization**: Learns your specific vocabulary (e.g., Engineering, Medicine, Law).
        - **Precision**: Improves topic detection and recommendation accuracy.
        - **Active Recall**: Better synchronization between your notes and generated quizzes.
        """)

    st.markdown("### Ready to Learn?")
    if st.button("🚀 Train My Twin Now", use_container_width=True):
        with st.status("🧠 Twin is Learning...", expanded=True) as status:
            st.write("Analyzing your document database...")
            time.sleep(1)
            
            st.write("Extracting linguistic patterns...")
            time.sleep(1.5)
            
            st.write("Optimizing local classifier...")
            result_topic = train_local_model()
            
            st.write("Calibrating difficulty engine...")
            result_diff = train_difficulty_model()
            
            st.info(f"Topic Engine: {result_topic}")
            st.info(f"Difficulty Engine: {result_diff}")
            
            status.update(label="✅ Optimization Complete!", state="complete")
            
        st.success("Your Digital Twin has been successfully optimized based on your data.")
        st.balloons()

    st.markdown("---")
    st.warning("Note: Optimization works best when you have at least 5-10 processed documents in your database.")

if __name__ == "__main__":
    set_page_config(title="Train Twin - NeuroTwin AI")
    show_train_ui()
