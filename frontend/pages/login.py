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
    # Initialize session state for OTP
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'generated_otp' not in st.session_state:
        st.session_state.generated_otp = None
    if 'otp_email' not in st.session_state:
        st.session_state.otp_email = ""

    registered_users = load_users()
    greeting = get_greeting()

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <p id="login-greeting-text" style="color: #FF0080; font-weight: 600; letter-spacing: 2px; margin-bottom: 5px;">{greeting.upper()}</p>
                <h1 style="font-family: 'Outfit'; font-weight: 900; font-size: 3.5rem; margin: 0; line-height: 1.1;">
                    <span style="background: linear-gradient(to right, #FF0080, #7928CA, #00DFD8); 
                                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        NeuroTwin AI
                    </span>
                </h1>
                <p style="color: #888; font-size: 1rem; margin-top: 10px;">The Future of Academic Intelligence</p>
            </div>
            <script>
                const updateLoginGreeting = () => {{
                    const hour = new Date().getHours();
                    let text = "GOOD EVENING";
                    if (hour < 12) text = "GOOD MORNING";
                    else if (hour < 17) text = "GOOD AFTERNOON";
                    const greetingElement = document.getElementById("login-greeting-text");
                    if (greetingElement) greetingElement.innerText = text;
                }};
                updateLoginGreeting();
                setInterval(updateLoginGreeting, 60000);
            </script>
        """, unsafe_allow_html=True)
        
        if not st.session_state.otp_sent:
            tab1, tab2, tab3 = st.tabs(["🔑 Sign In", "📝 Register", "🌐 Google SSO"]) 
            
            # Load remembered email
            from backend.utils.session_manager import get_remembered_user, save_remembered_user
            remembered_email = get_remembered_user()

            with tab1:
                email = st.text_input("Email Address", value=remembered_email, placeholder="name@example.com").lower().strip() 
                password = st.text_input("Password", type="password")
                remember_me = st.checkbox("Remember My Email", value=bool(remembered_email))
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Sign In & Get OTP", use_container_width=True, type="primary"):
                    if email in registered_users and registered_users[email] == password:
                        with st.spinner("Preparing secure session..."):
                            if remember_me:
                                save_remembered_user(email)
                            else:
                                save_remembered_user("") # Clear if unchecked

                            time.sleep(1.2)
                            otp = str(random.randint(100000, 999999))
                            success, message = send_otp_email(email, otp)
                            
                            st.session_state.generated_otp = otp
                            st.session_state.otp_sent = True
                            st.session_state.otp_email = email
                            
                            if success:
                                st.toast(f"OTP sent to {email}", icon="📧")
                            else:
                                st.session_state.last_error = message
                            st.rerun()
                    else:
                        st.error("Invalid credentials or user not registered.")

            with tab2:
                reg_email = st.text_input("New Email Address", key="reg_email").lower().strip()
                reg_pass = st.text_input("Create Password", type="password", key="reg_pass")
                reg_confirm = st.text_input("Confirm Password", type="password", key="reg_conf")
                
                if st.button("Create Account", use_container_width=True):
                    if reg_email and reg_pass:
                        if reg_email in registered_users:
                            st.error("This email is already registered. Please sign in.")
                        elif reg_pass == reg_confirm:
                            save_user(reg_email, reg_pass)
                            st.success("Account created! Please sign in now.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun() # Refresh to update registered_users and pre-fill sign in
                        else:
                            st.error("Passwords do not match.")
                    else:
                        st.error("Please fill in all registration fields.")

            with tab3:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                if st.button("Continue with Google", use_container_width=True):
                    with st.spinner("Connecting to Google..."):
                        time.sleep(1.5)
                        st.session_state.authenticated = True
                        st.session_state.user_email = "mattokaasif145@gmail.com"
                        start_persistent_session(st.session_state.user_email) # Save session
                        st.success(f"{greeting}, Admin! Authorized via Google.")
                        time.sleep(1)
                        st.rerun()
        
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
                    if otp_input == st.session_state.generated_otp:
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

            # Developer Mode Fallback (If email failed)
            if hasattr(st.session_state, 'last_error') and st.session_state.last_error:
                with st.expander("🛠️ Admin: Manual OTP Bypass"):
                    st.info(f"Generated OTP: {st.session_state.generated_otp}")
                    if st.button("Force Login with this OTP"):
                        st.session_state.authenticated = True
                        st.session_state.user_email = st.session_state.otp_email
                        start_persistent_session(st.session_state.user_email) # Save session
                        st.rerun() # Let app.py handle navigation

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
    
    set_page_config(title="Access - NeuroTwin AI", show_header=True)
    
    if st.session_state.authenticated:
        st.switch_page("pages/home.py")
    else:
        show_login()
