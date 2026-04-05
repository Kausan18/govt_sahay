import streamlit as st
from api_client import call

st.set_page_config(page_title="Your Profile — YojanaConnect", page_icon="👤", layout="centered")

# Auth guard
if "user_id" not in st.session_state:
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #F7F4EF; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.page-header {
    padding: 36px 0 24px;
}
.step-bar {
    display: flex;
    gap: 6px;
    margin-bottom: 20px;
}
.step { height: 4px; flex: 1; border-radius: 2px; background: #E2E5EF; }
.step.done { background: #138808; }
.step.active { background: #FF9933; }

.page-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.9rem;
    font-weight: 600;
    color: #1A1F3C;
    margin-bottom: 6px;
}
.page-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    color: #8A90A2;
    margin-bottom: 32px;
}
.section-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #A0A6BA;
    margin: 24px 0 12px;
}
div[data-testid="stSelectbox"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 10px !important;
    border: 1.5px solid #E2E5EF !important;
    background: #fff !important;
    font-size: 0.95rem !important;
}
div[data-testid="stSelectbox"] > div:focus-within,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #FF9933 !important;
    box-shadow: 0 0 0 3px rgba(255,153,51,0.10) !important;
}
.stButton > button {
    background: #1A1F3C !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 12px 32px !important;
    border: none !important;
}
.stButton > button:hover { background: #FF9933 !important; color: #1A1F3C !important; }
label { font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; color: #4A5068 !important; }
</style>

<div class="page-header">
    <div class="step-bar">
        <div class="step active"></div>
        <div class="step"></div>
        <div class="step"></div>
        <div class="step"></div>
    </div>
    <div class="page-title">Set up your profile</div>
    <div class="page-sub">This helps us find schemes you're actually eligible for. All fields required.</div>
</div>
""", unsafe_allow_html=True)

# Load existing profile if present
existing = {}
try:
    res = call("/profile/get-profile", {"user_id": st.session_state["user_id"]})
    if res.get("profile"):
        existing = res["profile"]
except:
    pass

with st.form("profile_form"):
    st.markdown('<div class="section-label">Personal details</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full name", value=existing.get("name", ""), placeholder="As per Aadhaar")
    with col2:
        age = st.number_input("Age", min_value=1, max_value=120, value=int(existing.get("age", 25)))

    col3, col4 = st.columns(2)
    with col3:
        gender = st.selectbox("Gender", ["male", "female", "other"],
                              index=["male","female","other"].index(existing.get("gender","male")))
    with col4:
        religion = st.selectbox("Religion", ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"],
                                index=["Hindu","Muslim","Christian","Sikh","Buddhist","Jain","Other"].index(
                                    existing.get("religion","Hindu")))

    st.markdown('<div class="section-label">Social & economic background</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        caste = st.selectbox("Caste category", ["General", "OBC", "SC", "ST", "EWS"],
                             index=["General","OBC","SC","ST","EWS"].index(existing.get("caste","General")))
    with col6:
        income = st.number_input("Annual income (₹)", min_value=0, step=5000,
                                 value=int(existing.get("income", 0)),
                                 help="Enter your approximate yearly household income")

    st.markdown('<div class="section-label">Location & occupation</div>', unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    with col7:
        states = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
                  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
                  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
                  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
                  "Uttarakhand","West Bengal","Delhi","Jammu & Kashmir","Ladakh","Puducherry"]
        state_idx = states.index(existing.get("state", "Karnataka")) if existing.get("state") in states else 0
        state = st.selectbox("State / UT", states, index=state_idx)
    with col8:
        occupations = ["Student", "Farmer", "Agricultural Laborer", "Daily Wage Worker", "Self-employed",
                       "Private Sector Employee", "Government Employee", "Business Owner",
                       "Homemaker", "Unemployed", "Retired", "Other"]
        occ_idx = occupations.index(existing.get("occupation","Student")) if existing.get("occupation") in occupations else 0
        occupation = st.selectbox("Occupation", occupations, index=occ_idx)

    submitted = st.form_submit_button("Save profile & continue →", use_container_width=True)

if submitted:
    with st.spinner("Saving your profile..."):
        try:
            call("/profile/save-profile", {
                "user_id": st.session_state["user_id"],
                "name": name, "caste": caste, "age": age,
                "occupation": occupation, "religion": religion,
                "income": income, "state": state, "gender": gender
            })
            # Store in session for later use
            st.session_state["profile"] = {
                "name": name, "caste": caste, "age": age, "occupation": occupation,
                "religion": religion, "income": income, "state": state, "gender": gender
            }
            st.success("Profile saved!")
            st.switch_page("pages/2_locker.py")
        except Exception as e:
            st.error(f"Could not save profile: {e}")