"""
Unit tests for the Carbon Footprint Calculator Service.
"""
import pytest
from src.services.carbon_calculator import CarbonCalculatorService


def test_transport_emissions():
    # Petrol: 0.20 per km
    assert CarbonCalculatorService.calculate_transport(100, "petrol_car") == 20.0
    # Diesel: 0.17 per km
    assert CarbonCalculatorService.calculate_transport(100, "diesel_car") == 17.0
    # EV: 0.05 per km
    assert CarbonCalculatorService.calculate_transport(100, "electric_car") == 5.0
    # Bike/Walk: 0.0 per km
    assert CarbonCalculatorService.calculate_transport(100, "bicycle_or_walk") == 0.0
    
    # Negative distance error
    with pytest.raises(ValueError, match="Distance cannot be negative"):
        CarbonCalculatorService.calculate_transport(-10, "petrol_car")


def test_electricity_emissions():
    # 100 kWh * 0.82
    assert CarbonCalculatorService.calculate_electricity(100) == 82.0
    assert CarbonCalculatorService.calculate_electricity(0) == 0.0

    with pytest.raises(ValueError, match="Electricity usage cannot be negative"):
        CarbonCalculatorService.calculate_electricity(-1)


def test_food_emissions():
    # Vegan: 1.50 per day
    assert CarbonCalculatorService.calculate_food("vegan", 10) == 15.0
    # Vegetarian: 2.50 per day
    assert CarbonCalculatorService.calculate_food("vegetarian", 10) == 25.0
    # Heavy meat: 7.20 per day
    assert CarbonCalculatorService.calculate_food("heavy_meat", 10) == 72.0

    with pytest.raises(ValueError, match="Days cannot be negative"):
        CarbonCalculatorService.calculate_food("vegetarian", -1)


def test_water_emissions():
    # 1000 Liters * 0.0003
    assert CarbonCalculatorService.calculate_water(1000) == 0.3
    assert CarbonCalculatorService.calculate_water(0) == 0.0

    with pytest.raises(ValueError, match="Water usage cannot be negative"):
        CarbonCalculatorService.calculate_water(-100)


def test_waste_emissions():
    # 10 kg waste, no recycle: 10 * 0.50 = 5.0
    assert CarbonCalculatorService.calculate_waste(10, False) == 5.0
    # 10 kg waste, recycling: 10 * 0.25 = 2.5
    assert CarbonCalculatorService.calculate_waste(10, True) == 2.5

    with pytest.raises(ValueError, match="Waste quantity cannot be negative"):
        CarbonCalculatorService.calculate_waste(-5, False)


def test_total_footprint():
    inputs = {
        "transport_distance": 50.0,
        "vehicle_type": "petrol_car",    # 50 * 0.20 = 10.0
        "electricity_kwh": 100.0,        # 100 * 0.82 = 82.0
        "diet_type": "vegan",            # 30 * 1.50 = 45.0
        "diet_days": 30,
        "water_liters": 2000.0,          # 2000 * 0.0003 = 0.6
        "waste_kg": 20.0,                # 20 * 0.50 = 10.0
        "recycles_or_composts": False    # total: 10 + 82 + 45 + 0.6 + 10 = 147.6
    }
    
    # We pass the dictionary to evaluate
    result = CarbonCalculatorService.calculate_total_footprint(inputs)
    assert result["transport_emissions"] == 10.0
    assert result["electricity_emissions"] == 82.0
    assert result["food_emissions"] == 45.0
    assert result["water_emissions"] == 0.6
    assert result["waste_emissions"] == 10.0
    assert result["total_emissions"] == 147.6


def test_total_footprint_invalid():
    with pytest.raises(ValueError):
        CarbonCalculatorService.calculate_total_footprint({"transport_distance": "invalid_number"})
