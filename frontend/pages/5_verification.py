import streamlit as st
from api_client import call
import requests, os
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Verification — YojanaConnect", page_icon="✅", layout="centered")
if "user_id" not in st.session_state: st.switch_page("app.py")
if "verify_scheme_id" not in st.session_state: st.switch_page("pages/3_schemes.py")

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
.pg-title { font-family:'Playfair Display',serif; font-size:2rem; font-weight:700; color:#1C1C1A; margin-bottom:4px; }
.pg-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; color:#8A8A84; margin-bottom:32px; }

/* result cards */
.result-verified {
    background:#F0FAF0; border:2px solid #138808; border-radius:20px;
    padding:40px 36px; text-align:center; margin-bottom:20px;
}
.result-failed {
    background:#FFF4F4; border:2px solid #E74C3C; border-radius:20px;
    padding:40px 36px; text-align:center; margin-bottom:20px;
}
.r-icon { font-size:3rem; margin-bottom:14px; }
.r-title { font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; margin-bottom:8px; }
.r-title.ok  { color:#0B6E04; }
.r-title.fail { color:#C0392B; }
.r-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; line-height:1.65; }
.r-sub.ok   { color:#1D8A14; }
.r-sub.fail { color:#C0392B; }

/* doc check rows */
.sec-label { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#B0B0AA; margin:28px 0 14px; }
.doc-check { background:#fff; border:1.5px solid #E8E8E3; border-radius:14px; padding:16px 20px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
.dc-name { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; font-weight:600; color:#1C1C1A; }
.dc-issue { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.78rem; color:#C0392B; margin-top:3px; }
.badge-pass { background:#E8F7E8; color:#138808; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.72rem; font-weight:600; padding:4px 12px; border-radius:20px; }
.badge-fail { background:#FFF0F0; color:#C0392B; font-family:'Plus Jakarta Sans',sans-serif; font-size:0.72rem; font-weight:600; padding:4px 12px; border-radius:20px; }

/* next step cards */
.next-card { background:#1C1C1A; border-radius:16px; padding:26px 28px; margin-bottom:14px; }
.next-title { font-family:'Playfair Display',serif; font-size:1.1rem; color:#fff; margin-bottom:6px; }
.next-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.86rem; color:#9A9A94; line-height:1.6; }

/* AI explanation */
.ai-explain { background:#fff; border:1.5px solid #E8E8E3; border-radius:16px; padding:22px 24px; margin-bottom:14px; }
.ai-explain-label { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#B0B0AA; margin-bottom:10px; }
.ai-explain-text { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; color:#2A2A28; line-height:1.7; }

/* buttons */
.stButton > button {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.92rem !important;
    font-weight:600 !important; border-radius:12px !important; padding:12px 24px !important;
    border:none !important; background:#1C1C1A !important; color:#fff !important;
    transition:all 0.18s !important;
}
.stButton > button:hover { background:#138808 !important; transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(19,136,8,0.25) !important; }
.pdf-btn > button { background:#138808 !important; }
.pdf-btn > button:hover { background:#0e6b07 !important; }
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pg-wrap">
    <div class="step-track">
        <div class="stp done"></div><div class="stp done"></div>
        <div class="stp done"></div><div class="stp now"></div>
    </div>
    <div class="pg-title">Verification result</div>
    <div class="pg-sub">We matched your documents against your profile and scheme requirements.</div>
</div>
""", unsafe_allow_html=True)

vkey = f"vres_{st.session_state['verify_scheme_id']}"
if vkey not in st.session_state:
    with st.spinner("Running document verification… This may take a moment."):
        try:
            result = call("/verify/run", {
                "user_id": st.session_state["user_id"],
                "scheme_id": st.session_state["verify_scheme_id"]
            })
            st.session_state[vkey] = result
        except Exception as e:
            st.error(f"Verification failed: {e}")
            st.stop()

result = st.session_state[vkey]
verified = result.get("verified", False)
missing = result.get("missing_docs", [])
issues = result.get("issues", [])
doc_results = result.get("doc_results", {})


# Face verification status banner
face_verified = st.session_state.get("face_verified", None)
if face_verified is True:
    st.markdown("""
    <div style="background:#E8F7E8;border:1.5px solid #138808;border-radius:14px;
         padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:12px">
        <span style="font-size:1.3rem">🧑</span>
        <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.84rem;
                 font-weight:600;color:#0B6E04">Face verification passed</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.78rem;
                 color:#1D8A14">Live photo matched your profile photo successfully</div>
        </div>
    </div>""", unsafe_allow_html=True)
elif face_verified is False:
    st.markdown("""
    <div style="background:#FFF8EE;border:1.5px solid #FF9933;border-radius:14px;
         padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:12px">
        <span style="font-size:1.3rem">⚠️</span>
        <div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.84rem;
                 font-weight:600;color:#8B5E1A">Face verification skipped or failed</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.78rem;
                 color:#8B5E1A">Document verification still proceeded — consider retrying face check</div>
        </div>
    </div>""", unsafe_allow_html=True)

# Result card
if verified:
    st.markdown("""
    <div class="result-verified">
        <div class="r-icon">✅</div>
        <div class="r-title ok">You're verified!</div>
        <div class="r-sub ok">All documents match your profile. You are eligible to apply for this scheme.</div>
    </div>""", unsafe_allow_html=True)
else:
    reasons_html = "".join([f"<li style='margin-bottom:6px'>{r}</li>" for r in missing + issues])
    st.markdown(f"""
    <div class="result-failed">
        <div class="r-icon">⚠️</div>
        <div class="r-title fail">Verification incomplete</div>
        <div class="r-sub fail">
            <ul style="text-align:left;margin-top:12px;padding-left:20px;line-height:1.8">
                {reasons_html}
            </ul>
        </div>
    </div>""", unsafe_allow_html=True)

# Document breakdown
if doc_results:
    st.markdown('<div class="sec-label">Document check breakdown</div>', unsafe_allow_html=True)
    for doc_type, res in doc_results.items():
        passed = res.get("passed", False)
        doc_issues = res.get("issues", [])
        issues_html = "".join([f'<div class="dc-issue">{i}</div>' for i in doc_issues])
        badge = '<span class="badge-pass">✓ Passed</span>' if passed else '<span class="badge-fail">✗ Failed</span>'
        st.markdown(f"""
        <div class="doc-check">
            <div>
                <div class="dc-name">{doc_type.replace('_',' ').title()}</div>
                {issues_html}
            </div>
            {badge}
        </div>""", unsafe_allow_html=True)

if missing:
    st.markdown('<div class="sec-label">Missing documents</div>', unsafe_allow_html=True)
    for doc in missing:
        st.markdown(f"""
        <div class="doc-check">
            <div class="dc-name">{doc.replace('_',' ').title()}</div>
            <span class="badge-fail">Not uploaded</span>
        </div>""", unsafe_allow_html=True)

# Next steps
st.markdown('<div class="sec-label">Next steps</div>', unsafe_allow_html=True)
scheme = st.session_state.get("selected_scheme", {})

if verified:
    portal_link = f'<br><br><a href="{scheme["official_url"]}" target="_blank" style="color:#FF9933;font-weight:600">Visit official portal ↗</a>' if scheme.get("official_url") else ""
    st.markdown(f"""
    <div class="next-card">
        <div class="next-title">Apply on the official portal</div>
        <div class="next-sub">Your documents are verified. Head to the government portal with your documents ready.{portal_link}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Application guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="pdf-btn">', unsafe_allow_html=True)
    if st.button("📄  Download step-by-step PDF guide", use_container_width=True):
        with st.spinner("Generating PDF…"):
            try:
                pdf_res = requests.get(
                    f"{BASE}/api/verify/generate-pdf/{st.session_state['user_id']}/{st.session_state['verify_scheme_id']}",
                    timeout=30
                )
                if pdf_res.ok:
                    st.download_button(
                        label="⬇  Save PDF to device",
                        data=pdf_res.content,
                        file_name=f"apply_{scheme.get('name','scheme').replace(' ','_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Could not generate PDF.")
            except Exception as e:
                st.error(f"PDF error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="next-card">
        <div class="next-title">How to fix this</div>
        <div class="next-sub">Resolve the issues listed above, then re-verify. You can upload missing documents from the scheme detail page.</div>
    </div>""", unsafe_allow_html=True)

    if "vai_explain" not in st.session_state:
        with st.spinner("AI is explaining what went wrong…"):
            try:
                r = call("/ai/ask-scheme", {
                    "scheme_id": st.session_state["verify_scheme_id"],
                    "question": (f"Verification failed for these reasons: {', '.join(missing+issues)}. "
                                 f"Explain clearly in simple language what the user needs to fix and the exact steps."),
                    "language": "English"
                })
                st.session_state["vai_explain"] = r.get("answer", "")
            except:
                st.session_state["vai_explain"] = ""

    if st.session_state.get("vai_explain"):
        st.markdown(f"""
        <div class="ai-explain">
            <div class="ai-explain-label">AI Guidance</div>
            <div class="ai-explain-text">{st.session_state['vai_explain']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("← Back to scheme", use_container_width=True):
        st.switch_page("pages/4_scheme_detail.py")
with c2:
    if st.button("Browse other schemes →", use_container_width=True):
        st.switch_page("pages/3_schemes.py")