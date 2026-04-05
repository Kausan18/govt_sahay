import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("BACKEND_URL", "http://localhost:8000")

def call(endpoint: str, payload: dict = None, method: str = "POST"):
    """Make API call to backend. Supports GET and POST."""
    url = f"{BASE}/api{endpoint}"
    try:
        if method == "GET":
            res = requests.get(url, timeout=30)
        else:
            res = requests.post(url, json=payload or {}, timeout=30)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to backend. Is it running on port 8000?")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. Backend may be overloaded.")
    except requests.exceptions.HTTPError as e:
        try:
            detail = res.json().get("detail", str(e))
        except:
            detail = str(e)
        raise Exception(f"API error: {detail}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")