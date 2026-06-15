"""
Gamification service for the Paryavaran application.
Manages user green points, daily action streaks, and badges criteria checks.
"""
from typing import List, Tuple, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.models.database import User, CarbonLog, ActionLog, Badge
from src.repositories.base import UserRepository, CarbonLogRepository, ActionLogRepository, BadgeRepository


class GamificationService:
    """
    Business logic for reward points, streak tracking, and badges updates.
    """

    # Badge definitions and user-friendly labels
    BADGE_INFO = {
        "eco_novice": "Eco Novice (Completed first calculation)",
        "carbon_tracker": "Carbon Analyst (Completed 5 calculations)",
        "commute_champion": "Commute Champion (Logged 5 sustainable travel actions)",
        "green_chef": "Green Chef (Logged 7 plant-based food actions)",
        "waste_warrior": "Waste Warrior (Logged 3 recycling/composting actions)",
        "earth_guardian": "Earth Guardian (Earned 1000 Green Points)"
    }

    # Points values
    POINTS_CALCULATION: int = 50       # Points for filling the calculator
    ACTION_POINTS = {
        "commute_bicycle": 30,
        "commute_public_transit": 20,
        "eat_vegan": 25,
        "eat_vegetarian": 15,
        "unplug_appliances": 15,
        "recycle_items": 10,
        "compost_organic": 20
    }

    # Estimated carbon reduction values (in kg CO2 saved per action logged)
    ACTION_REDUCTIONS = {
        "commute_bicycle": 3.0,          # Average car commute replacement
        "commute_public_transit": 2.0,
        "eat_vegan": 2.5,                # Daily savings vs high meat diet
        "eat_vegetarian": 1.5,
        "unplug_appliances": 0.5,
        "recycle_items": 0.4,
        "compost_organic": 0.8
    }

    @classmethod
    def calculate_streak(cls, last_logged: Optional[date], current_date: date, current_streak: int) -> int:
        """
        Calculates user activity streak.
        - If last logged was yesterday, streak increments by 1.
        - If last logged was today, streak remains the same.
        - If last logged was before yesterday, streak resets to 1.
        """
        if last_logged is None:
            return 1
        
        diff = (current_date - last_logged).days
        if diff == 0:
            return current_streak if current_streak > 0 else 1
        elif diff == 1:
            return current_streak + 1
        else:
            return 1

    @classmethod
    def evaluate_new_badges(cls, db: Session, user: User) -> List[str]:
        """
        Analyzes user history and awards any newly earned badges.
        Returns a list of newly unlocked badge names.
        """
        user_repo = UserRepository(db)
        carbon_repo = CarbonLogRepository(db)
        action_repo = ActionLogRepository(db)
        badge_repo = BadgeRepository(db)

        # Get existing badge names
        existing_badges = {b.badge_name for b in badge_repo.get_by_user(user.id)}
        newly_unlocked: List[str] = []

        # 1. Eco Novice: completed at least 1 calculation
        if "eco_novice" not in existing_badges:
            total_calcs = len(carbon_repo.get_by_user(user.id, limit=2))
            if total_calcs >= 1:
                newly_unlocked.append("eco_novice")

        # 2. Carbon Tracker: completed 5 calculations
        if "carbon_tracker" not in existing_badges:
            total_calcs = len(carbon_repo.get_by_user(user.id, limit=10))
            if total_calcs >= 5:
                newly_unlocked.append("carbon_tracker")

        # Get all logged actions to evaluate action-specific badges
        all_actions = action_repo.get_recent_by_user(user.id, limit=100)

        # 3. Commute Champion: 5 sustainable travel actions
        if "commute_champion" not in existing_badges:
            travel_count = sum(1 for a in all_actions if a.action_type in ("commute_bicycle", "commute_public_transit"))
            if travel_count >= 5:
                newly_unlocked.append("commute_champion")

        # 4. Green Chef: 7 plant-based food actions
        if "green_chef" not in existing_badges:
            food_count = sum(1 for a in all_actions if a.action_type in ("eat_vegan", "eat_vegetarian"))
            if food_count >= 7:
                newly_unlocked.append("green_chef")

        # 5. Waste Warrior: 3 recycling/composting actions
        if "waste_warrior" not in existing_badges:
            waste_count = sum(1 for a in all_actions if a.action_type in ("recycle_items", "compost_organic"))
            if waste_count >= 3:
                newly_unlocked.append("waste_warrior")

        # 6. Earth Guardian: 1000+ points
        if "earth_guardian" not in existing_badges:
            if user.green_points >= 1000:
                newly_unlocked.append("earth_guardian")

        # Save newly unlocked badges to the DB
        for badge_name in newly_unlocked:
            badge_repo.create(user.id, badge_name)

        return newly_unlocked

    @classmethod
    def log_calculation_reward(cls, db: Session, user_id: int) -> Tuple[int, List[str]]:
        """
        Rewards user for completing a footprint calculation.
        Adds points and updates badges.
        """
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user:
            return 0, []

        points_earned = cls.POINTS_CALCULATION
        
        # Update user's green points
        user_repo.update_stats(user_id, points_add=points_earned)
        
        # Check badges
        new_badges = cls.evaluate_new_badges(db, user)
        return points_earned, new_badges

    @classmethod
    def log_sustainable_action(cls, db: Session, user_id: int, action_type: str) -> Tuple[int, float, int, List[str]]:
        """
        Records a user's sustainable action.
        - Calculates points earned and emissions saved.
        - Updates user streak and total points.
        - Checks for badge unlocks.
        Returns: (points_earned, emissions_reduced, new_streak, new_badges)
        """
        user_repo = UserRepository(db)
        action_repo = ActionLogRepository(db)
        
        user = user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if action_type not in cls.ACTION_POINTS:
            raise ValueError(f"Unknown action type: {action_type}")

        points = cls.ACTION_POINTS[action_type]
        reduction = cls.ACTION_REDUCTIONS[action_type]
        today_date = date.today()

        # Update streak
        new_streak = cls.calculate_streak(user.last_logged_date, today_date, user.streak_count)
        
        # Apply streak multiplier: 1.2x points for streaks of 3 days or more
        streak_multiplier = 1.2 if new_streak >= 3 else 1.0
        final_points = int(points * streak_multiplier)

        # Log action to DB
        action_repo.create(
            user_id=user_id,
            action_type=action_type,
            points_earned=final_points,
            emissions_reduced=reduction,
            logged_date=today_date
        )

        # Update user stats
        user_repo.update_stats(
            user_id=user_id,
            points_add=final_points,
            new_streak=new_streak,
            last_logged=today_date
        )

        # Re-fetch user to get updated points for badge evaluation
        user = user_repo.get_by_id(user_id)
        new_badges = cls.evaluate_new_badges(db, user)

        return final_points, reduction, new_streak, new_badges
