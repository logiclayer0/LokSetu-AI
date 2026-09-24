import pandas as pd
import random
from faker import Faker


fake = Faker("en_IN")


CATEGORIES = ["Road", "Water", "Electricity", "Sanitation", "Health", "Education", "Transport", "Other"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]


def generate_complaints(n=500):
    rows = []
    for i in range(n):
        rows.append({
            "complaint_id": f"LS-{1000 + i}",
            "citizen_name": fake.name(),
            "citizen_phone": fake.phone_number(),
            "location": random.choice(CITIES),
            "category": random.choice(CATEGORIES),
            "priority": random.choice(PRIORITIES),
            "description": fake.sentence(nb_words=15),
            "created_at": fake.date_time_this_year().isoformat()
        })
    return pd.DataFrame(rows)


def generate_beneficiaries(n=1000):
    rows = []
    for i in range(n):
        rows.append({
            "beneficiary_id": f"BEN-{2000 + i}",
            "name": fake.name(),
            "aadhaar_hash": fake.sha256()[:16],
            "ration_card": fake.bothify(text="RC-####-????"),
            "land_record_id": fake.bothify(text="LR-######"),
            "district": random.choice(CITIES),
            "income": random.randint(10000, 200000)
        })
    return pd.DataFrame(rows)


def generate_hotspot_data(n=200):
    rows = []
    for i in range(n):
        rows.append({
            "region_id": f"R-{i}",
            "population": random.randint(5000, 100000),
            "infrastructure_index": round(random.uniform(2.0, 9.0), 2),
            "complaint_count": random.randint(10, 500),
            "avg_income": random.randint(15000, 80000),
            "priority_score": round(random.uniform(1.0, 10.0), 2)
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    generate_complaints().to_csv("../processed/complaints.csv", index=False)
    generate_beneficiaries().to_csv("../processed/beneficiaries.csv", index=False)
    generate_hotspot_data().to_csv("../processed/hotspot_data.csv", index=False)
    print("Synthetic data generated in ../processed/")