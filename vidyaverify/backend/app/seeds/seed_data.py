"""
Synthetic seed script for VidyaVerify.
Creates 5 fictional institutions, programmes, academic years, approved intake,
and demo users for every role.

Run: python -m app.seeds.seed_data
"""

import sys
import os

# Allow running as module from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datetime import date, datetime, timezone
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.enums import UserRole, InstitutionType, ProgrammeLevel
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.approved_intake import ApprovedIntake
from app.models.user import User
from app.models.student import Student


INSTITUTIONS = [
    {
        "name": "Indian Institute of Technology - Demopur",
        "short_name": "IIT-Demo",
        "aicte_id": "AICTE-DEMO-001",
        "institution_type": InstitutionType.TECHNICAL_INSTITUTE,
        "state": "Maharashtra",
        "district": "Pune",
        "city": "Pune",
        "address": "IIT Campus, Demo Road, Pune - 411001",
        "pincode": "411001",
        "phone": "02012345678",
        "email": "admin@iit-demo.edu.in",
        "website": "https://iit-demo.edu.in",
        "establishment_year": 1958,
    },
    {
        "name": "National Institute of Technology - Synthetica",
        "short_name": "NIT-Synth",
        "aicte_id": "AICTE-DEMO-002",
        "institution_type": InstitutionType.TECHNICAL_INSTITUTE,
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "city": "Bengaluru",
        "address": "NIT Campus, Synth Nagar, Bengaluru - 560001",
        "pincode": "560001",
        "phone": "08012345678",
        "email": "admin@nit-synth.edu.in",
        "website": "https://nit-synth.edu.in",
        "establishment_year": 1965,
    },
    {
        "name": "Fictitious University of Technology",
        "short_name": "FUT",
        "aicte_id": "AICTE-DEMO-003",
        "institution_type": InstitutionType.DEEMED_UNIVERSITY,
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "Chennai",
        "address": "FUT Campus, Anna Salai, Chennai - 600001",
        "pincode": "600001",
        "phone": "04412345678",
        "email": "admin@fut.edu.in",
        "website": "https://fut.edu.in",
        "establishment_year": 1978,
    },
    {
        "name": "Demotown Engineering College",
        "short_name": "DEC",
        "aicte_id": "AICTE-DEMO-004",
        "institution_type": InstitutionType.AFFILIATED_COLLEGE,
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "city": "Lucknow",
        "address": "DEC Road, Gomti Nagar, Lucknow - 226001",
        "pincode": "226001",
        "phone": "05212345678",
        "email": "admin@dec.edu.in",
        "website": "https://dec.edu.in",
        "establishment_year": 1990,
    },
    {
        "name": "Synthetic Polytechnic Institute",
        "short_name": "SPI",
        "aicte_id": "AICTE-DEMO-005",
        "institution_type": InstitutionType.AUTONOMOUS_COLLEGE,
        "state": "Gujarat",
        "district": "Ahmedabad",
        "city": "Ahmedabad",
        "address": "SPI Complex, SG Road, Ahmedabad - 380001",
        "pincode": "380001",
        "phone": "07912345678",
        "email": "admin@spi.edu.in",
        "website": "https://spi.edu.in",
        "establishment_year": 2002,
    },
]

PROGRAMMES_BY_INST = {
    "AICTE-DEMO-001": [
        {"name": "B.Tech Computer Science", "code": "BTECH-CS", "level": "undergraduate", "duration_years": 4},
        {"name": "B.Tech Electrical Engineering", "code": "BTECH-EE", "level": "undergraduate", "duration_years": 4},
        {"name": "M.Tech Artificial Intelligence", "code": "MTECH-AI", "level": "postgraduate", "duration_years": 2},
    ],
    "AICTE-DEMO-002": [
        {"name": "B.Tech Mechanical Engineering", "code": "BTECH-ME", "level": "undergraduate", "duration_years": 4},
        {"name": "B.Tech Civil Engineering", "code": "BTECH-CE", "level": "undergraduate", "duration_years": 4},
        {"name": "M.Tech Structural Engineering", "code": "MTECH-SE", "level": "postgraduate", "duration_years": 2},
    ],
    "AICTE-DEMO-003": [
        {"name": "B.Tech Information Technology", "code": "BTECH-IT", "level": "undergraduate", "duration_years": 4},
        {"name": "BCA", "code": "BCA", "level": "undergraduate", "duration_years": 3},
        {"name": "MCA", "code": "MCA", "level": "postgraduate", "duration_years": 2},
    ],
    "AICTE-DEMO-004": [
        {"name": "B.Tech Computer Science", "code": "BTECH-CS", "level": "undergraduate", "duration_years": 4},
        {"name": "Diploma in Civil Engineering", "code": "DIP-CE", "level": "diploma", "duration_years": 3},
    ],
    "AICTE-DEMO-005": [
        {"name": "Diploma in Mechanical Engineering", "code": "DIP-ME", "level": "diploma", "duration_years": 3},
        {"name": "Diploma in Electronics", "code": "DIP-EL", "level": "diploma", "duration_years": 3},
    ],
}

