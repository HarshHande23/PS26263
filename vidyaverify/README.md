# VidyaVerify

> **AICTE Problem Statement 26263** — APAAR-Based Student Data Management and Verification Platform

VidyaVerify is a centralized platform for AICTE-approved institutions to manage student enrolment records, detect duplicate registrations, validate APAAR identifiers (format only — no live API), and flag intake discrepancies.

> ⚠️ **All data is synthetic.** This system does not connect to any real APAAR verification service or AICTE production API.

---

## Quick Start (Docker)

### Prerequisites
- Docker Desktop 24+
- Docker Compose v2+

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd vidyaverify

# 2. Copy and configure environment
cp .env.example .env
# Edit .env — change SECRET_KEY and POSTGRES_PASSWORD at minimum

# 3. Start all services
docker compose up --build

# 4. Open the application
#    Frontend: http://localhost:5173
#    Backend API docs: http://localhost:8000/docs
```

The startup sequence automatically:
- Runs Alembic migrations (`alembic upgrade head`)
- Seeds the database with 5 institutions, programmes, academic years, and demo accounts
- Starts the FastAPI backend on port 8000
- Starts the Vite frontend on port 5173

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up a local .env (copy from root .env.example)
# Update DATABASE_URL to point to your local PostgreSQL

# Run migrations
alembic upgrade head

# Seed the database
python -m app.seeds.seed_data

# Start the dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

---

## Demo Accounts (Development Only)

| Role                  | Email                          | Password       |
|-----------------------|--------------------------------|----------------|
| Super Administrator   | superadmin@vidyaverify.dev     | SuperAdmin@123 |
| AICTE Administrator   | aicte.admin@vidyaverify.dev    | AicteAdmin@123 |
| College Administrator | college.admin@iit-demo.dev     | CollegeAdmin@123|
| Admission Staff       | admission.staff@iit-demo.dev   | AdmitStaff@123 |
| Authorized Verifier   | verifier@vidyaverify.dev       | Verifier@123   |
| Student               | student@iit-demo.dev           | Student@123    |

> ⚠️ These credentials are for **local development only**. Never use them in production.

---

## Project Structure

```
vidyaverify/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (v1)
│   │   ├── core/         # Config, security, dependencies
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── repositories/ # DB query layer
│   │   └── seeds/        # Synthetic seed data
│   ├── alembic/          # DB migrations
│   ├── tests/            # Pytest suite
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/          # Axios clients & React Query hooks
│       ├── components/   # Shared UI components
│       ├── layouts/      # App shell, sidebar
│       ├── pages/        # Route-level page components
│       ├── hooks/        # Custom hooks
│       ├── types/        # TypeScript types
│       └── utils/        # Helpers
├── sample-data/
│   └── student_import_template.xlsx
├── docs/
│   └── api.md
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Git Workflow

Branch: `feature/core-platform`

Conventional commit prefixes used:
- `chore:` — setup, configuration
- `feat:` — new features
- `test:` — test additions

---

## Tech Stack

| Layer     | Technologies |
|-----------|-------------|
| Frontend  | React 18, TypeScript, Vite 5, Tailwind CSS 3, shadcn/ui, TanStack Query v5, React Hook Form + Zod, Recharts, Lucide React |
| Backend   | Python 3.12, FastAPI 0.111, SQLAlchemy 2.0, Alembic, Pydantic 2, Pandas, OpenPyXL, Pytest |
| Database  | PostgreSQL 16 |
| Auth      | JWT (HS256), bcrypt password hashing |
| Infra     | Docker, Docker Compose |

---

## Security Notes

- Passwords are hashed with bcrypt (passlib)
- JWT tokens signed with HS256 — secret from `SECRET_KEY` env var
- APAAR IDs are never logged in plaintext
- All student queries are scoped to the authenticated user's institution
- File uploads are restricted to `.csv` / `.xlsx`, max 10 MB
- No real APAAR or AICTE API keys are used
