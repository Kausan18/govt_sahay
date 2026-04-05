from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.grok_service import ask_about_scheme, situational_query
from services.scoring_engine import rank_schemes_for_user
from config import supabase

router = APIRouter()

class SchemeQueryRequest(BaseModel):
    scheme_id: str
    question: str
    language: str = "English"

class SituationalRequest(BaseModel):
    user_id: str
    situation: str

@router.post("/ask-scheme")
def ask_scheme(req: SchemeQueryRequest):
    scheme_res = supabase.table("schemes").select("*").eq("id", req.scheme_id).execute()
    if not scheme_res.data:
        raise HTTPException(status_code=404, detail="Scheme not found")
    answer = ask_about_scheme(scheme_res.data[0], req.question, req.language)
    return {"answer": answer}

# In ai_assistant.py — add fallback if no ranked schemes
@router.post("/situational")
def situational(req: SituationalRequest):
    profile_res = supabase.table("profiles").select("*").eq("user_id", req.user_id).execute()
    profile = profile_res.data[0] if profile_res.data else {}
    
    try:
        schemes = rank_schemes_for_user(req.user_id)
    except Exception:
        schemes = []
    
    if not schemes:
        # Fetch all schemes without scoring as fallback
        all_res = supabase.table("schemes").select("name,description,benefits,income_limit,occupations").limit(20).execute()
        schemes = all_res.data if all_res.data else []
    
    answer = situational_query(profile, req.situation, schemes)
    return {"answer": answer}