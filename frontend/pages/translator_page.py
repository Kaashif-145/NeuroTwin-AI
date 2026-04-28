import streamlit as st
from backend.services.translator import translate_text
from frontend.utils.i18n import _t

def show_translator():
    st.title("🌍 " + _t("nav_translator"))
    st.markdown("Instantly translate your study materials into your preferred language.", help="Powered by M2M100 Neural Machine Translation.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Source Text")
        source_text = st.text_area("Enter or paste text to translate:", height=300, placeholder="Paste your study notes or questions here...")
        
    with col2:
        st.subheader("Translation")
        
        # We can map Streamlit session lang state to the translation target by default
        available_langs = {
            "Hindi": "hi",
            "Punjabi": "pa",
            "Spanish": "es",
            "French": "fr",
            "English": "en"
        }
        
        # Try to find the default index based on the chosen language setting
        current_lang_code = st.session_state.get('target_lang', 'hi')
        default_idx = 0
        for i, (name, code) in enumerate(available_langs.items()):
            if code == current_lang_code:
                default_idx = i
                break
                
        target_lang_name = st.selectbox("Target Language", options=list(available_langs.keys()), index=default_idx)
        target_lang_code = available_langs[target_lang_name]
        
        # Read-only text area for output
        if st.button("Translate Text", use_container_width=True, type="primary"):
            if not source_text.strip():
                st.warning("Please enter some text to translate.")
            else:
                with st.spinner(f"Translating to {target_lang_name}..."):
                    try:
                        translated_result = translate_text(source_text, target_lang=target_lang_code)
                        st.success("Translation Complete!")
                        st.info(translated_result)
                    except Exception as e:
                        st.error(f"Error during translation: {e}")
        else:
            st.info("Translation will appear here.")

show_translator()
