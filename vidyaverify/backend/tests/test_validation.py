"""Tests for the validation engine (unit tests, no DB required)."""
import pytest
from datetime import date, timedelta
from app.services.validation_engine import ValidationEngine, hash_apaar, mask_apaar

engine = ValidationEngine()


class TestFieldValidation:
    def test_missing_name_produces_error(self):
        row = {"full_name": "", "apaar_id": "123456789012"}
        findings = engine.validate_row(row, 2)
        rule_ids = [f["rule_id"] for f in findings]
        assert "RULE_MISSING_NAME" in rule_ids

    def test_valid_row_produces_no_name_error(self):
        row = {
            "full_name": "Aarav Kumar",
            "apaar_id": "123456789012",
            "date_of_birth": date(2002, 5, 15),
            "enrolment_number": "2024CS001",
            "programme_id": "some-id",
            "academic_year_id": "some-ay",
        }
        findings = engine.validate_row(row, 2)
        assert not any(f["rule_id"] == "RULE_MISSING_NAME" for f in findings)

    def test_missing_apaar_produces_warning(self):
        row = {"full_name": "Student A", "apaar_id": ""}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_MISSING_APAAR" for f in findings)

    def test_malformed_apaar_produces_error(self):
        row = {"full_name": "Student B", "apaar_id": "ABC123"}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_MALFORMED_APAAR" for f in findings)

    def test_valid_apaar_no_format_error(self):
        row = {"full_name": "Student C", "apaar_id": "123456789012"}
        findings = engine.validate_row(row, 2)
        assert not any(f["rule_id"] == "RULE_MALFORMED_APAAR" for f in findings)

    def test_future_dob_produces_error(self):
        future = date.today() + timedelta(days=100)
        row = {"full_name": "Future Kid", "date_of_birth": future}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_FUTURE_DOB" for f in findings)

    def test_malformed_email_warning(self):
        row = {"full_name": "Bad Email", "email": "not-an-email"}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_MALFORMED_EMAIL" for f in findings)

    def test_valid_email_no_warning(self):
        row = {"full_name": "Good Email", "email": "valid@example.com"}
        findings = engine.validate_row(row, 2)
        assert not any(f["rule_id"] == "RULE_MALFORMED_EMAIL" for f in findings)

    def test_missing_programme_warning(self):
        row = {"full_name": "No Prog"}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_MISSING_PROGRAMME" for f in findings)

    def test_missing_academic_year_warning(self):
        row = {"full_name": "No AY"}
        findings = engine.validate_row(row, 2)
        assert any(f["rule_id"] == "RULE_MISSING_ACAD_YEAR" for f in findings)


class TestWithinFileDuplicates:
    def test_detects_apaar_duplicate(self):
        rows = [
            {"full_name": "Student A", "apaar_id": "123456789012"},
            {"full_name": "Student B", "apaar_id": "123456789012"},  # same APAAR
        ]
        dups = engine.detect_within_file_duplicates(rows)
        assert len(dups) == 1
        assert dups[0][2] == "apaar_hash_match"

    def test_detects_name_dob_duplicate(self):
        rows = [
            {"full_name": "Priya Sharma", "apaar_id": "", "date_of_birth": "2002-05-15"},
            {"full_name": "Priya Sharma", "apaar_id": "", "date_of_birth": "2002-05-15"},
        ]
        dups = engine.detect_within_file_duplicates(rows)
        assert len(dups) >= 1
        assert any(d[2] == "name_dob_match" for d in dups)

    def test_no_duplicates_in_clean_file(self):
        rows = [
            {"full_name": "Student A", "apaar_id": "111111111111", "date_of_birth": "2000-01-01"},
            {"full_name": "Student B", "apaar_id": "222222222222", "date_of_birth": "2001-02-02"},
            {"full_name": "Student C", "apaar_id": "333333333333", "date_of_birth": "2002-03-03"},
        ]
        dups = engine.detect_within_file_duplicates(rows)
        assert len(dups) == 0

    def test_malformed_apaar_not_checked_for_dup(self):
        rows = [
            {"full_name": "Student A", "apaar_id": "BAD"},
            {"full_name": "Student B", "apaar_id": "BAD"},
        ]
        dups = engine.detect_within_file_duplicates(rows)
        # Malformed APAARs should not cause false APAAR-hash duplicates
        assert not any(d[2] == "apaar_hash_match" for d in dups)


class TestAPAARHashing:
    def test_hash_is_deterministic(self):
        h1 = hash_apaar("123456789012")
        h2 = hash_apaar("123456789012")
        assert h1 == h2

    def test_different_apaar_different_hash(self):
        h1 = hash_apaar("123456789012")
        h2 = hash_apaar("999999999999")
        assert h1 != h2

    def test_mask_shows_last_four(self):
        masked = mask_apaar("123456789012")
        assert masked.endswith("9012")
        assert "XXXX" in masked

    def test_hash_is_not_raw_apaar(self):
        raw = "123456789012"
        h = hash_apaar(raw)
        assert raw not in h
