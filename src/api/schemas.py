"""
Pydantic schemas for request validation and response serialization in Paryavaran.
Ensures strong typing and data integrity.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict


# --- Authentication Schemas ---

class UserRegister(BaseModel):
    """Schema for registering a new user."""
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_\-]+$")
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema for logging in."""
    username: str
    password: str


class Token(BaseModel):
    """Authentication token schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload schema."""
    username: Optional[str] = None
    user_id: Optional[int] = None


# --- Carbon Calculator Schemas ---

class CarbonCalculationInput(BaseModel):
    """Schema for inputting footprint parameters."""
    transport_distance: float = Field(default=0.0, ge=0.0, description="Distance in kilometers")
    vehicle_type: str = Field(default="petrol_car", description="Type of vehicle used")
    electricity_kwh: float = Field(default=0.0, ge=0.0, description="Electricity consumed in kWh")
    diet_type: str = Field(default="vegetarian", description="Primary dietary pattern")
    diet_days: int = Field(default=30, ge=0, le=31, description="Number of days in the period")
    water_liters: float = Field(default=0.0, ge=0.0, description="Water consumed in liters")
    waste_kg: float = Field(default=0.0, ge=0.0, description="Waste generated in kilograms")
    recycles_or_composts: bool = Field(default=False, description="Actively recycles or composts waste")

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle(cls, v: str) -> str:
        valid_vehicles = {"petrol_car", "diesel_car", "electric_car", "motorbike", "public_transit", "bicycle_or_walk"}
        if v not in valid_vehicles:
            raise ValueError(f"vehicle_type must be one of {valid_vehicles}")
        return v

    @field_validator("diet_type")
    @classmethod
    def validate_diet(cls, v: str) -> str:
        valid_diets = {"heavy_meat", "flexitarian", "vegetarian", "vegan"}
        if v not in valid_diets:
            raise ValueError(f"diet_type must be one of {valid_diets}")
        return v


class CarbonCalculationResponse(BaseModel):
    """Schema for serialized footprint results."""
    id: int
    logged_at: datetime
    transport_emissions: float
    electricity_emissions: float
    food_emissions: float
    water_emissions: float
    waste_emissions: float
    total_emissions: float
    transport_details: Dict[str, Any]
    electricity_details: Dict[str, Any]
    food_details: Dict[str, Any]
    water_details: Dict[str, Any]
    waste_details: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# --- Sustainable Action Tracker Schemas ---

class ActionLogInput(BaseModel):
    """Schema for logging a sustainable action."""
    action_type: str = Field(..., description="Action identifier")

    @field_validator("action_type")
    @classmethod
    def validate_action(cls, v: str) -> str:
        valid_actions = {
            "commute_bicycle", 
            "commute_public_transit", 
            "eat_vegan", 
            "eat_vegetarian", 
            "unplug_appliances", 
            "recycle_items", 
            "compost_organic"
        }
        if v not in valid_actions:
            raise ValueError(f"action_type must be one of {valid_actions}")
        return v


class ActionLogResponse(BaseModel):
    """Schema for serializing logged actions."""
    id: int
    action_type: str
    points_earned: int
    emissions_reduced: float
    logged_date: date

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Analytics Schemas ---

class RecommendationResponse(BaseModel):
    """Schema for personalized footprint advice."""
    category: str
    priority: str
    tip: str
    action_type: str


class TargetComparison(BaseModel):
    """Comparison of emissions against Climate targets."""
    target: float
    difference: float
    meets_target: bool
    percent_of_target: float


class CarbonHistoryItem(BaseModel):
    """Historical timeline footprint record."""
    date: str
    total_emissions: float
    transport_emissions: float
    electricity_emissions: float
    food_emissions: float
    water_emissions: float
    waste_emissions: float


class DashboardSummaryResponse(BaseModel):
    """Comprehensive payload for loading the main user page."""
    username: str
    green_points: int
    streak_count: int
    total_logs_count: int
    latest_log: Optional[CarbonCalculationResponse] = None
    target_comparison: Optional[TargetComparison] = None
    recommendations: List[RecommendationResponse] = []
    badges: List[str] = []
    recent_actions: List[ActionLogResponse] = []
    historical_data: List[CarbonHistoryItem] = []
