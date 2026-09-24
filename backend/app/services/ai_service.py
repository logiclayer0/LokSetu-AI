import json
import logging
from groq import Groq

from app.core.config import settings


logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:200]}")
    return content


async def categorize_complaint(text: str) -> dict:
    system_prompt = (
        "You are an AI classifier for citizen complaints in India. "
        "Classify the complaint and return ONLY valid JSON with keys: "
        "category, department, priority, summary. "
        "category must be one of: Road, Water, Electricity, Sanitation, Health, Education, Transport, Other. "
        "department must be one of: PWD, Jal Board, Electricity Board, Municipal, Health Dept, Education Dept, Transport Dept, General. "
        "priority must be one of: Low, Medium, High, Critical."
    )
    try:
        result = _call_groq(system_prompt, text, json_mode=True)
        parsed = json.loads(result)
        logger.info(f"Categorized: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"categorize_complaint FAILED: {type(e).__name__} - {str(e)}")
        return {
            "category": "Other",
            "department": "General",
            "priority": "Medium",
            "summary": text[:200]
        }


async def simulate_policy_impact(title: str, description: str, region: str, budget: float) -> dict:
    system_prompt = (
        "You are a policy impact simulation AI for Indian governance. "
        "Analyze the proposed policy and return ONLY valid JSON with keys: "
        "estimated_beneficiaries, budget_utilization_percent, risk_score, "
        "expected_impact, recommendations (array of strings), "
        "duplicate_risk_percent, timeline_months."
    )
    user_prompt = (
        f"Policy Title: {title}\n"
        f"Description: {description}\n"
        f"Region: {region}\n"
        f"Budget: {budget} crore INR"
    )
    try:
        result = _call_groq(system_prompt, user_prompt, json_mode=True)
        parsed = json.loads(result)
        logger.info(f"Policy simulation: {parsed}")
        return parsed
    except Exception as e:
        logger.error(f"simulate_policy_impact FAILED: {type(e).__name__} - {str(e)}")
        return {
            "estimated_beneficiaries": 0,
            "budget_utilization_percent": 0,
            "risk_score": 0,
            "expected_impact": "Unable to simulate",
            "recommendations": [],
            "duplicate_risk_percent": 0,
            "timeline_months": 0
        }


async def generate_insights(complaints: list[dict]) -> dict:
    system_prompt = (
        "You are a governance analytics AI. Analyze citizen complaints and return ONLY valid JSON "
        "with keys: top_issues (array), emerging_trends (array), recommended_actions (array)."
    )
    user_prompt = json.dumps(complaints[:50])
    try:
        result = _call_groq(system_prompt, user_prompt, json_mode=True)
        return json.loads(result)
    except Exception as e:
        logger.error(f"generate_insights FAILED: {type(e).__name__} - {str(e)}")
        return {"top_issues": [], "emerging_trends": [], "recommended_actions": []}
