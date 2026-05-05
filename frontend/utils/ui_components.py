import os

import streamlit as st

from frontend.utils.doc_manager import (
    get_active_doc_panel,
    has_active_docs,
    remove_doc,
    restore_uploaded_docs,
)
from frontend.utils.i18n import _t


def inject_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.error(f"CSS file not found at {css_path}")
    
    # Inject MathJax for better formula rendering
    st.markdown("""
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <script>
            window.MathJax = {
              tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true
              }
            };
        </script>
    """, unsafe_allow_html=True)


def inject_pwa_meta():
    """Injects PWA and Mobile-specific meta tags to allow 'Add to Home Screen' functionality."""
    st.markdown("""
        <script>
            // Create a dynamic PWA manifest
            const manifest = {
                "name": "NeuroTwin AI Platform",
                "short_name": "NeuroTwin",
                "description": "The Future of Academic Intelligence",
                "start_url": ".",
                "display": "standalone",
                "background_color": "#0E1117",
                "theme_color": "#6C5CE7",
                "orientation": "portrait",
                "icons": [
                    {
                        "src": "https://raw.githubusercontent.com/Kaashif-145/NeuroTwin-AI/main/icon.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "any maskable"
                    }
                ]
            };
            
            const stringManifest = JSON.stringify(manifest);
            const blob = new Blob([stringManifest], {type: 'application/json'});
            const manifestURL = URL.createObjectURL(blob);
            
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = manifestURL;
            document.head.appendChild(link);

            // Apple iOS specific tags
            const metaApple = document.createElement('meta');
            metaApple.name = 'apple-mobile-web-app-capable';
            metaApple.content = 'yes';
            document.head.appendChild(metaApple);

            const metaStatus = document.createElement('meta');
            metaStatus.name = 'apple-mobile-web-app-status-bar-style';
            metaStatus.content = 'black-translucent';
            document.head.appendChild(metaStatus);
            
            const metaTitle = document.createElement('meta');
            metaTitle.name = 'apple-mobile-web-app-title';
            metaTitle.content = 'NeuroTwin';
            document.head.appendChild(metaTitle);
        </script>
    """, unsafe_allow_html=True)


def set_page_config(title="NeuroTwin AI", icon="🧪", show_header=False):
    try:
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="collapsed", # Collapse sidebar for Top Nav feel
        )
    except:
        # Page config can only be set once, ignore subsequent calls
        pass
        
    inject_custom_css()
    inject_pwa_meta()
    
    # Use a session state flag that we'll check, but we need to reset it 
    # at the start of the main app.py run.
    # For now, let's just use the show_header parameter.
    if show_header:
        render_top_navigation()

