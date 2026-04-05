import streamlit as st
from api_client import call

st.set_page_config(page_title="Schemes — YojanaConnect", page_icon="📋", layout="wide")

if "user_id" not in st.session_state:
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] { background: #F7F4EF; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

.step-bar { display: flex; gap: 6px; margin-bottom: 20px; max-width: 480px; }
.step { height: 4px; flex: 1; border-radius: 2px; background: #E2E5EF; }
.step.done { background: #138808; }
.step.active { background: #FF9933; }

.page-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.9rem; font-weight: 600; color: #1A1F3C; margin-bottom: 4px;
}
.page-sub { font-family: 'DM Sans', sans-serif; font-size: 0.92rem; color: #8A90A2; margin-bottom: 24px; }

.scheme-card {
    background: #fff;
    border: 1.5px solid #E2E5EF;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    transition: border-color 0.15s, box-shadow 0.15s;
    cursor: pointer;
    position: relative;
}
.scheme-card:hover { border-color: #FF9933; box-shadow: 0 4px 20px rgba(255,153,51,0.10); }
.scheme-rank {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem; font-weight: 500; color: #A0A6BA;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;
}
.scheme-name {
    font-family: 'Noto Serif', serif;
    font-size: 1.05rem; font-weight: 600; color: #1A1F3C; margin-bottom: 4px;
}
.scheme-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem; color: #6A7090; line-height: 1.5; margin-bottom: 10px;
}
.scheme-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem; font-weight: 500;
    padding: 3px 10px; border-radius: 20px;
    background: #F0F2FA; color: #4A5068;
}
.tag.score { background: #EDFBE9; color: #138808; }
.score-bar-wrap { margin: 8px 0 4px; }
.score-bar {
    height: 3px; border-radius: 2px;
    background: linear-gradient(90deg, #138808 0%, #FF9933 100%);
}

.ai-panel {
    background: #1A1F3C;
    border-radius: 16px;
    padding: 24px 22px;
    position: sticky;
    top: 20px;
}
.ai-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 4px;
}
.ai-sub { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: #8A90A2; margin-bottom: 16px; }
.ai-bubble {
    background: #262C50;
    border-radius: 12px;
    padding: 14px 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.87rem; color: #C8CCE0;
    line-height: 1.6; margin-bottom: 12px;
}
.stTextInput input {
    background: #262C50 !important; color: #fff !important;
    border: 1.5px solid #3A4070 !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input::placeholder { color: #606890 !important; }
.stButton > button {
    background: #FF9933 !important; color: #1A1F3C !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    border-radius: 10px !important; padding: 10px 20px !important; border: none !important;
}
.stButton > button:hover { background: #fff !important; }
.stSelectbox > div { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; }
label { font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important; color: #8A90A2 !important; }
.empty-state {
    text-align: center; padding: 60px 20px;
    font-family: 'DM Sans', sans-serif; color: #A0A6BA;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
</style>

<div style="padding: 28px 0 16px">
    <div class="step-bar">
        <div class="step done"></div>
        <div class="step done"></div>
        <div class="step active"></div>
        <div class="step"></div>
    </div>
    <div class="page-title">Schemes matched for you</div>
    <div class="page-sub">Ranked by how well each scheme fits your profile. Click any scheme to explore.</div>
</div>
""", unsafe_allow_html=True)

# Load schemes
@st.cache_data(ttl=120, show_spinner=False)
def load_schemes(user_id):
    try:
        res = call(f"/schemes/ranked/{user_id}", method="GET")
        return res.get("schemes", [])
    except:
        return []

schemes = load_schemes(st.session_state["user_id"])

# Layout: schemes list left, AI panel right
col_schemes, col_ai = st.columns([2.2, 1], gap="large")

with col_schemes:
    if not schemes:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <div>No schemes found. Make sure your profile is complete.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Filter row
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            search = st.text_input("Search schemes", placeholder="e.g. farmer, education, health...",
                                   label_visibility="collapsed")
        with filter_col2:
            sort_by = st.selectbox("Sort by", ["Best match", "Name A-Z"], label_visibility="collapsed")

        filtered = schemes
        if search:
            q = search.lower()
            filtered = [s for s in schemes if q in s.get("name","").lower() or q in s.get("description","").lower()]
        if sort_by == "Name A-Z":
            filtered = sorted(filtered, key=lambda x: x.get("name",""))

        st.markdown(f"<p style='font-family:DM Sans,sans-serif;font-size:0.82rem;color:#A0A6BA;margin-bottom:16px'>"
                    f"{len(filtered)} schemes found</p>", unsafe_allow_html=True)

        max_score = max((s.get("score", 0) for s in filtered), default=1) or 1

        for i, scheme in enumerate(filtered[:30]):
            score = scheme.get("score", 0)
            score_pct = int((score / max_score) * 100)
            docs_needed = len(scheme.get("required_docs", []))

            with st.container():
                st.markdown(f"""
                <div class="scheme-card">
                    <div class="scheme-rank">#{i+1} match</div>
                    <div class="scheme-name">{scheme.get('name','Unnamed Scheme')}</div>
                    <div class="scheme-desc">{scheme.get('description','')[:120]}{"..." if len(scheme.get('description','')) > 120 else ""}</div>
                    <div class="score-bar-wrap">
                        <div class="score-bar" style="width:{score_pct}%"></div>
                    </div>
                    <div class="scheme-tags">
                        <span class="tag score">Match score: {score}</span>
                        <span class="tag">{docs_needed} docs required</span>
                        <span class="tag">{scheme.get('state','All India')}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                if st.button("View details →", key=f"scheme_{scheme['id']}", use_container_width=True):
                    st.session_state["selected_scheme_id"] = scheme["id"]
                    st.session_state["selected_scheme"] = scheme
                    st.switch_page("pages/4_scheme_detail.py")

with col_ai:
    st.markdown("""
    <div class="ai-panel">
        <div class="ai-title">Situation-based AI</div>
        <div class="ai-sub">Describe your situation and I'll suggest the best schemes for you.</div>
    </div>""", unsafe_allow_html=True)

    # Situational chat
    if "situational_history" not in st.session_state:
        st.session_state["situational_history"] = []

    with st.container():
        # Show conversation
        for msg in st.session_state["situational_history"][-6:]:
            role_label = "You" if msg["role"] == "user" else "AI"
            bubble_style = "background:#262C50;color:#C8CCE0" if msg["role"] == "assistant" else "background:#FF9933;color:#1A1F3C"
            st.markdown(f"""
            <div style="{bubble_style};border-radius:10px;padding:10px 14px;
                font-family:DM Sans,sans-serif;font-size:0.84rem;line-height:1.55;
                margin-bottom:8px">
                <span style="font-size:0.72rem;font-weight:500;opacity:0.7">{role_label}</span><br>
                {msg['content']}
            </div>""", unsafe_allow_html=True)

        # Example prompts
        if not st.session_state["situational_history"]:
            st.markdown("""
            <div style="margin-bottom:12px">
                <p style="font-family:DM Sans,sans-serif;font-size:0.78rem;color:#8A90A2;margin-bottom:8px">Try asking:</p>
            </div>""", unsafe_allow_html=True)
            examples = ["I'm a farmer facing drought losses", "My child needs education support", "I have a health emergency"]
            for ex in examples:
                if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                    st.session_state["situational_history"].append({"role":"user","content":ex})
                    with st.spinner("Thinking..."):
                        try:
                            res = call("/ai/situational", {
                                "user_id": st.session_state["user_id"],
                                "situation": ex
                            })
                            st.session_state["situational_history"].append(
                                {"role":"assistant","content":res.get("answer","No answer.")}
                            )
                        except Exception as e:
                            st.session_state["situational_history"].append(
                                {"role":"assistant","content":f"Error: {e}"}
                            )
                    st.rerun()

        user_q = st.text_input("Ask about your situation...", key="sit_input",
                               label_visibility="collapsed",
                               placeholder="e.g. I need help as a widow with children")
        if st.button("Ask AI →", key="sit_submit", use_container_width=True):
            if user_q:
                st.session_state["situational_history"].append({"role":"user","content":user_q})
                with st.spinner("Finding relevant schemes..."):
                    try:
                        res = call("/ai/situational", {
                            "user_id": st.session_state["user_id"],
                            "situation": user_q
                        })
                        st.session_state["situational_history"].append(
                            {"role":"assistant","content":res.get("answer","No answer.")}
                        )
                    except Exception as e:
                        st.session_state["situational_history"].append(
                            {"role":"assistant","content":f"Error: {e}"}
                        )
                st.rerun()