# VidyaVerify — Architecture Overview

VidyaVerify is a centralized platform designed for AICTE-approved higher-education institutions and regulatory authorities. It enables verified student record management, bulk onboarding, automated APAAR validation, duplicate enrolment detection across institutions, and intake quota discrepancy monitoring.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (React 18 + Vite + Tailwind + shadcn/ui)"]
        UI_Dashboards["Role-Aware Dashboards (AICTE & College)"]
        UI_Directory["Institutions & Student Directories"]
        UI_Bulk["Bulk CSV / XLSX Upload Wizard"]
        UI_Findings["Findings & Duplicates Engine"]
        UI_Alerts["Intake & Integrity Alerts"]
    end

    subgraph API_Gateway ["FastAPI Backend (REST API v1)"]
        AuthRouter["/api/v1/auth (JWT + RBAC)"]
        InstRouter["/api/v1/institutions (Multi-Tenant CRUD)"]
        StudRouter["/api/v1/students (Record Lifecycle)"]
        UploadRouter["/api/v1/uploads (Pandas & OpenPyXL Pipeline)"]
        FindRouter["/api/v1/findings (Validation Engine)"]
        AlertRouter["/api/v1/alerts (Notifications)"]
    end

    subgraph Engine ["Validation & Verification Services"]
        ValEngine["ValidationEngine (13 Configurable Rules)"]
        DedupEngine["Deduplication Engine (SHA-256 APAAR + Multi-Factor)"]
        IntakeCalc["Intake Discrepancy & Seat Headroom Calculator"]
    end

    subgraph Storage ["Database (PostgreSQL 16 / SQLite for isolated testing)"]
        DB_Users["Users & Audit Logs"]
        DB_Institutions["Institutions, Programmes, Academic Years, Approved Intake"]
        DB_Students["Students (Masked APAAR, Enrolment History)"]
        DB_Uploads["Upload Submissions & Import Errors"]
        DB_Findings["Validation Findings & Duplicate Cases"]
    end

    Frontend -->|HTTP / Bearer JWT| API_Gateway
    API_Gateway --> Engine
    API_Gateway --> Storage
    Engine --> Storage
```

---

## 2. APAAR Privacy & Security Architecture

1. **Synthetic & Zero Raw Storage**:
   - In accordance with privacy safeguards, the **raw 12-digit APAAR ID is NEVER persisted in plain text**.
   - Raw APAAR IDs are hashed using **SHA-256** (`apaar_id_hash`) for deterministic cross-institution duplicate matching.
   - For user interfaces and staff displays, a masked format (`apaar_id_masked`: `XXXX-XXXX-1234`) is rendered showing only the trailing 4 digits.
   - Raw APAAR IDs are stripped from logs and audit events.

2. **UUID Primary Keys**:
   - APAAR ID is **never used as a primary key**. All entities use UUIDv4 identifiers.
   - This prevents identity-binding bugs, supports transfers across institutions, and facilitates legitimate historical record tracking.

---

## 3. Role-Based Access Control (RBAC) Matrix

| Resource / Action | Super Admin | AICTE Admin | College Admin | Admission Staff | Authorized Verifier | Student |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Create Institution | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Institution | ✅ | ✅ | Own only | ❌ | ❌ | ❌ |
| View All Institutions | ✅ | ✅ | Own only | Own only | List only | ❌ |
| Create Student Record | ✅ | ✅ | Own inst | Own inst | ❌ | ❌ |
| View Cross-Institution Records | ✅ | ✅ | ❌ | ❌ | Verification view only | Own record |
| Bulk CSV/XLSX Upload | ✅ | ✅ | Own inst | Own inst | ❌ | ❌ |
| Resolve Validation Findings | ✅ | ✅ | Own inst | ❌ | ❌ | ❌ |
| Acknowledge Alerts | ✅ | ✅ | Own inst | ❌ | ❌ | ❌ |
| Delete Student Record | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 4. Multi-Tenant Institution Data Isolation

- Backend database dependencies enforce institution scoping:
  - If a user has `role in ['college_admin', 'admission_staff']`, their `institution_id` token claim restricts all queries (`Student.institution_id == user.institution_id`).
  - Request parameter spoofing (e.g. submitting `institution_id` in query parameters or payload) is strictly validated against the user's authenticated token claims.
  - Cross-institution duplicate records trigger review alerts rather than automatic rejections, allowing authorized administrators to review genuine transfer cases versus fraudulent double admissions.
