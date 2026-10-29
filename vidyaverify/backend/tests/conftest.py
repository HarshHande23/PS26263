"""
Pytest configuration and shared fixtures for VidyaVerify backend tests.
Uses an in-memory SQLite database for fast, isolated tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.core.security import get_password_hash
from app.core.enums import UserRole
from app.models.user import User
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.approved_intake import ApprovedIntake

# Use SQLite for tests (in-memory)
TEST_DATABASE_URL = "sqlite:///./test_vidyaverify.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Seed helpers ─────────────────────────────────────────────────────────────

def make_institution(db, aicte_id="TEST-001", name="Test University"):
    inst = Institution(
        name=name,
        short_name="TU",
        aicte_id=aicte_id,
        institution_type="technical_institute",
        state="Maharashtra",
        is_active=True,
    )
    db.add(inst)
    db.flush()
    return inst


def make_programme(db, institution_id, code="BTECH-CS", name="B.Tech CS"):
    prog = Programme(
        institution_id=institution_id,
        name=name,
        code=code,
        level="undergraduate",
        duration_years=4,
        is_active=True,
    )
    db.add(prog)
    db.flush()
    return prog


def make_academic_year(db, institution_id, label="2024-25"):
    ay = AcademicYear(
        institution_id=institution_id,
        label=label,
        start_year=2024,
        end_year=2025,
        is_current=True,
    )
    db.add(ay)
    db.flush()
    return ay


def make_intake(db, programme_id, academic_year_id, category="general", seats=60):
    intake = ApprovedIntake(
        programme_id=programme_id,
        academic_year_id=academic_year_id,
        category=category,
        approved_seats=seats,
    )
    db.add(intake)
    db.flush()
    return intake


def make_user(db, email, password="Test@1234", role=UserRole.COLLEGE_ADMIN, institution_id=None):
    user = User(
        email=email,
        full_name=f"Test User ({role.value})",
        hashed_password=get_password_hash(password),
        role=role,
        institution_id=institution_id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_token(client, email, password="Test@1234"):
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_headers(client, email, password="Test@1234"):
    token = get_token(client, email, password)
    return {"Authorization": f"Bearer {token}"}
