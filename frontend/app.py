import streamlit as st
import requests

st.set_page_config(page_title="Connection Test")
st.title("🔌 Frontend ↔ Backend Test")

if st.button("Test Connection"):
    try:
        res = requests.get("http://localhost:8000/api/ping", timeout=5)
        res.raise_for_status()
        st.success(res.json()["message"])
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend not running on http://localhost:8000")
    except Exception as e:
        st.error(f"❌ Error: {e}")