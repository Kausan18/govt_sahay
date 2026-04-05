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
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #F7F4EF; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.step-bar { display: flex; gap: 6px; margin-bottom: 20px; }
.step { height: 4px; flex: 1; border-radius: 2px; background: #E2E5EF; }
.step.done { background: #138808; }
.step.active { background: #FF9933; }

.page-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.9rem; font-weight: 600; color: #1A1F3C; margin-bottom: 6px;
}
.page-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem; color: #8A90A2; margin-bottom: 8px;
}
.choice-card {
    background: #fff;
    border: 2px solid #E2E5EF;
    border-radius: 14px;
    padding: 24px 28px;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
    margin-bottom: 14px;
}
.choice-card:hover { border-color: #FF9933; box-shadow: 0 4px 16px rgba(255,153,51,0.12); }
.choice-card.selected { border-color: #138808; box-shadow: 0 4px 16px rgba(19,136,8,0.10); }
.choice-icon { font-size: 1.8rem; margin-bottom: 8px; }
.choice-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.05rem; font-weight: 600; color: #1A1F3C; margin-bottom: 4px;
}
.choice-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.84rem; color: #8A90A2;
}
.doc-card {
    background: #fff;
    border: 1.5px solid #E2E5EF;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.doc-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem; font-weight: 500; color: #1A1F3C; margin-bottom: 4px;
}
.doc-hint {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem; color: #A0A6BA; margin-bottom: 10px;
}
.uploaded-badge {
    display: inline-block;
    background: #EDFBE9; color: #138808;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem; font-weight: 500;
    padding: 3px 10px; border-radius: 20px;
}
.stButton > button {
    background: #1A1F3C !important; color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important; font-weight: 500 !important;
    border-radius: 10px !important; padding: 12px 32px !important; border: none !important;
}
.stButton > button:hover { background: #FF9933 !important; color: #1A1F3C !important; }
.skip-btn > button {
    background: transparent !important; color: #8A90A2 !important;
    border: 1.5px solid #E2E5EF !important; font-size: 0.88rem !important;
}
.skip-btn > button:hover { border-color: #1A1F3C !important; color: #1A1F3C !important; }
label { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; color: #4A5068 !important; }
</style>

<div style="padding: 36px 0 8px">
    <div class="step-bar">
        <div class="step done"></div>
        <div class="step active"></div>
        <div class="step"></div>
        <div class="step"></div>
    </div>
    <div class="page-title">Your digital locker</div>
    <div class="page-sub">Upload documents now for faster scheme verification, or skip and add them later per scheme.</div>
</div>
""", unsafe_allow_html=True)

# --- Choice ---
if "locker_choice" not in st.session_state:
    st.session_state["locker_choice"] = None

col1, col2 = st.columns(2)
with col1:
    upload_selected = st.session_state["locker_choice"] == "upload"
    card_class = "choice-card selected" if upload_selected else "choice-card"
    st.markdown(f"""
    <div class="{card_class}">
        <div class="choice-icon">📂</div>
        <div class="choice-title">Upload documents now</div>
        <div class="choice-desc">Faster verification. Documents pre-fill your applications automatically.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Choose this", key="btn_upload", use_container_width=True):
        st.session_state["locker_choice"] = "upload"
        st.rerun()

with col2:
    skip_selected = st.session_state["locker_choice"] == "skip"
    card_class2 = "choice-card selected" if skip_selected else "choice-card"
    st.markdown(f"""
    <div class="{card_class2}">
        <div class="choice-icon">⚡</div>
        <div class="choice-title">Skip for now</div>
        <div class="choice-desc">Browse schemes first. Upload documents when you find one to apply for.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Choose this", key="btn_skip", use_container_width=True):
        st.session_state["locker_choice"] = "skip"
        st.rerun()

# --- Upload Section ---
if st.session_state["locker_choice"] == "upload":
    st.markdown("<br>", unsafe_allow_html=True)

    DOCS = [
        ("aadhar",  "Aadhaar Card",         "Required for identity verification (PDF/JPG/PNG)"),
        ("income",  "Income Certificate",    "Issued by a government officer (PDF/JPG/PNG)"),
        ("caste",   "Caste Certificate",     "For SC/ST/OBC applicants (PDF/JPG/PNG)"),
        ("dob",     "Date of Birth Proof",   "Birth certificate or Class 10 marksheet (PDF/JPG/PNG)"),
        ("basic",   "Any other certificate", "Domicile, disability cert, etc. (PDF/JPG/PNG)"),
    ]

    # Fetch already uploaded docs
    uploaded_types = set()
    try:
        res = requests.post(f"{BASE}/api/locker/get-documents",
                            params={"user_id": st.session_state["user_id"]}, timeout=10)
        if res.ok:
            uploaded_types = {d["doc_type"] for d in res.json().get("documents", [])}
    except:
        pass

    upload_results = {}

    for doc_type, title, hint in DOCS:
        already = doc_type in uploaded_types
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-title">{title}{"&nbsp;&nbsp;<span class='uploaded-badge'>✓ Uploaded</span>" if already else ""}</div>
            <div class="doc-hint">{hint}</div>
        </div>""", unsafe_allow_html=True)

        file = st.file_uploader(
            f"{'Replace' if already else 'Upload'} {title}",
            type=["pdf", "jpg", "jpeg", "png"],
            key=f"file_{doc_type}",
            label_visibility="collapsed"
        )
        upload_results[doc_type] = file

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Save documents & continue →", use_container_width=True):
        any_uploaded = False
        errors = []
        for doc_type, file in upload_results.items():
            if file is not None:
                try:
                    res = requests.post(
                        f"{BASE}/api/locker/upload-document",
                        data={"user_id": st.session_state["user_id"], "doc_type": doc_type},
                        files={"file": (file.name, file.getvalue(), file.type)},
                        timeout=30
                    )
                    if res.ok:
                        any_uploaded = True
                    else:
                        errors.append(f"{doc_type}: {res.json().get('detail','Upload failed')}")
                except Exception as e:
                    errors.append(f"{doc_type}: {e}")

        if errors:
            for err in errors:
                st.error(err)
        else:
            st.success("Documents saved!" if any_uploaded else "No new files selected — proceeding.")
            st.switch_page("pages/3_schemes.py")

# --- Skip Section ---
elif st.session_state["locker_choice"] == "skip":
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("You can upload documents from any scheme's detail page when you're ready to apply.")
    if st.button("Browse schemes →", use_container_width=True):
        st.switch_page("pages/3_schemes.py")