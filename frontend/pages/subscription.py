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

def process_payment(plan_name, amount):
    """Simulates a secure Razorpay/UPI checkout flow with dynamic fields."""
    st.markdown("---")
    st.subheader(f"💳 Checkout: {plan_name}")
    st.write(f"Amount to pay: **₹{amount}**")
    
    # Selection outside form triggers immediate rerun/update of fields below
    method = st.radio("Select Payment Method", ["UPI (GPay / PhonePe)", "Credit/Debit Card", "NetBanking"], horizontal=True)
    
    with st.form(key=f"checkout_form_{plan_name}"):
        if method == "UPI (GPay / PhonePe)":
            st.markdown("#### 📱 UPI Payment")
            st.text_input("Enter UPI ID (e.g., user@okaxis)")
            st.write("OR")
            st.info("💡 You can also scan the QR code in the next step.")
            
        elif method == "Credit/Debit Card":
            st.markdown("#### 💳 Card Details")
            st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX")
            c1, c2 = st.columns(2)
            c1.text_input("Expiry", placeholder="MM/YY")
            c2.text_input("CVV", type="password", placeholder="***")
            
        elif method == "NetBanking":
            st.markdown("#### 🏦 Select Bank")
            st.selectbox("Choose your bank", ["SBI", "HDFC", "ICICI", "Axis", "Kotak"])
            
        submitted = st.form_submit_button(f"Securely Pay ₹{amount}")
        
        if submitted:
            with st.spinner("🔒 Connecting to Razorpay secure gateway..."):
                import time
                time.sleep(2)
                st.session_state.active_plan = plan_name
                st.success(f"🎉 Payment Successful! Your {plan_name} is now active.")
                st.balloons()
                # Clear checkout state
                if 'checkout_plan' in st.session_state:
                    del st.session_state.checkout_plan
                time.sleep(1)
                st.rerun()

def show_subscription():
    if 'active_plan' not in st.session_state:
        st.session_state.active_plan = "Free"

    st.title("💎 Premium Subscriptions & Plans")
    st.markdown(f"Current Plan: **{st.session_state.active_plan}**")
    
    st.markdown("""
        <style>
        .payment-icons {
            font-size: 1.5rem;
            margin-top: 10px;
            opacity: 0.8;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cloudflare Global Network Banner
    st.markdown("""
        <div style="background: rgba(243, 128, 32, 0.1); border: 1px solid #F38020; border-radius: 12px; padding: 15px; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 2rem;">⚡</span>
                <div>
                    <h4 style="margin: 0; color: #F38020;">Accelerated by Cloudflare Global Edge</h4>
                    <p style="margin: 0; font-size: 0.85rem; color: #ccc;">Your data is processed and delivered via Cloudflare's 300+ global data centers for ultra-low latency.</p>
                </div>
            </div>
            <div class="cloudflare-badge">🛡️ Cloudflare Protected</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="cloudflare-badge" style="background: #333;">CF-STATIC</div>
            <h3>🌱 Basic Scholar</h3>
            <h2 style="color: #00ffcc;">₹29 <small>/month</small></h2>
            <p>Perfect for starting your study journey.</p>
            <div class="payment-icons">📱 💳 🏦</div>
            <ul>
                <li>✅ <b>20 Documents / Day</b></li>
                <li>✅ Detailed AI Explanations</li>
                <li>✅ Cloudflare Optimized Delivery</li>
                <li>✅ Exam Prep Glossary</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Basic Plan", use_container_width=True, key="btn_rural"):
            st.session_state.checkout_plan = ("Basic Scholar", 29)

    with col2:
        st.markdown("""
        <div class="pricing-card" style="border: 2px solid #F38020;">
            <div class="cloudflare-badge">MOST POPULAR</div>
            <h3>🏢 Advanced Learner</h3>
            <h2 style="color: #F38020;">₹99 <small>/month</small></h2>
            <p>Full depth analysis for dedicated students.</p>
            <div class="payment-icons">💳 📱 🏦</div>
            <ul>
                <li>✅ <b>90 Documents / Day</b></li>
                <li>✅ <b>Priority Cloudflare CDN</b></li>
                <li>✅ Multi-Slide Concept Deep Dives</li>
                <li>✅ Unlimited Knowledge Bases</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Advanced Plan", use_container_width=True, key="btn_urban"):
            st.session_state.checkout_plan = ("Advanced Learner", 99)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <div class="cloudflare-badge" style="background: #a29bfe;">CF-ENTERPRISE</div>
            <h3>🤝 Master & Sponsor</h3>
            <h2 style="color: #a29bfe;">₹299 <small>/month</small></h2>
            <p>Empower yourself & sponsor a peer.</p>
            <div class="payment-icons">🏦 💳 📱</div>
            <ul>
                <li>✅ <b>Unlimited Power</b></li>
                <li>✅ <b>Sponsor 1 Student in Need</b></li>
                <li>✅ <b>Enterprise Cloudflare WAF</b></li>
                <li>✅ Exclusive Mentor Badge</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Become a Sponsor", use_container_width=True, key="btn_sponsor"):
            st.session_state.checkout_plan = ("Socio Sponsor", 299)

    # Handle Checkout UI
    if 'checkout_plan' in st.session_state:
        plan_name, amount = st.session_state.checkout_plan
        process_payment(plan_name, amount)

    st.markdown("""
        <div class="cloudflare-footer">
            <p>Security and Performance by <a href="#" class="cloudflare-link">Cloudflare</a></p>
            <p style="font-size: 0.7rem;">Dashboard is secured by Cloudflare Web Application Firewall (WAF) and SSL/TLS Encryption.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    set_page_config(title="Subscription - NeuroTwin AI")
    show_subscription()
