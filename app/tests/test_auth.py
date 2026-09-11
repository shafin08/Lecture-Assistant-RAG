# ============================================================
# tests/test_auth.py
# Registration, login, token protection.
# Matched to the real API: register takes email + username +
# password; login is JSON with email + password; invalid
# credentials return 400 (per your endpoints).
# Fast — no API cost.
# ============================================================

import uuid
from tests.conftest import TEST_PASSWORD


def _email():
    return f"test_{uuid.uuid4().hex[:10]}@example.com"


def _register(client, email, password=TEST_PASSWORD):
    username = email.split("@")[0]
    return client.post("/auth/register",
                       json={"email": email, "username": username,
                             "password": password})


def test_register_success(client):
    r = _register(client, _email())
    assert r.status_code == 200


def test_register_duplicate_email(client):
    email = _email()
    assert _register(client, email).status_code == 200
    # Same email again -> your endpoint returns 400 "Email already in use"
    assert _register(client, email).status_code == 400


def test_login_success(client):
    email = _email()
    _register(client, email)
    r = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    email = _email()
    _register(client, email)
    r = client.post("/auth/login",
                    json={"email": email, "password": "Wrong!Password9x"})
    # Your endpoint returns 400 for invalid credentials
    assert r.status_code == 400


def test_login_unknown_user(client):
    r = client.post("/auth/login",
                    json={"email": "nobody@example.com", "password": TEST_PASSWORD})
    assert r.status_code == 400


def test_protected_requires_token(client):
    # No Authorization header on a protected route
    r = client.get("/conversation")
    # 401 if the auth dependency runs first; 403 on some setups
    assert r.status_code in (401, 403)


def test_protected_rejects_bad_token(client):
    r = client.get("/conversation",
                   headers={"Authorization": "Bearer garbage"})
    assert r.status_code in (401, 403)


def test_protected_accepts_valid_token(user, client):
    assert client.get("/conversation", headers=user["headers"]).status_code == 200
