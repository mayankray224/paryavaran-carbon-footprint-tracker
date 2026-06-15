"""
Unit tests for the AuthService.
"""
import pytest
from sqlalchemy.orm import Session
from src.services.auth import AuthService
from src.models.database import User


def test_auth_service_register_success(db_session: Session):
    success, message, data = AuthService.register_user(db_session, "authuser", "password123")
    assert success is True
    assert message == "Registration successful"
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify user actually created in DB
    user = db_session.query(User).filter(User.username == "authuser").first()
    assert user is not None
    assert user.username == "authuser"


def test_auth_service_register_duplicate(db_session: Session):
    # Register once
    success1, _, _ = AuthService.register_user(db_session, "authdupe", "password123")
    assert success1 is True

    # Register twice
    success2, message2, data2 = AuthService.register_user(db_session, "authdupe", "password123")
    assert success2 is False
    assert message2 == "Username is already taken"
    assert data2 == {}


def test_auth_service_authenticate_success(db_session: Session):
    # Register user first
    AuthService.register_user(db_session, "loginuser", "mypassword")

    # Authenticate
    success, message, data = AuthService.authenticate_user(db_session, "loginuser", "mypassword")
    assert success is True
    assert message == "Authentication successful"
    assert "access_token" in data


def test_auth_service_authenticate_wrong_password(db_session: Session):
    # Register user first
    AuthService.register_user(db_session, "loginuser", "mypassword")

    # Authenticate with wrong password
    success, message, data = AuthService.authenticate_user(db_session, "loginuser", "wrongpassword")
    assert success is False
    assert message == "Incorrect username or password"
    assert data == {}


def test_auth_service_authenticate_non_existent(db_session: Session):
    # Authenticate non-existent user
    success, message, data = AuthService.authenticate_user(db_session, "ghost", "password")
    assert success is False
    assert message == "Incorrect username or password"
    assert data == {}
