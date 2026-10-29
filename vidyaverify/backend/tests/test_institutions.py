"""Tests for institution management."""
import pytest
from tests.conftest import make_user, make_institution, auth_headers
from app.core.enums import UserRole


class TestInstitutions:
    def test_list_institutions_as_aicte_admin(self, client, db):
        make_institution(db, aicte_id="INST-LIST-001")
        make_user(db, "aicte_list@example.com", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_list@example.com")
        resp = client.get("/api/v1/institutions", headers=headers)
        assert resp.status_code == 200
        assert "items" in resp.json()
        assert resp.json()["total"] >= 1

    def test_college_admin_sees_only_own_institution(self, client, db):
        inst = make_institution(db, aicte_id="INST-SCOPE-001")
        make_institution(db, aicte_id="INST-SCOPE-002")  # another institution
        make_user(db, "ca_scope@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "ca_scope@example.com")
        resp = client.get("/api/v1/institutions", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["id"] == str(inst.id)

    def test_create_institution_as_super_admin(self, client, db):
        make_user(db, "super_inst@example.com", role=UserRole.SUPER_ADMIN)
        headers = auth_headers(client, "super_inst@example.com")
        resp = client.post("/api/v1/institutions", headers=headers, json={
            "name": "Test University",
            "aicte_id": "INST-NEW-001",
            "institution_type": "university",
            "state": "Rajasthan",
        })
        assert resp.status_code == 201
        assert resp.json()["aicte_id"] == "INST-NEW-001"

    def test_duplicate_aicte_id_rejected(self, client, db):
        make_institution(db, aicte_id="INST-DUP-001")
        make_user(db, "super_dup@example.com", role=UserRole.SUPER_ADMIN)
        headers = auth_headers(client, "super_dup@example.com")
        resp = client.post("/api/v1/institutions", headers=headers, json={
            "name": "Duplicate",
            "aicte_id": "INST-DUP-001",
            "institution_type": "university",
            "state": "Goa",
        })
        assert resp.status_code == 400

    def test_update_institution(self, client, db):
        inst = make_institution(db, aicte_id="INST-UPD-001")
        make_user(db, "super_upd@example.com", role=UserRole.SUPER_ADMIN)
        headers = auth_headers(client, "super_upd@example.com")
        resp = client.put(f"/api/v1/institutions/{inst.id}", headers=headers, json={
            "city": "Mumbai",
        })
        assert resp.status_code == 200
        assert resp.json()["city"] == "Mumbai"

    def test_get_nonexistent_institution_404(self, client, db):
        make_user(db, "super_404inst@example.com", role=UserRole.SUPER_ADMIN)
        headers = auth_headers(client, "super_404inst@example.com")
        resp = client.get("/api/v1/institutions/00000000-0000-0000-0000-000000000000", headers=headers)
        assert resp.status_code == 404
