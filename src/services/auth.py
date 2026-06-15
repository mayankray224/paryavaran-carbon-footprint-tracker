"""
Authentication service for the Paryavaran application.
Manages user registration, login verification, and token issuing.
"""
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session
from src.repositories.base import UserRepository
from src.utils.helpers import hash_password, verify_password, create_access_token


class AuthService:
    """
    Business logic for user onboarding and session authentication.
    """

    @classmethod
    def register_user(cls, db: Session, username: str, password_plain: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Registers a new user in the database and returns access tokens.
        Returns: (success_bool, message_str, token_data_dict)
        """
        user_repo = UserRepository(db)
        existing_user = user_repo.get_by_username(username)
        if existing_user:
            return False, "Username is already taken", {}

        try:
            hashed = hash_password(password_plain)
            user = user_repo.create(username, hashed)
            access_token = create_access_token(data={"sub": user.username, "id": user.id})
            return True, "Registration successful", {"access_token": access_token, "token_type": "bearer"}
        except Exception:
            return False, "Failed to register user due to an database/system error", {}

    @classmethod
    def authenticate_user(cls, db: Session, username: str, password_plain: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Authenticates an existing user's password and issues an access token.
        Returns: (success_bool, message_str, token_data_dict)
        """
        user_repo = UserRepository(db)
        user = user_repo.get_by_username(username)
        if not user or not verify_password(password_plain, user.password_hash):
            return False, "Incorrect username or password", {}

        access_token = create_access_token(data={"sub": user.username, "id": user.id})
        return True, "Authentication successful", {"access_token": access_token, "token_type": "bearer"}
