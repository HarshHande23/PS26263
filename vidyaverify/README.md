# VidyaVerify (विद्यावेरिफ़ाई)

> **AICTE Problem Statement ID: 26263**  
> **Development of an APAAR ID-Based Student Data Management and Verification Platform for AICTE-Approved Institutions**

VidyaVerify is a production-grade, centralized student data management, anomaly detection, and regulatory verification platform engineered for the All India Council for Technical Education (AICTE). It enables authorized institutions to manage student enrolments, detect cross-institution duplicate registrations, validate APAAR identifiers, enforce approved intake capacity caps, and issue tamper-resistant cryptographic QR verification tokens.

> ⚠️ **STATUTORY NOTICE — ALL DATA IS SYNTHETIC**  
> VidyaVerify is an official prototype testing platform. All candidate records, APAAR numbers, and verification responses operate against synthetic test fixtures and simulated provider adapters. No real citizen PII or live production government APIs are accessed.

---

## 🏛️ System Architecture & Key Capabilities

### 1. APAAR Verification Provider Architecture
- **Provider-Independent Adapter Interface**: Complete decoupling of application logic from external verification services (`BaseVerificationProvider`).
- **Simulated Test Adapter**: `MockApaarVerificationProvider` with controlled simulation modes:
  - Simulated Success (`VERIFIED_BY_PROVIDER`)
  - Identifier Not Found (`NOT_FOUND`)
  - Manual Review Required (`MANUAL_REVIEW_REQUIRED`)
  - Provider Unavailable (`PROVIDER_UNAVAILABLE`)
  - Simulated Timeout / Network Flake
- **Strict Labelling**: Every simulated outcome carries an immutable `SIMULATED VERIFICATION` badge and legal disclaimer.

### 2. Secure Cryptographic QR Verification & Public Endpoint
- Non-repudiable candidate verification via `/verify/:token` (publicly accessible).
- Zero-Plaintext Exposure: Raw 12-digit APAAR IDs are NEVER exposed or logged; stored as salted SHA-256 hashes with masked formats (`XXXX-XXXX-1234`).
- Cryptographic 7-day token issuance with revocation checks and expiry enforcement.

### 3. Institutional Data Quality Index (IDQI)
- Explainable institutional scoring formula:
  $$\text{IDQI} = 0.35 \times C_{\text{completeness}} + 0.25 \times A_{\text{apaar}} + 0.25 \times V_{\text{format}} + 0.15 \times I_{\text{intake}}$$
- Institutional letter grades (A, B, C, D) paired with actionable remediation directives.

### 4. Explainable Enrolment Anomaly Engine
- **Intake Capacity Breaches**: Immediate alerts when enrolment exceeds approved seats, calculating excess count, percentage overflow, and statistical Z-score:
  $$Z = \frac{\text{Enrolment} - \text{Intake}}{\sqrt{\text{Intake}}}$$
- **Demographic Uniformity Warnings**: Detects abnormal demographic clustering (e.g., >90% identical birth years or email patterns in batches).
- **Verification Failure Spikes**: Flags institutions with disproportionately high verification rejection rates (>50%).
- **Alert Lifecycle Management**: Multi-step transition workflow (`open` → `under_review` → `awaiting_institution_correction` → `acknowledged` → `resolved` / `dismissed`).

### 5. Regulatory Reports & Audit Trail
- 1-click official CSV and JSON streaming exports:
  - Enrolment Summary & Capacity Utilization Report
  - Intake Discrepancies & Regulatory Sanctions Report
  - Validation Findings & Data Quality Log
  - System Audit Trail & Chain of Custody (Actor, Action, Timestamp, IP)

### 6. Official Indian Government Portal Interface (Section 18)
- Designed following Government of India web standards:
  - Deep Navy (`#0B3C5D`) and Government Blue (`#1D4E89`) visual hierarchy
  - Subtle top Tricolour ribbon (`#FF9933` / `#FFFFFF` / `#138808`)
  - Accessibility Utility Bar with A- / A / A+ font scaling, high contrast toggle, and bilingual indicators
  - Restrained, legible typography and official statutory notices

---

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker Desktop 24+
- Docker Compose v2+

```bash
# 1. Clone the repository
git clone https://github.com/HarshHande23/PS26263.git
cd PS26263/vidyaverify

# 2. Copy and configure environment variables
cp .env.example .env

# 3. Start all services via Docker Compose
docker compose up --build

# 4. Open in browser:
#    Frontend: http://localhost:5173
#    Backend API Documentation: http://localhost:8000/docs
```

The Docker startup sequence automatically:
1. Runs Alembic database migrations (`alembic upgrade head`)
2. Seeds database with 5 approved institutions, programmes, intake limits, and demo users
3. Starts the FastAPI backend on port 8000
4. Builds and serves the Vite + React frontend on port 5173

