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

```text
┌─────────────────────────────────────────────────────────────┐
│                    Citizen Input Layer                       │
│         (Voice · Text · Messaging · Web Portal)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (FastAPI)                       │
│              JWT Auth · Rate Limiting · CORS                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  NLP Engine  │   │  Analytics   │   │   Policy     │
│  (Groq LLM)  │   │   Engine     │   │  Simulator   │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
        ┌─────────────────────────────────────┐
        │         Data Persistence Layer       │
        │  PostgreSQL · MongoDB · Neo4j · Redis│
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │      React Dashboard (Vercel)        │
        │   Role-Based UI · Live Analytics     │
        └─────────────────────────────────────┘
```

---

## Project Structure

```text
loksetu-ai/
├── frontend/                 React + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/       Reusable UI components
│   │   ├── pages/            Route pages
│   │   ├── hooks/            Custom React hooks
│   │   ├── services/         API service layer
│   │   ├── store/            Redux slices
│   │   └── utils/            Helper functions
│   └── vercel.json
│
├── backend/                  FastAPI + Python
│   ├── app/
│   │   ├── api/v1/           API endpoints
│   │   ├── core/             Config, security, database
│   │   ├── models/           Database models
│   │   ├── schemas/          Pydantic schemas
│   │   ├── services/         Business logic + AI
│   │   └── main.py           Application entry
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml-pipeline/              ML training scripts
│   ├── data/
│   ├── notebooks/
│   ├── models/
│   └── training/
│
├── data/                     Datasets
│   ├── raw/
│   ├── processed/
│   └── synthetic/
│
├── docs/                     Documentation
├── .github/workflows/        CI/CD
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 20+ |
| Git | Latest |
| Docker | Optional |

### Clone Repository

```bash
git clone https://github.com/your-username/loksetu-ai.git
cd loksetu-ai
```

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Service | URL |
|---------|-----|
| Backend | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |

---

## Environment Variables

### Backend (`backend/.env`)

```env
APP_NAME=LokSetu AI
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
API_V1_PREFIX=/api/v1

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

DATABASE_URL=sqlite:///./loksetu.db
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=loksetu_complaints
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=http://localhost:5173,https://lok-setu-ai.vercel.app
```

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=LokSetu AI
VITE_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (OAuth2 form) |
| POST | `/api/v1/auth/login-with-role` | Role-verified login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Complaints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/complaints/` | Submit new complaint |
| POST | `/api/v1/complaints/voice` | Voice complaint |
| GET | `/api/v1/complaints/` | List complaints |
| GET | `/api/v1/complaints/{id}` | Get complaint details |
| PATCH | `/api/v1/complaints/{id}/status` | Update status |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/overview` | Overview stats |
| GET | `/api/v1/analytics/categories` | Category distribution |
| GET | `/api/v1/analytics/hotspots` | Demand hotspots |
| GET | `/api/v1/analytics/priority` | Priority breakdown |

### Policy

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/policy/simulate` | Simulate policy impact |
| GET | `/api/v1/policy/recommendations` | AI recommendations |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/system-health` | Database health check |
| GET | `/api/v1/admin/stats` | Platform statistics |

---

## Demo Flow

| Step | Action |
|------|--------|
| 1 | Register as Admin at `/register` |
| 2 | Login with role selection |
| 3 | Dashboard shows live platform stats |
| 4 | Submit complaint in Hindi / English / Tamil — AI categorizes automatically |
| 5 | Analytics shows category pie chart + India demand hotspot map |
| 6 | Policy Simulator forecasts impact of any proposed policy |
| 7 | Role-based access — try logging in with different roles to see distinct portals |

---

## Deployment

### Frontend → Vercel

| Step | Action |
|------|--------|
| 1 | Import repository at [vercel.com](https://vercel.com) |
| 2 | Root directory: `frontend` |
| 3 | Add env var: `VITE_API_BASE_URL=https://loksetu-ai-tjuq.onrender.com/api/v1` |
| 4 | Deploy |

### Backend → Render

| Step | Action |
|------|--------|
| 1 | Create Web Service at [render.com](https://render.com) |
| 2 | Root directory: `backend` |
| 3 | Build command: `pip install -r requirements.txt` |
| 4 | Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| 5 | Add environment variables (see `.env.example`) |
| 6 | Deploy |

---

## Security & Privacy

| Feature | Description |
|---------|-------------|
| DPDP Act 2023 Compliant | Uses synthetic data for demonstration |
| JWT Authentication | Secure token-based auth |
| Bcrypt Password Hashing | Industry-standard encryption |
| Role-Based Access Control | Granular permissions per role |
| CORS Protection | Whitelisted origins only |

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Team

Built with passion for **BRICS Innovation Challenge 2026**

---

<div align="center">

**LokSetu AI** — *Bridging Citizens and Policymakers through AI*

⭐ Star this repository if you find it useful

</div>
