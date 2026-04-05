import streamlit as st
from api_client import call

st.set_page_config(page_title="Schemes — YojanaConnect", page_icon="📋", layout="wide")
if "user_id" not in st.session_state:
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing:border-box; }
[data-testid="stAppViewContainer"] { background:#FAFAF8; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
.stApp { background:#FAFAF8; }

.pg-wrap { padding:32px 0 20px; }
.step-track { display:flex; gap:6px; margin-bottom:24px; max-width:320px; }
.stp { height:4px; flex:1; border-radius:4px; background:#E8E8E3; }
.stp.done { background:#138808; }
.stp.now  { background:#FF9933; }
.pg-title { font-family:'Playfair Display',serif; font-size:2rem; font-weight:700; color:#1C1C1A; margin-bottom:4px; }
.pg-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; color:#8A8A84; margin-bottom:24px; }

/* scheme card */
.scheme-card {
    background:#fff; border:1.5px solid #E8E8E3; border-radius:16px;
    padding:22px 24px; margin-bottom:12px;
    transition:border-color 0.18s, box-shadow 0.18s;
}
.scheme-card:hover { border-color:#138808; box-shadow:0 4px 24px rgba(19,136,8,0.09); }
.sc-rank { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#B0B0AA; margin-bottom:4px; }
.sc-name { font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:700; color:#1C1C1A; margin-bottom:5px; }
.sc-desc { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; color:#6B6B65; line-height:1.55; margin-bottom:12px; }
.sc-bar-bg { height:3px; background:#EBEBЕ6; border-radius:2px; margin:0 0 10px; }
.sc-bar { height:3px; border-radius:2px; background:linear-gradient(90deg,#138808,#FF9933); }
.sc-tags { display:flex; gap:7px; flex-wrap:wrap; }
.tag { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.72rem; font-weight:500; padding:4px 10px; border-radius:20px; }
.tag-score { background:#E8F7E8; color:#138808; }
.tag-neutral { background:#F2F2EE; color:#5A5A55; }

/* search */
div[data-testid="stTextInput"] input {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.92rem !important;
    color:#1C1C1A !important; background:#fff !important;
    border:1.5px solid #E2E2DC !important; border-radius:12px !important; padding:12px 16px !important;
}
div[data-testid="stTextInput"] input:focus { border-color:#138808 !important; box-shadow:0 0 0 3px rgba(19,136,8,0.09) !important; }
div[data-testid="stTextInput"] input::placeholder { color:#C0C0BA !important; }
div[data-testid="stSelectbox"] > div > div {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.92rem !important;
    color:#1C1C1A !important; background:#fff !important;
    border:1.5px solid #E2E2DC !important; border-radius:12px !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label { display:none !important; }

/* AI panel */
.ai-panel {
    background:#1C1C1A; border-radius:20px; padding:26px 24px; position:sticky; top:20px;
}
.ai-head { font-family:'Playfair Display',serif; font-size:1.15rem; color:#fff; margin-bottom:4px; }
.ai-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.8rem; color:#7A7A74; margin-bottom:20px; line-height:1.55; }
.ai-bubble-user { background:#FF9933; color:#1C1C1A; border-radius:12px 12px 4px 12px; padding:11px 14px; margin-bottom:8px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; line-height:1.5; }
.ai-bubble-bot  { background:#2A2A28; color:#D0D0CA; border-radius:12px 12px 12px 4px; padding:11px 14px; margin-bottom:8px; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; line-height:1.6; }
.ai-label { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; opacity:0.55; margin-bottom:3px; }

div[data-testid="stTextInput"].dark-input input {
    background:#2A2A28 !important; color:#fff !important;
    border:1.5px solid #3A3A38 !important; border-radius:12px !important;
}

/* buttons */
.stButton > button {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.9rem !important;
    font-weight:600 !important; border-radius:10px !important; padding:10px 18px !important;
    border:none !important; background:#1C1C1A !important; color:#fff !important;
    transition:all 0.18s !important;
}
.stButton > button:hover { background:#138808 !important; transform:translateY(-1px) !important; }

.empty-state { text-align:center; padding:60px 20px; font-family:'Plus Jakarta Sans',sans-serif; color:#A0A09A; }
.empty-icon { font-size:2.8rem; margin-bottom:14px; }
.count-line { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.82rem; color:#A0A09A; margin-bottom:16px; }
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pg-wrap">
    <div class="step-track">
        <div class="stp done"></div><div class="stp done"></div>
        <div class="stp now"></div><div class="stp"></div>
    </div>
    <div class="pg-title">Schemes matched for you</div>
    <div class="pg-sub">Ranked by how well each scheme fits your profile. Click any scheme to explore.</div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=120, show_spinner=False)
def load_schemes(uid):
    try:
        return call(f"/schemes/ranked/{uid}", method="GET").get("schemes", [])
    except:
        return []

schemes = load_schemes(st.session_state["user_id"])
col_list, col_ai = st.columns([2.2, 1], gap="large")

with col_list:
    if not schemes:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <div>No schemes found. Make sure your profile is complete.</div>
        </div>""", unsafe_allow_html=True)
    else:
        r1, r2 = st.columns([2.5, 1])
        with r1:
            search = st.text_input("Search", placeholder="🔍  Search schemes — farmer, education, health…", label_visibility="collapsed")
        with r2:
            sort_by = st.selectbox("Sort", ["Best match","Name A–Z"], label_visibility="collapsed")

        filtered = schemes
        if search:
            q = search.lower()
            filtered = [s for s in filtered if q in s.get("name","").lower() or q in s.get("description","").lower()]
        if sort_by == "Name A–Z":
            filtered = sorted(filtered, key=lambda x: x.get("name",""))

        max_score = max((s.get("score",0) for s in filtered), default=1) or 1
        st.markdown(f'<div class="count-line">{len(filtered)} scheme{"s" if len(filtered)!=1 else ""} found</div>', unsafe_allow_html=True)

        for i, scheme in enumerate(filtered[:30]):
            score = scheme.get("score", 0)
            pct = int((score / max_score) * 100)
            docs = len(scheme.get("required_docs", []))
            states_str = scheme.get("states", ["all"])
            state_label = "All India" if "all" in states_str else states_str[0]

            st.markdown(f"""
            <div class="scheme-card">
                <div class="sc-rank">#{i+1} match</div>
                <div class="sc-name">{scheme.get('name','Unnamed')}</div>
                <div class="sc-desc">{scheme.get('description','')[:130]}{'…' if len(scheme.get('description',''))>130 else ''}</div>
                <div class="sc-bar-bg"><div class="sc-bar" style="width:{pct}%"></div></div>
                <div class="sc-tags">
                    <span class="tag tag-score">Match score: {score}</span>
                    <span class="tag tag-neutral">{docs} docs required</span>
                    <span class="tag tag-neutral">{state_label}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            if st.button("View details →", key=f"s_{scheme['id']}", use_container_width=True):
                st.session_state["selected_scheme_id"] = scheme["id"]
                st.session_state["selected_scheme"] = scheme
                st.switch_page("pages/4_scheme_detail.py")

with col_ai:
    st.markdown("""
    <div class="ai-panel">
        <div class="ai-head">Situation AI</div>
        <div class="ai-sub">Describe your situation and I'll suggest the best schemes for you.</div>
    </div>""", unsafe_allow_html=True)

    if "sit_hist" not in st.session_state:
        st.session_state["sit_hist"] = []

    for msg in st.session_state["sit_hist"][-6:]:
        if msg["role"] == "user":
            st.markdown(f'<div class="ai-label" style="color:#FF9933">You</div><div class="ai-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-label" style="color:#7A7A74">AI</div><div class="ai-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    if not st.session_state["sit_hist"]:
        st.markdown('<p style="font-family:Plus Jakarta Sans,sans-serif;font-size:0.76rem;color:#6A6A64;margin-bottom:8px">Try asking:</p>', unsafe_allow_html=True)
        for ex in ["I'm a farmer facing drought losses","My child needs education support","I have a medical emergency at home"]:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state["sit_hist"].append({"role":"user","content":ex})
                with st.spinner("Thinking…"):
                    try:
                        r = call("/ai/situational", {"user_id": st.session_state["user_id"], "situation": ex})
                        st.session_state["sit_hist"].append({"role":"assistant","content":r.get("answer","No response.")})
                    except Exception as e:
                        st.session_state["sit_hist"].append({"role":"assistant","content":f"Error: {e}"})
                st.rerun()

    user_q = st.text_input("Ask about your situation…", key="sit_q", label_visibility="collapsed",
                           placeholder="e.g. I need help as a widow with children")
    if st.button("Ask AI →", key="sit_go", use_container_width=True) and user_q:
        st.session_state["sit_hist"].append({"role":"user","content":user_q})
        with st.spinner("Finding relevant schemes…"):
            try:
                r = call("/ai/situational", {"user_id": st.session_state["user_id"], "situation": user_q})
                st.session_state["sit_hist"].append({"role":"assistant","content":r.get("answer","No response.")})
            except Exception as e:
                st.session_state["sit_hist"].append({"role":"assistant","content":f"Error: {e}"})
        st.rerun()

    if st.session_state["sit_hist"]:
        if st.button("Clear", key="sit_clear"):
            st.session_state["sit_hist"] = []
            st.rerun()