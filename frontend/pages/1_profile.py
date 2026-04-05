import streamlit as st
from api_client import call

st.set_page_config(page_title="Profile — YojanaConnect", page_icon="👤", layout="centered")
if "user_id" not in st.session_state:
    st.switch_page("app.py")

COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
[data-testid="stAppViewContainer"] { background: #FAFAF8; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
.stApp { background: #FAFAF8; }

.pg-wrap { padding: 40px 0 20px; }
.step-track { display:flex; gap:6px; margin-bottom:28px; max-width:320px; }
.stp { height:4px; flex:1; border-radius:4px; background:#EBEBЕ6; }
.stp.done { background:#138808; }
.stp.now  { background:#FF9933; }

.pg-title {
    font-family:'Playfair Display',serif;
    font-size:2rem; font-weight:700; color:#1C1C1A;
    letter-spacing:-0.01em; margin-bottom:6px;
}
.pg-sub {
    font-family:'Plus Jakarta Sans',sans-serif;
    font-size:0.9rem; color:#8A8A84; margin-bottom:32px;
}
.sec-label {
    font-family:'Plus Jakarta Sans',sans-serif;
    font-size:0.7rem; font-weight:600; text-transform:uppercase;
    letter-spacing:0.12em; color:#B0B0AA; margin:28px 0 14px;
    display:flex; align-items:center; gap:10px;
}
.sec-label::after {
    content:''; flex:1; height:1px; background:#EBEBЕ6;
}

/* inputs */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.84rem !important; font-weight:500 !important;
    color:#3A3A38 !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.95rem !important; color:#1C1C1A !important;
    background:#fff !important;
    border:1.5px solid #E2E2DC !important;
    border-radius:12px !important; padding:12px 16px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color:#138808 !important;
    box-shadow:0 0 0 3px rgba(19,136,8,0.10) !important;
}
div[data-testid="stTextInput"] input::placeholder { color:#C8C8C2 !important; }

div[data-testid="stSelectbox"] > div > div {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.95rem !important; color:#1C1C1A !important;
    background:#fff !important;
    border:1.5px solid #E2E2DC !important;
    border-radius:12px !important;
}

/* form submit / buttons */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.95rem !important; font-weight:600 !important;
    border-radius:12px !important; padding:13px 28px !important;
    border:none !important;
    background:#1C1C1A !important; color:#fff !important;
    transition:all 0.2s !important;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    background:#138808 !important;
    box-shadow:0 6px 20px rgba(19,136,8,0.25) !important;
    transform:translateY(-1px) !important;
}
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
</style>
"""
st.markdown(COMMON_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="pg-wrap">
    <div class="step-track">
        <div class="stp now"></div>
        <div class="stp"></div>
        <div class="stp"></div>
        <div class="stp"></div>
    </div>
    <div class="pg-title">Your profile</div>
    <div class="pg-sub">Help us find schemes you're actually eligible for. Takes under 2 minutes.</div>
</div>
""", unsafe_allow_html=True)

existing = {}
try:
    res = call("/profile/get-profile", {"user_id": st.session_state["user_id"]})
    if res.get("profile"):
        existing = res["profile"]
except:
    pass

with st.form("profile_form"):
    st.markdown('<div class="sec-label">Personal details</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full name", value=existing.get("name",""), placeholder="As per Aadhaar")
    with c2:
        age = st.number_input("Age", min_value=1, max_value=120, value=int(existing.get("age", 25)))

    c3, c4 = st.columns(2)
    with c3:
        gender_opts = ["Male", "Female", "Other"]
        g_val = existing.get("gender", "Male")
        g_idx = next((i for i,v in enumerate(gender_opts) if v.lower()==g_val.lower()), 0)
        gender = st.selectbox("Gender", gender_opts, index=g_idx)
    with c4:
        rel_opts = ["Hindu","Muslim","Christian","Sikh","Buddhist","Jain","Other"]
        r_val = existing.get("religion","Hindu")
        r_idx = next((i for i,v in enumerate(rel_opts) if v==r_val), 0)
        religion = st.selectbox("Religion", rel_opts, index=r_idx)

    st.markdown('<div class="sec-label">Economic background</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        caste_opts = ["General","OBC","SC","ST","EWS"]
        ca_val = existing.get("caste","General")
        ca_idx = next((i for i,v in enumerate(caste_opts) if v==ca_val), 0)
        caste = st.selectbox("Caste category", caste_opts, index=ca_idx)
    with c6:
        income = st.number_input("Annual income (₹)", min_value=0, step=5000,
                                  value=int(existing.get("income",0)),
                                  help="Approximate yearly household income")

    st.markdown('<div class="sec-label">Location &amp; occupation</div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        states = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
                  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
                  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
                  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
                  "Uttarakhand","West Bengal","Delhi","Jammu & Kashmir","Ladakh","Puducherry"]
        s_val = existing.get("state","Karnataka")
        s_idx = states.index(s_val) if s_val in states else 10
        state = st.selectbox("State / UT", states, index=s_idx)
    with c8:
        occ_opts = ["Student","Farmer","Agricultural Laborer","Daily Wage Worker","Self-employed",
                    "Private Sector Employee","Government Employee","Business Owner",
                    "Homemaker","Unemployed","Retired","Other"]
        o_val = existing.get("occupation","Student")
        o_idx = occ_opts.index(o_val) if o_val in occ_opts else 0
        occupation = st.selectbox("Occupation", occ_opts, index=o_idx)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Save & continue →", use_container_width=True)

if submitted:
    with st.spinner("Saving your profile..."):
        try:
            call("/profile/save-profile", {
                "user_id": st.session_state["user_id"],
                "name": name, "caste": caste, "age": int(age),
                "occupation": occupation, "religion": religion,
                "income": int(income), "state": state, "gender": gender
            })
            st.session_state["profile"] = {
                "name": name, "caste": caste, "age": age,
                "occupation": occupation, "religion": religion,
                "income": income, "state": state, "gender": gender
            }
            st.switch_page("pages/2_locker.py")
        except Exception as e:
            st.error(f"Could not save profile: {e}")