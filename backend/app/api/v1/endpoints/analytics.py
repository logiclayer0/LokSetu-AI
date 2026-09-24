from fastapi import APIRouter
from app.services.analytics_service import (
    get_category_distribution,
    get_demand_hotspots,
    get_priority_breakdown,
)


router = APIRouter()


@router.get("/overview")
async def analytics_overview():
    return {
        "total_complaints": 0,
        "pending": 0,
        "resolved": 0,
        "high_priority": 0
    }


@router.get("/categories")
async def category_distribution():
    return get_category_distribution()


@router.get("/hotspots")
async def demand_hotspots():
    return get_demand_hotspots()


@router.get("/priority")
async def priority_breakdown():
    return get_priority_breakdown()