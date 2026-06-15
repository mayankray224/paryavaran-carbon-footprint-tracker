"""
Unit tests for the Gamification Service.
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.models.database import User, CarbonLog, ActionLog, Badge
from src.repositories.base import UserRepository, CarbonLogRepository, ActionLogRepository, BadgeRepository
from src.services.gamification import GamificationService


def test_streak_calculation():
    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    # First log
    assert GamificationService.calculate_streak(None, today, 0) == 1
    # Logged again today
    assert GamificationService.calculate_streak(today, today, 3) == 3
    # Logged consecutive day
    assert GamificationService.calculate_streak(yesterday, today, 2) == 3
    # Broken streak
    assert GamificationService.calculate_streak(two_days_ago, today, 5) == 1


def test_log_calculation_reward(db_session: Session):
    user_repo = UserRepository(db_session)
    user = user_repo.create("gamer", "password123")

    # Initial points should be 0
    assert user.green_points == 0

    # Add calculation reward
    points, badges = GamificationService.log_calculation_reward(db_session, user.id)
    assert points == 50
    # User gets eco_novice badge on first calculation because a CarbonLog exists
    # Wait, in evaluate_new_badges, it checks if a CarbonLog exists in the DB.
    # Since we haven't created a CarbonLog, they don't get the badge yet. Let's create one.
    carbon_repo = CarbonLogRepository(db_session)
    carbon_repo.create(
        user_id=user.id,
        transport_emissions=5.0, electricity_emissions=5.0, food_emissions=5.0, water_emissions=5.0, waste_emissions=5.0,
        transport_details={}, electricity_details={}, food_details={}, water_details={}, waste_details={}
    )

    # Re-evaluate badges
    user = user_repo.get_by_id(user.id)
    new_badges = GamificationService.evaluate_new_badges(db_session, user)
    assert "eco_novice" in new_badges


def test_log_sustainable_action(db_session: Session):
    user_repo = UserRepository(db_session)
    user = user_repo.create("eco_warrior", "password123")

    # Log bicycle commute
    points, reduction, streak, badges = GamificationService.log_sustainable_action(
        db_session, user.id, "commute_bicycle"
    )
    assert points == 30  # Base point value
    assert reduction == 3.0  # kg CO2
    assert streak == 1

    # Verify user stats updated
    user = user_repo.get_by_id(user.id)
    assert user.green_points == 30
    assert user.streak_count == 1
    assert user.last_logged_date == date.today()


def test_streak_multiplier_active(db_session: Session):
    user_repo = UserRepository(db_session)
    # Setup user with yesterday last logged and streak count = 2
    user = user_repo.create("streaker", "password123")
    user.streak_count = 2
    user.last_logged_date = date.today() - timedelta(days=1)
    db_session.commit()

    # Log action today - streak becomes 3, triggering 1.2x points
    # Bicycle commute base is 30 points. 30 * 1.2 = 36 points
    points, reduction, streak, badges = GamificationService.log_sustainable_action(
        db_session, user.id, "commute_bicycle"
    )
    assert streak == 3
    assert points == 36


def test_invalid_action_type(db_session: Session):
    user_repo = UserRepository(db_session)
    user = user_repo.create("novice", "password123")

    with pytest.raises(ValueError, match="Unknown action type"):
        GamificationService.log_sustainable_action(db_session, user.id, "invalid_action")
