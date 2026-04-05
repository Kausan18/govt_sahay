from db import get_profile
from config import supabase

def score_scheme(profile: dict, scheme: dict) -> int:
    score = 0
    reasons = []

    # Hard filters (eliminates if fails)
    if scheme["min_age"] and profile["age"] < scheme["min_age"]: return -1
    if scheme["max_age"] and profile["age"] > scheme["max_age"]: return -1
    if scheme["income_limit"] and profile["income"] > scheme["income_limit"]: return -1
    if "all" not in scheme["genders"] and profile["gender"] not in scheme["genders"]: return -1
    if "all" not in scheme["states"] and profile["state"] not in scheme["states"]: return -1

    # Positive scoring (higher = better match)
    if profile["caste"] in scheme["castes"]: score += 30
    if profile["occupation"] in scheme["occupations"]: score += 25
    if profile["religion"] in scheme["religions"]: score += 15
    
    # Bonus for fewer required docs (easier to apply)
    score += max(0, 20 - len(scheme["required_docs"]) * 4)

    return score

def rank_schemes_for_user(user_id: str) -> list:
    profile_res = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    if not profile_res.data: return []
    profile = profile_res.data[0]

    schemes_res = supabase.table("schemes").select("*").execute()
    ranked = []
    for scheme in schemes_res.data:
        score = score_scheme(profile, scheme)
        if score >= 0:
            ranked.append({**scheme, "score": score})

    return sorted(ranked, key=lambda x: x["score"], reverse=True)