def render_top_navigation():
    """Adds a futuristic top navigation bar with language switcher to the application."""
    # Top Branding Bar
    st.markdown("""
        <style>
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 20px;
        }
        .logo-area {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .actions-area {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .deploy-btn {
            background: #6C5CE7 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 5px 20px !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    header_col1, header_col2 = st.columns([2, 1])
    
    with header_col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;">
                <span style="font-size: 1.8rem;">🧠</span>
                <span style="font-weight: 800; font-size: 1.4rem; letter-spacing: 1px; font-family: 'Outfit';">
                    NEUROTWIN <span style="color: #00D2D3;">AI</span>
                </span>
            </div>
        """, unsafe_allow_html=True)
        
    with header_col2:
        # Action Bar in Top Right
        act_col1, act_col2, act_col3 = st.columns([1.5, 1, 0.3])
        
        with act_col1:
            languages = {
                "English": "en",
                "Hindi": "hi",
                "Punjabi": "pa",
                "Spanish": "es",
                "French": "fr",
            }
            lang_list = list(languages.keys())
            current_lang = next((name for name, code in languages.items() if code == st.session_state.get('target_lang', 'en')), "English")
            selected_lang = st.selectbox("Lang", options=lang_list, index=lang_list.index(current_lang), label_visibility="collapsed", key="top_nav_lang")
            if languages[selected_lang] != st.session_state.get('target_lang'):
                st.session_state.target_lang = languages[selected_lang]
                st.rerun()
        
        with act_col2:
            st.button("Deploy", use_container_width=True, type="primary")
            
        with act_col3:
            st.markdown("<div style='font-size: 1.5rem; padding-top: 5px;'>⋮</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin-top: 0; margin-bottom: 25px; opacity: 0.1;'>", unsafe_allow_html=True)
    
    # Navigation Links - Final Comprehensive Map
    pages_links = {
        "🏠 HOME": "pages/home.py",
        "📂 LIBRARY": "pages/upload_page.py",
        "📄 ROAST 🔥": "pages/cv_ats_checker.py",
        "💻 CODE": "pages/code_hub.py",
        "📝 EXAMS": "pages/exam_builder.py",
        "📊 DECKS": "pages/presentation_creator.py",
        "🧠 TWIN": "pages/digital_twin_dashboard.py",
        "💬 CHAT": "pages/chat_assistant.py",
        "🌍 TRANSLATE": "pages/translator_page.py",
        "📈 PROGRESS": "pages/progress_tracking.py",
        "💎 PLANS": "pages/subscription.py",
    }
    
    # Custom CSS for the top nav buttons - High Fidelity Quantum Design
    st.markdown("""
        <style>
        /* Force single line for the entire nav block */
        [data-testid="stHorizontalBlock"] {
            gap: 0.3rem !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            padding-bottom: 10px !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.1) 0%, rgba(0, 209, 255, 0.1) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #E0E0E0 !important;
            font-size: 0.62rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px !important;
            transition: all 0.3s ease !important;
            height: 42px !important;
            padding: 0 8px !important;
            backdrop-filter: blur(8px) !important;
            white-space: nowrap !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            animation: breathing-glow 3s infinite ease-in-out !important;
        }
        
        /* The Eye-Catching Breathing Glow */
        @keyframes breathing-glow {
            0% { border-color: rgba(108, 92, 231, 0.2); box-shadow: 0 0 5px rgba(108, 92, 231, 0.1); }
            50% { border-color: rgba(0, 209, 255, 0.5); box-shadow: 0 0 15px rgba(0, 209, 255, 0.2); }
            100% { border-color: rgba(108, 92, 231, 0.2); box-shadow: 0 0 5px rgba(108, 92, 231, 0.1); }
        }

        .stButton > button:hover {
            animation: none !important;
            border-color: #00D1FF !important;
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.3) 0%, rgba(0, 209, 255, 0.3) 100%) !important;
            box-shadow: 0 0 20px rgba(0, 209, 255, 0.5) !important;
            transform: translateY(-2px) !important;
            color: #FFFFFF !important;
        }

        /* Active State */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6C5CE7 0%, #00D1FF 100%) !important;
            border: none !important;
            box-shadow: 0 0 15px rgba(108, 92, 231, 0.6) !important;
            color: white !important;
        }

        /* Hide Streamlit default button padding */
        .stButton > button div p {
            margin: 0 !important;
            white-space: nowrap !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render Buttons in Columns
    nav_cols = st.columns(len(pages_links))
    for i, (label, path) in enumerate(pages_links.items()):
        with nav_cols[i]:
            # Simple check to highlight the 'Active' page
            is_active = False
            # Check if current path is in the button path
            if path == "app.py" and st.session_state.get("auth_redirect") == "home":
                is_active = True
            
            if st.button(label, key=f"top_nav_{i}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.switch_page(path)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


def render_sidebar_settings():
    restore_uploaded_docs()

    if has_active_docs():
        st.sidebar.markdown("---")
        actions = get_active_doc_panel(
            key_prefix="sidebar_docs",
            show_manage_button=True,
            in_sidebar=True,
            show_action_buttons=False,
        )

        if actions["remove_doc"]:
            removed = remove_doc(actions["remove_doc"])
            if removed and st.session_state.get("uploaded_docs"):
                st.session_state.docs_need_reprocess = True
            st.switch_page("pages/upload_page.py")

    st.sidebar.markdown("---")
    st.sidebar.subheader(f"🌐 {_t('lang_settings')}")
    languages = {
        "English": "en",
        "Hindi (हिन्दी)": "hi",
        "Punjabi (ਪੰਜਾਬੀ)": "pa",
        "Spanish (Español)": "es",
        "French (Français)": "fr",
    }

    lang_list = list(languages.keys())
    current_lang_code = st.session_state.get("target_lang", "en")
    current_index = 0
    for i, code in enumerate(languages.values()):
        if code == current_lang_code:
            current_index = i
            break

    selected_lang_name = st.sidebar.selectbox(
        _t("choose_lang"),
        options=lang_list,
        index=current_index,
    )
    new_lang_code = languages[selected_lang_name]

    if st.session_state.get("target_lang") != new_lang_code:
        st.session_state.target_lang = new_lang_code
        st.rerun()
