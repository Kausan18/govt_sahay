from config import supabase

def get_or_create_user(email: str):
    res = supabase.table("users").select("id").eq("email", email).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]["id"]
    res = supabase.table("users").insert({"email": email}).execute()
    return res.data[0]["id"]

def save_profile(user_id: str, data: dict):
    return supabase.table("profiles").upsert({"user_id": user_id, **data}).execute()

def get_profile(user_id: str):
    res = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data and len(res.data) > 0 else None

def save_document_metadata(user_id: str, doc_type: str, storage_path: str):
    """Save document metadata to database"""
    return supabase.table("documents").insert({
        "user_id": user_id,
        "doc_type": doc_type,
        "storage_path": storage_path
    }).execute()

def get_user_documents(user_id: str):
    """Get all documents for a user"""
    res = supabase.table("documents").select("*").eq("user_id", user_id).execute()
    return res.data

def get_document_by_type(user_id: str, doc_type: str):
    """Get specific document by type"""
    res = supabase.table("documents").select("*").eq("user_id", user_id).eq("doc_type", doc_type).execute()
    return res.data[0] if res.data and len(res.data) > 0 else None