import easyocr
import re
from PIL import Image
import io
from difflib import SequenceMatcher

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en', 'hi'], gpu=False)
    return _reader


def extract_text_from_image(file_bytes: bytes) -> str:
    # Detect PDF
    if file_bytes[:4] == b'%PDF':
        try:
            import fitz  # pymupdf
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + " "
                else:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    result = get_reader().readtext(img, detail=0)
                    text += " ".join(result) + " "
            return text.lower()
        except Exception as e:
            return f"pdf_error: {e}"
    else:
        image = Image.open(io.BytesIO(file_bytes))
        result = get_reader().readtext(image, detail=0)
        return " ".join(result).lower()


def fuzzy_match(a: str, b: str, threshold: float = 0.75) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def verify_aadhar(ocr_text: str, profile: dict) -> dict:
    issues = []
    name = profile.get("name", "").lower().strip()

    name_parts = [p for p in name.split() if len(p) > 2]
    name_found = any(
        fuzzy_match(part, chunk)
        for part in name_parts
        for chunk in ocr_text.split()
    )
    if name and not name_found:
        issues.append(f"Name '{profile['name']}' could not be matched in Aadhaar")

    if not re.search(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}', ocr_text):
        issues.append("No valid Aadhaar number pattern detected")

    return {"passed": len(issues) == 0, "issues": issues}


def verify_income_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    income = int(profile.get("income", 0))
    numbers = [int(n) for n in re.findall(r'\b\d{4,7}\b', ocr_text)]
    income_found = any(abs(n - income) <= income * 0.15 for n in numbers)
    if not income_found:
        issues.append(f"Declared income Rs.{income:,} not found in certificate (±15%)")
    return {"passed": len(issues) == 0, "issues": issues}


def verify_caste_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    caste = profile.get("caste", "").lower().strip()
    caste_aliases = {
        "sc": ["scheduled caste", "sc"],
        "st": ["scheduled tribe", "st"],
        "obc": ["other backward", "obc"],
        "general": ["general", "open", "unreserved"],
        "ews": ["economically weaker", "ews"],
    }
    search_terms = caste_aliases.get(caste, [caste])
    found = any(term in ocr_text for term in search_terms) or fuzzy_match(caste, ocr_text[:200])
    if caste and not found:
        issues.append(f"Caste category '{profile['caste']}' not matched in certificate")
    return {"passed": len(issues) == 0, "issues": issues}


def verify_face_match(profile_photo_bytes: bytes, live_photo_bytes: bytes) -> dict:
    """Compare profile photo with live webcam capture using DeepFace."""
    import tempfile
    import os

    issues = []
    tmp1 = tmp2 = None

    try:
        from deepface import DeepFace

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f1:
            f1.write(profile_photo_bytes)
            tmp1 = f1.name

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f2:
            f2.write(live_photo_bytes)
            tmp2 = f2.name

        result = DeepFace.verify(
            img1_path=tmp1,
            img2_path=tmp2,
            model_name="VGG-Face",
            detector_backend="opencv",
            enforce_detection=True,
            distance_metric="cosine"
        )

        verified = result.get("verified", False)
        distance = round(result.get("distance", 1.0), 3)
        confidence = round((1 - distance) * 100, 1)

        if not verified:
            issues.append(f"Face does not match profile photo (confidence: {confidence}%)")

        return {
            "passed": verified,
            "confidence": confidence,
            "distance": distance,
            "issues": issues
        }

    except Exception as e:
        error_msg = str(e)
        if "Face could not be detected" in error_msg:
            issues.append("No face detected in the image. Please ensure your face is clearly visible and well-lit.")
        elif "number of faces" in error_msg.lower():
            issues.append("Multiple faces detected. Please ensure only you are in frame.")
        else:
            issues.append(f"Face verification error: {error_msg}")
        return {"passed": False, "confidence": 0, "issues": issues}

    finally:
        for tmp in [tmp1, tmp2]:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except:
                    pass