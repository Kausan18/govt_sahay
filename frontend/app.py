import streamlit as st
from api_client import call

st.set_page_config(
    page_title="YojanaConnect — Find Your Schemes",
    page_icon="🇮🇳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] {
    background: #F7F4EF;
}
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.hero-wrap {
    text-align: center;
    padding: 56px 0 32px;
}
.flag-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    margin-bottom: 28px;
}
.flag-saffron { width: 48px; height: 6px; background: #FF9933; border-radius: 3px 0 0 3px; }
.flag-white   { width: 48px; height: 6px; background: #fff; border: 1px solid #eee; }
.flag-green   { width: 48px; height: 6px; background: #138808; border-radius: 0 3px 3px 0; }

.app-title {
    font-family: 'Noto Serif', serif;
    font-size: 2.6rem;
    font-weight: 600;
    color: #1A1F3C;
    line-height: 1.15;
    margin-bottom: 10px;
}
.app-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.05rem;
    color: #5A6072;
    font-weight: 300;
    margin-bottom: 40px;
}
.card {
    background: #fff;
    border-radius: 16px;
    padding: 36px 40px;
    box-shadow: 0 2px 24px rgba(26,31,60,0.07);
    max-width: 440px;
    margin: 0 auto;
}
.card-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.3rem;
    color: #1A1F3C;
    margin-bottom: 6px;
}
.card-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    color: #8A90A2;
    margin-bottom: 28px;
}
.trust-row {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin-top: 40px;
    flex-wrap: wrap;
}
.trust-item {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    color: #8A90A2;
    display: flex;
    align-items: center;
    gap: 6px;
}
.trust-dot { width: 6px; height: 6px; border-radius: 50%; background: #138808; display: inline-block; }
div[data-testid="stTextInput"] input {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 10px !important;
    border: 1.5px solid #E2E5EF !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    background: #FAFAF8 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #FF9933 !important;
    box-shadow: 0 0 0 3px rgba(255,153,51,0.12) !important;
}
.stButton > button {
    width: 100%;
    background: #1A1F3C !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 13px 0 !important;
    border: none !important;
    letter-spacing: 0.02em;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #FF9933 !important;
    color: #1A1F3C !important;
}
.stAlert { border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; }
</style>

<div class="hero-wrap">
    <div class="flag-bar">
        <div class="flag-saffron"></div>
        <div class="flag-white"></div>
        <div class="flag-green"></div>
    </div>
    <div class="app-title">YojanaConnect</div>
    <div class="app-sub">Discover government schemes you're eligible for — verified, ranked, and explained simply.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Continue with your email</div>', unsafe_allow_html=True)
st.markdown('<div class="card-sub">No password needed. We\'ll find or create your account.</div>', unsafe_allow_html=True)

email = st.text_input("Email address", placeholder="you@example.com", label_visibility="collapsed")

if st.button("Continue →"):
    if not email or "@" not in email:
        st.error("Please enter a valid email address.")
    else:
        with st.spinner("Signing you in..."):
            try:
                res = call("/auth/simple-login", {"email": email})
                st.session_state["user_id"] = res["user_id"]
                st.session_state["email"] = email
                st.success("Welcome! Redirecting to your profile...")
                st.switch_page("pages/1_profile.py")
            except Exception as e:
                st.error(f"Login failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="trust-row">
    <span class="trust-item"><span class="trust-dot"></span> 1,000+ schemes indexed</span>
    <span class="trust-item"><span class="trust-dot"></span> AI-powered matching</span>
    <span class="trust-item"><span class="trust-dot"></span> Secure & private</span>
</div>
""", unsafe_allow_html=True)