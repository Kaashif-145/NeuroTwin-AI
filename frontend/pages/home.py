import streamlit as st
import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.utils.ui_components import set_page_config
from frontend.utils.i18n import _t

import datetime

def get_greeting_key():
    hour = datetime.datetime.now().hour
    if hour < 12: return "greeting_morning"
    elif hour < 17: return "greeting_afternoon"
    else: return "greeting_evening"

def show_home():
    # Welcome Banner logic
    email = st.session_state.get('user_email', 'Student')
    # Treat both the specific email and any 'verified_user' placeholder as Admin
    is_admin = email == "mattokaasif145@gmail.com" or "verified_user" in email.lower()
    user_display = "Admin" if is_admin else email.split('@')[0].capitalize()
    
    greeting_key = get_greeting_key()
    greeting = _t(greeting_key)
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1A1A2E 0%, #16213E 100%); 
                    padding: 50px; border-radius: 30px; color: white; margin-bottom: 35px;
                    border: 1px solid rgba(255,255,255,0.05);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);">
            <div style="display: inline-block; background: #0052FF; color: white; padding: 4px 12px; 
                        border-radius: 4px; font-weight: 700; font-size: 0.75rem; margin-bottom: 15px; 
                        letter-spacing: 1px; text-transform: uppercase;">
                {greeting}
            </div>
            <h1 style="color: #FFFFFF; margin-bottom: 8px; font-weight: 800; font-family: 'Outfit'; 
                       text-shadow: 0 4px 10px rgba(0,0,0,0.3); font-size: 3.2rem;">
                {_t('welcome_back')}, {user_display}! <span style="font-style: normal;">👋</span>
            </h1>
            <p style="font-size: 1.15rem; color: #AAA; font-weight: 400; letter-spacing: 0.5px;">
                {_t('home_subtitle')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate metrics from actual history data (filtered by user)
    history_file = os.path.join(project_root, "database", "upload_history.json")
    doc_count = 0
    completed_count = 0
    
    import json
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                full_history = json.load(f)
                # Admin (mattokaasif145@gmail.com) sees EVERYTHING. 
                # Others see only their own docs.
                if is_admin:
                    user_history = full_history
                else:
                    user_history = [item for item in full_history if item.get("user_email") == email]
                
                doc_count = len(user_history)
                completed_count = sum(1 for item in user_history if item.get("completed", False))
        except:
            pass
    
    progress = (completed_count / doc_count * 100) if doc_count > 0 else 0

    with col1:
        st.metric(label=_t('docs_processed'), value=str(doc_count))
    with col2:
        st.metric(label=_t('learn_progress'), value=f"{int(progress)}%")
    with col3:
        st.metric(label=_t('topics_mastered'), value=str(completed_count))

    st.markdown(f"### {_t('recent_activity')}")
    if doc_count > 0:
        st.success(_t('success_docs'))
        st.info(_t('info_concepts'))
    else:
        st.warning(_t('no_docs'))

if __name__ == "__main__":
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Please login to access this page.")
        if st.button("Go to Login"):
            st.switch_page("app.py")
    else:
        set_page_config(title="Home - NeuroTwin AI")
        show_home()
