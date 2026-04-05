import easyocr
import re
from PIL import Image
import io

# Lazy load — only initializes when first OCR call is made, not at server startup
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    result = get_reader().readtext(image, detail=0)
    return " ".join(result).lower()


def verify_aadhar(ocr_text: str, profile: dict) -> dict:
    issues = []
    name = profile.get("name", "").lower()
    if name and name not in ocr_text:
        issues.append(f"Name '{profile['name']}' not found in Aadhaar")
    if not re.search(r'\d{4}\s?\d{4}\s?\d{4}', ocr_text):
        issues.append("No valid Aadhaar number detected")
    return {"passed": len(issues) == 0, "issues": issues}


def verify_income_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    income = int(profile.get("income", 0))
    numbers = re.findall(r'\d+', ocr_text)
    income_found = any(abs(int(n) - income) < 5000 for n in numbers if len(n) >= 4)
    if not income_found:
        issues.append(f"Income of Rs.{income} not found in certificate")
    return {"passed": len(issues) == 0, "issues": issues}


def verify_caste_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    caste = profile.get("caste", "").lower()
    if caste and caste not in ocr_text:
        issues.append(f"Caste '{profile['caste']}' not found in certificate")
    return {"passed": len(issues) == 0, "issues": issues}