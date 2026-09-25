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
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(w in lower for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani"]):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "sewage", "sewer", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        # Map category to department if invalid
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage
    if any(w in lower for w in [
        "water", "pipeline", "tap", "supply", "leak", "leakage",
        "sewer", "sewar", "sewage", "nala", "nalah",
        "paani", "pani", "pani nahi", "jal"
    ]):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(w in lower for w in [
        "garbage", "drain", "sanitation", "waste", "trash",
        "kachra", "kooda", "safai", "toilet", "latrine"
    ]):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(w in lower for w in [
        "road", "pothole", "street", "footpath", "bridge",
        "sadak", "gaddha", "gadhe", "rasta"
    ]):
        category, department = "Road", "PWD"
    # Electricity
    elif any(w in lower for w in [
        "electric", "power", "light", "transformer", "outage",
        "bijli", "current", "current nahi", "light nahi"
    ]):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in [
        "hospital", "clinic", "health", "doctor", "medical", "aspatal"
    ]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in [
        "school", "college", "education", "teacher", "vidyalaya"
    ]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in [
        "bus", "traffic", "transport", "auto", "rickshaw", "metro"
    ]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(w in lower for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water", "pipeline", "tap", "supply", "leak", "leakage",
            "sewer", "sewar", "sewage", "nala", "nalah",
            "paani", "pani", "jal", "pipe", "pipeline toot",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage", "drain", "sanitation", "waste", "trash",
            "kachra", "kooda", "safai", "toilet", "latrine", "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road", "pothole", "street", "footpath", "bridge",
            "sadak", "gaddha", "gadhe", "rasta", "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric", "power", "light", "transformer", "outage",
            "bijli", "current", "current nahi", "light nahi", "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }


def _call_groq(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Groq call - model: {settings.GROQ_MODEL}, json_mode: {json_mode}")
    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    logger.info(f"Groq response: {content[:300] if content else 'EMPTY'}")
    return content or ""


def _extract_json(text: str) -> dict:
    """Extract JSON from response, even if model wraps it in markdown."""
    if not text:
        raise ValueError("Empty response from model")
    text = text.strip()
    # Remove markdown code blocks if present
    if "```" in text:
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = text.replace("```", "")
    text = text.strip()
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
        lower = category.lower()
        if any(w in lower for w in ["road", "pothole", "street", "footpath", "bridge", "sadak"]):
            category = "Road"
        elif any(
            w in lower
            for w in ["water", "pipeline", "tap", "supply", "leak", "paani", "pani", "sewer", "sewar", "sewage"]
        ):
            category = "Water"
        elif any(w in lower for w in ["electric", "power", "light", "transformer", "outage", "bijli"]):
            category = "Electricity"
        elif any(w in lower for w in ["sanit", "garbage", "drain", "waste", "kachra"]):
            category = "Sanitation"
        elif any(w in lower for w in ["health", "hospital", "clinic", "doctor"]):
            category = "Health"
        elif any(w in lower for w in ["school", "educat", "college", "teacher"]):
            category = "Education"
        elif any(w in lower for w in ["bus", "transport", "traffic", "auto"]):
            category = "Transport"
        else:
            category = "Other"

    department = str(parsed.get("department", "General")).strip()
    if department not in VALID_DEPARTMENTS:
        dept_map = {
            "Road": "PWD",
            "Water": "Jal Board",
            "Electricity": "Electricity Board",
            "Sanitation": "Municipal",
            "Health": "Health Dept",
            "Education": "Education Dept",
            "Transport": "Transport Dept",
            "Other": "General",
        }
        department = dept_map.get(category, "General")

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
        "summary": summary,
    }


def _keyword_fallback(text: str) -> dict:
    """Keyword-based classification when LLM fails. Supports English + Hindi + common typos."""
    lower = text.lower()
    category = "Other"
    department = "General"
    priority = "Medium"

    # Water / sewer / leakage (including typos like sewar)
    if any(
        w in lower
        for w in [
            "water",
            "pipeline",
            "tap",
            "supply",
            "leak",
            "leakage",
            "sewer",
            "sewar",
            "sewage",
            "nala",
            "nalah",
            "paani",
            "pani",
            "jal",
            "pipe",
        ]
    ):
        category, department = "Water", "Jal Board"
    # Sanitation / garbage
    elif any(
        w in lower
        for w in [
            "garbage",
            "drain",
            "sanitation",
            "waste",
            "trash",
            "kachra",
            "kooda",
            "safai",
            "toilet",
            "latrine",
            "ganda",
        ]
    ):
        category, department = "Sanitation", "Municipal"
    # Road
    elif any(
        w in lower
        for w in [
            "road",
            "pothole",
            "street",
            "footpath",
            "bridge",
            "sadak",
            "gaddha",
            "gadhe",
            "rasta",
            "khadanja",
        ]
    ):
        category, department = "Road", "PWD"
    # Electricity
    elif any(
        w in lower
        for w in [
            "electric",
            "power",
            "light",
            "transformer",
            "outage",
            "bijli",
            "current",
            "bijlee",
        ]
    ):
        category, department = "Electricity", "Electricity Board"
    # Health
    elif any(w in lower for w in ["hospital", "clinic", "health", "doctor", "medical", "aspatal"]):
        category, department = "Health", "Health Dept"
    # Education
    elif any(w in lower for w in ["school", "college", "education", "teacher", "vidyalaya"]):
        category, department = "Education", "Education Dept"
    # Transport
    elif any(w in lower for w in ["bus", "traffic", "transport", "auto", "rickshaw", "metro"]):
        category, department = "Transport", "Transport Dept"

    if any(w in lower for w in ["urgent", "emergency", "danger", "critical", "accident", "turant", "jaldi"]):
        priority = "Critical"
    elif any(w in lower for w in ["serious", "major", "high", "bahut"]):
        priority = "High"

    return {
        "category": category,
        "department": department,
        "priority": priority,
        "summary": text[:200],
    }
