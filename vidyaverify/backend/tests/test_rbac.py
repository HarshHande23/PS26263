"""Tests for role-based access control."""
import pytest
from tests.conftest import make_user, make_institution, auth_headers
from app.core.enums import UserRole


class TestRBAC:
    def test_student_cannot_list_all_students(self, client, db):
        inst = make_institution(db, aicte_id="RBAC-001")
        make_user(db, "student_rbac@example.com", role=UserRole.STUDENT, institution_id=inst.id)
        headers = auth_headers(client, "student_rbac@example.com")
        resp = client.get("/api/v1/students", headers=headers)
        assert resp.status_code == 403

    def test_verifier_can_list_students(self, client, db):
        make_user(db, "verifier_rbac@example.com", role=UserRole.AUTHORIZED_VERIFIER)
        headers = auth_headers(client, "verifier_rbac@example.com")
        resp = client.get("/api/v1/students", headers=headers)
        assert resp.status_code == 200

    def test_college_admin_cannot_create_institution(self, client, db):
        inst = make_institution(db, aicte_id="RBAC-002")
        make_user(db, "ca_rbac@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "ca_rbac@example.com")
        resp = client.post("/api/v1/institutions", headers=headers, json={
            "name": "New Inst",
            "aicte_id": "RBAC-NEW",
            "institution_type": "university",
            "state": "Bihar",
        })
        assert resp.status_code == 403

    def test_aicte_admin_can_create_institution(self, client, db):
        make_user(db, "aicte_rbac@example.com", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_rbac@example.com")
        resp = client.post("/api/v1/institutions", headers=headers, json={
            "name": "AICTE Created Inst",
            "aicte_id": "RBAC-AICTE-NEW",
            "institution_type": "university",
            "state": "Delhi",
        })
        assert resp.status_code == 201

    def test_super_admin_can_create_user(self, client, db):
        make_user(db, "super_rbac@example.com", role=UserRole.SUPER_ADMIN)
        headers = auth_headers(client, "super_rbac@example.com")
        resp = client.post("/api/v1/auth/users", headers=headers, json={
            "email": "new_user_rbac@example.com",
            "full_name": "New User",
            "password": "NewPass@123",
            "role": "student",
        })
        assert resp.status_code == 201

    def test_college_admin_cannot_create_user(self, client, db):
        inst = make_institution(db, aicte_id="RBAC-003")
        make_user(db, "ca_rbac2@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "ca_rbac2@example.com")
        resp = client.post("/api/v1/auth/users", headers=headers, json={
            "email": "blocked@example.com",
            "full_name": "Blocked",
            "password": "Pass@123",
            "role": "student",
        })
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_any_endpoint(self, client, db):
        resp = client.get("/api/v1/institutions")
        assert resp.status_code == 401
