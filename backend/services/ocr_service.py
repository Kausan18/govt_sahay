# Replace extract_text_from_image in ocr_service.py
import easyocr
import re
from PIL import Image
import io
import fitz  # pip install pymupdf

# In ocr_service.py — add at top
from difflib import SequenceMatcher

def fuzzy_match(a: str, b: str, threshold: float = 0.75) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def verify_aadhar(ocr_text: str, profile: dict) -> dict:
    issues = []
    name = profile.get("name", "").lower().strip()
    
    # Check each word of the name individually (handles middle name differences)
    name_parts = [p for p in name.split() if len(p) > 2]
    name_found = any(
        fuzzy_match(part, chunk)
        for part in name_parts
        for chunk in ocr_text.split()
    )
    if name and not name_found:
        issues.append(f"Name '{profile['name']}' could not be matched in Aadhaar")
    
    # Aadhaar number: 12 digits in groups of 4
    if not re.search(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}', ocr_text):
        issues.append("No valid Aadhaar number pattern detected")
    
    # DOB check if age available
    age = profile.get("age")
    if age:
        dob_years = re.findall(r'\b(19|20)\d{2}\b', ocr_text)
        if not dob_years:
            issues.append("Date of birth not clearly readable in Aadhaar")
    
    return {"passed": len(issues) == 0, "issues": issues}

def verify_income_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    income = int(profile.get("income", 0))
    # Extract all 4–7 digit numbers from the text
    numbers = [int(n) for n in re.findall(r'\b\d{4,7}\b', ocr_text)]
    # Allow ±15% variance (certificates sometimes show different fiscal year amounts)
    income_found = any(abs(n - income) <= income * 0.15 for n in numbers)
    if not income_found:
        issues.append(f"Declared income Rs.{income:,} not found in certificate (±15%)")
    return {"passed": len(issues) == 0, "issues": issues}

def verify_caste_cert(ocr_text: str, profile: dict) -> dict:
    issues = []
    caste = profile.get("caste", "").lower().strip()
    # Common aliases mapping
    caste_aliases = {
        "sc": ["scheduled caste", "sc"],
        "st": ["scheduled tribe", "st"],
        "obc": ["other backward", "obc"],
        "general": ["general", "open", "unreserved"],
    }
    search_terms = caste_aliases.get(caste, [caste])
    found = any(term in ocr_text for term in search_terms) or fuzzy_match(caste, ocr_text[:200])
    if caste and not found:
        issues.append(f"Caste category '{profile['caste']}' not matched in certificate")
    return {"passed": len(issues) == 0, "issues": issues}

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en', 'hi'], gpu=False)  # Add Hindi for Indian docs
    return _reader

def extract_text_from_image(file_bytes: bytes) -> str:
    # Detect if PDF
    if file_bytes[:4] == b'%PDF':
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            # Try native text first (faster)
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + " "
            else:
                # Fall back to OCR on rasterised page
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                result = get_reader().readtext(img, detail=0)
                text += " ".join(result) + " "
        return text.lower()
    else:
        image = Image.open(io.BytesIO(file_bytes))
        result = get_reader().readtext(image, detail=0)
        return " ".join(result).lower()