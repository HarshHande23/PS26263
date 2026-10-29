"""
Tests for Analytics, Explainable Data Quality Scoring, Alert Review Workflow, and Duplicate Reviews.
"""

from uuid import uuid4
from datetime import date
import pytest
from tests.conftest import (
    make_user, make_institution, make_programme, make_academic_year, make_intake, auth_headers
)
from app.core.enums import UserRole, VerificationStatus
from app.models.student import Student
from app.models.alert import Alert
from app.models.duplicate_case import DuplicateCase


class TestAnalyticsAndDataQuality:
    def test_college_dashboard_data_quality(self, client, db):
        inst = make_institution(db, aicte_id="DQ-001")
        prog = make_programme(db, inst.id, code="BTECH-DQ")
        ay = make_academic_year(db, inst.id, label="2024-25")
        user = make_user(db, "admin_dq@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "admin_dq@example.com")

        # Add 2 students
        s1 = Student(
            institution_id=inst.id,
            programme_id=prog.id,
            academic_year_id=ay.id,
            full_name="Complete Student",
            enrolment_number="ENR-DQ-1",
            date_of_birth=date(2004, 1, 1),
            email="s1@example.com",
            verification_status=VerificationStatus.VERIFIED_BY_PROVIDER,
        )
        s2 = Student(
            institution_id=inst.id,
            programme_id=prog.id,
            academic_year_id=ay.id,
            full_name="Incomplete Student",
            enrolment_number="ENR-DQ-2",
            date_of_birth=None,  # Missing DOB
            email=None,
        )
        db.add_all([s1, s2])
        db.commit()

        resp = client.get("/api/v1/dashboard/college", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_students"] == 2
        assert "data_quality" in data
        dq = data["data_quality"]
        assert 0.0 <= dq["score"] <= 100.0
        assert dq["grade"] in ("A", "B", "C", "D")
        assert len(dq["factors"]) > 0
        assert len(dq["actionable_recommendations"]) > 0

    def test_aicte_analytics_endpoint(self, client, db):
        inst = make_institution(db, aicte_id="AICTE-AN-001")
        user = make_user(db, "aicte_an@example.com", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_an@example.com")

        resp = client.get("/api/v1/dashboard/analytics", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "enrolment_by_state" in data
        assert "enrolment_by_programme" in data
        assert "verification_status_dist" in data
        assert "intake_vs_enrolment" in data
        assert "institution_data_quality" in data


class TestAlertAndDuplicateWorkflows:
    def test_alert_transition_workflow(self, client, db):
        inst = make_institution(db, aicte_id="ALT-WF-001")
        aicte_user = make_user(db, "aicte_alt@example.com", role=UserRole.AICTE_ADMIN)
        aicte_headers = auth_headers(client, "aicte_alt@example.com")
        college_user = make_user(db, "college_alt@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        college_headers = auth_headers(client, "college_alt@example.com")

        # Create intake exceeded alert
        alert = Alert(
            institution_id=inst.id,
            alert_type="intake_exceeded",
            severity="error",
            title="Intake Limit Exceeded",
            status="open",
        )
        db.add(alert)
        db.commit()

        # 1. College admin attempts to resolve AICTE regulatory alert -> FORBIDDEN (403)
        res1 = client.post(
            f"/api/v1/alerts/{alert.id}/transition",
            headers=college_headers,
            json={"status": "resolved", "resolution_reason": "Trying to self-resolve"},
        )
        assert res1.status_code == 403

        # 2. AICTE admin resolves without reason -> BAD REQUEST (400)
        res2 = client.post(
            f"/api/v1/alerts/{alert.id}/transition",
            headers=aicte_headers,
            json={"status": "resolved", "resolution_reason": ""},
        )
        assert res2.status_code == 400

        # 3. AICTE admin transitions to under_review -> SUCCESS (200)
        res3 = client.post(
            f"/api/v1/alerts/{alert.id}/transition",
            headers=aicte_headers,
            json={"status": "under_review", "resolution_reason": "Investigating intake records"},
        )
        assert res3.status_code == 200
        assert res3.json()["status"] == "under_review"

        # 4. AICTE admin resolves with proper reason -> SUCCESS (200)
        res4 = client.post(
            f"/api/v1/alerts/{alert.id}/transition",
            headers=aicte_headers,
            json={"status": "resolved", "resolution_reason": "Verified supernumerary seats approved by council."},
        )
        assert res4.status_code == 200
        assert res4.json()["status"] == "resolved"

    def test_duplicate_review_workflow(self, client, db):
        inst1 = make_institution(db, aicte_id="DUP-REV-1")
        inst2 = make_institution(db, aicte_id="DUP-REV-2")
        s1 = Student(institution_id=inst1.id, full_name="Student 1")
        s2 = Student(institution_id=inst2.id, full_name="Student 2")
        db.add_all([s1, s2])
        db.flush()

        dup = DuplicateCase(
            student_a_id=s1.id,
            student_b_id=s2.id,
            institution_a_id=inst1.id,
            institution_b_id=inst2.id,
            match_reason="apaar_hash_match",
            confidence="high",
            status="suspected",
        )
        db.add(dup)
        db.commit()

        aicte_user = make_user(db, "aicte_dup@example.com", role=UserRole.AICTE_ADMIN)
        aicte_headers = auth_headers(client, "aicte_dup@example.com")
        college_user = make_user(db, "college_dup@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst1.id)
        college_headers = auth_headers(client, "college_dup@example.com")

        # College admin cannot review duplicate case (403)
        c_res = client.post(
            f"/api/v1/findings/duplicates/{dup.id}/review",
            headers=college_headers,
            json={"status": "confirmed", "notes": "Not permitted"},
        )
        assert c_res.status_code == 403

        # AICTE admin can review and confirm
        a_res = client.post(
            f"/api/v1/findings/duplicates/{dup.id}/review",
            headers=aicte_headers,
            json={"status": "confirmed", "notes": "Concurrent enrolment verified. Alerting both institutions."},
        )
        assert a_res.status_code == 200
        assert a_res.json()["status"] == "confirmed"
