"""Tests for authentication endpoints."""
import pytest
from tests.conftest import make_user, auth_headers, get_token
from app.core.enums import UserRole


class TestLogin:
    def test_login_success(self, client, db):
        make_user(db, "login_test@example.com", password="Test@1234", role=UserRole.COLLEGE_ADMIN)
        resp = client.post("/api/v1/auth/login", data={
            "username": "login_test@example.com", "password": "Test@1234"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login_test@example.com"

    def test_login_wrong_password(self, client, db):
        make_user(db, "wrong_pw@example.com", password="CorrectPass@1")
        resp = client.post("/api/v1/auth/login", data={
            "username": "wrong_pw@example.com", "password": "WrongPass@1"
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        resp = client.post("/api/v1/auth/login", data={
            "username": "nobody@example.com", "password": "anything"
        })
        assert resp.status_code == 401

    def test_get_me(self, client, db):
        make_user(db, "me_test@example.com", role=UserRole.AICTE_ADMIN)
        headers = auth_headers(client, "me_test@example.com")
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "me_test@example.com"
        assert resp.json()["role"] == "aicte_admin"

    def test_get_me_no_token(self, client, db):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_invalid_token(self, client, db):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code == 401

    def test_inactive_user_cannot_login(self, client, db):
        from app.models.user import User
        user = make_user(db, "inactive@example.com", role=UserRole.STUDENT)
        user.is_active = False
        db.flush()
        resp = client.post("/api/v1/auth/login", data={
            "username": "inactive@example.com", "password": "Test@1234"
        })
        assert resp.status_code in (400, 401)
