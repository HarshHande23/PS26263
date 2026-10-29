"""Tests for bulk import: CSV parsing, validation, duplicates, intake."""
import io
import pytest
from tests.conftest import (
    make_user, make_institution, make_programme, make_academic_year, make_intake, auth_headers
)
from app.core.enums import UserRole


def _csv(rows: list[dict]) -> bytes:
    header = "full_name,apaar_id,date_of_birth,gender,email,enrolment_number,programme_code,academic_year,admission_date,admission_category,is_supernumerary,is_nri,is_oci,is_foreign_national,is_pwd\n"
    lines = []
    for r in rows:
        lines.append(
            f"{r.get('full_name','')},{r.get('apaar_id','')},{r.get('date_of_birth','')},{r.get('gender','Male')},"
            f"{r.get('email','')},{r.get('enrolment_number','')},{r.get('programme_code','')},{r.get('academic_year','')},"
            f"{r.get('admission_date','2024-08-01')},{r.get('admission_category','general')},"
            f"{r.get('is_supernumerary','false')},{r.get('is_nri','false')},{r.get('is_oci','false')},"
            f"{r.get('is_foreign_national','false')},{r.get('is_pwd','false')}"
        )
    return (header + "\n".join(lines) + "\n").encode()


def _upload(client, headers, institution_id, rows, filename="test.csv"):
    csv_bytes = _csv(rows)
    return client.post(
        "/api/v1/uploads",
        headers=headers,
        params={"institution_id": str(institution_id)},
        files={"file": (filename, io.BytesIO(csv_bytes), "text/csv")},
    )


