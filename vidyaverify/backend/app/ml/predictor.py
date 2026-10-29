"""
VidyaVerify Isolation Forest — Prediction Service
===================================================
Loads the trained Isolation Forest pipeline, scores one or more
submission rows, and returns structured results.

Result schema per row:
  - row_number       : int  (1-indexed CSV row)
  - anomaly_score    : float  (Isolation Forest decision_function value;
                               more negative = more anomalous)
  - risk_level       : str   "critical" | "high" | "medium" | "low" | "normal"
  - is_anomaly       : bool  (IsolationForest predict == -1)
  - detected_issues  : list[str]  human-readable explanations
  - model_note       : str   always "STATISTICAL ANOMALY — SYNTHETIC MODEL"

IMPORTANT
---------
The model output is a statistical anomaly score derived from structural
and format features of the submitted data.  It does NOT verify APAAR ID
authenticity, does NOT query any government database, and MUST NOT be
interpreted as proof of fraud or identity irregularity.
All results carry the mandatory label: STATISTICAL ANOMALY — SYNTHETIC MODEL
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

from app.ml.features import extract_batch, extract_features, FEATURE_NAMES

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "isolation_forest.joblib")

# Module-level model cache — loaded once, reused across requests
_pipeline = None

MODEL_LABEL = "STATISTICAL ANOMALY — SYNTHETIC MODEL"


def _load_model():
    """Lazily load the trained pipeline from disk."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    if not os.path.exists(MODEL_PATH):
        logger.warning(
            "Isolation Forest model not found at %s. "
            "Run: python -m app.ml.train_model",
            MODEL_PATH,
        )
        return None
    try:
        _pipeline = joblib.load(MODEL_PATH)
        logger.info("Isolation Forest model loaded from %s", MODEL_PATH)
        return _pipeline
    except Exception as exc:
        logger.error("Failed to load ML model: %s", exc)
        return None


def _score_to_risk(score: float, is_anomaly: bool) -> str:
    """
    Map Isolation Forest decision_function score → human-readable risk level.

    IsolationForest.decision_function returns:
      negative values → more anomalous
      positive values → more normal
    Typical range: roughly -0.5 … +0.5

    We define thresholds empirically on the synthetic corpus.
    """
    if not is_anomaly:
        return "normal"
    if score < -0.20:
        return "critical"
    if score < -0.10:
        return "high"
    if score < 0.00:
        return "medium"
    return "low"


def _explain_issues(row: Dict[str, Any], score: float, is_anomaly: bool) -> List[str]:
    """
    Produce human-readable explanations for the flagged row.
    These are rule-based post-hoc explanations — the model itself
    is unsupervised.
    """
    from datetime import date
    from app.ml.features import _parse_date, APAAR_RE, EMAIL_RE

    issues: List[str] = []
    today = date.today()

    dob = _parse_date(row.get("date_of_birth"))
    adm = _parse_date(row.get("admission_date"))

    if dob and dob > today:
        issues.append(f"Date of birth ({dob}) is in the future.")

    if dob and not (dob > today):
        age = (today - dob).days / 365.25
        if age < 15:
            issues.append(f"Unusually young age at admission ({age:.1f} years) — verify DOB.")
        elif age > 60:
            issues.append(f"Unusually advanced age ({age:.1f} years) — verify DOB.")

    if adm and adm > today:
        issues.append(f"Admission date ({adm}) is in the future.")

    apaar = str(row.get("apaar_id") or "").strip()
    if not apaar:
        issues.append("Missing APAAR ID.")
    elif not APAAR_RE.match(apaar):
        issues.append(f"Malformed APAAR ID: '{apaar}' does not match 12-digit format.")

    email = str(row.get("email") or "").strip()
    if email and not EMAIL_RE.match(email):
        issues.append(f"Invalid email format: '{email}'.")

    if not str(row.get("full_name") or "").strip():
        issues.append("Missing full name.")

    if not str(row.get("enrolment_number") or "").strip():
        issues.append("Missing enrolment number.")

    if is_anomaly and not issues:
        # Model flagged it but no specific rule matched — report statistical flag
        issues.append(
            f"Statistical anomaly detected by Isolation Forest "
            f"(score={score:.4f}). Manual review recommended."
        )

    return issues


def score_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score a list of submission row dicts through the Isolation Forest.

    Parameters
    ----------
    rows : list[dict]
        Raw rows from the uploaded CSV/XLSX (post column-normalisation).
        Rows are 0-indexed internally; row_number in output is 1-indexed
        (matching the CSV, where row 1 is the header).

    Returns
    -------
    list[dict] — one result dict per row, all with model_note label.
    """
    pipeline = _load_model()
    results = []

    if pipeline is None:
        # Model not available — return a graceful degraded result per row
        for i, row in enumerate(rows, start=2):  # 2 = first data row after header
            results.append({
                "row_number": i,
                "anomaly_score": None,
                "risk_level": "unknown",
                "is_anomaly": False,
                "detected_issues": ["ML model not available — skipping anomaly scoring."],
                "model_note": MODEL_LABEL,
            })
        return results

    X = extract_batch(rows)  # shape (N, 10)

    scores: np.ndarray = pipeline.decision_function(X)   # float per row
    predictions: np.ndarray = pipeline.predict(X)        # +1 normal, -1 anomaly

    for i, (row, score, pred) in enumerate(zip(rows, scores, predictions), start=2):
        is_anomaly = bool(pred == -1)
        risk = _score_to_risk(float(score), is_anomaly)
        issues = _explain_issues(row, float(score), is_anomaly)
        results.append({
            "row_number": i,
            "anomaly_score": round(float(score), 6),
            "risk_level": risk,
            "is_anomaly": is_anomaly,
            "detected_issues": issues,
            "model_note": MODEL_LABEL,
        })

    return results


def score_single_row(row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
    """Convenience wrapper for a single row."""
    results = score_rows([row])
    r = results[0]
    r["row_number"] = row_number
    return r


def model_is_available() -> bool:
    """Return True if the trained model file exists and is loadable."""
    return _load_model() is not None

