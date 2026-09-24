from fastapi import APIRouter, HTTPException

from app.core.database import (
    get_mongodb,
    get_redis,
    get_neo4j,
)


router = APIRouter()


@router.get("/system-health")
async def system_health():
    status = {"postgres": "unknown", "mongodb": "unknown", "redis": "unknown", "neo4j": "unknown"}

    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["postgres"] = "healthy"
    except Exception as e:
        status["postgres"] = f"error: {str(e)}"

    try:
        mongo = get_mongodb()
        if mongo is not None:
            await mongo.command("ping")
            status["mongodb"] = "healthy"
    except Exception as e:
        status["mongodb"] = f"error: {str(e)}"

    try:
        redis_conn = get_redis()
        if redis_conn:
            await redis_conn.ping()
            status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"

    try:
        neo = get_neo4j()
        if neo:
            neo.verify_connectivity()
            status["neo4j"] = "healthy"
    except Exception as e:
        status["neo4j"] = f"error: {str(e)}"

    return status


@router.get("/stats")
async def admin_stats():
    return {
        "total_users": 0,
        "total_complaints": 0,
        "total_policies_simulated": 0,
        "active_regions": 0
    }