ACADEMIC_YEARS = [
    {"label": "2022-23", "start_year": 2022, "end_year": 2023, "is_current": False},
    {"label": "2023-24", "start_year": 2023, "end_year": 2024, "is_current": False},
    {"label": "2024-25", "start_year": 2024, "end_year": 2025, "is_current": True},
]

# Intake: programme_code -> {academic_year_label -> {category -> seats}}
INTAKE = {
    "BTECH-CS": {
        "2024-25": {"general": 60, "obc": 27, "sc": 15, "st": 7, "ews": 6},
        "2023-24": {"general": 60, "obc": 27, "sc": 15, "st": 7, "ews": 6},
    },
    "BTECH-EE": {
        "2024-25": {"general": 60, "obc": 27, "sc": 15, "st": 7, "ews": 6},
    },
    "MTECH-AI": {
        "2024-25": {"general": 18, "obc": 9, "sc": 5, "st": 2},
    },
    "BTECH-ME": {
        "2024-25": {"general": 60, "obc": 27, "sc": 15, "st": 7, "ews": 6},
    },
    "BTECH-CE": {
        "2024-25": {"general": 45, "obc": 20, "sc": 12, "st": 5, "ews": 5},
    },
    "MTECH-SE": {
        "2024-25": {"general": 18},
    },
    "BTECH-IT": {
        "2024-25": {"general": 60, "obc": 27, "sc": 15, "st": 7, "ews": 6},
    },
    "BCA": {
        "2024-25": {"general": 60},
    },
    "MCA": {
        "2024-25": {"general": 30},
    },
    "DIP-CE": {
        "2024-25": {"general": 60},
    },
    "DIP-ME": {
        "2024-25": {"general": 60},
    },
    "DIP-EL": {
        "2024-25": {"general": 60},
    },
}

DEMO_USERS = [
    {
        "email": "superadmin@vidyaverify.dev",
        "full_name": "Super Administrator",
        "password": "SuperAdmin@123",
        "role": UserRole.SUPER_ADMIN,
        "institution_key": None,
    },
    {
        "email": "aicte.admin@vidyaverify.dev",
        "full_name": "AICTE Administrator",
        "password": "AicteAdmin@123",
        "role": UserRole.AICTE_ADMIN,
        "institution_key": None,
    },
    {
        "email": "college.admin@iit-demo.dev",
        "full_name": "IIT-Demo College Admin",
        "password": "CollegeAdmin@123",
        "role": UserRole.COLLEGE_ADMIN,
        "institution_key": "AICTE-DEMO-001",
    },
    {
        "email": "admission.staff@iit-demo.dev",
        "full_name": "IIT-Demo Admission Staff",
        "password": "AdmitStaff@123",
        "role": UserRole.ADMISSION_STAFF,
        "institution_key": "AICTE-DEMO-001",
    },
    {
        "email": "verifier@vidyaverify.dev",
        "full_name": "Authorized Verifier",
        "password": "Verifier@123",
        "role": UserRole.AUTHORIZED_VERIFIER,
        "institution_key": None,
    },
    {
        "email": "student@iit-demo.dev",
        "full_name": "Demo Student",
        "password": "Student@123",
        "role": UserRole.STUDENT,
        "institution_key": "AICTE-DEMO-001",
    },
]

SAMPLE_STUDENTS = [
    {
        "full_name": "Aarav Kumar",
        "enrolment_number": "2024CS001",
        "gender": "Male",
        "admission_category": "general",
        "programme_code": "BTECH-CS",
        "academic_year_label": "2024-25",
        "institution_key": "AICTE-DEMO-001",
        "apaar_id": "123456789001",
    },
    {
        "full_name": "Priya Sharma",
        "enrolment_number": "2024CS002",
        "gender": "Female",
        "admission_category": "obc",
        "programme_code": "BTECH-CS",
        "academic_year_label": "2024-25",
        "institution_key": "AICTE-DEMO-001",
        "apaar_id": "123456789002",
    },
    {
        "full_name": "Rahul Singh",
        "enrolment_number": "2024EE001",
        "gender": "Male",
        "admission_category": "sc",
        "programme_code": "BTECH-EE",
        "academic_year_label": "2024-25",
        "institution_key": "AICTE-DEMO-001",
        "apaar_id": "123456789003",
    },
    {
        "full_name": "Meera Nair",
        "enrolment_number": "2024ME001",
        "gender": "Female",
        "admission_category": "general",
        "programme_code": "BTECH-ME",
        "academic_year_label": "2024-25",
        "institution_key": "AICTE-DEMO-002",
        "apaar_id": "123456789004",
    },
    {
        "full_name": "Arjun Patel",
        "enrolment_number": "2024IT001",
        "gender": "Male",
        "admission_category": "general",
        "programme_code": "BTECH-IT",
        "academic_year_label": "2024-25",
        "institution_key": "AICTE-DEMO-003",
        "apaar_id": "123456789005",
    },
]


