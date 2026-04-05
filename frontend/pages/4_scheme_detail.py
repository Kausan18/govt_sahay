import streamlit as st
from api_client import call
import requests, os
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Scheme Detail — YojanaConnect", page_icon="📄", layout="wide")
if "user_id" not in st.session_state: st.switch_page("app.py")
if "selected_scheme_id" not in st.session_state: st.switch_page("pages/3_schemes.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing:border-box; }
[data-testid="stAppViewContainer"] { background:#FAFAF8; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
.stApp { background:#FAFAF8; }

/* hero */
.hero-card {
    background:#1C1C1A; border-radius:20px; padding:36px 40px; margin-bottom:18px; position:relative; overflow:hidden;
}
.hero-card::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:240px; height:240px; border-radius:50%;
    background:rgba(255,153,51,0.07);
}
.hero-badge { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#FF9933; margin-bottom:10px; }
.hero-title { font-family:'Playfair Display',serif; font-size:1.8rem; font-weight:700; color:#fff; margin-bottom:10px; line-height:1.2; }
.hero-desc { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.92rem; color:#9A9A94; line-height:1.65; }

/* info cards */
.info-card { background:#fff; border:1.5px solid #E8E8E3; border-radius:16px; padding:24px 26px; margin-bottom:14px; }
.ic-title { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#B0B0AA; margin-bottom:16px; }

/* benefit row */
.ben-row { display:flex; align-items:flex-start; gap:10px; margin-bottom:10px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; color:#2A2A28; line-height:1.55; }
.ben-dot { width:7px; height:7px; border-radius:50%; background:#138808; flex-shrink:0; margin-top:6px; }

/* doc pills */
.pill { display:inline-block; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.76rem; font-weight:600; padding:5px 13px; border-radius:20px; margin:3px 3px 3px 0; }
.pill-have    { background:#E8F7E8; color:#138808; }
.pill-missing { background:#FFF0F0; color:#C0392B; }

/* AI chat */
.chat-panel { background:#1C1C1A; border-radius:20px; padding:26px 24px; position:sticky; top:20px; }
.chat-head { font-family:'Playfair Display',serif; font-size:1.1rem; color:#fff; margin-bottom:4px; }
.chat-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.8rem; color:#7A7A74; margin-bottom:18px; line-height:1.55; }
.chat-user { background:#FF9933; color:#1C1C1A; border-radius:12px 12px 4px 12px; padding:11px 14px; margin-bottom:8px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; line-height:1.5; }
.chat-ai   { background:#2A2A28; color:#D0D0CA; border-radius:12px 12px 12px 4px; padding:11px 14px; margin-bottom:8px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; line-height:1.6; }
.chat-sender { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; opacity:0.55; margin-bottom:3px; }

/* inputs */
div[data-testid="stTextInput"] input {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.9rem !important;
    color:#fff !important; background:#2A2A28 !important;
    border:1.5px solid #3A3A38 !important; border-radius:12px !important; padding:12px 16px !important;
}
div[data-testid="stTextInput"] input::placeholder { color:#5A5A55 !important; }
div[data-testid="stTextInput"] input:focus { border-color:#FF9933 !important; box-shadow:none !important; }
div[data-testid="stSelectbox"] > div > div {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.88rem !important;
    color:#fff !important; background:#2A2A28 !important;
    border:1.5px solid #3A3A38 !important; border-radius:12px !important;
}
div[data-testid="stSelectbox"] label { font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.8rem !important; color:#7A7A74 !important; }
div[data-testid="stTextInput"] label { color:#7A7A74 !important; font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.8rem !important; }

/* buttons */
.stButton > button {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.9rem !important;
    font-weight:600 !important; border-radius:10px !important; padding:11px 20px !important;
    border:none !important; background:#FF9933 !important; color:#1C1C1A !important;
    transition:all 0.18s !important;
}
.stButton > button:hover { background:#fff !important; transform:translateY(-1px) !important; }

.verify-btn > button { background:#138808 !important; color:#fff !important; font-size:0.95rem !important; padding:13px 24px !important; }
.verify-btn > button:hover { background:#0e6b07 !important; }
.back-btn > button { background:#2A2A28 !important; color:#D0D0CA !important; font-size:0.84rem !important; }
.back-btn > button:hover { background:#3A3A38 !important; color:#fff !important; }

[data-testid="stFileUploader"] { border:1.5px dashed #3A3A38 !important; border-radius:12px !important; background:#2A2A28 !important; }
[data-testid="stFileUploader"] label { color:#9A9A94 !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
.stExpander { border:1.5px solid #E8E8E3 !important; border-radius:14px !important; }
</style>
""", unsafe_allow_html=True)

# Back button
st.markdown('<div class="back-btn">', unsafe_allow_html=True)
if st.button("← Back to schemes"):
    st.switch_page("pages/3_schemes.py")
st.markdown('</div>', unsafe_allow_html=True)

scheme = st.session_state.get("selected_scheme")
if not scheme:
    try:
        scheme = call(f"/schemes/{st.session_state['selected_scheme_id']}", method="GET")
        st.session_state["selected_scheme"] = scheme
    except:
        st.error("Could not load scheme details.")
        st.stop()

# Fetch uploaded docs
uploaded_types = set()
try:
    r = requests.get(f"{BASE}/api/locker/get-documents",
                     params={"user_id": st.session_state["user_id"]}, timeout=10)
    if r.ok:
        uploaded_types = {d["doc_type"] for d in r.json().get("documents", [])}
except:
    pass

required_docs = scheme.get("required_docs", [])
missing_docs = [d for d in required_docs if d not in uploaded_types]
has_all = len(missing_docs) == 0

col_info, col_chat = st.columns([1.8, 1], gap="large")

with col_info:
    # Hero
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-badge">Government Scheme</div>
        <div class="hero-title">{scheme.get('name','')}</div>
        <div class="hero-desc">{scheme.get('description','')}</div>
    </div>""", unsafe_allow_html=True)

    # Benefits
    benefits = scheme.get("benefits", "")
    if benefits:
        st.markdown('<div class="info-card"><div class="ic-title">What you get</div>', unsafe_allow_html=True)
        for line in benefits.split("\n"):
            if line.strip():
                st.markdown(f'<div class="ben-row"><div class="ben-dot"></div><div>{line.strip()}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Eligibility
    st.markdown('<div class="info-card"><div class="ic-title">Eligibility</div>', unsafe_allow_html=True)
    elig = []
    if scheme.get("min_age") or scheme.get("max_age"):
        elig.append(f"Age: {scheme.get('min_age','any')} – {scheme.get('max_age','any')} years")
    if scheme.get("income_limit"):
        elig.append(f"Annual income below ₹{scheme['income_limit']:,}")
    if scheme.get("castes") and "all" not in scheme.get("castes",[]):
        elig.append(f"Caste: {', '.join(scheme['castes'])}")
    if scheme.get("states") and "all" not in scheme.get("states",[]):
        elig.append(f"State: {', '.join(scheme['states'])}")
    for item in elig:
        st.markdown(f'<div class="ben-row"><div class="ben-dot"></div><div>{item}</div></div>', unsafe_allow_html=True)
    if not elig:
        st.markdown('<div class="ben-row"><div class="ben-dot"></div><div>Open to all eligible citizens</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Documents
    st.markdown('<div class="info-card"><div class="ic-title">Required documents</div>', unsafe_allow_html=True)
    for doc in required_docs:
        if doc in uploaded_types:
            st.markdown(f'<span class="pill pill-have">✓ {doc.replace("_"," ").title()}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="pill pill-missing">✗ {doc.replace("_"," ").title()} — missing</span>', unsafe_allow_html=True)

    if missing_docs:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning(f"You're missing {len(missing_docs)} document(s). Upload them below to apply.")
        with st.expander("Upload missing documents"):
            for doc_type in missing_docs:
                f = st.file_uploader(doc_type.replace("_"," ").title(), type=["pdf","jpg","jpeg","png"], key=f"miss_{doc_type}")
                if f and st.button(f"Upload {doc_type}", key=f"upbtn_{doc_type}"):
                    try:
                        r = requests.post(f"{BASE}/api/locker/upload-document",
                                          data={"user_id":st.session_state["user_id"],"doc_type":doc_type},
                                          files={"file":(f.name,f.getvalue(),f.type)}, timeout=30)
                        if r.ok: st.success(f"{doc_type} uploaded!"); st.rerun()
                        else: st.error("Upload failed.")
                    except Exception as e: st.error(str(e))
    st.markdown('</div>', unsafe_allow_html=True)

    # CTAs
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="verify-btn">', unsafe_allow_html=True)
    btn_label = "Verify & apply →" if has_all else "Verify with available documents →"
    if st.button(btn_label, use_container_width=True):
        st.session_state["verify_scheme_id"] = scheme["id"]
        st.switch_page("pages/5_verification.py")
    st.markdown('</div>', unsafe_allow_html=True)

    if scheme.get("official_url"):
        st.markdown(f"""
        <a href="{scheme['official_url']}" target="_blank"
           style="display:inline-block;margin-top:12px;font-family:'Plus Jakarta Sans',sans-serif;
           font-size:0.87rem;color:#138808;text-decoration:none;font-weight:500">
           Visit official government portal ↗
        </a>""", unsafe_allow_html=True)

with col_chat:
    st.markdown("""
    <div class="chat-panel">
        <div class="chat-head">Ask about this scheme</div>
        <div class="chat-sub">Get answers in your language — Hindi, Kannada, Tamil, and more.</div>
    </div>""", unsafe_allow_html=True)

    lang_key = f"lang_{scheme['id']}"
    hist_key = f"hist_{scheme['id']}"
    if lang_key not in st.session_state: st.session_state[lang_key] = "English"
    if hist_key not in st.session_state: st.session_state[hist_key] = []

    lang = st.selectbox("Reply language",
                        ["English","Hindi","Kannada","Tamil","Telugu","Bengali","Marathi","Gujarati","Punjabi","Malayalam","Odia"],
                        key=lang_key)

    for msg in st.session_state[hist_key][-8:]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-sender" style="color:#FF9933">You</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-sender" style="color:#6A6A64">AI</div><div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    if not st.session_state[hist_key]:
        for s in ["How do I apply?","What documents do I need?","How long does approval take?"]:
            if st.button(s, key=f"sug_{s}_{scheme['id']}", use_container_width=True):
                st.session_state[hist_key].append({"role":"user","content":s})
                with st.spinner("…"):
                    try:
                        r = call("/ai/ask-scheme", {"scheme_id":scheme["id"],"question":s,"language":st.session_state[lang_key]})
                        st.session_state[hist_key].append({"role":"assistant","content":r.get("answer","")})
                    except Exception as e:
                        st.session_state[hist_key].append({"role":"assistant","content":str(e)})
                st.rerun()

    q = st.text_input("Type your question…", key=f"q_{scheme['id']}", label_visibility="collapsed",
                      placeholder="e.g. मुझे इस योजना के बारे में बताएं")
    if st.button("Send →", key=f"send_{scheme['id']}", use_container_width=True) and q.strip():
        st.session_state[hist_key].append({"role":"user","content":q})
        with st.spinner("Answering…"):
            try:
                r = call("/ai/ask-scheme", {"scheme_id":scheme["id"],"question":q,"language":st.session_state[lang_key]})
                st.session_state[hist_key].append({"role":"assistant","content":r.get("answer","")})
            except Exception as e:
                st.session_state[hist_key].append({"role":"assistant","content":str(e)})
        st.rerun()

    if st.session_state[hist_key]:
        if st.button("Clear chat", key=f"clr_{scheme['id']}"):
            st.session_state[hist_key] = []
            st.rerun()