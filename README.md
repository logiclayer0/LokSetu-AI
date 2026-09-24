<div align="center">

# LokSetu AI

### A Multilingual Digital Public Good for Citizen-Centric Infrastructure Planning

**Built for BRICS Innovation Challenge 2026**

[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)](https://lok-setu-ai.vercel.app)
[![API Docs](https://img.shields.io/badge/API-Docs-blue?style=for-the-badge)](https://loksetu-ai-tjuq.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

</div>

---

## Live Links

| Service | URL |
|---------|-----|
| **Frontend** | https://lok-setu-ai.vercel.app |
| **Backend API** | https://loksetu-ai-tjuq.onrender.com |
| **API Documentation** | https://loksetu-ai-tjuq.onrender.com/docs |
| **Health Check** | https://loksetu-ai-tjuq.onrender.com/health |

> **Note:** Backend is hosted on Render's free tier. First request may take 30-60 seconds due to cold start.

---

## Problem Statement

Governments across BRICS nations struggle to consolidate citizen feedback and align it with national infrastructure priorities. Development requests live in fragmented systems, leading to:

- Misaligned public spending
- Unaddressed infrastructure gaps
- No measurable impact of large-scale digital public infrastructure initiatives

---

## Solution

**LokSetu AI** is a scalable, multilingual AI platform designed as a Digital Public Good. It aggregates citizen development requests via **voice, text, and messaging apps** across diverse linguistic regions. The system combines citizen feedback with national demographic data, infrastructure indices, and public investment plans — surfacing **demand hotspots** and recommending **high-priority development projects** to policymakers.

---

## Core Features

| Feature | Description |
|---------|-------------|
| **Multilingual Aggregation** | Supports 13+ Indian languages with automatic detection and translation |
| **AI-Powered Categorization** | Groq LLaMA 3.3 70B classifies complaints and routes them to correct departments |
| **Demand Hotspot Detection** | Geospatial analytics identifies high-priority zones on interactive maps |
| **Duplicate Detection** | Graph intelligence prevents fraudulent and duplicate beneficiary entries |
| **Policy Simulation Engine** | AI forecasts policy impact before implementation |
| **Real-Time Analytics** | Live dashboards for policymakers with actionable insights |
| **Role-Based Access Control** | Separate portals for Admin, Citizen, Officer, and Analyst |
| **Multi-Country Architecture** | Built for BRICS — scalable across nations |

---

## Role-Based Portals

| Role | Access |
|------|--------|
| **Admin** | Dashboard, Complaints, Analytics, Policy Simulator, Admin Panel |
| **Citizen** | My Complaints, New Complaint |
| **Officer** | Department Complaints, Analytics |
| **Analyst** | Analytics, Policy Simulator |

---

## Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| React 18 | Component-based UI |
| Vite | Lightning-fast build tool |
| TailwindCSS | Utility-first styling with dark mode |
| Redux Toolkit | State management |
| Recharts | Data visualization |
| Leaflet | Interactive maps |
| React Router v6 | Client-side routing |
| Axios | HTTP client |
| Framer Motion | Animations |

### Backend

| Technology | Purpose |
|------------|---------|
| FastAPI | Modern async Python framework |
| Uvicorn | ASGI server |
| Pydantic | Data validation |
| SQLAlchemy | ORM |
| SQLite / PostgreSQL | Relational database |
| MongoDB | Complaint document store |
| Redis | Caching layer |
| Neo4j | Graph database for duplicate detection |
| python-jose | JWT authentication |
| passlib + bcrypt | Password hashing |

### AI / NLP

| Technology | Purpose |
|------------|---------|
| Groq API | LLaMA 3.3 70B for ultra-fast inference |
| Whisper Large v3 | Voice transcription |
| LangChain | LLM orchestration |
| HuggingFace Transformers | NLP pipelines |
| scikit-learn + XGBoost | ML models |

### DevOps

| Technology | Purpose |
|------------|---------|
| Docker + Docker Compose | Containerization |
| GitHub Actions | CI/CD |
| Vercel | Frontend deployment |
| Render | Backend deployment |

---

## Architecture
