# LokSetu AI - API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

### POST /auth/register
Register a new user.

**Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepass",
  "role": "citizen"
}
```
## POST /auth/login
Login and receive tokens.

Body (form-data):

username: email

password: password

Response:
```
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```
## Complaints
POST /complaints/
Create a new complaint.

Body:
```
{
  "citizen_name": "John",
  "citizen_phone": "9876543210",
  "location": "Delhi",
  "latitude": 28.6,
  "longitude": 77.2,
  "description": "Road is broken",
  "language": "auto"
}
```
POST /complaints/voice
Upload voice complaint (multipart).

GET /complaints/
List all complaints with optional filters.

GET /complaints/{id}
Get complaint by ID.

PATCH /complaints/{id}/status
Update complaint status.

Analytics
GET /analytics/overview
Overview stats.

GET /analytics/categories
Category distribution.

GET /analytics/hotspots
Demand hotspots.

GET /analytics/priority
Priority breakdown.

Policy
POST /policy/simulate
Simulate policy impact.

Body:
```
{
  "policy_title": "Ration Increase",
  "policy_description": "Increase from 5kg to 7kg",
  "target_region": "Delhi",
  "budget_in_crores": 500
}
```
## GET /policy/recommendations
Get AI recommendations.

Admin
GET /admin/system-health
Check health of all databases.

GET /admin/stats
Admin statistics.

---

### 📄 `docs/demo_script.md`

```markdown
# LokSetu AI - Demo Script

## Duration: 3 minutes

### 0:00 - 0:20 | Introduction
"LokSetu AI is a multilingual Digital Public Good that bridges citizens and policymakers across BRICS nations."

### 0:20 - 1:00 | Problem
"Governments receive citizen feedback in fragmented systems. Development requests go unheard. Spending is misaligned."

### 1:00 - 1:40 | Solution Demo
1. Show complaint submission (voice + text in Hindi).
2. AI categorizes and routes in real-time.
3. Show duplicate detection in Neo4j.

### 1:40 - 2:20 | Analytics + Policy Simulator
1. Show demand hotspot map.
2. Run policy simulation for "Ration Increase in Delhi".
3. Display AI-generated impact forecast.

### 2:20 - 2:50 | Tech Stack
"Built on FastAPI, React, Groq LLaMA 3.3 70B, PostgreSQL, MongoDB, Neo4j, Redis."

### 2:50 - 3:00 | Closing
"LokSetu AI - A Digital Public Good for BRICS. Scalable, multilingual, impactful."