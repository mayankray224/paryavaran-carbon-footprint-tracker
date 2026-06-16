"""
API route definitions for the Paryavaran application.
Implements endpoints for authentication, footprint calculations, action logging, and dashboard analytics.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.models.database import get_db, User, CarbonLog, ActionLog
from src.repositories.base import UserRepository, CarbonLogRepository, ActionLogRepository, BadgeRepository
from src.services.carbon_calculator import CarbonCalculatorService
from src.services.gamification import GamificationService
from src.services.insights import InsightsService
from src.services.auth import AuthService
from src.utils.helpers import decode_access_token
from src.api.schemas import (
    UserRegister, UserLogin, Token, TokenData,
    CarbonCalculationInput, CarbonCalculationResponse,
    ActionLogInput, ActionLogResponse, DashboardSummaryResponse,
    RecommendationResponse, TargetComparison, CarbonHistoryItem
)

router = APIRouter(prefix="/api")
security_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to authenticate requests. Extracts JWT and retrieves the current user.
    Raises HTTP 401 if unauthorized.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# --- AUTHENTICATION ENDPOINTS ---

@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Registers a new user and returns an access token.
    """
    success, message, data = AuthService.register_user(db, user_data.username, user_data.password)
    if not success:
        if message == "Username is already taken":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    return data


@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Authenticates user and returns an access token.
    """
    success, message, data = AuthService.authenticate_user(db, credentials.username, credentials.password)
    if not success:
        if message == "Incorrect username or password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    return data


# --- CARBON CALCULATOR ENDPOINTS ---

@router.post("/calculator/calculate", response_model=Dict[str, Any])
def calculate_footprint(
    inputs: CarbonCalculationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculates carbon footprint based on user inputs, logs the results in the database,
    and updates user green points/badges.
    """
    try:
        # Calculate carbon values using helper service
        results = CarbonCalculatorService.calculate_total_footprint(inputs.model_dump())
        
        # Save log in database
        carbon_repo = CarbonLogRepository(db)
        log = carbon_repo.create(
            user_id=current_user.id,
            transport_emissions=results["transport_emissions"],
            electricity_emissions=results["electricity_emissions"],
            food_emissions=results["food_emissions"],
            water_emissions=results["water_emissions"],
            waste_emissions=results["waste_emissions"],
            transport_details={"distance_km": inputs.transport_distance, "vehicle_type": inputs.vehicle_type},
            electricity_details={"kwh": inputs.electricity_kwh},
            food_details={"diet_type": inputs.diet_type, "days": inputs.diet_days},
            water_details={"liters": inputs.water_liters},
            waste_details={"waste_kg": inputs.waste_kg, "recycles_or_composts": inputs.recycles_or_composts}
        )

        # Trigger points and badges reward logic
        points_earned, new_badges = GamificationService.log_calculation_reward(db, current_user.id)

        # Get personalized recommendations based on this calculation
        recommendations = InsightsService.generate_recommendations(log)

        return {
            "log": CarbonCalculationResponse.model_validate(log),
            "points_earned": points_earned,
            "new_badges_unlocked": new_badges,
            "recommendations": recommendations
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating your footprint"
        )


# --- ACTION TRACKER ENDPOINTS ---

@router.post("/tracker/actions", response_model=Dict[str, Any])
def log_action(
    action_input: ActionLogInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Logs a sustainable action completed by the user.
    Updates daily eco-streak, awards points and carbon reduction values, and unlocks badges.
    """
    try:
        points, reduction, streak, new_badges = GamificationService.log_sustainable_action(
            db=db,
            user_id=current_user.id,
            action_type=action_input.action_type
        )

        return {
            "message": "Action logged successfully",
            "points_earned": points,
            "emissions_reduced_kg": reduction,
            "current_streak": streak,
            "new_badges_unlocked": new_badges
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log sustainable action"
        )


@router.get("/tracker/actions", response_model=List[ActionLogResponse])
def get_recent_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ActionLog]:
    """
    Retrieves the user's historical log of sustainable actions.
    """
    action_repo = ActionLogRepository(db)
    return action_repo.get_recent_by_user(current_user.id, limit=50)


# --- DASHBOARD SUMMARY ENDPOINT ---

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieves all user summary data for loading the dashboard in one call.
    Includes current stats, latest log details, comparisons, active streak, badge list,
    logged actions list, and historical charts series data.
    """
    try:
        carbon_repo = CarbonLogRepository(db)
        action_repo = ActionLogRepository(db)
        badge_repo = BadgeRepository(db)

        # Retrieve user objects
        user_logs = carbon_repo.get_by_user(current_user.id, limit=20)
        recent_actions = action_repo.get_recent_by_user(current_user.id, limit=10)
        badges = [b.badge_name for b in badge_repo.get_by_user(current_user.id)]

        latest_log: Optional[CarbonLog] = user_logs[0] if user_logs else None
        
        target_comp = None
        recommendations = []
        if latest_log:
            summary_data = InsightsService.get_footprint_summary(latest_log)
            comp_data = summary_data["target_comparison"]
            target_comp = TargetComparison(
                target=comp_data["target"],
                difference=comp_data["difference"],
                meets_target=comp_data["meets_target"],
                percent_of_target=comp_data["percent_of_target"]
            )
            recommendations = [
                RecommendationResponse(
                    category=r["category"],
                    priority=r["priority"],
                    tip=r["tip"],
                    action_type=r["action_type"]
                ) for r in InsightsService.generate_recommendations(latest_log, summary=summary_data)
            ]

        # Prepare historical series for chart plotting (older logs first)
        historical_data = []
        for log in reversed(user_logs):
            log_date_str = log.logged_at.strftime("%b %d, %Y")
            historical_data.append(
                CarbonHistoryItem(
                    date=log_date_str,
                    total_emissions=round(log.total_emissions, 1),
                    transport_emissions=round(log.transport_emissions, 1),
                    electricity_emissions=round(log.electricity_emissions, 1),
                    food_emissions=round(log.food_emissions, 1),
                    water_emissions=round(log.water_emissions, 1),
                    waste_emissions=round(log.waste_emissions, 1)
                )
            )

        return {
            "username": current_user.username,
            "green_points": current_user.green_points,
            "streak_count": current_user.streak_count,
            "total_logs_count": len(user_logs),
            "latest_log": CarbonCalculationResponse.model_validate(latest_log) if latest_log else None,
            "target_comparison": target_comp,
            "recommendations": recommendations,
            "badges": badges,
            "recent_actions": [ActionLogResponse.model_validate(a) for a in recent_actions],
            "historical_data": historical_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard metrics"
        )
