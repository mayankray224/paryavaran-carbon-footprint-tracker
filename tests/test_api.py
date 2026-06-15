"""
Integration tests for the Paryavaran FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.models.database import User


# --- AUTH ENDPOINTS TESTS ---

def test_register_user_success(client: TestClient):
    payload = {
        "username": "newuser",
        "password": "strongpassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_duplicate_username(client: TestClient):
    payload = {
        "username": "dupe",
        "password": "password123"
    }
    # Register first time
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Register second time
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Username is already taken"


def test_register_invalid_inputs(client: TestClient):
    # Username too short
    payload = {
        "username": "ab",
        "password": "password123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422

    # Password too short
    payload = {
        "username": "validname",
        "password": "123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient):
    user_payload = {
        "username": "loginuser",
        "password": "password123"
    }
    # Register
    client.post("/api/auth/register", json=user_payload)

    # Login
    response = client.post("/api/auth/login", json=user_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client: TestClient):
    payload = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


# --- CALCULATOR ENDPOINT TESTS ---

def test_calculate_footprint_unauthorized(client: TestClient):
    payload = {
        "transport_distance": 100,
        "vehicle_type": "petrol_car",
        "electricity_kwh": 50,
        "diet_type": "vegan",
        "diet_days": 30,
        "water_liters": 1000,
        "waste_kg": 10,
        "recycles_or_composts": True
      }
    response = client.post("/api/calculator/calculate", json=payload)
    assert response.status_code == 403  # Bearer authentication header missing


def test_calculate_footprint_success(client: TestClient, auth_headers: dict):
    payload = {
        "transport_distance": 100.0,
        "vehicle_type": "petrol_car",
        "electricity_kwh": 50.0,
        "diet_type": "vegan",
        "diet_days": 30,
        "water_liters": 1000.0,
        "waste_kg": 10.0,
        "recycles_or_composts": True
    }
    response = client.post("/api/calculator/calculate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "log" in data
    assert data["points_earned"] == 50
    assert "new_badges_unlocked" in data
    assert len(data["recommendations"]) > 0

    # Verify calculations:
    # transport: 100 * 0.20 = 20.0
    # electricity: 50 * 0.82 = 41.0
    # food: 30 * 1.5 = 45.0
    # water: 1000 * 0.0003 = 0.3
    # waste: 10 * 0.25 = 2.5
    # total: 20 + 41 + 45 + 0.3 + 2.5 = 108.8
    assert data["log"]["total_emissions"] == 108.8


def test_calculate_footprint_validation_error(client: TestClient, auth_headers: dict):
    payload = {
        "transport_distance": -10,  # Negative values invalid
        "vehicle_type": "petrol_car"
    }
    response = client.post("/api/calculator/calculate", json=payload, headers=auth_headers)
    assert response.status_code == 422


# --- ACTION TRACKER ENDPOINT TESTS ---

def test_log_action_success(client: TestClient, auth_headers: dict):
    payload = {
        "action_type": "commute_bicycle"
    }
    response = client.post("/api/tracker/actions", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Action logged successfully"
    assert data["points_earned"] == 30
    assert data["emissions_reduced_kg"] == 3.0
    assert data["current_streak"] == 1


def test_get_recent_actions(client: TestClient, auth_headers: dict):
    # Log two actions
    client.post("/api/tracker/actions", json={"action_type": "commute_bicycle"}, headers=auth_headers)
    client.post("/api/tracker/actions", json={"action_type": "unplug_appliances"}, headers=auth_headers)

    response = client.get("/api/tracker/actions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert data[0]["action_type"] in ("commute_bicycle", "unplug_appliances")


# --- DASHBOARD SUMMARY ENDPOINT TESTS ---

def test_dashboard_summary_empty(client: TestClient, auth_headers: dict):
    response = client.get("/api/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["green_points"] == 0
    assert data["streak_count"] == 0
    assert data["latest_log"] is None
    assert len(data["badges"]) == 0
    assert len(data["recent_actions"]) == 0
    assert len(data["historical_data"]) == 0


def test_dashboard_summary_populated(client: TestClient, auth_headers: dict):
    # Perform a footprint calculation first
    calc_payload = {
        "transport_distance": 100.0,
        "vehicle_type": "petrol_car",
        "electricity_kwh": 50.0,
        "diet_type": "vegan",
        "diet_days": 30,
        "water_liters": 1000.0,
        "waste_kg": 10.0,
        "recycles_or_composts": True
    }
    client.post("/api/calculator/calculate", json=calc_payload, headers=auth_headers)
    
    # Log an action
    client.post("/api/tracker/actions", json={"action_type": "commute_bicycle"}, headers=auth_headers)

    # Fetch dashboard summary
    response = client.get("/api/dashboard/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    # Verify values aggregated
    # calculation points (50) + action points (30) = 80 GP
    assert data["green_points"] == 80
    assert data["streak_count"] == 1
    assert data["total_logs_count"] == 1
    assert data["latest_log"]["total_emissions"] == 108.8
    assert len(data["badges"]) > 0  # eco_novice badge should be unlocked
    assert len(data["recent_actions"]) == 1
    assert len(data["historical_data"]) == 1
    assert len(data["recommendations"]) > 0
