import os
import pytest
from datetime import date
from uuid import uuid4

from app.ml.features import extract_features, extract_batch, N_FEATURES
from app.ml.predictor import score_rows, model_is_available, MODEL_LABEL
from app.ml.train_model import generate_synthetic_dataset, train_and_save, MODEL_PATH
from app.models.anomaly_record import AnomalyRecord
from app.models.alert import Alert


def test_feature_extraction():
    row = {
        "full_name": "Test Student",
        "date_of_birth": "2004-05-10",
        "admission_date": "2024-08-01",
        "apaar_id": "123456789012",
        "email": "test@college.edu",
        "enrolment_number": "ENR001",
        "is_supernumerary": "false",
    }
    vec = extract_features(row)
    assert len(vec) == N_FEATURES
    assert vec[3] == 1.0  # has_apaar
    assert vec[4] == 0.0  # apaar_malformed == False
    assert vec[7] == 1.0  # has_name == True


def test_model_is_available():
    assert model_is_available() is True
    assert os.path.exists(MODEL_PATH)


def test_score_rows_identifies_anomalies():
    normal_row = {
        "full_name": "Valid Student",
        "date_of_birth": "2004-05-10",
        "admission_date": "2024-08-01",
        "apaar_id": "123456789012",
        "email": "valid@college.edu",
        "enrolment_number": "ENR001",
        "is_supernumerary": "false",
    }
    anomalous_row = {
        "full_name": "",  # missing name
        "date_of_birth": "2035-01-01",  # future DOB
        "admission_date": "2024-08-01",
        "apaar_id": "INVALID",  # malformed APAAR
        "email": "notanemail",  # malformed email
        "enrolment_number": "",  # missing enrolment
        "is_supernumerary": "false",
    }

    results = score_rows([normal_row, anomalous_row])
    assert len(results) == 2

    # Normal row check
    res_normal = results[0]
    assert res_normal["model_note"] == MODEL_LABEL
    assert res_normal["row_number"] == 2
    assert isinstance(res_normal["anomaly_score"], float)

    # Anomalous row check
    res_anom = results[1]
    assert res_anom["row_number"] == 3
    assert res_anom["is_anomaly"] is True
    assert res_anom["risk_level"] in ("critical", "high", "medium")
    assert len(res_anom["detected_issues"]) >= 2
