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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

[data-testid="stAppViewContainer"] {
    background: #FAFAF8;
    min-height: 100vh;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
[data-testid="stDecoration"] { display: none; }
.stApp { background: #FAFAF8; }

/* ── hero section ── */
.hero {
    padding: 64px 0 40px;
    text-align: center;
}
.tricolor {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    margin-bottom: 36px;
}
.tri-s { width: 56px; height: 7px; background: #FF9933; border-radius: 4px 0 0 4px; }
.tri-w { width: 56px; height: 7px; background: #ffffff; border: 1px solid #e5e5e3; }
.tri-g { width: 56px; height: 7px; background: #138808; border-radius: 0 4px 4px 0; }
.chakra {
    width: 14px; height: 14px;
    border: 2px solid #000080;
    border-radius: 50%;
    position: absolute;
    margin-left: 64px;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 700;
    color: #1C1C1A;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 14px;
}
.hero-title span { color: #138808; }
.hero-sub {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem;
    color: #6B6B65;
    font-weight: 400;
    max-width: 440px;
    margin: 0 auto 48px;
    line-height: 1.65;
}

/* ── auth card ── */
.auth-card {
    background: #ffffff;
    border: 1px solid #E8E8E3;
    border-radius: 20px;
    padding: 44px 48px;
    max-width: 440px;
    margin: 0 auto;
    box-shadow: 0 4px 32px rgba(0,0,0,0.06);
}
.auth-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #A0A09A;
    margin-bottom: 6px;
}
.auth-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: #1C1C1A;
    margin-bottom: 6px;
}
.auth-sub {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.88rem;
    color: #8A8A84;
    margin-bottom: 28px;
}

/* ── inputs ── */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #3A3A38 !important;
    margin-bottom: 6px !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #1C1C1A !important;
    background: #F9F9F7 !important;
    border: 1.5px solid #E2E2DC !important;
    border-radius: 12px !important;
    padding: 13px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #138808 !important;
    box-shadow: 0 0 0 3px rgba(19,136,8,0.10) !important;
    background: #fff !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #C0C0BA !important; }

/* selectbox */
div[data-testid="stSelectbox"] > div > div {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #1C1C1A !important;
    background: #F9F9F7 !important;
    border: 1.5px solid #E2E2DC !important;
    border-radius: 12px !important;
}

/* ── buttons ── */
.stButton > button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    padding: 13px 28px !important;
    border: none !important;
    background: #1C1C1A !important;
    color: #ffffff !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #138808 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(19,136,8,0.25) !important;
}

/* ── trust bar ── */
.trust-bar {
    display: flex;
    justify-content: center;
    gap: 36px;
    margin-top: 48px;
    flex-wrap: wrap;
}
.trust-item {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.82rem;
    color: #8A8A84;
    display: flex;
    align-items: center;
    gap: 7px;
}
.trust-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #138808;
    flex-shrink: 0;
}

/* alerts */
.stAlert {
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
</style>

<div class="hero">
    <div class="tricolor">
        <div class="tri-s"></div>
        <div class="tri-w"></div>
        <div class="tri-g"></div>
    </div>
    <div class="hero-title">Yojana<span>Connect</span></div>
    <div class="hero-sub">Discover every government scheme you qualify for — matched to your profile, verified, and explained simply.</div>
</div>

<div class="auth-card">
    <div class="auth-label">Get started</div>
    <div class="auth-title">Enter your email</div>
    <div class="auth-sub">No password needed. We'll find or create your account instantly.</div>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div style="max-width:440px;margin:0 auto;padding:0 0 8px">', unsafe_allow_html=True)
    email = st.text_input("Email address", placeholder="you@example.com", label_visibility="collapsed")
    if st.button("Continue →", use_container_width=True):
        if not email or "@" not in email:
            st.error("Please enter a valid email address.")
        else:
            with st.spinner("Signing you in..."):
                try:
                    res = call("/auth/simple-login", {"email": email})
                    st.session_state["user_id"] = res["user_id"]
                    st.session_state["email"] = email
                    st.switch_page("pages/1_profile.py")
                except Exception as e:
                    st.error(f"Login failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="trust-bar">
    <span class="trust-item"><span class="trust-dot"></span> 1,000+ schemes indexed</span>
    <span class="trust-item"><span class="trust-dot"></span> AI-powered matching</span>
    <span class="trust-item"><span class="trust-dot"></span> Secure &amp; private</span>
</div>
""", unsafe_allow_html=True)