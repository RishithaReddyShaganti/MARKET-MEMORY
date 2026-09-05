# Market Memory

**Don't just watch stocks. Understand what changed.**

Market Memory is an intent-aware smart watchlist focused on attention management: eventually, it will help investors understand what meaningfully changed in the stocks they care about since they last checked.

> This repository currently implements the persistence and watchlist layer only. Attention intelligence, scoring, AI, market-data integrations, caching, and authentication are intentionally out of scope.

## Planned architecture

One FastAPI application with modular internal services. The frontend communicates with the backend over HTTP and PostgreSQL provides persistence. This is deliberately a modular monolith, not a microservice system.

## Planned stack

- Frontend: React, TypeScript, Vite, Tailwind CSS
- Backend: Python 3.10+, FastAPI, Pydantic, SQLAlchemy (planned for a later milestone)
- Data store: PostgreSQL

## Development setup

Prerequisites: Python 3.10+ and Node.js 20+.

Copy the example environment files before customizing local settings. Set `DATABASE_URL` in `backend/.env` with your local PostgreSQL credentials; credentials are never committed.

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/health`.

Run backend tests:

```powershell
cd backend
pytest
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Create a production build with:

```powershell
npm run build
```
