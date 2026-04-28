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

def show_flashcard_ui():
    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access this page.")
        return

    st.title(f"🎴 {_t('flash_title')}")
    st.markdown(_t('flash_desc'))

    if 'current_flashcards' not in st.session_state or not st.session_state.current_flashcards:
        st.info("No flashcards found. Please upload a document to generate them automatically!")
        return

    cards = st.session_state.current_flashcards
    
    if 'card_index' not in st.session_state:
        st.session_state.card_index = 0
    if 'card_flipped' not in st.session_state:
        st.session_state.card_flipped = False

    idx = st.session_state.card_index
    card = cards[idx]

    # Display Progress
    st.progress((idx + 1) / len(cards))
    st.write(f"Card {idx + 1} of {len(cards)}")

    # Flashcard CSS for Flip Animation (simplified for Streamlit)
    st.markdown("""
        <style>
        .flashcard {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 50px;
            text-align: center;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            border: 2px solid rgba(0, 255, 255, 0.3);
            margin-bottom: 20px;
            transition: transform 0.6s;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render Card
    display_text = card['back'] if st.session_state.card_flipped else card['front']
    label = _t("next") if st.session_state.card_flipped else _t("prev") # Or use specific Front/Back keys if added
    # Let's use generic FRONT/BACK if not in i18n, or add them. I'll use placeholders for now or just the keys.
    label = "BACK" if st.session_state.card_flipped else "FRONT"
    
    st.markdown(f"""
        <div class="flashcard">
            <div>
                <small style='opacity: 0.5;'>[{label}]</small><br>
                {display_text}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(f"⬅️ {_t('prev')}") and st.session_state.card_index > 0:
            st.session_state.card_index -= 1
            st.session_state.card_flipped = False
            st.rerun()
            
    with col2:
        if st.button(f"🔄 {_t('flip')}"):
            st.session_state.card_flipped = not st.session_state.card_flipped
            st.rerun()
            
    with col3:
        if st.button(f"{_t('next')} ➡️") and st.session_state.card_index < len(cards) - 1:
            st.session_state.card_index += 1
            st.session_state.card_flipped = False
            st.rerun()

    st.markdown("---")
    if st.button(_t("reset")):
        st.session_state.card_index = 0
        st.session_state.card_flipped = False
        st.rerun()

if __name__ == "__main__":
    set_page_config(title="Flashcards - NeuroTwin AI")
    show_flashcard_ui()
