from collections import Counter


def get_category_distribution() -> dict:
    from app.api.v1.endpoints.complaints import fake_complaints_db
    if not fake_complaints_db:
        return {"categories": [], "counts": []}
    counter = Counter(c["category"] for c in fake_complaints_db)
    return {
        "categories": list(counter.keys()),
        "counts": list(counter.values())
    }


def get_demand_hotspots() -> dict:
    from app.api.v1.endpoints.complaints import fake_complaints_db
    hotspots = {}
    for c in fake_complaints_db:
        loc = c.get("location", "Unknown")
        hotspots[loc] = hotspots.get(loc, 0) + 1
    sorted_hotspots = sorted(hotspots.items(), key=lambda x: x[1], reverse=True)
    return {
        "hotspots": [
            {"location": loc, "count": count, "priority": "High" if count > 10 else "Medium"}
            for loc, count in sorted_hotspots[:20]
        ]
    }


def get_priority_breakdown() -> dict:
    from app.api.v1.endpoints.complaints import fake_complaints_db
    if not fake_complaints_db:
        return {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    counter = Counter(c["priority"] for c in fake_complaints_db)
    return dict(counter)


def calculate_impact_score(complaint_count: int, population: int, infrastructure_index: float) -> float:
    if population == 0:
        return 0.0
    demand_ratio = complaint_count / population
    score = (demand_ratio * 1000) + (10 - infrastructure_index)
    return round(min(max(score, 0), 10), 2)