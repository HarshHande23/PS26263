"""
Tests for Anomaly Detection, Explainability, and Regulatory Reports (CSV & JSON).
"""

from datetime import date
from uuid import uuid4
import pytest

from tests.conftest import (
    make_user, make_institution, make_programme, make_academic_year, make_intake, auth_headers
)
from app.core.enums import UserRole
from app.models.student import Student
from app.models.audit_log import AuditLog
from app.services.anomaly_detector import run_full_anomaly_scan, sync_anomalies_to_alerts


class TestAnomalyDetection:
    def test_anomaly_intake_surge_detection(self, db):
        inst = make_institution(db, aicte_id="ANOM-001")
        prog = make_programme(db, inst.id, code="BTECH-ANOM")
        ay = make_academic_year(db, inst.id, label="2024-25")
        make_intake(db, prog.id, ay.id, seats=5)

        # Enrol 8 students (exceeding capacity of 5)
        for i in range(8):
            s = Student(
                institution_id=inst.id,
                programme_id=prog.id,
                academic_year_id=ay.id,
                full_name=f"Student {i}",
                enrolment_number=f"ENR-ANOM-{i}",
                date_of_birth=date(2004, 1, 1),
            )
            db.add(s)
        db.commit()

        anomalies = run_full_anomaly_scan(db, institution_id=inst.id)
        assert len(anomalies) >= 1
        surge = next(a for a in anomalies if a["anomaly_type"] == "INTAKE_CAPACITY_EXCEEDED")
        assert surge["metrics"]["enrolment_count"] == 8
        assert surge["metrics"]["approved_intake"] == 5
        assert surge["metrics"]["excess"] == 3
        assert surge["metrics"]["percent_exceeded"] == 60.0
        assert "Z-score" in surge["explanation"]

    def test_sync_anomalies_to_alerts(self, db):
        inst = make_institution(db, aicte_id="ANOM-002")
        prog = make_programme(db, inst.id, code="BTECH-SYNC")
        ay = make_academic_year(db, inst.id, label="2024-25")
        make_intake(db, prog.id, ay.id, seats=2)

        for i in range(4):
            db.add(
                Student(
                    institution_id=inst.id,
                    programme_id=prog.id,
                    academic_year_id=ay.id,
                    full_name=f"Student Sync {i}",
                    enrolment_number=f"ENR-SYNC-{i}",
                    date_of_birth=date(2004, 1, 1),
                )
            )
        db.commit()

        new_alerts = sync_anomalies_to_alerts(db)
        assert new_alerts >= 1


class TestRegulatoryReportsEndpoints:
    def test_enrolment_summary_json_and_csv(self, client, db):
        inst = make_institution(db, aicte_id="REP-001")
        prog = make_programme(db, inst.id, code="BTECH-REP")
        ay = make_academic_year(db, inst.id, label="2024-25")
        make_intake(db, prog.id, ay.id, seats=60)
        make_user(db, "aicte_rep@aicte.gov.in", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_rep@aicte.gov.in")

        # JSON response
        resp_json = client.get("/api/v1/reports/enrolment-summary?format=json", headers=headers)
        assert resp_json.status_code == 200
        data = resp_json.json()
        assert "count" in data
        assert any(item["aicte_id"] == "REP-001" for item in data["data"])

        # CSV response
        resp_csv = client.get("/api/v1/reports/enrolment-summary?format=csv", headers=headers)
        assert resp_csv.status_code == 200
        assert resp_csv.headers["content-type"].startswith("text/csv")
        assert "aicte_id,institution_name" in resp_csv.text
        assert "REP-001" in resp_csv.text

    def test_intake_discrepancies_report(self, client, db):
        inst = make_institution(db, aicte_id="DISC-001")
        prog = make_programme(db, inst.id, code="BTECH-DISC")
        ay = make_academic_year(db, inst.id, label="2024-25")
        make_intake(db, prog.id, ay.id, seats=2)

        for i in range(4):
            db.add(
                Student(
                    institution_id=inst.id,
                    programme_id=prog.id,
                    academic_year_id=ay.id,
                    full_name=f"Student Disc {i}",
                    enrolment_number=f"ENR-DISC-{i}",
                    date_of_birth=date(2004, 1, 1),
                )
            )
        db.commit()

        make_user(db, "aicte_disc@aicte.gov.in", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_disc@aicte.gov.in")

        resp = client.get("/api/v1/reports/intake-discrepancies?format=json", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        disc_row = next((r for r in data["data"] if r["aicte_id"] == "DISC-001"), None)
        assert disc_row is not None
        assert disc_row["excess_count"] == 2

    def test_college_admin_forbidden_on_cross_inst_discrepancies(self, client, db):
        inst = make_institution(db, aicte_id="COL-RESTRICT")
        make_user(db, "col_user@example.com", role=UserRole.COLLEGE_ADMIN, institution_id=inst.id)
        headers = auth_headers(client, "col_user@example.com")

        # College admin forbidden from cross-institution discrepancy endpoint
        resp = client.get("/api/v1/reports/intake-discrepancies", headers=headers)
        assert resp.status_code == 403

    def test_audit_logs_report(self, client, db):
        make_user(db, "aicte_audit@aicte.gov.in", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "aicte_audit@aicte.gov.in")

        log = AuditLog(
            action="student.bulk_import",
            resource_type="Submission",
            resource_id=str(uuid4()),
            details={"imported_count": 50},
        )
        db.add(log)
        db.commit()

        resp = client.get("/api/v1/reports/audit-logs?format=json", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1
        assert any(l["action"] == "student.bulk_import" for l in data["data"])
