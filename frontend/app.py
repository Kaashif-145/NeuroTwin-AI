import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

# Add the project root to sys.path for proper module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from backend.utils.firebase_init import initialize_firebase
from frontend.utils.i18n import _t
from backend.utils.session_manager import get_persistent_session, start_persistent_session

def main():
    # Set page config and inject CSS
    set_page_config(title="NeuroTwin AI", icon="🧠", show_header=True)
    
    # Initialize Firebase
    initialize_firebase()
    
    # Initialize session state for auth
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        # Check for persistent session (survives refresh)
        saved_email = get_persistent_session()
        if saved_email:
            st.session_state.authenticated = True
            st.session_state.user_email = saved_email
        else:
            st.session_state.authenticated = False
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'target_lang' not in st.session_state:
        st.session_state.target_lang = 'en'

    if not st.session_state.authenticated:
        from frontend.pages.login import show_login
        show_login()
    else:
        # Define Navigation using external page files with dynamic translation
        pages = {
            _t("nav_main"): [
                st.Page("pages/home.py", title=_t("nav_home"), icon="🏠", default=True),
                st.Page("pages/subscription.py", title=_t("nav_subscription"), icon="💎"),
                st.Page("pages/export_page.py", title=_t("nav_export"), icon="📦"),
            ],
            _t("nav_assistant"): [
                st.Page("pages/upload_page.py", title=_t("nav_upload"), icon="📄"),
                st.Page("pages/digital_twin_dashboard.py", title=_t("nav_dashboard"), icon="🧠"),
                st.Page("pages/translator_page.py", title=_t("nav_translator"), icon="🌍"),
                st.Page("pages/chat_assistant.py", title=_t("nav_chat"), icon="💬"),
            ],
            _t("nav_learning"): [
                st.Page("pages/quiz_page.py", title=_t("nav_quiz"), icon="🎯"),
                st.Page("pages/flashcard_ui.py", title=_t("nav_flashcards"), icon="🎴"),
                st.Page("pages/recommendation_page.py", title=_t("nav_recommendations"), icon="💡"),
                st.Page("pages/progress_tracking.py", title=_t("nav_progress"), icon="📈"),
                st.Page("pages/train_ui.py", title=_t("nav_optimize"), icon="🔋"),
            ],
            _t("nav_career"): [
                st.Page("pages/cv_ats_checker.py", title=_t("nav_resume"), icon="📄"),
                st.Page("pages/code_hub.py", title=_t("nav_code"), icon="💻"),
            ]
        }
        
        pg = st.navigation(pages, position="top")
        
        with st.sidebar:
            st.markdown("---")
            if st.button("Logout", use_container_width=True, type="primary"):
                from backend.utils.session_manager import end_persistent_session
                end_persistent_session()
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.otp_sent = False
                st.session_state.generated_otp = None
                st.session_state.otp_email = ""
                st.rerun()
                
        pg.run()

# Streamlit runs this file as a module (not __main__),
# so main() must be called at module level to render the app.
main()
