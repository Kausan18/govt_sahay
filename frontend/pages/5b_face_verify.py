import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np
import requests
import os
import time
import threading
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Face Verification — YojanaConnect", page_icon="📷", layout="centered")
if "user_id" not in st.session_state:
    st.switch_page("app.py")
if "verify_scheme_id" not in st.session_state:
    st.switch_page("pages/3_schemes.py")

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

.layer-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:#F2F2EE; border:1.5px solid #E2E2DC; border-radius:30px;
    padding:6px 16px; margin-bottom:24px;
    font-family:'Plus Jakarta Sans',sans-serif; font-size:0.78rem; font-weight:600;
    color:#5A5A55; letter-spacing:0.04em;
}
.layer-dot { width:8px; height:8px; border-radius:50%; background:#FF9933; flex-shrink:0; }

.camera-frame {
    background:#1C1C1A; border-radius:20px; padding:28px;
    margin-bottom:20px; text-align:center;
}
.cam-title { font-family:'Playfair Display',serif; font-size:1.2rem; color:#fff; margin-bottom:6px; }
.cam-sub { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; color:#7A7A74; margin-bottom:20px; }

.tip-row {
    display:flex; gap:10px; align-items:flex-start; margin-bottom:8px;
    font-family:'Plus Jakarta Sans',sans-serif; font-size:0.84rem; color:#5A5A55;
}
.tip-icon { flex-shrink:0; width:22px; height:22px; border-radius:50%; background:#E8F7E8;
            display:flex; align-items:center; justify-content:center; font-size:0.72rem; }

.result-ok   { background:#F0FAF0; border:2px solid #138808; border-radius:20px; padding:36px; text-align:center; margin-bottom:20px; }
.result-fail { background:#FFF4F4; border:2px solid #E74C3C; border-radius:20px; padding:36px; text-align:center; margin-bottom:20px; }
.r-icon  { font-size:3rem; margin-bottom:12px; }
.r-title { font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; margin-bottom:8px; }
.r-sub   { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.9rem; line-height:1.65; }
.r-title.ok { color:#0B6E04; } .r-sub.ok { color:#1D8A14; }
.r-title.fail { color:#C0392B; } .r-sub.fail { color:#922B21; }

.conf-bar-wrap { margin:16px auto 0; max-width:280px; }
.conf-label { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.78rem; color:#6B6B65; margin-bottom:6px; }
.conf-bar-bg { background:#E8E8E3; border-radius:4px; height:8px; }
.conf-bar { height:8px; border-radius:4px; transition:width 0.5s; }
.conf-bar.high { background:#138808; }
.conf-bar.low  { background:#E74C3C; }

.stButton > button {
    font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.95rem !important;
    font-weight:600 !important; border-radius:12px !important; padding:13px 28px !important;
    border:none !important; background:#1C1C1A !important; color:#fff !important;
    transition:all 0.18s !important;
}
.stButton > button:hover { background:#138808 !important; transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(19,136,8,0.25) !important; }

.skip-note { font-family:'Plus Jakarta Sans',sans-serif; font-size:0.8rem; color:#A0A09A; text-align:center; margin-top:12px; }
.stAlert { border-radius:12px !important; font-family:'Plus Jakarta Sans',sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pg-wrap">
    <div class="step-track">
        <div class="stp done"></div><div class="stp done"></div>
        <div class="stp now"></div><div class="stp"></div>
    </div>
    <div class="pg-title">Face verification</div>
    <div class="pg-sub">Layer 2 of 2 — we'll take a live photo and match it against your profile photo.</div>
</div>
<div class="layer-badge">
    <div class="layer-dot"></div>
    Layer 2 · Live face match
</div>
""", unsafe_allow_html=True)

# ── State ──────────────────────────────────────────────
if "face_result" not in st.session_state:
    st.session_state["face_result"] = None
if "captured_frame" not in st.session_state:
    st.session_state["captured_frame"] = None
if "capture_trigger" not in st.session_state:
    st.session_state["capture_trigger"] = False

# ── Video processor ────────────────────────────────────
class FaceCapture(VideoProcessorBase):
    """Draws a face oval guide and captures frame on demand."""

    def __init__(self):
        self.frame_lock = threading.Lock()
        self.latest_frame = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        h, w = img.shape[:2]

        # Draw oval face guide
        cx, cy = w // 2, h // 2
        rx, ry = int(w * 0.18), int(h * 0.32)
        overlay = img.copy()
        cv2.ellipse(overlay, (cx, cy), (rx, ry), 0, 0, 360, (19, 136, 8), 3)
        # Dim outside oval
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(mask, (cx, cy), (rx, ry), 0, 0, 360, 255, -1)
        dark = img.copy()
        dark[:] = (dark * 0.4).astype(np.uint8)
        img = np.where(mask[:, :, None] == 255, img, dark)
        cv2.ellipse(img, (cx, cy), (rx, ry), 0, 0, 360, (19, 136, 8), 3)

        # Guide text
        cv2.putText(img, "Position face in oval", (cx - 115, cy + ry + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 190), 1, cv2.LINE_AA)

        with self.frame_lock:
            self.latest_frame = img.copy()

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def get_frame(self):
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None


# ── RTC config (for deployment; localhost works without this) ──
RTC_CONFIG = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# ── Tips ───────────────────────────────────────────────
st.markdown("""
<div style="background:#fff;border:1.5px solid #E8E8E3;border-radius:16px;padding:22px 24px;margin-bottom:20px">
    <p style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.12em;color:#B0B0AA;margin-bottom:14px">Tips for best results</p>
    <div class="tip-row"><div class="tip-icon">💡</div><div>Ensure your face is well lit — avoid strong backlighting</div></div>
    <div class="tip-row"><div class="tip-icon">👁️</div><div>Look directly at the camera and remove glasses if possible</div></div>
    <div class="tip-row"><div class="tip-icon">📸</div><div>Keep the same neutral expression as your profile photo</div></div>
</div>
""", unsafe_allow_html=True)

# ── Show result if already captured ────────────────────
if st.session_state["face_result"] is not None:
    res = st.session_state["face_result"]
    conf = res.get("confidence", 0)
    passed = res.get("passed", False)

    if passed:
        st.markdown(f"""
        <div class="result-ok">
            <div class="r-icon">✅</div>
            <div class="r-title ok">Face matched!</div>
            <div class="r-sub ok">Your live photo matches your profile photo with {conf}% confidence.</div>
            <div class="conf-bar-wrap">
                <div class="conf-label">Match confidence: {conf}%</div>
                <div class="conf-bar-bg">
                    <div class="conf-bar high" style="width:{min(conf,100)}%"></div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Proceed to final verification →", use_container_width=True):
                st.session_state["face_verified"] = True
                st.switch_page("pages/5_verification.py")
        with col2:
            if st.button("Retake photo", use_container_width=True):
                st.session_state["face_result"] = None
                st.session_state["captured_frame"] = None
                st.rerun()

    else:
        issues = res.get("issues", ["Face did not match."])
        st.markdown(f"""
        <div class="result-fail">
            <div class="r-icon">❌</div>
            <div class="r-title fail">Face not matched</div>
            <div class="r-sub fail">{issues[0] if issues else 'Match failed.'}</div>
            <div class="conf-bar-wrap">
                <div class="conf-label">Match confidence: {conf}%</div>
                <div class="conf-bar-bg">
                    <div class="conf-bar low" style="width:{min(conf,100)}%"></div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Try again", use_container_width=True):
                st.session_state["face_result"] = None
                st.session_state["captured_frame"] = None
                st.rerun()
        with col2:
            if st.button("Skip face check →", use_container_width=True):
                st.session_state["face_verified"] = False
                st.switch_page("pages/5_verification.py")

else:
    # ── Live camera ────────────────────────────────────
    st.markdown("""
    <div class="camera-frame">
        <div class="cam-title">Live camera</div>
        <div class="cam-sub">Position your face inside the oval, then click Capture.</div>
    </div>""", unsafe_allow_html=True)

    ctx = webrtc_streamer(
        key="face-capture",
        video_processor_factory=FaceCapture,
        rtc_configuration=RTC_CONFIG,
        media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
        async_processing=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if ctx.video_processor:
        if st.button("📸  Capture & verify", use_container_width=True):
            frame = ctx.video_processor.get_frame()
            if frame is not None:
                # Convert BGR → RGB → JPEG bytes
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=92)
                live_bytes = buf.getvalue()
                st.session_state["captured_frame"] = live_bytes

                with st.spinner("Comparing with your profile photo…"):
                    try:
                        resp = requests.post(
                            f"{BASE}/api/verify/verify-face",
                            data={"user_id": st.session_state["user_id"]},
                            files={"live_photo": ("live.jpg", live_bytes, "image/jpeg")},
                            timeout=60
                        )
                        if resp.ok:
                            st.session_state["face_result"] = resp.json()
                        else:
                            detail = resp.json().get("detail", "Verification failed")
                            st.session_state["face_result"] = {
                                "passed": False, "confidence": 0, "issues": [detail]
                            }
                    except Exception as e:
                        st.session_state["face_result"] = {
                            "passed": False, "confidence": 0,
                            "issues": [f"Connection error: {e}"]
                        }
                st.rerun()
            else:
                st.warning("Camera not ready yet. Wait a moment and try again.")
    else:
        st.info("Click 'START' above to activate your camera.")

    # ── No profile photo fallback ─────────────────────
    st.markdown("""
    <p class="skip-note">
        Don't have a profile photo uploaded? 
        <a href="#" onclick="window.location.href='pages/1_profile.py'" 
           style="color:#138808;font-weight:600">Update your profile</a> 
        or skip this step.
    </p>""", unsafe_allow_html=True)

    if st.button("Skip face verification →", use_container_width=False):
        st.session_state["face_verified"] = False
        st.switch_page("pages/5_verification.py")

# ── Back button ────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("← Back to scheme"):
    st.switch_page("pages/4_scheme_detail.py")