"""Test user management and solidification system.

This module provides a centralized system for managing test users to avoid
repeated registration during testing and improve test performance.

Usage:
    from app.core.test_users import test_user_manager

    # Get or create a test user
    user_data = test_user_manager.get_or_create_test_user(db, "nutrition")

    # Get test user token
    token = test_user_manager.get_test_user_token(db, "nutrition")

    # Clean up test users
    test_user_manager.cleanup_test_users(db)
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import create_user, get_password_hash


# Configure logging
logger = logging.getLogger(__name__)


class TestUserManager:
    """Manage test users to avoid repeated registration in tests."""

    TEST_USERS_FILE = Path(__file__).parent.parent.parent / "test_users.json"

    # Predefined test users with different roles/purposes
    DEFAULT_TEST_USERS = [
        {
            "email": "test.user@example.com",
            "username": "testuser",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "purpose": "default",
            "description": "Default test user for general testing",
        },
        {
            "email": "nutrition.test@example.com",
            "username": "nutritiontest",
            "password": "NutritionTest123!",
            "full_name": "Nutrition Test User",
            "purpose": "nutrition",
            "description": "Test user for nutrition analysis testing",
        },
        {
            "email": "habit.test@example.com",
            "username": "habittest",
            "password": "HabitTest123!",
            "full_name": "Habit Test User",
            "purpose": "habit",
            "description": "Test user for habit tracking testing",
        },
        {
            "email": "admin.test@example.com",
            "username": "admintest",
            "password": "AdminTest123!",
            "full_name": "Admin Test User",
            "purpose": "admin",
            "description": "Test user for admin functionality testing",
        },
    ]

    def __init__(self):
        self.test_users = {}
        self._load_test_users()

    def _load_test_users(self) -> None:
        """Load test users from file or create default structure."""
        try:
            if self.TEST_USERS_FILE.exists():
                with open(self.TEST_USERS_FILE, "r") as f:
                    self.test_users = json.load(f)
                logger.info(
                    f"Loaded {len(self.test_users)} test users from {self.TEST_USERS_FILE}"
                )
            else:
                self.test_users = {}
                self._save_test_users()
                logger.info(f"Created new test users file at {self.TEST_USERS_FILE}")
        except Exception as e:
            logger.error(f"Failed to load test users: {e}")
            self.test_users = {}

    def _save_test_users(self) -> None:
        """Save test users to file."""
        try:
            with open(self.TEST_USERS_FILE, "w") as f:
                json.dump(self.test_users, f, indent=2, default=str)
            logger.debug(
                f"Saved {len(self.test_users)} test users to {self.TEST_USERS_FILE}"
            )
        except Exception as e:
            logger.error(f"Failed to save test users: {e}")

    def _get_default_user_config(self, purpose: str = "default") -> Dict[str, Any]:
        """Get default user configuration for a specific purpose.

        Args:
            purpose: User purpose (default, nutrition, habit, admin)

        Returns:
            User configuration dictionary
        """
        for user_config in self.DEFAULT_TEST_USERS:
            if user_config["purpose"] == purpose:
                return user_config.copy()

        # Fallback to default
        return self.DEFAULT_TEST_USERS[0].copy()

    def get_or_create_test_user(
        self, db: Session, purpose: str = "default"
    ) -> Dict[str, Any]:
        """Get existing test user or create if not exists.

        Args:
            db: Database session
            purpose: User purpose (default, nutrition, habit, admin)

        Returns:
            Dictionary with user data including id, email, and password
        """
        user_key = f"user_{purpose}"

        # Check if we have cached user data
        if user_key in self.test_users:
            cached_data = self.test_users[user_key]

            # Check if user still exists in database
            existing_user = (
                db.query(User).filter(User.email == cached_data["email"]).first()
            )

            if existing_user:
                logger.debug(f"Found existing test user: {cached_data['email']}")
                return {
                    **cached_data,
                    "id": existing_user.id,
                    "exists": True,
                    "purpose": purpose,
                }
            else:
                logger.warning(
                    f"Cached test user not found in DB: {cached_data['email']}"
                )

        # Create new test user
        user_config = self._get_default_user_config(purpose)

        try:
            # Check if user already exists with this email
            existing_user = (
                db.query(User).filter(User.email == user_config["email"]).first()
            )

            if existing_user:
                logger.info(f"Test user already exists: {user_config['email']}")
                user_data = {
                    "email": existing_user.email,
                    "username": existing_user.username,
                    "user_id": existing_user.id,
                    "created_at": existing_user.created_at.isoformat()
                    if existing_user.created_at
                    else None,
                    "access_token": None,
                    "token_expires": None,
                    "purpose": purpose,
                }
            else:
                # Create new user using auth_service
                from app.schemas.user import UserCreate

                user_create = UserCreate(
                    email=user_config["email"],
                    username=user_config["username"],
                    password=user_config["password"],
                    confirm_password=user_config["password"],
                    full_name=user_config["full_name"],
                    age=25,  # Default values
                    height=170,
                    initial_weight=70000,
                    target_weight=65000,
                    activity_level="moderate",
                    dietary_preferences=None,  # Use None instead of empty list
                )

                # Convert UserCreate to dict for auth_service
                user_dict = user_create.dict()
                user_dict["hashed_password"] = get_password_hash(
                    user_config["password"]
                )

                # Create user using auth_service
                from app.services.auth_service import create_user

                user = create_user(db, user_dict)

                logger.info(f"Created new test user: {user.email} (ID: {user.id})")

                user_data = {
                    "email": user.email,
                    "username": user.username,
                    "user_id": user.id,
                    "created_at": user.created_at.isoformat()
                    if user.created_at
                    else None,
                    "access_token": None,
                    "token_expires": None,
                    "purpose": purpose,
                }

            # Save for future use
            self.test_users[user_key] = user_data
            self._save_test_users()

            return {
                **user_data,
                "id": user_data["user_id"],
                "exists": existing_user is not None,
                "password": user_config["password"],  # Include password for login
            }

        except Exception as e:
            logger.error(f"Failed to get/create test user: {e}")
            raise

    def get_test_user_token(
        self, db: Session, purpose: str = "default"
    ) -> Optional[str]:
        """Get or refresh test user authentication token.

        Args:
            db: Database session
            purpose: User purpose (default, nutrition, habit, admin)

        Returns:
            Authentication token or None if failed
        """
        user_key = f"user_{purpose}"

        # Check if we have a valid cached token
        if user_key in self.test_users:
            user_data = self.test_users[user_key]

            if user_data.get("access_token") and user_data.get("token_expires"):
                expires = datetime.fromisoformat(user_data["token_expires"])
                if expires > datetime.now() + timedelta(minutes=5):
                    logger.debug(f"Using cached token for {purpose} user")
                    return user_data["access_token"]

        # Need to login and get new token
        try:
            user_info = self.get_or_create_test_user(db, purpose)

            # Import here to avoid circular imports
            from app.api.v1.endpoints.auth import authenticate_user, create_access_token

            # Authenticate user - handle ValueError exceptions
            try:
                user = authenticate_user(db, user_info["email"], user_info["password"])
            except ValueError as e:
                logger.error(
                    f"Failed to authenticate test user {user_info['email']}: {e}"
                )
                return None

            # Create access token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )

            # Update and save token
            user_data = self.test_users[user_key]
            user_data.update(
                {
                    "access_token": access_token,
                    "token_expires": (
                        datetime.now() + access_token_expires
                    ).isoformat(),
                }
            )
            self._save_test_users()

            logger.debug(f"Generated new token for {purpose} user")
            return access_token

        except Exception as e:
            logger.error(f"Failed to get test user token: {e}")
            return None

    def get_test_user_with_token(
        self, db: Session, purpose: str = "default"
    ) -> Dict[str, Any]:
        """Get test user data with authentication token.

        Args:
            db: Database session
            purpose: User purpose (default, nutrition, habit, admin)

        Returns:
            Dictionary with user data and token
        """
        user_data = self.get_or_create_test_user(db, purpose)
        token = self.get_test_user_token(db, purpose)

        return {
            **user_data,
            "access_token": token,
            "headers": {"Authorization": f"Bearer {token}"} if token else {},
        }

    def cleanup_test_users(
        self, db: Session, keep_users: bool = True
    ) -> Dict[str, Any]:
        """Clean up test users from database.

        Args:
            db: Database session
            keep_users: If True, only remove from cache, not from database

        Returns:
            Cleanup results
        """
        results = {"cache_cleared": 0, "users_deleted": 0, "errors": []}

        try:
            # Clear cache
            cache_count = len(self.test_users)
            self.test_users = {}
            self._save_test_users()
            results["cache_cleared"] = cache_count

            if not keep_users:
                # Delete test users from database
                for user_config in self.DEFAULT_TEST_USERS:
                    try:
                        user = (
                            db.query(User)
                            .filter(User.email == user_config["email"])
                            .first()
                        )

                        if user:
                            db.delete(user)
                            results["users_deleted"] += 1
                            logger.info(f"Deleted test user: {user.email}")
                    except Exception as e:
                        results["errors"].append(
                            f"Failed to delete {user_config['email']}: {e}"
                        )

                db.commit()

            logger.info(f"Test user cleanup completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Test user cleanup failed: {e}")
            results["errors"].append(str(e))
            return results

    def list_test_users(self, db: Session) -> List[Dict[str, Any]]:
        """List all test users with their status.

        Args:
            db: Database session

        Returns:
            List of test user information
        """
        users = []

        for purpose in ["default", "nutrition", "habit", "admin"]:
            try:
                user_key = f"user_{purpose}"
                cached_data = self.test_users.get(user_key, {})

                # Check database status
                db_user = None
                if cached_data.get("email"):
                    db_user = (
                        db.query(User)
                        .filter(User.email == cached_data["email"])
                        .first()
                    )

                user_info = {
                    "purpose": purpose,
                    "email": cached_data.get("email", "unknown"),
                    "in_cache": user_key in self.test_users,
                    "in_database": db_user is not None,
                    "user_id": db_user.id if db_user else None,
                    "token_valid": False,
                    "description": self._get_default_user_config(purpose).get(
                        "description", ""
                    ),
                }

                # Check token validity
                if cached_data.get("access_token") and cached_data.get("token_expires"):
                    expires = datetime.fromisoformat(cached_data["token_expires"])
                    user_info["token_valid"] = expires > datetime.now()
                    user_info["token_expires"] = cached_data["token_expires"]

                users.append(user_info)

            except Exception as e:
                logger.error(f"Failed to get info for {purpose} user: {e}")
                users.append({"purpose": purpose, "error": str(e)})

        return users

    def validate_test_users(self, db: Session) -> Dict[str, Any]:
        """Validate all test users and return status.

        Args:
            db: Database session

        Returns:
            Validation results
        """
        validation = {
            "test_users_file_exists": self.TEST_USERS_FILE.exists(),
            "test_users_file_path": str(self.TEST_USERS_FILE),
            "cached_users": len(self.test_users),
            "users": [],
            "summary": {
                "total_expected": len(self.DEFAULT_TEST_USERS),
                "in_cache": 0,
                "in_database": 0,
                "tokens_valid": 0,
            },
        }

        users_list = self.list_test_users(db)
        validation["users"] = users_list

        for user_info in users_list:
            if user_info.get("in_cache"):
                validation["summary"]["in_cache"] += 1
            if user_info.get("in_database"):
                validation["summary"]["in_database"] += 1
            if user_info.get("token_valid"):
                validation["summary"]["tokens_valid"] += 1

        # Overall status
        if (
            validation["summary"]["in_database"]
            == validation["summary"]["total_expected"]
        ):
            validation["status"] = "all_users_available"
        elif validation["summary"]["in_database"] > 0:
            validation["status"] = "partial_users_available"
        else:
            validation["status"] = "no_users_available"

        return validation


# Global instance for application-wide use
test_user_manager = TestUserManager()


# Convenience functions
def get_test_user(db: Session, purpose: str = "default") -> Dict[str, Any]:
    """Get test user data (convenience function).

    Args:
        db: Database session
        purpose: User purpose

    Returns:
        User data dictionary
    """
    return test_user_manager.get_or_create_test_user(db, purpose)


def get_test_token(db: Session, purpose: str = "default") -> Optional[str]:
    """Get test user token (convenience function).

    Args:
        db: Database session
        purpose: User purpose

    Returns:
        Authentication token
    """
    return test_user_manager.get_test_user_token(db, purpose)


if __name__ == "__main__":
    """Test the test user management system."""
    print("Test User Management System")
    print("=" * 50)

    # Note: This requires a database connection to run fully
    print("System initialized. Use in tests with database session.")
    print(f"Test users file: {TestUserManager.TEST_USERS_FILE}")
    print(f"Default test users: {len(TestUserManager.DEFAULT_TEST_USERS)}")

    # Show default user configurations
    print("\nDefault Test User Configurations:")
    print("-" * 30)
    for user_config in TestUserManager.DEFAULT_TEST_USERS:
        print(
            f"  {user_config['purpose']:10} {user_config['email']:30} {user_config['description']}"
        )
