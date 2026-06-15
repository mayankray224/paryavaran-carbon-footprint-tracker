# Paryavaran API Documentation

This document describes the REST API endpoints provided by the Paryavaran Carbon Footprint Tracker backend. All endpoints are prefixed with `/api`.

## Authentication Endpoints

### 1. User Registration
* **Endpoint:** `POST /api/auth/register`
* **Request Body:**
  ```json
  {
    "username": "eco_warrior",
    "password": "securepassword123"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer"
  }
  ```

### 2. User Login
* **Endpoint:** `POST /api/auth/login`
* **Request Body:**
  ```json
  {
    "username": "eco_warrior",
    "password": "securepassword123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer"
  }
  ```

---

## Carbon Calculator Endpoints

### 3. Calculate Footprint
* **Endpoint:** `POST /api/calculator/calculate`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Request Body:**
  ```json
  {
    "transport_distance": 120.5,
    "vehicle_type": "petrol_car",
    "electricity_kwh": 350.0,
    "diet_type": "vegetarian",
    "diet_days": 30,
    "water_liters": 4500.0,
    "waste_kg": 15.0,
    "recycles_or_composts": true
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "log": {
      "id": 1,
      "logged_at": "2026-06-15T23:32:47.123456",
      "transport_emissions": 24.1,
      "electricity_emissions": 287.0,
      "food_emissions": 75.0,
      "water_emissions": 1.35,
      "waste_emissions": 3.75,
      "total_emissions": 391.2,
      "transport_details": {"distance_km": 120.5, "vehicle_type": "petrol_car"},
      "electricity_details": {"kwh": 350.0},
      "food_details": {"diet_type": "vegetarian", "days": 30},
      "water_details": {"liters": 4500.0},
      "waste_details": {"waste_kg": 15.0, "recycles_or_composts": true}
    },
    "points_earned": 50,
    "new_badges_unlocked": ["eco_novice"],
    "recommendations": [
      {
        "category": "Electricity",
        "priority": "High",
        "tip": "Electricity usage dominates your footprint. Try unplugging standby devices, upgrading to LED lightbulbs, or looking into local community solar options.",
        "action_type": "unplug_appliances"
      }
    ]
  }
  ```

---

## Sustainable Action Tracker Endpoints

### 4. Log Action
* **Endpoint:** `POST /api/tracker/actions`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Request Body:**
  ```json
  {
    "action_type": "commute_bicycle"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "message": "Action logged successfully",
    "points_earned": 30,
    "emissions_reduced_kg": 3.0,
    "current_streak": 1,
    "new_badges_unlocked": []
  }
  ```

### 5. Get Recent Actions
* **Endpoint:** `GET /api/tracker/actions`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "action_type": "commute_bicycle",
      "points_earned": 30,
      "emissions_reduced": 3.0,
      "logged_date": "2026-06-15"
    }
  ]
  ```

---

## Dashboard Endpoints

### 6. Get Dashboard Summary
* **Endpoint:** `GET /api/dashboard/summary`
* **Headers:** `Authorization: Bearer <JWT_TOKEN>`
* **Success Response (200 OK):**
  ```json
  {
    "username": "eco_warrior",
    "green_points": 80,
    "streak_count": 1,
    "total_logs_count": 1,
    "latest_log": { ... },
    "target_comparison": {
      "target": 166.67,
      "difference": 224.53,
      "meets_target": false,
      "percent_of_target": 234.7
    },
    "recommendations": [ ... ],
    "badges": ["eco_novice"],
    "recent_actions": [ ... ],
    "historical_data": [
      {
        "date": "Jun 15, 2026",
        "total_emissions": 391.2,
        "transport_emissions": 24.1,
        "electricity_emissions": 287.0,
        "food_emissions": 75.0,
        "water_emissions": 1.35,
        "waste_emissions": 3.75
      }
    ]
  }
  ```
