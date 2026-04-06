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
    if file_bytes[:4] == b'%PDF':
        try:
            import fitz
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


def fuzzy_match(a: str, b: str, threshold: float = 0.72) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def _name_found_in_text(name: str, ocr_text: str) -> bool:
    """Multi-strategy name matching robust to OCR noise and formatting."""
    name = name.lower().strip()
    parts = [p for p in name.split() if len(p) > 2]

    # Strategy 1: exact full name substring
    if name in ocr_text:
        return True

    # Strategy 2: all significant parts present with fuzzy tolerance
    words = ocr_text.split()
    if all(any(fuzzy_match(part, w) for w in words) for part in parts):
        return True

    # Strategy 3: at least 60% of name parts matched (handles missing middle name)
    matched = sum(1 for part in parts if any(fuzzy_match(part, w) for w in words))
    if parts and matched / len(parts) >= 0.6:
        return True

    return False


def verify_aadhar(ocr_text: str, profile: dict) -> dict:
    """
    Runs two independent sub-checks:
      1. Name match — profile name vs OCR text
      2. Aadhaar number match — profile aadhaar_number vs OCR text
    Both must pass for the document to be verified.
    Results are returned per sub-check so the UI can show each separately.
    """
    issues = []
    sub_checks = {}

    # ── Sub-check 1: Name ─────────────────────────────────────────────────────
    name = profile.get("name", "").strip()
    if name:
        name_found = _name_found_in_text(name, ocr_text)
        if name_found:
            sub_checks["name_match"] = {
                "label": "Name verification",
                "passed": True,
                "detail": f"'{name}' matched in Aadhaar document"
            }
        else:
            sub_checks["name_match"] = {
                "label": "Name verification",
                "passed": False,
                "detail": f"Name '{name}' could not be matched in Aadhaar document"
            }
            issues.append(f"Name '{name}' not found in Aadhaar document")
    else:
        sub_checks["name_match"] = {
            "label": "Name verification",
            "passed": False,
            "detail": "No name found in profile to verify"
        }
        issues.append("Profile name is missing — cannot verify name on Aadhaar")

    # ── Sub-check 2: Aadhaar number ───────────────────────────────────────────
    aadhaar_in_profile = str(profile.get("aadhaar_number") or "").strip()
    if aadhaar_in_profile and len(aadhaar_in_profile) == 12:
        # Remove spaces/dashes from OCR text for comparison
        ocr_digits_only = re.sub(r'[\s\-]', '', ocr_text)
        last4 = aadhaar_in_profile[-4:]

        # Check 1: full 12-digit match in stripped OCR
        full_match = aadhaar_in_profile in ocr_digits_only

        # Check 2: pattern match with spaces (e.g. "1234 5678 9012")
        spaced_pattern = (
            aadhaar_in_profile[:4] + r'[\s\-]?' +
            aadhaar_in_profile[4:8] + r'[\s\-]?' +
            aadhaar_in_profile[8:]
        )
        pattern_match = bool(re.search(spaced_pattern, ocr_text))

        # Check 3: last-4 fallback (Aadhaar often partially masked on docs)
        last4_pattern = r'[xX*]{4}[\s\-]?[xX*]{4}[\s\-]?' + last4
        last4_match = bool(re.search(last4_pattern, ocr_text)) or last4 in ocr_text

        number_found = full_match or pattern_match or last4_match

        if number_found:
            sub_checks["number_match"] = {
                "label": "Aadhaar number verification",
                "passed": True,
                "detail": f"Aadhaar number ending in {last4} confirmed in document"
            }
        else:
            sub_checks["number_match"] = {
                "label": "Aadhaar number verification",
                "passed": False,
                "detail": f"Aadhaar number ending in {last4} not found in document"
            }
            issues.append(f"Aadhaar number (ending {last4}) not found in document")
    elif aadhaar_in_profile:
        # Malformed number in profile
        sub_checks["number_match"] = {
            "label": "Aadhaar number verification",
            "passed": False,
            "detail": "Aadhaar number in profile is not 12 digits — please update your profile"
        }
        issues.append("Aadhaar number in profile is invalid — please re-enter it")
    else:
        # No aadhaar number stored — just check a pattern exists
        if re.search(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}', ocr_text):
            sub_checks["number_match"] = {
                "label": "Aadhaar number verification",
                "passed": True,
                "detail": "12-digit Aadhaar number pattern found in document"
            }
        else:
            sub_checks["number_match"] = {
                "label": "Aadhaar number verification",
                "passed": False,
                "detail": "No Aadhaar number found in document. Add your Aadhaar number to your profile for stricter verification."
            }
            issues.append("No Aadhaar number detected in document")

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "sub_checks": sub_checks   # NEW — returned to frontend for detailed display
    }


def verify_income_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    income = int(profile.get("income", 0))
    if income == 0:
        return {"passed": True, "issues": [], "sub_checks": {}}
    numbers = [int(n) for n in re.findall(r'\b\d{4,7}\b', ocr_text)]
    income_found = any(abs(n - income) <= income * 0.20 for n in numbers)
    if not income_found:
        issues.append(f"Declared income Rs.{income:,} not found in certificate (±20% tolerance)")
    return {"passed": len(issues) == 0, "issues": issues, "sub_checks": {}}


def verify_caste_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    caste = profile.get("caste", "").lower().strip()
    caste_aliases = {
        "sc": ["scheduled caste", "sc", "s.c"],
        "st": ["scheduled tribe", "st", "s.t"],
        "obc": ["other backward", "obc", "o.b.c"],
        "ews": ["economically weaker", "ews", "e.w.s"],
        "general": ["general", "open", "unreserved", "ur"],
    }
    search_terms = caste_aliases.get(caste, [caste])
    found = any(term in ocr_text for term in search_terms)
    if caste and not found:
        issues.append(f"Caste category '{profile['caste']}' not matched in certificate")
    return {"passed": len(issues) == 0, "issues": issues, "sub_checks": {}}


def verify_face_match(profile_photo_bytes: bytes, live_photo_bytes: bytes) -> dict:
    import tempfile, os
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
            img1_path=tmp1, img2_path=tmp2,
            model_name="VGG-Face", detector_backend="opencv",
            enforce_detection=False, distance_metric="cosine",
            threshold=0.45
        )
        verified = result.get("verified", False)
        distance = round(result.get("distance", 1.0), 3)
        confidence = round(max(0, (1 - distance / 0.45) * 100), 1)

        # Borderline leniency for poor webcam quality
        if not verified and distance < 0.50:
            verified = True
            confidence = round(max(0, (1 - distance / 0.50) * 100), 1)

        if not verified:
            issues.append(f"Face does not match profile photo (similarity: {confidence:.0f}%)")

        return {"passed": verified, "confidence": confidence, "distance": distance, "issues": issues}

    except Exception as e:
        error_msg = str(e)
        if "Face could not be detected" in error_msg or "opencv" in error_msg.lower():
            issues.append("Face not clearly detected. Ensure good lighting and face the camera directly.")
        elif "number of faces" in error_msg.lower():
            issues.append("Multiple faces detected. Ensure only you are visible in frame.")
        else:
            issues.append(f"Face verification error — try retaking the photo.")
        return {"passed": False, "confidence": 0, "distance": 1.0, "issues": issues}
    finally:
        for tmp in [tmp1, tmp2]:
            if tmp and os.path.exists(tmp):
                try: os.unlink(tmp)
                except: pass