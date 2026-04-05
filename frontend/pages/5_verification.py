import streamlit as st
from api_client import call
import requests
import os

BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Verification — YojanaConnect", page_icon="✅", layout="centered")

if "user_id" not in st.session_state:
    st.switch_page("app.py")
if "verify_scheme_id" not in st.session_state:
    st.switch_page("pages/3_schemes.py")

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

.page-title { font-family: 'Noto Serif', serif; font-size: 1.9rem; font-weight: 600; color: #1A1F3C; margin-bottom: 6px; }
.page-sub { font-family: 'DM Sans', sans-serif; font-size: 0.92rem; color: #8A90A2; margin-bottom: 32px; }

.result-card {
    border-radius: 16px; padding: 36px 40px; text-align: center; margin-bottom: 20px;
}
.result-card.verified { background: #EDFBE9; border: 2px solid #138808; }
.result-card.failed   { background: #FEF0F0; border: 2px solid #C0392B; }

.result-icon { font-size: 3rem; margin-bottom: 12px; }
.result-title {
    font-family: 'Noto Serif', serif;
    font-size: 1.5rem; font-weight: 600; margin-bottom: 8px;
}
.result-title.verified { color: #0B6E04; }
.result-title.failed   { color: #922B21; }
.result-sub { font-family: 'DM Sans', sans-serif; font-size: 0.9rem; line-height: 1.6; }
.result-sub.verified { color: #1D8A14; }
.result-sub.failed   { color: #C0392B; }

.doc-result-card {
    background: #fff; border-radius: 12px; padding: 16px 20px;
    margin-bottom: 10px; border: 1.5px solid #E2E5EF;
    display: flex; justify-content: space-between; align-items: center;
}
.doc-result-name { font-family: 'DM Sans', sans-serif; font-size: 0.9rem; color: #1A1F3C; font-weight: 500; }
.doc-result-issues { font-family: 'DM Sans', sans-serif; font-size: 0.8rem; color: #C0392B; margin-top: 4px; }
.pass-badge { background: #EDFBE9; color: #138808; font-family: 'DM Sans', sans-serif;
              font-size: 0.75rem; font-weight: 500; padding: 4px 12px; border-radius: 20px; }
.fail-badge { background: #FEF0F0; color: #C0392B; font-family: 'DM Sans', sans-serif;
              font-size: 0.75rem; font-weight: 500; padding: 4px 12px; border-radius: 20px; }

.section-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem; font-weight: 500; color: #A0A6BA;
    text-transform: uppercase; letter-spacing: 0.07em; margin: 24px 0 12px;
}
.next-step-card {
    background: #1A1F3C; border-radius: 14px; padding: 24px 28px; margin-bottom: 12px;
}
.next-title { font-family: 'Noto Serif', serif; font-size: 1.05rem; color: #fff; margin-bottom: 6px; }
.next-sub { font-family: 'DM Sans', sans-serif; font-size: 0.85rem; color: #A8ADCC; line-height: 1.55; }

.stButton > button {
    background: #1A1F3C !important; color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important; font-weight: 500 !important;
    border-radius: 10px !important; padding: 12px 24px !important; border: none !important;
}
.stButton > button:hover { background: #FF9933 !important; color: #1A1F3C !important; }
.pdf-btn > button { background: #138808 !important; }
.pdf-btn > button:hover { background: #0e6006 !important; }
</style>

<div style="padding: 28px 0 8px">
    <div class="step-bar">
        <div class="step done"></div>
        <div class="step done"></div>
        <div class="step done"></div>
        <div class="step active"></div>
    </div>
    <div class="page-title">Verification result</div>
    <div class="page-sub">We matched your documents against your profile and scheme requirements.</div>
</div>
""", unsafe_allow_html=True)

# Run verification (only once per session per scheme)
verify_key = f"verify_result_{st.session_state['verify_scheme_id']}"

if verify_key not in st.session_state:
    with st.spinner("Running document verification... This may take a moment."):
        try:
            result = call("/verify/run", {
                "user_id": st.session_state["user_id"],
                "scheme_id": st.session_state["verify_scheme_id"]
            })
            st.session_state[verify_key] = result
        except Exception as e:
            st.error(f"Verification failed: {e}")
            st.stop()

result = st.session_state[verify_key]
verified = result.get("verified", False)
missing = result.get("missing_docs", [])
issues = result.get("issues", [])
doc_results = result.get("doc_results", {})

# Main result card
if verified:
    st.markdown("""
    <div class="result-card verified">
        <div class="result-icon">✅</div>
        <div class="result-title verified">You're verified!</div>
        <div class="result-sub verified">All your documents match your profile. You're eligible to apply for this scheme.</div>
    </div>""", unsafe_allow_html=True)
else:
    all_reasons = missing + issues
    reasons_html = "".join([f"<li>{r}</li>" for r in all_reasons])
    st.markdown(f"""
    <div class="result-card failed">
        <div class="result-icon">⚠️</div>
        <div class="result-title failed">Verification incomplete</div>
        <div class="result-sub failed">
            <ul style="text-align:left;margin-top:10px;padding-left:20px">
                {reasons_html}
            </ul>
        </div>
    </div>""", unsafe_allow_html=True)

# Document breakdown
if doc_results:
    st.markdown('<div class="section-title">Document check breakdown</div>', unsafe_allow_html=True)
    for doc_type, res in doc_results.items():
        passed = res.get("passed", False)
        doc_issues = res.get("issues", [])
        badge = '<span class="pass-badge">✓ Passed</span>' if passed else '<span class="fail-badge">✗ Failed</span>'
        issues_html = ""
        if doc_issues:
            issues_html = f'<div class="doc-result-issues">{"<br>".join(doc_issues)}</div>'
        st.markdown(f"""
        <div class="doc-result-card">
            <div>
                <div class="doc-result-name">{doc_type.replace('_',' ').title()}</div>
                {issues_html}
            </div>
            {badge}
        </div>""", unsafe_allow_html=True)

if missing:
    st.markdown('<div class="section-title">Missing documents</div>', unsafe_allow_html=True)
    for doc in missing:
        st.markdown(f"""
        <div class="doc-result-card">
            <div class="doc-result-name">{doc.replace('_',' ').title()}</div>
            <span class="fail-badge">Not uploaded</span>
        </div>""", unsafe_allow_html=True)

# Next steps
st.markdown('<div class="section-title">Next steps</div>', unsafe_allow_html=True)

scheme = st.session_state.get("selected_scheme", {})

if verified:
    st.markdown(f"""
    <div class="next-step-card">
        <div class="next-title">Apply on the official portal</div>
        <div class="next-sub">
            Visit the government website with your documents ready.
            Your details have been pre-verified — the application process should be straightforward.
            {f'<br><br><a href="{scheme["official_url"]}" target="_blank" style="color:#FF9933">Official portal ↗</a>' if scheme.get("official_url") else ""}
        </div>
    </div>""", unsafe_allow_html=True)

    # PDF download
    st.markdown('<div class="section-title">Download application guide</div>', unsafe_allow_html=True)
    if st.button("📄 Download step-by-step application PDF", use_container_width=True):
        with st.spinner("Generating PDF..."):
            try:
                pdf_res = requests.get(
                    f"{BASE}/api/verify/generate-pdf/{st.session_state['user_id']}/{st.session_state['verify_scheme_id']}",
                    timeout=30
                )
                if pdf_res.ok:
                    st.download_button(
                        label="⬇ Save PDF to device",
                        data=pdf_res.content,
                        file_name=f"apply_{scheme.get('name','scheme').replace(' ','_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Could not generate PDF.")
            except Exception as e:
                st.error(f"PDF error: {e}")
else:
    # AI explanation of failure
    if issues or missing:
        st.markdown("""
        <div class="next-step-card">
            <div class="next-title">What to do next</div>
            <div class="next-sub">
                Fix the issues above, then re-verify. You can upload missing documents
                from the scheme detail page and run verification again.
            </div>
        </div>""", unsafe_allow_html=True)

    # AI explains why
    # In 5_verification.py — replace the AI explain block
if "verify_ai_explain" not in st.session_state:
    with st.spinner("AI is explaining what went wrong..."):
        try:
            all_issues_text = ", ".join(missing + issues)
            explain_lang = st.session_state.get("preferred_language", "English")
            res = call("/ai/ask-scheme", {
                "scheme_id": st.session_state["verify_scheme_id"],
                "question": (
                    f"The user's verification failed for these reasons: {all_issues_text}. "
                    f"Explain in simple, friendly language what went wrong and exactly what "
                    f"the user needs to do to fix it. Be specific and encouraging."
                ),
                "language": explain_lang
            })
            st.session_state["verify_ai_explain"] = res.get("answer", "")
        except:
            st.session_state["verify_ai_explain"] = ""

    if st.session_state.get("verify_ai_explain"):
        st.markdown(f"""
        <div style="background:#fff;border-radius:12px;padding:18px 22px;
             border:1.5px solid #E2E5EF;margin-bottom:14px">
            <div style="font-family:DM Sans,sans-serif;font-size:0.75rem;font-weight:500;
                 color:#A0A6BA;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px">
                AI guidance
            </div>
            <div style="font-family:DM Sans,sans-serif;font-size:0.9rem;color:#2A3050;line-height:1.65">
                {st.session_state["verify_ai_explain"]}
            </div>
        </div>""", unsafe_allow_html=True)

# Navigation
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    if st.button("← Back to scheme", use_container_width=True):
        st.switch_page("pages/4_scheme_detail.py")
with col2:
    if st.button("Browse other schemes →", use_container_width=True):
        st.switch_page("pages/3_schemes.py")