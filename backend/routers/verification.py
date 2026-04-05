from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from config import supabase
from db import get_profile
from services.ocr_service import extract_text_from_image, verify_aadhar, verify_income_cert, verify_caste_cert
from services.pdf_generator import generate_application_guide

router = APIRouter()


class VerifyRequest(BaseModel):
    user_id: str
    scheme_id: str


@router.get("/generate-pdf/{user_id}/{scheme_id}")
async def generate_pdf(user_id: str, scheme_id: str):
    profile = get_profile(user_id)
    scheme_res = supabase.table("schemes").select("*").eq("id", scheme_id).execute()
    if not scheme_res.data:
        raise HTTPException(status_code=404, detail="Scheme not found")
    pdf = generate_application_guide(scheme_res.data[0], profile)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=apply_{scheme_id}.pdf"}
    )


@router.post("/run")
async def run_verification(req: VerifyRequest):
    profile = get_profile(req.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    scheme_res = supabase.table("schemes").select("required_docs").eq("id", req.scheme_id).execute()
    required_docs = scheme_res.data[0]["required_docs"] if scheme_res.data else []

    docs_res = supabase.table("documents").select("*").eq("user_id", req.user_id).execute()
    uploaded = {d["doc_type"]: d["storage_path"] for d in docs_res.data}

    all_issues = []
    missing_docs = []
    results = {}

    for doc_type in required_docs:
        if doc_type not in uploaded:
            missing_docs.append(doc_type)
            continue

        path = uploaded[doc_type]
        file_data = supabase.storage.from_("locker").download(path)
        ocr_text = extract_text_from_image(file_data)

        if doc_type == "aadhar":
            result = verify_aadhar(ocr_text, profile)
        elif doc_type == "income":
            result = verify_income_cert(ocr_text, profile)
        elif doc_type == "caste":
            result = verify_caste_cert(ocr_text, profile)
        else:
            result = {"passed": True, "issues": []}

        results[doc_type] = result
        if not result["passed"]:
            all_issues.extend(result["issues"])

    verified = len(missing_docs) == 0 and len(all_issues) == 0
    status = "verified" if verified else "failed"

    supabase.table("verifications").insert({
        "user_id": req.user_id,
        "scheme_id": req.scheme_id,
        "status": status,
        "reasons": missing_docs + all_issues
    }).execute()

    return {
        "verified": verified,
        "missing_docs": missing_docs,
        "issues": all_issues,
        "doc_results": results
    }