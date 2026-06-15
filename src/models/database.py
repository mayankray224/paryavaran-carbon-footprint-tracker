"""
Database models and connection setup for the Paryavaran application.
Uses SQLAlchemy to define schemas for users, carbon calculations, actions, and badges.
"""
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from src.config.settings import settings

# Create database engine
# SQLite needs connect_args={"check_same_thread": False} for FastAPI async setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """
    User model representing registered individuals.
    Tracks their details, gamification metrics (points, streaks), and relationships.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    green_points = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    last_logged_date = Column(Date, nullable=True)

    # Relationships
    carbon_logs = relationship("CarbonLog", back_populates="user", cascade="all, delete-orphan")
    action_logs = relationship("ActionLog", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("Badge", back_populates="user", cascade="all, delete-orphan")


class CarbonLog(Base):
    """
    Model representing calculated carbon footprints over transport, energy, food, water, and waste.
    """
    __tablename__ = "carbon_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Emissions (in kg CO2)
    transport_emissions = Column(Float, default=0.0)
    electricity_emissions = Column(Float, default=0.0)
    food_emissions = Column(Float, default=0.0)
    water_emissions = Column(Float, default=0.0)
    waste_emissions = Column(Float, default=0.0)
    total_emissions = Column(Float, default=0.0)

    # Structured inputs for audit/tracking purposes
    transport_details = Column(JSON, nullable=True)
    electricity_details = Column(JSON, nullable=True)
    food_details = Column(JSON, nullable=True)
    water_details = Column(JSON, nullable=True)
    waste_details = Column(JSON, nullable=True)

    # Relationship
    user = relationship("User", back_populates="carbon_logs")


class ActionLog(Base):
    """
    Model to track sustainable actions completed by users (e.g. public transport, vegetarian days).
    """
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # e.g., 'commute_bicycle', 'eat_vegan'
    points_earned = Column(Integer, default=0)
    emissions_reduced = Column(Float, default=0.0)  # in kg CO2 saved
    logged_date = Column(Date, default=datetime.date.today)

    # Relationship
    user = relationship("User", back_populates="action_logs")


class Badge(Base):
    """
    Badges unlocked by users as they achieve sustainability milestones.
    """
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_name = Column(String, nullable=False)  # e.g., 'eco_novice', 'waste_warrior'
    awarded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="badges")


def init_db():
    """
    Initialize and create all database tables.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency to get a local database session.
    Ensures the session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
