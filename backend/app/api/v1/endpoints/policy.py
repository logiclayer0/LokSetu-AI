from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import simulate_policy_impact


router = APIRouter()


class PolicySimulationRequest(BaseModel):
    policy_title: str
    policy_description: str
    target_region: str
    budget_in_crores: float


@router.post("/simulate")
async def simulate_policy(request: PolicySimulationRequest):
    result = await simulate_policy_impact(
        title=request.policy_title,
        description=request.policy_description,
        region=request.target_region,
        budget=request.budget_in_crores
    )
    return result


@router.get("/recommendations")
async def get_recommendations():
    return {
        "recommendations": [
            {
                "project": "Road Repair - Sector 12",
                "priority": "High",
                "estimated_cost": "2.5 Cr",
                "impact_score": 8.7,
                "beneficiaries": 15000
            }
        ]
    }