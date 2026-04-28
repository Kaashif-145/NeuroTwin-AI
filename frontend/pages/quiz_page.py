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

def show_quiz_page():
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        return

    st.title(f"🎯 {_t('quiz_title')}")
    st.markdown(_t('quiz_desc'))

    if 'current_quiz_sets' not in st.session_state or not st.session_state.current_quiz_sets:
        st.info("No quiz found. Please upload a document to generate quizzes automatically!")
        return

    quiz_sets = st.session_state.current_quiz_sets
    
    # Robust type checking for session state compatibility
    if not isinstance(quiz_sets, dict):
        quiz_sets = {_t("mastery"): quiz_sets}
        
    # Translate keys if they are defaults
    display_sets = {}
    for k, v in quiz_sets.items():
        if k == "Mastery Challenge": display_sets[_t("mastery")] = v
        elif k == "Foundation Quiz": display_sets[_t("foundation")] = v
        else: display_sets[k] = v

    selected_set_name = st.selectbox(f"🎯 {_t('choose_lang')}", options=list(display_sets.keys()))
    quiz_data = display_sets[selected_set_name]
    
    if st.session_state.get('active_quiz_name') != selected_set_name:
        st.session_state.active_quiz_name = selected_set_name
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False

    # Store user answers in session state
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    score = 0
    submitted = st.session_state.get('quiz_submitted', False)

    for i, item in enumerate(quiz_data):
        st.markdown(f"### Q{i+1}: {item['question']}")
        
        # Determine current selection
        current_selection = st.session_state.user_answers.get(i, None)
        
        if submitted:
            # Show correct/incorrect feedback
            selected = st.radio(f"Select an answer for Q{i+1}", options=item['options'], 
                               index=item['options'].index(current_selection) if current_selection else 0,
                               key=f"q_{i}", disabled=True)
            if selected == item['answer']:
                st.success(f"Correct! ({item['answer']})")
                score += 1
            else:
                st.error(f"Incorrect. The correct answer was: {item['answer']}")
        else:
            selected = st.radio(f"Select an answer for Q{i+1}", options=item['options'], 
                               index=0, key=f"q_{i}")
            st.session_state.user_answers[i] = selected

    if not submitted:
        if st.button(_t("submit"), use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
    else:
        st.markdown(f"## 🏁 {_t('score')}: {score} / {len(quiz_data)}")
        if st.button(_t("reset"), use_container_width=True):
            st.session_state.quiz_submitted = False
            st.session_state.user_answers = {}
            st.rerun()

if __name__ == "__main__":
    set_page_config(title="AI Quiz - NeuroTwin AI")
    show_quiz_page()