---

## 💻 Local Development Setup (Manual)

### Backend (FastAPI + Python 3.12+)

```bash
cd vidyaverify/backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial demonstration data
python -m app.seeds.seed_data

# Launch development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React + TypeScript + Vite)

```bash
cd vidyaverify/frontend

# Install dependencies
npm install

# Launch frontend dev server
npm run dev
# Or build for production:
npm run build
```

---

## 🔑 Demo Accounts (For Hackathon Evaluation)

All demonstration accounts use the password: **`Demo@1234`** (or seed credentials `SuperAdmin@123` / `AicteAdmin@123`):

| Role | Username / Email | Scope & Permissions |
| :--- | :--- | :--- |
| **Super Administrator** | `superadmin@vidyaverify.gov.in` | Global system control, user provisioning, audit inspection |
| **AICTE Administrator** | `aicte.admin@aicte.gov.in` | Cross-institution dashboard, anomaly scans, duplicate review |
| **College Administrator** | `admin@coep.ac.in` | COEP Pune institution records, student registrations, IDQI score |
| **Admission Staff** | `staff@coep.ac.in` | COEP Pune bulk uploads, student editing, validation fixes |
| **Authorized Verifier** | `verifier@tcs.com` | Minimum-access credential verification and QR token checks |
| **Student** | `student1@coep.ac.in` | Restricted to own student record and verification certificate |

---

## 🧪 Comprehensive Automated Test Suite

VidyaVerify includes 77 unit, integration, and security regression tests covering all API endpoints, RBAC policies, and verification adapters:

```bash
cd vidyaverify/backend
.venv\Scripts\activate
pytest tests/ -v
```

### Test Coverage Highlights:
- `test_auth.py`: JWT login, password hashing, active session validation
- `test_rbac.py`: Multi-tenant isolation; verifies college admins cannot read or modify other institutions' data
- `test_validation.py`: Deterministic SHA-256 APAAR hashing, Luhn checksum validation, bulk CSV upload validation
- `test_verification.py`: Mock provider modes (Success, Timeout, Offline, Manual Review) and cryptographic QR token lifecycle
- `test_analytics.py`: IDQI quality scoring formula, alert transition authorization, duplicate review rulings
- `test_reports_and_anomalies.py`: Z-score intake surge detection, CSV streaming exports, and regulatory compliance logs

---

## 📂 Repository Layout

```
vidyaverify/
├── backend/
│   ├── alembic/                 # Alembic database migrations
│   ├── app/
│   │   ├── api/v1/              # Versioned API routes
│   │   │   ├── alerts.py        # Lifecycle transition endpoints
│   │   │   ├── auth.py          # JWT authentication & session management
│   │   │   ├── dashboard.py     # AICTE analytics & College IDQI endpoints
│   │   │   ├── findings.py      # Validation errors & duplicate cases
│   │   │   ├── institutions.py  # Multi-institution management
│   │   │   ├── reports.py       # CSV/JSON regulatory reporting
│   │   │   ├── students.py      # Student CRUD & enrolment history
│   │   │   ├── uploads.py       # CSV/XLSX bulk import processing
│   │   │   └── verification.py  # Mock APAAR provider & QR token endpoints
│   │   ├── core/                # DB engine, JWT tokens, RBAC dependencies
│   │   ├── models/              # SQLAlchemy 2.0 ORM database models
│   │   ├── schemas/             # Pydantic v2 validation schemas
│   │   ├── seeds/               # Synthetic database seeding script
│   │   └── services/            # Anomaly detector, verification adapter, IDQI
│   ├── tests/                   # Pytest test suite (77 passing tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API clients & typed service calls
│   │   ├── components/gov/      # Government Design System (UtilityBar, Header, Footer)
│   │   ├── layouts/             # AppLayout with national navigation
│   │   ├── pages/               # Dashboards, reports, validation, public QR page
│   │   └── types/               # TypeScript data definitions
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛡️ Security & Privacy Guarantees

1. **Zero Raw APAAR Storage**: Raw 12-digit APAAR numbers are discarded immediately after computing deterministic SHA-256 hashes (`apaar_id_hash`) and 4-digit masked representations (`apaar_id_masked`).
2. **Multi-Tenant Row-Level Isolation**: College administrators are cryptographically restricted to their institution's `institution_id`. Cross-institution queries return 403 Forbidden.
3. **Cryptographic QR Non-Repudiation**: Verification tokens are generated with high-entropy cryptographic strings, expire automatically after 7 days, and support instant revocation.
4. **Comprehensive Audit Trail**: Every administrative action, bulk import, and verification lookup is permanently appended to `audit_logs` with actor metadata and UTC timestamps.
