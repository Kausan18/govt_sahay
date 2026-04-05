# backend/main.py — replace entire file with this
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import profile_locker, schemes, verification, ai_assistant

app = FastAPI(title="GovScheme API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_locker.router, prefix="/api/auth",    tags=["Auth"])
app.include_router(profile_locker.router, prefix="/api/profile", tags=["Profile"])
app.include_router(profile_locker.router, prefix="/api/locker",  tags=["Locker"])
app.include_router(schemes.router,        prefix="/api/schemes", tags=["Schemes"])
app.include_router(verification.router,   prefix="/api/verify",  tags=["Verification"])
app.include_router(ai_assistant.router,   prefix="/api/ai",      tags=["AI"])

@app.get("/api/ping")
def ping():
    return {"status": "connected", "message": "Backend is running!"}