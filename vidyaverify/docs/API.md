# VidyaVerify REST API Specification (v1)

Base URL: `/api/v1`

All authenticated endpoints require an `Authorization: Bearer <token>` HTTP header.

---

## 1. Authentication (`/api/v1/auth`)

### `POST /auth/login`
- **Request**: `application/x-www-form-urlencoded`
  - `username`: Email address
  - `password`: Password string
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Full Name",
      "role": "college_admin",
      "institution_id": "uuid"
    }
  }
  ```

### `GET /auth/me`
- **Response**: Current authenticated user details with role and institution association.

---

## 2. Institutions (`/api/v1/institutions`)

- `GET /institutions`: Paginated list with search, filter by state, type. (AICTE admins see all; College admins restricted to own).
- `POST /institutions`: Create institution (Super Admin & AICTE Admin).
- `GET /institutions/{id}`: Detailed view including programmes and academic years.
- `PUT /institutions/{id}`: Update institution details.
- `GET /institutions/{id}/programmes`: List academic programmes for institution.
- `GET /institutions/{id}/academic-years`: List academic years configured for institution.
- `GET /institutions/{id}/intake`: Query approved seat intake by programme and category.

---

## 3. Students (`/api/v1/students`)

- `GET /students`: Paginated student directory with search, filter by status, category, institution.
- `POST /students`: Enroll student. Evaluates format checks and logs enrolment history.
- `GET /students/{id}`: Retrieve student record (with masked APAAR ID).
- `PUT /students/{id}`: Update student fields. Automatically logs changes to `enrolment_history`.
- `DELETE /students/{id}`: Hard deletion (Super Admin only).
- `GET /students/{id}/history`: Retrieve complete historical movement, status transitions, and audit records.

---

## 4. Bulk Import (`/api/v1/uploads`)

- `POST /uploads`: Upload CSV or XLSX file (`multipart/form-data`). Runs synchronous parsing, row validation, within-file duplicate check, cross-institution duplicate check, and intake checks.
- `GET /uploads`: List previous submission jobs for institution.
- `GET /uploads/{id}`: Summary metrics (`total_rows`, `valid_rows`, `invalid_rows`, `duplicate_rows`, `imported_rows`).
- `GET /uploads/{id}/errors`: Granular row-by-row error report with cell-level reason.
- `GET /uploads/{id}/rejected-export`: Stream rejected rows formatted as downloadable CSV.
- `GET /uploads/template/download`: Download pre-configured CSV import template.

---

## 5. Validation Findings & Duplicates (`/api/v1/findings`)

- `GET /findings`: Filter findings by severity (`error`, `warning`, `info`) and status (`open`, `resolved`, `dismissed`).
- `POST /findings/{id}/resolve`: Mark finding resolved with optional remediation note.
- `POST /findings/{id}/dismiss`: Dismiss false positive finding.
- `GET /findings/duplicates`: Review suspected cross-institution enrolment conflicts.

---

## 6. Alerts & Notifications (`/api/v1/alerts`)

- `GET /alerts`: Real-time regulatory alerts (e.g. intake quota exceeded).
- `POST /alerts/{id}/acknowledge`: Mark alert acknowledged by administrator.
