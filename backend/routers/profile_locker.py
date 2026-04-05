from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from config import supabase
from db import get_or_create_user, save_profile, get_profile, save_document_metadata
import uuid

router = APIRouter()

# Request Models
class LoginRequest(BaseModel):
    email: str

class ProfileRequest(BaseModel):
    user_id: str
    name: str
    caste: str
    age: int
    occupation: str
    religion: str
    income: int
    state: str
    gender: str

class DocumentUploadRequest(BaseModel):
    user_id: str
    doc_type: str  # 'aadhar', 'income', 'caste', 'dob', 'basic'

# 1. Simple Login - Create or fetch user
@router.post("/simple-login")
def simple_login(req: LoginRequest):
    try:
        user_id = get_or_create_user(req.email)
        return {"user_id": user_id, "message": "Login successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Save/Update Profile
@router.post("/save-profile")
def save_user_profile(req: ProfileRequest):
    try:
        data = {
            "name": req.name,
            "caste": req.caste,
            "age": req.age,
            "occupation": req.occupation,
            "religion": req.religion,
            "income": req.income,
            "state": req.state,
            "gender": req.gender
        }
        save_profile(req.user_id, data)
        return {"status": "success", "message": "Profile saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Get Profile
@router.get("/get-profile")
def get_user_profile(user_id: str):
    try:
        profile = get_profile(user_id)
        return {"profile": profile} if profile else {"profile": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. Upload Document to Supabase Storage
@router.post("/upload-document")
async def upload_document(
    user_id: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF and images allowed")
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"{user_id}/{doc_type}/{unique_filename}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase Storage
        supabase.storage.from_("locker").upload(storage_path, file_content, {"content-type": file.content_type})
        
        # Save metadata to database
        save_document_metadata(user_id, doc_type, storage_path)
        
        return {
            "status": "success",
            "message": "Document uploaded successfully",
            "storage_path": storage_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Get User's Documents
'''
@router.post("/get-documents")
def get_user_documents(user_id: str):
    try:
        res = supabase.table("documents").select("*").eq("user_id", user_id).execute()
        return {"documents": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
@router.get("/get-documents")
def get_user_documents(user_id: str):
    try:
        res = supabase.table("documents").select("*").eq("user_id", user_id).execute()
        return {"documents": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))