# LokSetu AI - System Architecture

## Overview

LokSetu AI is a multilingual, AI-powered Digital Public Good that aggregates citizen feedback and aligns it with national infrastructure priorities.

## High-Level Architecture
[Citizen Input: Voice / Text / Messaging]
|
v
[API Gateway - FastAPI]
|
+-----------+-----------+
| | |
v v v
[NLP Layer] [Auth Layer] [Rate Limit]
|
v
[Groq LLaMA 3.3 70B]
|
+-----------+-----------+
| | |
v v v
[PostgreSQL] [MongoDB] [Neo4j]
(Users) (Complaints) (Graph)
| | |
+-----------+-----------+
|
v
[Analytics Engine]
|
v
[React Dashboard]

## Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Gateway | FastAPI | Routing, validation, auth |
| NLP Engine | Groq LLaMA 3.3 70B | Categorization, translation, simulation |
| Relational DB | PostgreSQL | Users, roles, policies |
| Document DB | MongoDB | Complaints, unstructured data |
| Graph DB | Neo4j | Duplicate detection, relationships |
| Cache | Redis | Sessions, rate limiting |
| Frontend | React + Vite | Dashboard, analytics, simulator |

## Data Flow

1. Citizen submits complaint (voice/text).
2. NLP engine detects language and translates.
3. AI categorizes and assigns department + priority.
4. Data stored in MongoDB.
5. Graph engine checks for duplicates in Neo4j.
6. Analytics engine computes hotspots.
7. Dashboard displays results to policymakers.

## Deployment

- Frontend: Vercel
- Backend: Render
- Databases: Neon (Postgres), MongoDB Atlas, Neo4j Aura, Upstash (Redis)