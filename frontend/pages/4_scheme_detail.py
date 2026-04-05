import streamlit as st
from api_client import call
import requests
import os

BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Scheme Detail — YojanaConnect", page_icon="📄", layout="wide")

if "user_id" not in st.session_state:
    st.switch_page("app.py")
if "selected_scheme_id" not in st.session_state:
    st.switch_page("pages/3_schemes.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #F7F4EF; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.back-link {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem; color: #8A90A2;
    text-decoration: none; margin-bottom: 20px; display: inline-block;
    cursor: pointer;
}
.scheme-hero {
    background: #1A1F3C;
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.scheme-hero::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,153,51,0.08);
}
.hero-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem; font-weight: 500; color: #FF9933;
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;
}
.hero-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.6rem; font-weight: 600; color: #fff; margin-bottom: 10px;
}
.hero-desc { font-family: 'DM Sans', sans-serif; font-size: 0.92rem; color: #A8ADCC; line-height: 1.6; }

.info-card {
    background: #fff; border-radius: 14px; padding: 22px 24px;
    border: 1.5px solid #E2E5EF; margin-bottom: 14px;
}
.info-card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem; font-weight: 500; color: #A0A6BA;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 14px;
}
.benefit-row {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 10px;
    font-family: 'DM Sans', sans-serif; font-size: 0.9rem; color: #2A3050;
}
.benefit-dot { width: 6px; height: 6px; border-radius: 50%; background: #138808; margin-top: 7px; flex-shrink: 0; }
.doc-pill {
    display: inline-block;
    background: #FFF4E8; color: #C47B10;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem; font-weight: 500;
    padding: 5px 12px; border-radius: 20px; margin: 3px 3px 3px 0;
}
.doc-pill.have { background: #EDFBE9; color: #138808; }
.doc-pill.missing { background: #FEF0F0; color: #C0392B; }

.ai-chat-panel {
    background: #1A1F3C; border-radius: 16px; padding: 24px 22px;
    position: sticky; top: 20px;
}
.chat-title { font-family: 'Noto Serif', serif; font-size: 1.05rem; color: #fff; margin-bottom: 4px; }
.chat-sub { font-family: 'DM Sans', sans-serif; font-size: 0.8rem; color: #8A90A2; margin-bottom: 16px; }
.chat-msg-user {
    background: #FF9933; color: #1A1F3C; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 8px;
    font-family: 'DM Sans', sans-serif; font-size: 0.85rem; line-height: 1.5;
}
.chat-msg-ai {
    background: #262C50; color: #C8CCE0; border-radius: 10px;
    padding: 10px 14px; margin-bottom: 8px;
    font-family: 'DM Sans', sans-serif; font-size: 0.85rem; line-height: 1.6;
}
.stButton > button {
    background: #FF9933 !important; color: #1A1F3C !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    border-radius: 10px !important; padding: 10px 20px !important; border: none !important;
}
.stButton > button:hover { background: #fff !important; }
.verify-btn > button {
    background: #138808 !important; color: #fff !important;
    padding: 13px 24px !important; font-size: 0.95rem !important;
}
.verify-btn > button:hover { background: #0e6006 !important; }
.stTextInput input {
    background: #262C50 !important; color: #fff !important;
    border: 1.5px solid #3A4070 !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div { background: #262C50 !important; color: #fff !important; }
label { font-family: 'DM Sans', sans-serif !important; font-size: 0.82rem !important; color: #8A90A2 !important; }
</style>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to schemes"):
    st.switch_page("pages/3_schemes.py")

# Load scheme
scheme = st.session_state.get("selected_scheme")
if not scheme:
    try:
        scheme = call(f"/schemes/{st.session_state['selected_scheme_id']}", method="GET")
        st.session_state["selected_scheme"] = scheme
    except:
        st.error("Could not load scheme details.")
        st.stop()

# Load user's uploaded docs
uploaded_doc_types = set()
try:
    res = requests.get(f"{BASE}/api/locker/get-documents",
                       params={"user_id": st.session_state["user_id"]}, timeout=10)
    if res.ok:
        uploaded_doc_types = {d["doc_type"] for d in res.json().get("documents", [])}
except:
    pass

required_docs = scheme.get("required_docs", [])
missing_docs = [d for d in required_docs if d not in uploaded_doc_types]
has_all_docs = len(missing_docs) == 0

# Main layout
col_info, col_chat = st.columns([1.8, 1], gap="large")

with col_info:
    # Hero
    st.markdown(f"""
    <div class="scheme-hero">
        <div class="hero-label">Government Scheme</div>
        <div class="hero-title">{scheme.get('name','')}</div>
        <div class="hero-desc">{scheme.get('description','')}</div>
    </div>""", unsafe_allow_html=True)

    # Benefits
    benefits_text = scheme.get("benefits", "")
    if benefits_text:
        st.markdown('<div class="info-card"><div class="info-card-title">What you get</div>', unsafe_allow_html=True)
        for line in benefits_text.split("\n"):
            if line.strip():
                st.markdown(f"""<div class="benefit-row">
                    <div class="benefit-dot"></div>
                    <div>{line.strip()}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Eligibility summary
    st.markdown('<div class="info-card"><div class="info-card-title">Eligibility criteria</div>', unsafe_allow_html=True)
    elig_items = []
    if scheme.get("min_age") or scheme.get("max_age"):
        elig_items.append(f"Age: {scheme.get('min_age','any')} – {scheme.get('max_age','any')} years")
    if scheme.get("income_limit"):
        elig_items.append(f"Annual income below ₹{scheme['income_limit']:,}")
    if scheme.get("castes") and "all" not in scheme.get("castes", []):
        elig_items.append(f"Caste: {', '.join(scheme['castes'])}")
    if scheme.get("states") and "all" not in scheme.get("states", []):
        elig_items.append(f"State: {', '.join(scheme['states'])}")
    for item in elig_items:
        st.markdown(f"""<div class="benefit-row">
            <div class="benefit-dot"></div><div>{item}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Documents status
    st.markdown('<div class="info-card"><div class="info-card-title">Required documents</div>', unsafe_allow_html=True)
    for doc in required_docs:
        if doc in uploaded_doc_types:
            st.markdown(f'<span class="doc-pill have">✓ {doc.replace("_"," ").title()}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="doc-pill missing">✗ {doc.replace("_"," ").title()} — missing</span>', unsafe_allow_html=True)

    if missing_docs:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"You're missing {len(missing_docs)} document(s). Upload them below to apply.")

        # Inline upload for missing docs
        with st.expander("Upload missing documents"):
            for doc_type in missing_docs:
                file = st.file_uploader(f"{doc_type.replace('_',' ').title()}",
                                        type=["pdf","jpg","jpeg","png"], key=f"missing_{doc_type}")
                if file:
                    if st.button(f"Upload {doc_type}", key=f"up_{doc_type}"):
                        try:
                            res = requests.post(
                                f"{BASE}/api/locker/upload-document",
                                data={"user_id": st.session_state["user_id"], "doc_type": doc_type},
                                files={"file": (file.name, file.getvalue(), file.type)}, timeout=30
                            )
                            if res.ok:
                                st.success(f"{doc_type} uploaded!")
                                st.rerun()
                            else:
                                st.error("Upload failed.")
                        except Exception as e:
                            st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # CTA buttons
    st.markdown("<br>", unsafe_allow_html=True)
    if has_all_docs:
        st.markdown('<div class="verify-btn">', unsafe_allow_html=True)
        if st.button("Verify & apply for this scheme →", use_container_width=True):
            st.session_state["verify_scheme_id"] = scheme["id"]
            st.switch_page("pages/5_verification.py")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.button("Verify with available documents →", use_container_width=True):
            st.session_state["verify_scheme_id"] = scheme["id"]
            st.switch_page("pages/5_verification.py")

    if scheme.get("official_url"):
        st.markdown(f"""
        <a href="{scheme['official_url']}" target="_blank"
           style="display:inline-block;margin-top:10px;
           font-family:DM Sans,sans-serif;font-size:0.87rem;color:#1A1F3C;
           text-decoration:underline">
           Visit official government portal ↗
        </a>""", unsafe_allow_html=True)

with col_chat:
    st.markdown("""
    <div class="ai-chat-panel">
        <div class="chat-title">Ask about this scheme</div>
        <div class="chat-sub">Questions answered in your language. Try Hindi, Kannada, Tamil, etc.</div>
    </div>""", unsafe_allow_html=True)

    # Language selector & chat
    lang_key = f"chat_lang_{scheme['id']}"
    hist_key = f"chat_hist_{scheme['id']}"

    if lang_key not in st.session_state:
        st.session_state[lang_key] = "English"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []

    with st.container():
        lang = st.selectbox("Reply language", 
                            ["English", "Hindi", "Kannada", "Tamil", "Telugu", "Bengali", "Marathi",
                             "Gujarati", "Punjabi", "Malayalam", "Odia"],
                            key=lang_key, label_visibility="visible")

        # Chat history
        for msg in st.session_state[hist_key][-8:]:
            cls = "chat-msg-user" if msg["role"] == "user" else "chat-msg-ai"
            sender = "You" if msg["role"] == "user" else "AI"
            st.markdown(f"""
            <div class="{cls}">
                <span style="font-size:0.7rem;opacity:0.6;font-weight:500">{sender}</span><br>
                {msg['content']}
            </div>""", unsafe_allow_html=True)

        # Suggested questions
        if not st.session_state[hist_key]:
            suggestions = [
                "How do I apply for this scheme?",
                "What documents will I need?",
                "How long does approval take?",
            ]
            for s in suggestions:
                if st.button(s, key=f"sugg_{s}_{scheme['id']}", use_container_width=True):
                    st.session_state[hist_key].append({"role":"user","content":s})
                    with st.spinner("..."):
                        try:
                            res = call("/ai/ask-scheme", {
                                "scheme_id": scheme["id"],
                                "question": s,
                                "language": st.session_state[lang_key]
                            })
                            st.session_state[hist_key].append(
                                {"role":"assistant","content":res.get("answer","")}
                            )
                        except Exception as e:
                            st.session_state[hist_key].append({"role":"assistant","content":str(e)})
                    st.rerun()

        user_q = st.text_input("Type your question...", key=f"q_{scheme['id']}",
                               label_visibility="collapsed", placeholder="e.g. मुझे इस योजना के बारे में बताएं")

        if st.button("Send →", key=f"send_{scheme['id']}", use_container_width=True):
            if user_q.strip():
                st.session_state[hist_key].append({"role":"user","content":user_q})
                with st.spinner("Answering..."):
                    try:
                        res = call("/ai/ask-scheme", {
                            "scheme_id": scheme["id"],
                            "question": user_q,
                            "language": st.session_state[lang_key]
                        })
                        st.session_state[hist_key].append(
                            {"role":"assistant","content":res.get("answer","")}
                        )
                    except Exception as e:
                        st.session_state[hist_key].append({"role":"assistant","content":str(e)})
                st.rerun()

        if st.session_state[hist_key]:
            if st.button("Clear chat", key=f"clear_{scheme['id']}"):
                st.session_state[hist_key] = []
                st.rerun()