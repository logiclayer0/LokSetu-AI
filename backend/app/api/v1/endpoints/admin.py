from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal


router = APIRouter()


@router.get("/system-health")
async def system_health():
    status = {
        "database": "unknown",
        "api": "healthy",
        "ai_engine": "unknown",
    }

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["database"] = "healthy"
    except Exception:
        status["database"] = "unhealthy"

    try:
        if (
            settings.GROQ_API_KEY
            and settings.GROQ_API_KEY != "your_groq_api_key_here"
            and len(settings.GROQ_API_KEY) > 20
        ):
            status["ai_engine"] = "configured"
        else:
            status["ai_engine"] = "not configured"
    except Exception:
        status["ai_engine"] = "unknown"

    return status


@router.get("/stats")
async def admin_stats():
    total_users = 0
    total_complaints = 0
    total_policies = 0
    active_regions = 0

    try:
        from app.api.v1.endpoints.auth import fake_users_db
        total_users = len(fake_users_db)
    except Exception:
        pass

    try:
        from app.api.v1.endpoints.complaints import fake_complaints_db
        total_complaints = len(fake_complaints_db)
        regions = set()
        for c in fake_complaints_db:
            loc = c.get("location", "").strip()
            if loc:
                regions.add(loc)
        active_regions = len(regions)
        total_policies = total_complaints
    except Exception:
        pass

    return {
        "total_users": total_users,
        "total_complaints": total_complaints,
        "total_policies_simulated": total_policies,
        "active_regions": active_regions,
    }
