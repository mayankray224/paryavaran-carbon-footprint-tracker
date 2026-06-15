"""
Repository layer for database operations in the Paryavaran application.
Implements the repository pattern to isolate data access queries.
"""
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from src.models.database import User, CarbonLog, ActionLog, Badge


class UserRepository:
    """
    Handles queries and updates for the User table.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create(self, username: str, password_hash: str) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            green_points=0,
            streak_count=0
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_stats(self, user_id: int, points_add: int, new_streak: Optional[int] = None, last_logged: Optional[date] = None) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.green_points += points_add
            if new_streak is not None:
                user.streak_count = new_streak
            if last_logged is not None:
                user.last_logged_date = last_logged
            self.db.commit()
            self.db.refresh(user)
        return user


class CarbonLogRepository:
    """
    Handles queries and creations for the CarbonLog table.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, 
               transport_emissions: float, electricity_emissions: float,
               food_emissions: float, water_emissions: float, waste_emissions: float,
               transport_details: dict, electricity_details: dict,
               food_details: dict, water_details: dict, waste_details: dict) -> CarbonLog:
        total = transport_emissions + electricity_emissions + food_emissions + water_emissions + waste_emissions
        log = CarbonLog(
            user_id=user_id,
            transport_emissions=transport_emissions,
            electricity_emissions=electricity_emissions,
            food_emissions=food_emissions,
            water_emissions=water_emissions,
            waste_emissions=waste_emissions,
            total_emissions=total,
            transport_details=transport_details,
            electricity_details=electricity_details,
            food_details=food_details,
            water_details=water_details,
            waste_details=waste_details
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_user(self, user_id: int, limit: int = 100) -> List[CarbonLog]:
        return self.db.query(CarbonLog)\
            .filter(CarbonLog.user_id == user_id)\
            .order_by(CarbonLog.logged_at.desc())\
            .limit(limit).all()


class ActionLogRepository:
    """
    Handles queries and creations for sustainable actions logged by the user.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, action_type: str, points_earned: int, emissions_reduced: float, logged_date: date) -> ActionLog:
        log = ActionLog(
            user_id=user_id,
            action_type=action_type,
            points_earned=points_earned,
            emissions_reduced=emissions_reduced,
            logged_date=logged_date
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_user_date(self, user_id: int, check_date: date) -> List[ActionLog]:
        return self.db.query(ActionLog)\
            .filter(ActionLog.user_id == user_id, ActionLog.logged_date == check_date).all()

    def get_recent_by_user(self, user_id: int, limit: int = 100) -> List[ActionLog]:
        return self.db.query(ActionLog)\
            .filter(ActionLog.user_id == user_id)\
            .order_by(ActionLog.logged_date.desc(), ActionLog.id.desc())\
            .limit(limit).all()


class BadgeRepository:
    """
    Handles queries and insertions of unlocked Badges.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, badge_name: str) -> Badge:
        badge = Badge(user_id=user_id, badge_name=badge_name)
        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)
        return badge

    def get_by_user(self, user_id: int) -> List[Badge]:
        return self.db.query(Badge).filter(Badge.user_id == user_id).all()
