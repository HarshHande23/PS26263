"""
VidyaVerify Isolation Forest — Feature Engineering
====================================================
Converts a raw student submission row (dict from CSV/XLSX) into a
fixed-length numeric feature vector for the Isolation Forest model.

Features extracted (10 total):
  0  age_at_admission      – calculated age in years at admission date
  1  is_future_dob         – 1 if date_of_birth > today, else 0
  2  is_future_admission   – 1 if admission_date > today, else 0
  3  has_apaar             – 1 if a valid 12-digit APAAR ID is present
  4  apaar_malformed       – 1 if apaar_id exists but fails 12-digit check
  5  has_email             – 1 if email field is non-empty
  6  email_malformed       – 1 if email is present but has no '@'
  7  has_name              – 1 if full_name is non-empty
  8  is_supernumerary      – 1/0 boolean flag
  9  has_enrolment_number  – 1 if enrolment_number is non-empty

These features are entirely derived from data the institution submitted;
no government databases are contacted and no real APAAR IDs are stored.

NOTE: This module is labelled SYNTHETIC — it is trained on synthetically
generated data in the absence of any authorised real dataset.
"""

import re
from datetime import date, datetime
from typing import Any, Dict, List

import numpy as np

APAAR_RE = re.compile(r"^\d{12}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FEATURE_NAMES: List[str] = [
    "age_at_admission",
    "is_future_dob",
    "is_future_admission",
    "has_apaar",
    "apaar_malformed",
    "has_email",
    "email_malformed",
    "has_name",
    "is_supernumerary",
    "has_enrolment_number",
]
N_FEATURES = len(FEATURE_NAMES)


def _parse_date(val: Any) -> date | None:
    if not val:
        return None
    s = str(val).strip()
    if s in ("", "nan", "NaT", "None"):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    try:
        import pandas as pd
        return pd.to_datetime(s).date()
    except Exception:
        return None


def extract_features(row: Dict[str, Any]) -> np.ndarray:
    """
    Extract a 10-dimensional numeric feature vector from one submission row.

    Parameters
    ----------
    row : dict
        A single row from the uploaded CSV/XLSX, keyed by column name.

    Returns
    -------
    np.ndarray, shape (10,), dtype float32
    """
    today = date.today()

    # ── dates ─────────────────────────────────────────────────────────────────
    dob = _parse_date(row.get("date_of_birth"))
    adm = _parse_date(row.get("admission_date"))

    is_future_dob = int(dob is not None and dob > today)
    is_future_adm = int(adm is not None and adm > today)

    if dob is not None and adm is not None and not is_future_dob and not is_future_adm:
        age_at_admission = max(0.0, (adm - dob).days / 365.25)
    elif dob is not None and not is_future_dob:
        age_at_admission = max(0.0, (today - dob).days / 365.25)
    else:
        age_at_admission = 20.0  # neutral default

    # ── APAAR ─────────────────────────────────────────────────────────────────
    apaar_raw = str(row.get("apaar_id") or "").strip()
    has_apaar = int(bool(apaar_raw))
    apaar_malformed = int(bool(apaar_raw) and not APAAR_RE.match(apaar_raw))

    # ── email ─────────────────────────────────────────────────────────────────
    email = str(row.get("email") or "").strip()
    has_email = int(bool(email))
    email_malformed = int(bool(email) and not EMAIL_RE.match(email))

    # ── basic presence ────────────────────────────────────────────────────────
    has_name = int(bool(str(row.get("full_name") or "").strip()))

    sup_raw = str(row.get("is_supernumerary") or "false").strip().lower()
    is_supernumerary = int(sup_raw in ("1", "true", "yes", "y"))

    has_enrol = int(bool(str(row.get("enrolment_number") or "").strip()))

    return np.array(
        [
            age_at_admission,
            is_future_dob,
            is_future_adm,
            has_apaar,
            apaar_malformed,
            has_email,
            email_malformed,
            has_name,
            is_supernumerary,
            has_enrol,
        ],
        dtype=np.float32,
    )


def extract_batch(rows: List[Dict[str, Any]]) -> np.ndarray:
    """Vectorise a list of row dicts into shape (N, 10)."""
    return np.stack([extract_features(r) for r in rows], axis=0)

