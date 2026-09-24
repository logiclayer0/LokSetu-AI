import uuid
from datetime import datetime


def generate_complaint_id() -> str:
    return f"LS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def generate_user_id() -> str:
    return f"USR-{uuid.uuid4().hex[:8].upper()}"


def sanitize_text(text: str) -> str:
    return " ".join(text.strip().split())


def calculate_priority_score(complaint_count: int, population: int) -> float:
    if population == 0:
        return 0.0
    ratio = complaint_count / population
    return round(min(ratio * 10000, 10.0), 2)