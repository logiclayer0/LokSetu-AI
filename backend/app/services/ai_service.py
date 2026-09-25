import json
import logging
import re
from groq import Groq

from app.core.config import settings


logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)

VALID_CATEGORIES = {"Road", "Water", "Electricity", "Sanitation", "Health", "Education", "Transport", "Other"}
VALID_DEPARTMENTS = {"PWD", "Jal Board", "Electricity Board", "Municipal", "Health Dept", "Education Dept", "Transport Dept", "General"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: find first { ... } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not parse JSON from: {text[:300]}")


def _normalize_result(parsed: dict, original_text: str) -> dict:
    """Ensure all required keys exist and values are valid."""
    category = str(parsed.get("category", "Other")).strip()
    if category not in VALID_CATEGORIES:
        # Fuzzy match common variations
        lower = category.lower()
        if "road" in lower or "pothole" in lower or "street" in lower:
            category = "Road"
        elif "water" in lower or "pipeline" in lower or "tap" in lower:
            category = "Water"
        elif "electric" in lower or "power" in lower or "light" in lower:
            category = "Electricity"
        elif "sanit" in lower or "garbage" in lower or "drain" in lower or "sewage" in lower:
            category = "Sanitation"
        elif "health" in lower or "hospital" in lower or "clinic" in lower:
            category = "Health"
        elif "school" in lower or "educat" in lower or "college" in lower:
            category = "Education"
        elif "bus" in lower or "transport" in lower or "traffic" in lower:
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        department = "General"

    priority = str(parsed.get("priority", "Medium")).strip()
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    summary = str(parsed.get("summary", original_text[:200])).strip()
    if not summary:
        summary = original_text[:200]

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": summary
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


async def categorize_complaint(text: str) -> dict:
    system_prompt = (
        "You are an expert AI classifier for citizen complaints in India.\n"
        "Classify the complaint and return ONLY a valid JSON object with exactly these keys:\n"
        "  category, department, priority, summary\n\n"
        "Rules:\n"
        "- category MUST be one of: Road, Water, Electricity, Sanitation, Health, Education, Transport, Other\n"
        "- department MUST be one of: PWD, Jal Board, Electricity Board, Municipal, Health Dept, Education Dept, Transport Dept, General\n"
        "- priority MUST be one of: Low, Medium, High, Critical\n"
        "- summary: one short sentence summarizing the complaint\n"
        "- Do not add any extra text, markdown, or explanation. Return pure JSON only."
    )
    try:
        result = _call_groq(system_prompt, text, json_mode=True)
        parsed = _extract_json(result)
        normalized = _normalize_result(parsed, text)
        logger.info(f"Categorized successfully: {normalized}")
        return normalized
    except Exception as e:
        logger.error(f"categorize_complaint FAILED: {type(e).__name__} - {str(e)}")
        # Simple keyword-based fallback so we don't always return Other/Medium
        lower = text.lower()
        category = "Other"
        department = "General"
        priority = "Medium"

        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge"]):
            category, department = "Road", "PWD"
        elif any(w in lower for w in ["water", "pipeline", "tap", "supply", "leak"]):
            category, department = "Water", "Jal Board"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage"]):
            category, department = "Electricity", "Electricity Board"
        elif any(w in lower for w in ["garbage", "drain", "sewage", "sanitation", "waste"]):
            category, department = "Sanitation", "Municipal"
        elif any(w in lower for w in ["hospital", "clinic", "health", "doctor"]):
            category, department = "Health", "Health Dept"
        elif any(w in lower for w in ["school", "college", "education", "teacher"]):
            category, department = "Education", "Education Dept"
        elif any(w in lower for w in ["bus", "traffic", "transport", "auto"]):
            category, department = "Transport", "Transport Dept"

        if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident"]):
            priority = "Critical"
        elif any(w in lower for w in ["serious", "major", "high"]):
            priority = "High"

        return {
            "category": category,
            "department": department,
            "priority": priority,
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
        parsed = _extract_json(result)
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
        return _extract_json(result)
    except Exception as e:
        logger.error(f"generate_insights FAILED: {type(e).__name__} - {str(e)}")
        return {"top_issues": [], "emerging_trends": [], "recommended_actions": []}
