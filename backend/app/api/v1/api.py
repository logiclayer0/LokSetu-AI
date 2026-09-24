from fastapi import APIRouter

from app.api.v1.endpoints import auth, complaints, analytics, policy, admin


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(policy.router, prefix="/policy", tags=["Policy"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])