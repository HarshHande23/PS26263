"""
VidyaVerify Isolation Forest — Training Script
================================================
Generates a clearly-labelled SYNTHETIC training dataset and trains an
Isolation Forest model.  Run this once before starting the backend:

    cd vidyaverify/backend
    .venv/Scripts/python.exe -m app.ml.train_model

The trained model is saved to:
    vidyaverify/backend/app/ml/models/isolation_forest.joblib

SYNTHETIC DATA NOTICE
---------------------
No real student records, real APAAR IDs, or real government data are used.
The training corpus is generated procedurally to represent:
  - Typical normal enrolment patterns (≈90 % of rows)
  - Anomalous patterns the model should flag (≈10 % of rows):
      • Future date-of-birth
      • Impossible age (< 5 or > 80 years at admission)
      • Missing name
      • Malformed or absent APAAR with missing enrolment number
      • Future admission date
      • Malformed email address

This is explicitly a synthetic training corpus.  The model output
is labelled "STATISTICAL ANOMALY — SYNTHETIC MODEL" in all API
responses.  It is NOT a verification of identity or APAAR authenticity.
"""

import os
import random
from datetime import date, timedelta
from typing import Any, Dict, List

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from app.ml.features import extract_batch, N_FEATURES, FEATURE_NAMES

# ── paths ──────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "isolation_forest.joblib")

# ── hyper-parameters ───────────────────────────────────────────────────────
CONTAMINATION = 0.08   # expected fraction of anomalies in production data
N_ESTIMATORS = 200
RANDOM_STATE = 42
N_TRAIN_ROWS = 5000    # synthetic training corpus size


# ── data generation ────────────────────────────────────────────────────────

def _rand_date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _generate_normal_row() -> Dict[str, Any]:
    """Generate one plausible, well-formed student record."""
    today = date.today()
    dob = _rand_date_in_range(date(1995, 1, 1), date(2006, 12, 31))
    admission = _rand_date_in_range(date(2015, 6, 1), today - timedelta(days=30))
    apaar = str(random.randint(100_000_000_000, 999_999_999_999))  # 12 digits
    email = f"student{random.randint(1, 99999)}@college.edu.in"
    return {
        "full_name": f"Student Name {random.randint(1, 9999)}",
        "date_of_birth": dob.isoformat(),
        "admission_date": admission.isoformat(),
        "apaar_id": apaar,
        "email": email,
        "enrolment_number": f"ENRL{random.randint(10000, 99999)}",
        "is_supernumerary": str(random.random() < 0.05).lower(),
    }


def _generate_anomalous_row(anomaly_kind: int) -> Dict[str, Any]:
    """Generate one anomalous row of a specific kind."""
    today = date.today()
    base = _generate_normal_row()

    if anomaly_kind == 0:
        # Future date-of-birth
        future_dob = today + timedelta(days=random.randint(1, 3650))
        base["date_of_birth"] = future_dob.isoformat()

    elif anomaly_kind == 1:
        # Age < 5 years at admission (implausibly young)
        dob = today - timedelta(days=random.randint(30, 4 * 365))
        base["date_of_birth"] = dob.isoformat()
        base["admission_date"] = (today - timedelta(days=random.randint(1, 30))).isoformat()

    elif anomaly_kind == 2:
        # Age > 80 years at admission
        dob = today - timedelta(days=random.randint(80 * 365, 100 * 365))
        base["date_of_birth"] = dob.isoformat()

    elif anomaly_kind == 3:
        # Missing name + missing enrolment
        base["full_name"] = ""
        base["enrolment_number"] = ""

    elif anomaly_kind == 4:
        # Malformed APAAR (not 12 digits) + no enrolment
        base["apaar_id"] = "NOT_VALID_APAAR"
        base["enrolment_number"] = ""

    elif anomaly_kind == 5:
        # No APAAR at all + no enrolment + no email
        base["apaar_id"] = ""
        base["enrolment_number"] = ""
        base["email"] = ""

    elif anomaly_kind == 6:
        # Future admission date
        future_adm = today + timedelta(days=random.randint(1, 365))
        base["admission_date"] = future_adm.isoformat()

    elif anomaly_kind == 7:
        # Malformed email (no @)
        base["email"] = "notanemail.domain.com"

    elif anomaly_kind == 8:
        # Supernumerary with missing APAAR
        base["is_supernumerary"] = "true"
        base["apaar_id"] = ""

    return base


def generate_synthetic_dataset(n: int = N_TRAIN_ROWS) -> List[Dict[str, Any]]:
    """
    Create a mixed synthetic corpus: ~90 % normal, ~10 % anomalous.
    Clearly labelled as SYNTHETIC.
    """
    rows: List[Dict[str, Any]] = []
    n_anomaly = int(n * CONTAMINATION)
    n_normal = n - n_anomaly

    for _ in range(n_normal):
        rows.append(_generate_normal_row())

    n_kinds = 9
    for i in range(n_anomaly):
        rows.append(_generate_anomalous_row(i % n_kinds))

    random.shuffle(rows)
    print(f"[SYNTHETIC] Generated {n_normal} normal + {n_anomaly} anomalous training rows.")
    return rows


def train_and_save() -> None:
    """Train the Isolation Forest on synthetic data and persist it."""
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("[SYNTHETIC] Generating training corpus …")
    rows = generate_synthetic_dataset(N_TRAIN_ROWS)

    X: np.ndarray = extract_batch(rows)
    print(f"[ML] Feature matrix shape: {X.shape} | features: {FEATURE_NAMES}")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("iforest", IsolationForest(
            n_estimators=N_ESTIMATORS,
            contamination=CONTAMINATION,
            random_state=RANDOM_STATE,
            max_samples="auto",
            n_jobs=-1,
        )),
    ])

    print("[ML] Training Isolation Forest …")
    pipeline.fit(X)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"[ML] Model saved to: {MODEL_PATH}")

    # Quick sanity check
    scores = pipeline.decision_function(X)
    preds = pipeline.predict(X)
    n_flagged = int((preds == -1).sum())
    print(f"[ML] Sanity: {n_flagged}/{len(X)} rows flagged as anomalous "
          f"(contamination target ~ {int(CONTAMINATION * len(X))}).")
    print("[ML] Training complete. [OK]")


if __name__ == "__main__":
    train_and_save()

