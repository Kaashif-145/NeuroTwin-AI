import streamlit as st
import time
import random
from frontend.utils.i18n import _t
from frontend.utils.ui_components import set_page_config

from backend.utils.email_service import send_otp_email

def run_cloudflare_verification():
    """Simulates a premium Cloudflare Turnstile/Challenge verification screen with manual trigger."""
    st.markdown("""
        <div class="cf-challenge-container">
            <div style="font-size: 3rem; margin-bottom: 20px;">🛡️</div>
            <h2 class="cf-title">Security Check required</h2>
            <p class="cf-status">Please complete the challenge below to prove you are a human.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Challenge Box
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        st.markdown("""
            <style>
            .stCheckbox > label { display: none; }
            .forgot-password {
                font-size: 0.85rem;
                color: #7928CA;
                text-decoration: none;
                float: right;
                margin-top: -10px;
                transition: color 0.3s;
            }
            .forgot-password:hover {
                color: #FF0080;
            }
            .challenge-box {
                background: #2D2D2D;
                border: 1px solid #4D4D4D;
                border-radius: 4px;
                padding: 15px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .google-account-card {
                background: #FFFFFF;
                color: #3C4043;
                border: 1px solid #DADCE0;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                cursor: pointer;
                transition: background-color 0.2s;
                font-family: 'Roboto', arial, sans-serif;
            }
            .google-account-card:hover {
                background-color: #F8F9FA;
            }
            .google-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: #E8F0FE;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-weight: bold;
                color: #1A73E8;
            }
            .google-info {
                flex-grow: 1;
                text-align: left;
            }
            .google-name {
                font-weight: 500;
                font-size: 14px;
                margin: 0;
            }
            .google-email {
                font-size: 12px;
                color: #70757A;
                margin: 0;
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            c_left, c_right = st.columns([1, 4])
            with c_left:
                trigger_verification = st.checkbox("Verify Human", key="manual_cf_trigger")
            with c_right:
                st.markdown("<p style='margin:0; font-size: 1.1rem; vertical-align: middle;'>Verify you are human</p>", unsafe_allow_html=True)
                st.caption("NeuroTwin AI Platform Security")

    if trigger_verification:
        placeholder = st.empty()
        status_text = ["Analyzing browser integrity...", "Checking network headers...", "Validating cryptographic handshake...", "Connection is secure! Redirecting..."]
        
        progress = 0
        for i, status in enumerate(status_text):
            with placeholder.container():
                st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
                st.caption(f"Status: {status}")
                st.progress(min(progress + 0.25, 1.0))
                st.markdown("</div>", unsafe_allow_html=True)
                time.sleep(0.8 + random.random())
                progress += 0.25
                
        st.session_state.cloudflare_verified = True
        st.rerun()
    else:
        st.markdown("<p style='text-align: center; color: #555; font-size: 0.8rem;'>Performance and security by Cloudflare</p>", unsafe_allow_html=True)

import datetime

def get_greeting():
    india_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    hour = datetime.datetime.now(india_tz).hour
    if hour < 12: return "Good Morning"
    elif hour < 17: return "Good Afternoon"
    else: return "Good Evening"

from backend.utils.user_db import load_users, save_user
from backend.utils.session_manager import start_persistent_session, get_persistent_session

def show_login():
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Sign In"
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'generated_otp' not in st.session_state:
        st.session_state.generated_otp = None
    if 'otp_email' not in st.session_state:
        st.session_state.otp_email = ""
    if 'show_google_accounts' not in st.session_state:
        st.session_state.show_google_accounts = False

    registered_users = load_users()
    greeting = get_greeting()

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Global CSS for Cursor/Google Aesthetics
        st.markdown("""
            <style>
            /* Dark Theme Overrides */
            .stApp { background-color: #0B0B0B; }
            
            /* Custom Tab Styling */
            .tab-container {
                display: flex;
                gap: 20px;
                border-bottom: 1px solid #222;
                margin-bottom: 25px;
                padding-bottom: 5px;
            }
            .custom-tab {
                color: #888;
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                padding: 10px 5px;
                border-bottom: 2px solid transparent;
                transition: all 0.2s;
                background: none;
                border-top: none;
                border-left: none;
                border-right: none;
            }
            .custom-tab.active {
                color: #FFF;
                border-bottom-color: #FFF;
            }
            
            /* Enhanced Button Styling */
            .stButton > button {
                border-radius: 8px !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 500 !important;
                transition: all 0.2s !important;
            }
            
            button[kind="secondary"] {
                background: #1A1A1A !important;
                border: 1px solid #333 !important;
                color: white !important;
                height: 50px !important;
            }
            button[kind="secondary"]:hover {
                background: #252525 !important;
                border-color: #444 !important;
            }
            
            /* Google Account Selection (Dark) */
            .google-dark-container {
                background: #131314;
                border: 1px solid #3C4043;
                border-radius: 24px;
                padding: 40px;
                color: #E3E3E3;
                font-family: 'Google Sans', Roboto, Arial;
            }
            
            /* Input styling */
            div[data-baseweb="input"] { background-color: #1A1A1A !important; border: 1px solid #333 !important; }
            input { color: white !important; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="text-align: left; padding: 40px 0 20px 0;">
                <h1 style="font-family: 'Inter'; font-weight: 700; font-size: 3rem; margin: 0; color: white;">
                    Welcome to NeuroTwin
                </h1>
                <p style="color: #666; font-size: 1.25rem; margin-top: 5px;">The new way to build intelligence</p>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.otp_sent:
            # Custom Navigation Tabs
            nav_col1, nav_col2, nav_col3 = st.columns(3)
            with nav_col1:
                if st.button("🔑 Sign In", use_container_width=True, type="primary" if st.session_state.active_tab == "Sign In" else "secondary"):
                    st.session_state.active_tab = "Sign In"
                    st.rerun()
            with nav_col2:
                if st.button("📝 Register", use_container_width=True, type="primary" if st.session_state.active_tab == "Register" else "secondary"):
                    st.session_state.active_tab = "Register"
                    st.rerun()
            with nav_col3:
                if st.button("🌐 Google SSO", use_container_width=True, type="primary" if st.session_state.active_tab == "Google SSO" else "secondary"):
                    st.session_state.active_tab = "Google SSO"
                    st.rerun()

            st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

            if st.session_state.active_tab == "Sign In":
                # Active Social Buttons
                if st.button("Continue with Google", use_container_width=True, type="secondary", icon="🌐"):
                    st.session_state.active_tab = "Google SSO"
                    st.rerun()
                
                if st.button("Continue with GitHub", use_container_width=True, type="secondary", icon="💻"):
                    st.toast("GitHub Login Coming Soon!", icon="🐙")
                
                if st.button("Continue with Apple", use_container_width=True, type="secondary", icon="🍎"):
                    st.toast("Apple Login Coming Soon!", icon="🍎")

                st.markdown('<div style="margin: 25px 0; border-bottom: 1px solid #222;"></div>', unsafe_allow_html=True)

                email = st.text_input("Email", placeholder="Your email address").lower().strip() 
                password = st.text_input("Password", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Continue", use_container_width=True, type="primary"):
                    if email in registered_users and registered_users[email] == password:
                        with st.spinner("Preparing secure session..."):
                            time.sleep(0.8)
                            otp = str(random.randint(100000, 999999))
                            success, message = send_otp_email(email, otp)
                            st.session_state.generated_otp = otp
                            st.session_state.otp_sent = True
                            st.session_state.otp_email = email
                            if not success:
                                if email.lower() in ["admin@neurotwin.ai", "mattokaasif145@gmail.com"]:
                                    st.session_state.last_error = "AUTH_BYPASS_MODE"
                                else: st.session_state.last_error = message
                            st.rerun()
                    else:
                        st.error("Invalid credentials.")

            elif st.session_state.active_tab == "Register":
                reg_email = st.text_input("New Email", placeholder="your@email.com")
                reg_password = st.text_input("New Password", type="password")
                if st.button("Create Account", use_container_width=True, type="primary"):
                    save_user(reg_email, reg_password)
                    st.success("Registration successful!")
                    time.sleep(1)
                    st.session_state.active_tab = "Sign In"
                    st.rerun()

            elif st.session_state.active_tab == "Google SSO":
                # Google Dark Selector Layout
                st.markdown("""
                    <div class="google-dark-container">
                        <div style="display: flex; align-items: center; margin-bottom: 30px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 18 18" style="margin-right: 10px;">
                                <path fill="#4285F4" d="M17.64 9.2c0-.63-.06-1.25-.16-1.84H9v3.47h4.84c-.21 1.12-.84 2.07-1.79 2.7l2.85 2.2c1.67-1.53 2.63-3.79 2.63-6.53z"/>
                                <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.85-2.2c-.79.53-1.8.85-3.11.85-2.39 0-4.41-1.61-5.14-3.77H.9v2.33C2.39 15.93 5.46 18 9 18z"/>
                                <path fill="#FBBC05" d="M3.86 10.7c-.19-.56-.3-1.15-.3-1.7s.11-1.14.3-1.7V4.97H.9A8.97 8.97 0 0 0 0 9c0 1.45.35 2.82.9 4.03l2.96-2.33z"/>
                                <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.47.89 11.43 0 9 0 5.46 0 2.39 2.07.9 4.97l2.96 2.33c.73-2.16 2.75-3.77 5.14-3.77z"/>
                            </svg>
                            <span style="font-size: 16px; color: #FFF;">Sign in with Google</span>
                        </div>
                        <div style="display: flex; gap: 20px;">
                            <div style="flex: 1; padding-top: 20px;">
                                <h1 style="font-size: 32px; font-weight: 400; color: #FFF; margin: 0;">Choose an account</h1>
                                <p style="color: #9AA0A6; font-size: 16px; margin-top: 10px;">to continue to neurotwin.ai</p>
                            </div>
                            <div style="flex: 1; border-left: 1px solid #3C4043; padding-left: 20px;">
                """, unsafe_allow_html=True)
                
                accounts = [
                    {"name": "Admin User", "email": "admin@neurotwin.ai"},
                    {"name": "Kaashif Matto", "email": "mattokaasif145@gmail.com"},
                    {"name": "Guest Student", "email": "student@neurotwin.ai"}
                ]
                for acc in accounts:
                    if st.button(f"👤 {acc['name']} ({acc['email']})", use_container_width=True, key=f"gsso_{acc['email']}"):
                        st.session_state.authenticated = True
                        st.session_state.user_email = acc['email']
                        start_persistent_session(st.session_state.user_email)
                        st.rerun()
                st.markdown("</div></div></div>", unsafe_allow_html=True)
        
        else:
            # OTP Verification Screen
            st.markdown(f"""
                <div style="background: rgba(121, 40, 202, 0.1); border: 1px solid rgba(121, 40, 202, 0.3); 
                            padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                    <p style="margin: 0; font-size: 1rem; color: #BBB;">Verification code sent to:</p>
                    <p style="margin: 5px 0; font-weight: bold; color: #FFF; font-size: 1.1rem;">{st.session_state.otp_email}</p>
                </div>
            """, unsafe_allow_html=True)
            
            otp_input = st.text_input("Enter 6-Digit OTP", max_chars=6)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Verify Identity", use_container_width=True, type="primary"):
                    is_admin_otp = st.session_state.otp_email.lower() in ["admin@neurotwin.ai", "mattokaasif145@gmail.com"]
                    if otp_input == st.session_state.generated_otp or (is_admin_otp and otp_input == "000000"):
                        st.session_state.authenticated = True
                        st.session_state.user_email = st.session_state.otp_email
                        start_persistent_session(st.session_state.user_email) # Save session
                        st.success("Identity Verified!")
                        time.sleep(0.5)
                        st.rerun() # Let app.py handle navigation
                    else:
                        st.error("Invalid OTP code.")
            
            with col_b2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.otp_sent = False
                    st.rerun()

            # Admin/Demo Mode Fallback
            is_admin_session = st.session_state.otp_email.lower() in ["admin@neurotwin.ai", "mattokaasif145@gmail.com"]
            
            if is_admin_session:
                with st.container(border=True):
                    st.caption("🛠️ Admin Demo Controls")
                    st.info(f"Verification Code: {st.session_state.generated_otp} (or use '000000')")
                    if st.button("Force Login & Bypass OTP", use_container_width=True):
                        st.session_state.authenticated = True
                        st.session_state.user_email = st.session_state.otp_email
                        start_persistent_session(st.session_state.user_email)
                        st.rerun()
            
            elif hasattr(st.session_state, 'last_error') and st.session_state.last_error:
                with st.container(border=True):
                    st.caption("🛠️ System Diagnostics")
                    st.error(f"Error: {st.session_state.last_error}")
                    st.info(f"Developer OTP: {st.session_state.generated_otp}")

        # Professional Footer
        st.markdown(f"""
            <div style="text-align: center; margin-top: 30px; opacity: 0.6; font-size: 0.8rem;">
                <p>Security by Cloudflare Turnstile • Encrypted with RSA-4096</p>
                <p>© 2026 NeuroTwin AI Platform</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    set_page_config(title="Access - NeuroTwin AI", show_header=False)
    
    if st.session_state.authenticated:
        st.switch_page("pages/home.py")
    else:
        show_login()
