"""
Tests for Verification Provider Adapter, Simulated Mock Provider, and QR Verification Tokens.
"""

from datetime import datetime, timezone, timedelta
import pytest
from tests.conftest import (
    make_user, make_institution, make_programme, make_academic_year, auth_headers
)
from app.core.enums import UserRole, VerificationStatus
from app.models.student import Student
from app.services.verification_provider import MockApaarVerificationProvider


class TestVerificationProvider:
    def test_mock_provider_success(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("123456789012")
        assert res.status == VerificationStatus.VERIFIED_BY_PROVIDER
        assert res.is_simulated is True
        assert "SIMULATED VERIFICATION" in res.disclaimer
        assert res.response_code == "MATCH_CONFIRMED_200"

    def test_mock_provider_timeout_simulation(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("123456789012", simulate_failure_mode="timeout")
        assert res.status == VerificationStatus.PROVIDER_UNAVAILABLE
        assert "504" in res.response_code

    def test_mock_provider_unavailable_simulation(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("123456789012", simulate_failure_mode="unavailable")
        assert res.status == VerificationStatus.PROVIDER_UNAVAILABLE
        assert "503" in res.response_code

    def test_mock_provider_manual_review_simulation(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("123456789012", simulate_failure_mode="manual_review")
        assert res.status == VerificationStatus.MANUAL_REVIEW_REQUIRED
        assert "300" in res.response_code

    def test_mock_provider_not_found(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("000012345678")  # starts with 0000
        assert res.status == VerificationStatus.NOT_VERIFIED
        assert "404" in res.response_code

    def test_mock_provider_invalid_format(self):
        provider = MockApaarVerificationProvider()
        res = provider.verify_apaar("ABC12345")
        assert res.status == VerificationStatus.NOT_VERIFIED
        assert "400" in res.response_code


class TestVerificationEndpoints:
    def test_student_verification_success(self, client, db):
        inst = make_institution(db, aicte_id="VER-001")
        user = make_user(db, "staff_ver@example.com", role=UserRole.ADMISSION_STAFF, institution_id=inst.id)
        headers = auth_headers(client, "staff_ver@example.com")

        student = Student(
            institution_id=inst.id,
            full_name="Aarav Test",
            enrolment_number="VER-ST-001",
            apaar_id_masked="XXXX-XXXX-9012",
        )
        db.add(student)
        db.commit()

        resp = client.post(
            f"/api/v1/verification/students/{student.id}/verify",
            headers=headers,
            json={"apaar_id": "123456789012"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "verified_by_provider"
        assert data["is_simulated"] is True
        assert "SIMULATED VERIFICATION" in data["disclaimer"]

        # Check DB update
        db.refresh(student)
        assert student.verification_status == VerificationStatus.VERIFIED_BY_PROVIDER
        assert student.last_verified_at is not None

    def test_student_verification_cross_institution_forbidden(self, client, db):
        inst1 = make_institution(db, aicte_id="VER-INST1")
        inst2 = make_institution(db, aicte_id="VER-INST2")
        user1 = make_user(db, "admin_inst1@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst1.id)
        headers = auth_headers(client, "admin_inst1@example.com")

        student_inst2 = Student(
            institution_id=inst2.id,
            full_name="Student Other Inst",
            enrolment_number="VER-ST-002",
        )
        db.add(student_inst2)
        db.commit()

        # College admin of inst1 cannot verify student of inst2
        resp = client.post(
            f"/api/v1/verification/students/{student_inst2.id}/verify",
            headers=headers,
            json={"apaar_id": "123456789012"},
        )
        assert resp.status_code == 403

    def test_qr_token_generation_and_public_verification(self, client, db):
        inst = make_institution(db, aicte_id="QR-001", name="IIT QR Campus")
        prog = make_programme(db, inst.id, code="BTECH-AI", name="B.Tech Artificial Intelligence")
        ay = make_academic_year(db, inst.id, label="2024-25")
        user = make_user(db, "admin_qr@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "admin_qr@example.com")

        student = Student(
            institution_id=inst.id,
            programme_id=prog.id,
            academic_year_id=ay.id,
            full_name="Rohan QR Student",
            enrolment_number="QR-001",
            verification_status=VerificationStatus.VERIFIED_BY_PROVIDER,
        )
        db.add(student)
        db.commit()

        # 1. Generate QR token
        gen_resp = client.post(
            f"/api/v1/verification/students/{student.id}/generate-qr",
            headers=headers,
        )
        assert gen_resp.status_code == 200
        qr_data = gen_resp.json()
        token = qr_data["token"]
        assert token
        assert "/verify/qr?token=" in qr_data["verification_url"]

        # 2. Public lookup via token
        pub_resp = client.post(
            "/api/v1/verification/public/verify-token",
            json={"token": token},
        )
        assert pub_resp.status_code == 200
        pub_data = pub_resp.json()
        assert pub_data["record_status"] == "FOUND"
        assert pub_data["institution_name"] == "IIT QR Campus"
        assert pub_data["programme_name"] == "B.Tech Artificial Intelligence"
        assert pub_data["student_initials"] == "R. Q. S."
        assert pub_data["verification_status"] == "SIMULATED — VERIFIED"
        assert "SIMULATED VERIFICATION" in pub_data["disclaimer"]

        # 3. Revoke QR token
        revoke_resp = client.post(
            f"/api/v1/verification/students/{student.id}/revoke-qr",
            headers=headers,
        )
        assert revoke_resp.status_code == 200

        # 4. Lookup revoked token
        pub_revoked = client.post(
            "/api/v1/verification/public/verify-token",
            json={"token": token},
        )
        assert pub_revoked.status_code == 200
        assert pub_revoked.json()["record_status"] == "REVOKED"

    def test_qr_token_expired(self, client, db):
        inst = make_institution(db, aicte_id="QR-EXP-001")
        student = Student(
            institution_id=inst.id,
            full_name="Expired QR Student",
            qr_token="expired_test_token_123",
            qr_token_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            qr_token_revoked=False,
        )
        db.add(student)
        db.commit()

        resp = client.post(
            "/api/v1/verification/public/verify-token",
            json={"token": "expired_test_token_123"},
        )
        assert resp.status_code == 200
        assert resp.json()["record_status"] == "EXPIRED"

    def test_qr_token_invalid(self, client):
        resp = client.post(
            "/api/v1/verification/public/verify-token",
            json={"token": "completely_non_existent_token"},
        )
        assert resp.status_code == 200
        assert resp.json()["record_status"] == "INVALID_TOKEN"