def seed():
    import app.models
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[SEED] Starting seed...")

        # ── Institutions ──────────────────────────────────────────────────
        inst_map: dict[str, Institution] = {}
        for inst_data in INSTITUTIONS:
            existing = db.query(Institution).filter_by(aicte_id=inst_data["aicte_id"]).first()
            if existing:
                inst_map[inst_data["aicte_id"]] = existing
                print(f"  ✓ Institution already exists: {inst_data['short_name']}")
                continue
            inst = Institution(**inst_data)
            db.add(inst)
            db.flush()
            inst_map[inst_data["aicte_id"]] = inst
            print(f"  + Institution created: {inst_data['short_name']}")

        # ── Programmes ────────────────────────────────────────────────────
        prog_map: dict[tuple, Programme] = {}  # (aicte_id, code) -> Programme
        for aicte_id, progs in PROGRAMMES_BY_INST.items():
            inst = inst_map[aicte_id]
            for prog_data in progs:
                existing = db.query(Programme).filter_by(
                    institution_id=inst.id, code=prog_data["code"]
                ).first()
                if existing:
                    prog_map[(aicte_id, prog_data["code"])] = existing
                    continue
                prog = Programme(institution_id=inst.id, **prog_data)
                db.add(prog)
                db.flush()
                prog_map[(aicte_id, prog_data["code"])] = prog
                print(f"    + Programme: {prog_data['code']} @ {aicte_id}")

        # ── Academic Years ────────────────────────────────────────────────
        ay_map: dict[tuple, AcademicYear] = {}  # (aicte_id, label) -> AcademicYear
        for aicte_id in [i["aicte_id"] for i in INSTITUTIONS]:
            inst = inst_map[aicte_id]
            for ay_data in ACADEMIC_YEARS:
                existing = db.query(AcademicYear).filter_by(
                    institution_id=inst.id, label=ay_data["label"]
                ).first()
                if existing:
                    ay_map[(aicte_id, ay_data["label"])] = existing
                    continue
                ay = AcademicYear(institution_id=inst.id, **ay_data)
                db.add(ay)
                db.flush()
                ay_map[(aicte_id, ay_data["label"])] = ay

        # ── Approved Intake ───────────────────────────────────────────────
        for aicte_id, progs in PROGRAMMES_BY_INST.items():
            for prog_data in progs:
                prog = prog_map.get((aicte_id, prog_data["code"]))
                if not prog:
                    continue
                prog_intake = INTAKE.get(prog_data["code"], {})
                for ay_label, categories in prog_intake.items():
                    ay = ay_map.get((aicte_id, ay_label))
                    if not ay:
                        continue
                    for category, seats in categories.items():
                        existing = db.query(ApprovedIntake).filter_by(
                            programme_id=prog.id,
                            academic_year_id=ay.id,
                            category=category,
                        ).first()
                        if existing:
                            continue
                        intake = ApprovedIntake(
                            programme_id=prog.id,
                            academic_year_id=ay.id,
                            category=category,
                            approved_seats=seats,
                        )
                        db.add(intake)

        db.flush()
        print("  ✓ Approved intake configured")

        # ── Users ─────────────────────────────────────────────────────────
        for user_data in DEMO_USERS:
            existing = db.query(User).filter_by(email=user_data["email"]).first()
            if existing:
                print(f"  ✓ User already exists: {user_data['email']}")
                continue
            inst_id = None
            if user_data["institution_key"]:
                inst_id = inst_map[user_data["institution_key"]].id
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                institution_id=inst_id,
            )
            db.add(user)
            print(f"  + User created: {user_data['email']} ({user_data['role'].value})")

        db.flush()

        # ── Sample Students ───────────────────────────────────────────────
        from app.services.validation_engine import hash_apaar, mask_apaar
        for st_data in SAMPLE_STUDENTS:
            inst = inst_map[st_data["institution_key"]]
            prog = prog_map.get((st_data["institution_key"], st_data["programme_code"]))
            ay = ay_map.get((st_data["institution_key"], st_data["academic_year_label"]))

            existing = db.query(Student).filter_by(
                institution_id=inst.id,
                enrolment_number=st_data["enrolment_number"],
            ).first()
            if existing:
                continue

            student = Student(
                full_name=st_data["full_name"],
                gender=st_data["gender"],
                institution_id=inst.id,
                programme_id=prog.id if prog else None,
                academic_year_id=ay.id if ay else None,
                enrolment_number=st_data["enrolment_number"],
                admission_category=st_data["admission_category"],
                apaar_id_hash=hash_apaar(st_data["apaar_id"]),
                apaar_id_masked=mask_apaar(st_data["apaar_id"]),
                admission_date=date(2024, 8, 1),
                enrolment_status="active",
                validation_status="open",
            )
            db.add(student)
            print(f"  + Student created: {st_data['full_name']}")

        db.commit()
        print("[OK] Seed complete!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
