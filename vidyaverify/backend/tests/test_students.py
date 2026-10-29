"""Tests for student CRUD and institution data isolation."""
import pytest
from tests.conftest import (
    make_user, make_institution, make_programme, make_academic_year, auth_headers
)
from app.core.enums import UserRole


def _student_payload(institution_id, programme_id=None, academic_year_id=None, suffix="001"):
    return {
        "full_name": f"Test Student {suffix}",
        "institution_id": str(institution_id),
        "programme_id": str(programme_id) if programme_id else None,
        "academic_year_id": str(academic_year_id) if academic_year_id else None,
        "enrolment_number": f"2024CS{suffix}",
        "admission_category": "general",
        "enrolment_status": "active",
        "gender": "Male",
        "apaar_id": f"12345678{suffix}",
    }


class TestStudentCRUD:
    def test_create_student(self, client, db):
        inst = make_institution(db, aicte_id="STU-001")
        prog = make_programme(db, inst.id, code="BTECH-CS-STU")
        ay = make_academic_year(db, inst.id, label="2024-25-STU")
        make_user(db, "staff_stu@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_stu@example.com")

        payload = _student_payload(inst.id, prog.id, ay.id, "001")
        resp = client.post("/api/v1/students", headers=headers, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["full_name"] == "Test Student 001"
        assert data["enrolment_number"] == "2024CS001"
        # APAAR should be masked, not raw
        assert data.get("apaar_id_masked", "").startswith("XXXX")

    def test_get_student(self, client, db):
        inst = make_institution(db, aicte_id="STU-002")
        make_user(db, "staff_get@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_get@example.com")
        payload = _student_payload(inst.id, suffix="002")
        create_resp = client.post("/api/v1/students", headers=headers, json=payload)
        assert create_resp.status_code == 201
        student_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/students/{student_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == student_id

    def test_update_student(self, client, db):
        inst = make_institution(db, aicte_id="STU-003")
        make_user(db, "staff_upd@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_upd@example.com")
        payload = _student_payload(inst.id, suffix="003")
        create_resp = client.post("/api/v1/students", headers=headers, json=payload)
        student_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/students/{student_id}", headers=headers, json={
            "full_name": "Updated Name",
            "enrolment_status": "graduated",
        })
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"
        assert resp.json()["enrolment_status"] == "graduated"

    def test_delete_student_requires_super_admin(self, client, db):
        inst = make_institution(db, aicte_id="STU-004")
        make_user(db, "ca_del@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        make_user(db, "super_del@example.com", role=UserRole.SUPER_ADMIN)
        ca_headers = auth_headers(client, "ca_del@example.com")
        sa_headers = auth_headers(client, "super_del@example.com")

        payload = _student_payload(inst.id, suffix="004")
        create_resp = client.post("/api/v1/students", headers=ca_headers, json=payload)
        student_id = create_resp.json()["id"]

        # College admin cannot delete
        resp = client.delete(f"/api/v1/students/{student_id}", headers=ca_headers)
        assert resp.status_code == 403

        # Super admin can delete
        resp = client.delete(f"/api/v1/students/{student_id}", headers=sa_headers)
        assert resp.status_code == 204

    def test_get_nonexistent_student_returns_404(self, client, db):
        make_user(db, "admin_404@example.com", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "admin_404@example.com")
        resp = client.get("/api/v1/students/00000000-0000-0000-0000-000000000000", headers=headers)
        assert resp.status_code == 404


class TestDataIsolation:
    def test_college_admin_cannot_create_student_for_other_institution(self, client, db):
        inst_a = make_institution(db, aicte_id="ISO-001")
        inst_b = make_institution(db, aicte_id="ISO-002")
        make_user(db, "ca_iso@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst_a.id)
        headers = auth_headers(client, "ca_iso@example.com")

        payload = _student_payload(inst_b.id, suffix="ISO")  # points to inst_b
        resp = client.post("/api/v1/students", headers=headers, json=payload)
        assert resp.status_code == 403

    def test_college_admin_only_sees_own_institution_in_list(self, client, db):
        inst_a = make_institution(db, aicte_id="ISO-003")
        inst_b = make_institution(db, aicte_id="ISO-004")
        make_user(db, "ca_iso2@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst_a.id)
        make_user(db, "sa_iso2@example.com", role=UserRole.SUPER_ADMIN)

        sa_headers = auth_headers(client, "sa_iso2@example.com")
        ca_headers = auth_headers(client, "ca_iso2@example.com")

        # SA creates student at inst_b
        client.post("/api/v1/students", headers=sa_headers, json=_student_payload(inst_b.id, suffix="XYZ"))

        # CA at inst_a should not see inst_b students
        resp = client.get("/api/v1/students", headers=ca_headers)
        assert resp.status_code == 200
        for s in resp.json()["items"]:
            assert s["institution_id"] == str(inst_a.id)

    def test_college_admin_cannot_access_other_institution_detail(self, client, db):
        inst_a = make_institution(db, aicte_id="ISO-005")
        inst_b = make_institution(db, aicte_id="ISO-006")
        make_user(db, "ca_iso3@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst_a.id)
        make_user(db, "sa_iso3@example.com", role=UserRole.SUPER_ADMIN)
        sa_headers = auth_headers(client, "sa_iso3@example.com")
        ca_headers = auth_headers(client, "ca_iso3@example.com")

        create_resp = client.post("/api/v1/students", headers=sa_headers,
                                  json=_student_payload(inst_b.id, suffix="ZZZ"))
        student_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/students/{student_id}", headers=ca_headers)
        assert resp.status_code == 403

    def test_enrolment_history_tracked(self, client, db):
        inst = make_institution(db, aicte_id="ISO-007")
        make_user(db, "ca_hist@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "ca_hist@example.com")

        create_resp = client.post("/api/v1/students", headers=headers,
                                  json=_student_payload(inst.id, suffix="HIST"))
        student_id = create_resp.json()["id"]

        # Update status
        client.put(f"/api/v1/students/{student_id}", headers=headers,
                   json={"enrolment_status": "graduated"})

        # Check history
        hist_resp = client.get(f"/api/v1/students/{student_id}/history", headers=headers)
        assert hist_resp.status_code == 200
        assert len(hist_resp.json()) >= 2  # initial + update
