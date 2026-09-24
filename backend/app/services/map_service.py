from typing import Optional


def get_geojson_for_complaints(complaints: list[dict]) -> dict:
    features = []
    for c in complaints:
        if c.get("latitude") and c.get("longitude"):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [c["longitude"], c["latitude"]]
                },
                "properties": {
                    "complaint_id": c["complaint_id"],
                    "category": c["category"],
                    "priority": c["priority"],
                    "status": c["status"]
                }
            })
    return {"type": "FeatureCollection", "features": features}


def get_heatmap_data(complaints: list[dict]) -> list[list[float]]:
    heatmap = []
    for c in complaints:
        if c.get("latitude") and c.get("longitude"):
            intensity = {"Low": 0.3, "Medium": 0.6, "High": 0.8, "Critical": 1.0}.get(c["priority"], 0.5)
            heatmap.append([c["latitude"], c["longitude"], intensity])
    return heatmap


def get_region_bounds(region: str) -> Optional[dict]:
    region_bounds = {
        "delhi": {"lat": [28.4, 28.9], "lng": [76.8, 77.4]},
        "mumbai": {"lat": [18.8, 19.3], "lng": [72.7, 73.0]},
        "bangalore": {"lat": [12.8, 13.2], "lng": [77.4, 77.8]},
        "chennai": {"lat": [12.9, 13.3], "lng": [80.1, 80.4]},
        "kolkata": {"lat": [22.4, 22.8], "lng": [88.2, 88.5]}
    }
    return region_bounds.get(region.lower())