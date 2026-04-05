from fastapi import APIRouter, HTTPException
from services.scoring_engine import rank_schemes_for_user
from config import supabase

router = APIRouter()

@router.get("/ranked/{user_id}")
def get_ranked_schemes(user_id: str):
    try:
        return {"schemes": rank_schemes_for_user(user_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scheme_id}")
def get_scheme_detail(scheme_id: str):
    res = supabase.table("schemes").select("*").eq("id", scheme_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return res.data[0]