import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Digital Locker — YojanaConnect", page_icon="🔒", layout="centered")
if "user_id" not in st.session_state:
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing:border-box; }
[data-testid="stAppViewContainer"] { background:#FAFAF8; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
.stApp { background:#FAFAF8; }

.pg-wrap { padding:40px 0 20px; }
.step-track { display:flex; gap:6px; margin-bottom:28px; max-width:320px; }
.stp { height:4px; flex:1; border-radius:4px; background:#E8E8E3; }
.stp.done { background:#138808; }
.stp.now  { background:#FF9933; }
.pg-title { font-family:'Playfair Display',serif; font-size:2rem; font-weight:700; color:#1C1C1A; margin-bottom:6px; }
.pg-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; color:#8A8A84; margin-bottom:32px; }

/* choice cards */
.choice-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:28px; }
.choice-card {
    background:#fff; border:2px solid #E8E8E3; border-radius:18px;
    padding:28px 24px; text-align:center; cursor:pointer;
    transition:all 0.2s;
}
.choice-card.active { border-color:#138808; background:#F5FCF4; }
.choice-card:hover { border-color:#138808; }
.choice-icon { font-size:2rem; margin-bottom:10px; }
.choice-title { font-family:'Playfair Display',serif; font-size:1rem; font-weight:700; color:#1C1C1A; margin-bottom:4px; }
.choice-desc { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.8rem; color:#8A8A84; line-height:1.5; }

/* doc upload cards */
.doc-row {
    background:#fff; border:1.5px solid #E8E8E3; border-radius:14px;
    padding:18px 20px; margin-bottom:10px;
    display:flex; align-items:flex-start; gap:14px;
}
.doc-icon { font-size:1.4rem; flex-shrink:0; margin-top:2px; }
.doc-info { flex:1; }
.doc-name { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.92rem; font-weight:600; color:#1C1C1A; margin-bottom:2px; }
.doc-hint { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.78rem; color:#A0A09A; }
.badge-done { background:#E8F7E8; color:#138808; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.72rem; font-weight:600; padding:3px 10px; border-radius:20px; display:inline-block; margin-top:4px; }

/* info box */
.info-box { background:#FFF8F0; border:1.5px solid #FFE4B8; border-radius:14px; padding:18px 22px; margin-bottom:20px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.88rem; color:#8B5E1A; line-height:1.6; }

/* file uploader */
[data-testid="stFileUploader"] {
    background:#F9F9F7 !important;
    border:1.5px dashed #D0D0CA !important;
    border-radius:12px !important;
    padding:8px !important;
}
[data-testid="stFileUploader"] label {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.84rem !important; color:#6B6B65 !important;
}

/* buttons */
.stButton > button {
    font-family:'Plus Jakarta Sans',sans-serif !important;
    font-size:0.95rem !important; font-weight:600 !important;
    border-radius:12px !important; padding:13px 28px !important;
    border:none !important; background:#1C1C1A !important; color:#fff !important;
    transition:all 0.2s !important;
}
.stButton > button:hover { background:#138808 !important; transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(19,136,8,0.25) !important; }
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
label { font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.84rem !important; color:#3A3A38 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pg-wrap">
    <div class="step-track">
        <div class="stp done"></div>
        <div class="stp now"></div>
        <div class="stp"></div>
        <div class="stp"></div>
    </div>
    <div class="pg-title">Digital locker</div>
    <div class="pg-sub">Upload your documents for faster verification, or skip and upload later per scheme.</div>
</div>
""", unsafe_allow_html=True)

if "locker_choice" not in st.session_state:
    st.session_state["locker_choice"] = None

col1, col2 = st.columns(2)
with col1:
    active1 = "active" if st.session_state["locker_choice"] == "upload" else ""
    st.markdown(f"""
    <div class="choice-card {active1}">
        <div class="choice-icon">📂</div>
        <div class="choice-title">Upload now</div>
        <div class="choice-desc">Faster verification. Documents pre-fill applications automatically.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Upload documents", key="btn_upload", use_container_width=True):
        st.session_state["locker_choice"] = "upload"
        st.rerun()

with col2:
    active2 = "active" if st.session_state["locker_choice"] == "skip" else ""
    st.markdown(f"""
    <div class="choice-card {active2}">
        <div class="choice-icon">⚡</div>
        <div class="choice-title">Skip for now</div>
        <div class="choice-desc">Browse schemes first. Upload documents when you're ready to apply.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Browse schemes", key="btn_skip", use_container_width=True):
        st.session_state["locker_choice"] = "skip"
        st.rerun()

DOCS = [
    ("aadhar", "📋", "Aadhaar Card",        "PDF / JPG / PNG — required for identity verification"),
    ("income", "💰", "Income Certificate",   "PDF / JPG / PNG — issued by a government officer"),
    ("caste",  "📄", "Caste Certificate",    "PDF / JPG / PNG — for SC / ST / OBC applicants"),
    ("dob",    "🎂", "Date of Birth Proof",  "PDF / JPG / PNG — birth certificate or Class 10 marksheet"),
    ("basic",  "📁", "Other Certificate",    "PDF / JPG / PNG — domicile, disability cert, etc."),
]

if st.session_state["locker_choice"] == "upload":
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_types = set()
    try:
        res = requests.get(f"{BASE}/api/locker/get-documents",
                           params={"user_id": st.session_state["user_id"]}, timeout=10)
        if res.ok:
            uploaded_types = {d["doc_type"] for d in res.json().get("documents", [])}
    except:
        pass

    upload_results = {}
    for doc_type, icon, title, hint in DOCS:
        already = doc_type in uploaded_types
        badge = '<span class="badge-done">✓ Uploaded</span>' if already else ""
        st.markdown(f"""
        <div class="doc-row">
            <div class="doc-icon">{icon}</div>
            <div class="doc-info">
                <div class="doc-name">{title} {badge}</div>
                <div class="doc-hint">{hint}</div>
            </div>
        </div>""", unsafe_allow_html=True)
        upload_results[doc_type] = st.file_uploader(
            f"{'Replace' if already else 'Upload'} {title}",
            type=["pdf","jpg","jpeg","png"], key=f"file_{doc_type}",
            label_visibility="collapsed"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Save & continue →", use_container_width=True):
        errors = []
        any_up = False
        for doc_type, _, title, _ in DOCS:
            f = upload_results.get(doc_type)
            if f:
                try:
                    r = requests.post(
                        f"{BASE}/api/locker/upload-document",
                        data={"user_id": st.session_state["user_id"], "doc_type": doc_type},
                        files={"file": (f.name, f.getvalue(), f.type)}, timeout=30
                    )
                    if r.ok: any_up = True
                    else: errors.append(f"{title}: {r.json().get('detail','Upload failed')}")
                except Exception as e:
                    errors.append(f"{title}: {e}")
        if errors:
            for e in errors: st.error(e)
        else:
            st.success("Documents saved!" if any_up else "No new files selected — proceeding.")
            st.switch_page("pages/3_schemes.py")

elif st.session_state["locker_choice"] == "skip":
    st.markdown("""
    <div class="info-box">
        💡 You can upload documents directly from any scheme's detail page when you're ready to apply. Your profile data will still be used for matching.
    </div>""", unsafe_allow_html=True)
    if st.button("Browse matched schemes →", use_container_width=True):
        st.switch_page("pages/3_schemes.py")