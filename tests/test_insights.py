"""
Unit tests for the Insights and Recommendations Service.
"""
from datetime import datetime
from src.models.database import CarbonLog
from src.services.insights import InsightsService


def test_footprint_summary():
    log = CarbonLog(
        total_emissions=100.0,
        transport_emissions=50.0,
        electricity_emissions=20.0,
        food_emissions=15.0,
        water_emissions=5.0,
        waste_emissions=10.0,
        logged_at=datetime.utcnow()
    )

    summary = InsightsService.get_footprint_summary(log)
    assert summary["total_emissions"] == 100.0
    
    # Check category percentages
    assert summary["breakdown"]["transportation"]["percentage"] == 50.0
    assert summary["breakdown"]["electricity"]["percentage"] == 20.0
    assert summary["breakdown"]["food"]["percentage"] == 15.0
    assert summary["breakdown"]["water"]["percentage"] == 5.0
    assert summary["breakdown"]["waste"]["percentage"] == 10.0

    # Target comparison
    # Target is 166.67. User is 100.0. User meets target (100 <= 166.67)
    assert summary["target_comparison"]["meets_target"] is True
    assert summary["target_comparison"]["difference"] == round(100.0 - 166.67, 2)


def test_generate_recommendations_transport_heavy():
    log = CarbonLog(
        total_emissions=100.0,
        transport_emissions=60.0,  # Dominating category (60%)
        electricity_emissions=10.0,
        food_emissions=10.0,
        water_emissions=10.0,
        waste_emissions=10.0
    )

    recs = InsightsService.generate_recommendations(log)
    # The highest category should be Transportation with High priority
    assert any(r["category"] == "Transportation" and r["priority"] == "High" for r in recs)
    # Check that recommendation contains transport-related tip
    assert "commute_bicycle" in [r["action_type"] for r in recs]


def test_generate_recommendations_food_heavy():
    log = CarbonLog(
        total_emissions=80.0,
        transport_emissions=10.0,
        electricity_emissions=10.0,
        food_emissions=40.0,  # Dominating category (50%)
        water_emissions=10.0,
        waste_emissions=10.0
    )

    recs = InsightsService.generate_recommendations(log)
    assert any(r["category"] == "Food & Diet" and r["priority"] == "High" for r in recs)
    assert "eat_vegan" in [r["action_type"] for r in recs]
