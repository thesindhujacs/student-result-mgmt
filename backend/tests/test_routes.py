import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret"
    with app.test_client() as client:
        yield client

# ── Auth Tests ──────────────────────────────────────────

def test_login_missing_credentials(client):
    res = client.post("/api/auth/login", json={})
    assert res.status_code in [400, 401]

def test_login_invalid_credentials(client):
    res = client.post("/api/auth/login", json={"username": "nobody", "password": "wrong"})
    assert res.status_code == 401

def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200

# ── Student Tests ────────────────────────────────────────

def test_get_students_unauthorized(client):
    res = client.get("/api/students/")
    assert res.status_code == 403

def test_get_student_not_found(client):
    res = client.get("/api/students/1BG99CS999")
    assert res.status_code == 404

# ── Result Tests ─────────────────────────────────────────

def test_get_results_empty(client):
    res = client.get("/api/results/1BG99CS999")
    assert res.status_code == 200
    assert res.get_json() == []

def test_add_result_unauthorized(client):
    res = client.post("/api/results/", json={
        "usn": "1BG23CS133",
        "subject_code": "23CSE1663",
        "marks_obtained": 85
    })
    assert res.status_code == 403

# ── Grade Calculation Tests ──────────────────────────────

def test_grade_calculation():
    from routes.results import calculate_grade
    assert calculate_grade(95) == "O"
    assert calculate_grade(82) == "A+"
    assert calculate_grade(73) == "A"
    assert calculate_grade(63) == "B+"
    assert calculate_grade(53) == "B"
    assert calculate_grade(43) == "C"
    assert calculate_grade(30) == "F"
