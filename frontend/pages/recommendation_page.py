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

def show_recommendations():
    if not st.session_state.get('authenticated', False):
        st.warning(_t("Please login to access this page."))
        if st.button(_t("Go to Login")):
            st.switch_page("pages/login.py")
        return

    st.title(f"💡 {_t('nav_recommendations')}")
    st.markdown(_t("Personalized study paths based on your topic mastery."))

    # In a real app, this would call backend/services/recommendation_engine.py
    # For now, we'll show some smart placeholders.
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("### 📚 Focus Areas")
            st.warning("Low Mastery: Quantum Algorithms")
            st.info("Improvement Needed: Tensor Calculus")
            st.success("Mastered: Python Data Structures")

    with col2:
        st.markdown("### 🛠️ Recommended Actions")
        if st.button("Review Latest Summary", use_container_width=True):
            st.switch_page("pages/upload_page.py")
        if st.button("Take a Quiz Challenge", use_container_width=True):
            st.switch_page("pages/quiz_page.py")
        if st.button("Explore Dashboard", use_container_width=True):
            st.switch_page("pages/digital_twin_dashboard.py")

    st.markdown("---")
    st.markdown("### 🧭 Learning Path")
    st.markdown("""
    1. **Fundamental Mathematics** - 100% Complete
    2. **Quantum Mechanics Basics** - 65% Complete
    3. **Advanced Quantum Computing** - 10% Complete
    """)
    st.progress(0.45)

if __name__ == "__main__":
    set_page_config(title="Recommendations - NeuroTwin AI")
    show_recommendations()