class TestFileUpload:
    def test_upload_valid_csv(self, client, db):
        inst = make_institution(db, aicte_id="UPL-001")
        prog = make_programme(db, inst.id, code="BTECH-CS-UPL")
        ay = make_academic_year(db, inst.id, label="2024-25-UPL")
        make_intake(db, prog.id, ay.id, "general", 60)
        make_user(db, "staff_upl@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl@example.com")

        rows = [{"full_name": "Aarav Kumar", "apaar_id": "100000000001",
                 "enrolment_number": "2024UPL001", "programme_code": "BTECH-CS-UPL",
                 "academic_year": "2024-25-UPL"}]
        resp = _upload(client, headers, inst.id, rows)
        assert resp.status_code == 201
        data = resp.json()
        assert data["total_rows"] == 1
        assert data["imported_rows"] == 1
        assert data["status"] == "completed"

    def test_upload_missing_required_column_fails(self, client, db):
        inst = make_institution(db, aicte_id="UPL-002")
        make_user(db, "staff_upl2@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl2@example.com")

        bad_csv = b"apaar_id,date_of_birth\n123456789012,2002-01-01\n"
        resp = client.post(
            "/api/v1/uploads",
            headers=headers,
            params={"institution_id": str(inst.id)},
            files={"file": ("test.csv", io.BytesIO(bad_csv), "text/csv")},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "failed"

    def test_upload_detects_within_file_duplicates(self, client, db):
        inst = make_institution(db, aicte_id="UPL-003")
        prog = make_programme(db, inst.id, code="BTECH-CS-UPL3")
        ay = make_academic_year(db, inst.id, label="2024-25-UPL3")
        make_intake(db, prog.id, ay.id, "general", 60)
        make_user(db, "staff_upl3@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl3@example.com")

        rows = [
            {"full_name": "Same Person", "apaar_id": "200000000001", "enrolment_number": "DUP001"},
            {"full_name": "Same Person", "apaar_id": "200000000001", "enrolment_number": "DUP002"},
        ]
        resp = _upload(client, headers, inst.id, rows)
        assert resp.status_code == 201
        assert resp.json()["duplicate_rows"] >= 1

    def test_upload_invalid_rows_create_import_errors(self, client, db):
        inst = make_institution(db, aicte_id="UPL-004")
        make_user(db, "staff_upl4@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl4@example.com")

        rows = [{"full_name": "", "apaar_id": "BAD_FORMAT", "enrolment_number": ""}]
        resp = _upload(client, headers, inst.id, rows)
        assert resp.status_code == 201
        submission_id = resp.json()["id"]

        errors_resp = client.get(f"/api/v1/uploads/{submission_id}/errors", headers=headers)
        assert errors_resp.status_code == 200
        assert len(errors_resp.json()) > 0

    def test_reimport_same_enrolment_number_skipped(self, client, db):
        inst = make_institution(db, aicte_id="UPL-005")
        prog = make_programme(db, inst.id, code="BTECH-CS-UPL5")
        ay = make_academic_year(db, inst.id, label="2024-25-UPL5")
        make_intake(db, prog.id, ay.id, "general", 60)
        make_user(db, "staff_upl5@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl5@example.com")

        rows = [{"full_name": "Priya Sharma", "apaar_id": "300000000001",
                 "enrolment_number": "REIMPORT001", "programme_code": "BTECH-CS-UPL5",
                 "academic_year": "2024-25-UPL5"}]

        # First upload — should succeed
        resp1 = _upload(client, headers, inst.id, rows)
        assert resp1.json()["imported_rows"] == 1

        # Second upload — same enrolment number should be skipped
        resp2 = _upload(client, headers, inst.id, rows)
        assert resp2.json()["skipped_rows"] == 1

    def test_rejected_row_export(self, client, db):
        inst = make_institution(db, aicte_id="UPL-006")
        make_user(db, "staff_upl6@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl6@example.com")

        rows = [{"full_name": "", "apaar_id": "BADFORMAT"}]
        resp = _upload(client, headers, inst.id, rows)
        submission_id = resp.json()["id"]

        export_resp = client.get(f"/api/v1/uploads/{submission_id}/rejected-export", headers=headers)
        assert export_resp.status_code == 200
        assert "text/csv" in export_resp.headers["content-type"]

    def test_unsupported_file_type_rejected(self, client, db):
        inst = make_institution(db, aicte_id="UPL-007")
        make_user(db, "staff_upl7@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upl7@example.com")

        resp = client.post(
            "/api/v1/uploads",
            headers=headers,
            params={"institution_id": str(inst.id)},
            files={"file": ("malicious.exe", io.BytesIO(b"garbage"), "application/octet-stream")},
        )
        assert resp.status_code == 400

    def test_college_admin_cannot_upload_to_other_institution(self, client, db):
        inst_a = make_institution(db, aicte_id="UPL-008")
        inst_b = make_institution(db, aicte_id="UPL-009")
        make_user(db, "ca_upl@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst_a.id)
        headers = auth_headers(client, "ca_upl@example.com")

        rows = [{"full_name": "Injected Student", "apaar_id": "400000000001"}]
        # The institution_id param is ignored for college users — they get scoped to own inst
        resp = _upload(client, headers, inst_b.id, rows)
        # Should succeed but belong to inst_a, not inst_b
        assert resp.status_code == 201
        assert resp.json()["institution_id"] == str(inst_a.id)


class TestIntakeChecking:
    def test_intake_exceeded_creates_alert(self, client, db):
        inst = make_institution(db, aicte_id="INTAKE-001")
        prog = make_programme(db, inst.id, code="BTECH-CS-INT")
        ay = make_academic_year(db, inst.id, label="2024-25-INT")
        make_intake(db, prog.id, ay.id, "general", 1)  # Only 1 seat!
        make_user(db, "staff_int@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_int@example.com")

        rows = [
            {"full_name": "Student One", "apaar_id": "500000000001",
             "enrolment_number": "INT001", "programme_code": "BTECH-CS-INT",
             "academic_year": "2024-25-INT"},
            {"full_name": "Student Two", "apaar_id": "500000000002",
             "enrolment_number": "INT002", "programme_code": "BTECH-CS-INT",
             "academic_year": "2024-25-INT"},
        ]
        resp = _upload(client, headers, inst.id, rows)
        assert resp.status_code == 201
        assert resp.json()["intake_exceeded_rows"] >= 1
