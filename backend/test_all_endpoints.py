#!/usr/bin/env python3
"""
Comprehensive QA test for all API endpoints
"""

import sys
import asyncio
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, ".")

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.services.auth_service import get_password_hash

# Test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test user data
test_user = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "full_name": "Test User",
}


class EndpointTester:
    def __init__(self):
        self.results = []
        self.token = None
        self.user_id = None

    def log_result(self, endpoint: str, method: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details,
        }
        self.results.append(result)
        print(f"{'✓' if status == 'PASS' else '✗'} {method} {endpoint}: {status}")
        if details and status != "PASS":
            print(f"  Details: {details}")

    def setup_test_user(self):
        """Create a test user and get auth token"""
        try:
            # Create user directly in database
            db = TestingSessionLocal()
            hashed_password = get_password_hash(test_user["password"])
            user = User(
                email=test_user["email"],
                username=test_user["username"],
                hashed_password=hashed_password,
                full_name=test_user["full_name"],
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            self.user_id = user.id
            db.close()

            # Login to get token - using OAuth2 form data
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user["email"],
                    "password": test_user["password"],
                },
            )

            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.log_result(
                    "/auth/login", "POST", "PASS", "User created and logged in"
                )
            else:
                self.log_result(
                    "/auth/login", "POST", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("setup", "SETUP", "FAIL", f"Error: {str(e)}")

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        json: Dict = None,
        params: Dict = None,
        requires_auth: bool = True,
        expected_status: int = 200,
    ):
        """Test a single endpoint"""
        headers = {}
        if requires_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            if method == "GET":
                response = client.get(endpoint, headers=headers, params=params)
            elif method == "POST":
                response = client.post(endpoint, headers=headers, json=json)
            elif method == "PUT":
                response = client.put(endpoint, headers=headers, json=json)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=headers)
            else:
                self.log_result(
                    endpoint, method, "SKIP", f"Unsupported method: {method}"
                )
                return

            if response.status_code == expected_status:
                self.log_result(endpoint, method, "PASS")
            else:
                details = f"Expected {expected_status}, got {response.status_code}"
                if response.status_code >= 400:
                    try:
                        error_detail = response.json()
                        details += f" - {error_detail}"
                    except:
                        details += f" - Response: {response.text[:100]}"
                self.log_result(endpoint, method, "FAIL", details)

        except Exception as e:
            self.log_result(endpoint, method, "ERROR", f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run comprehensive tests for all modules"""
        print("=" * 80)
        print("COMPREHENSIVE QA TEST FOR ALL API ENDPOINTS")
        print("=" * 80)

        # Setup test user
        print("\n1. Setting up test environment...")
        self.setup_test_user()

        if not self.token:
            print("ERROR: Cannot proceed without authentication token")
            return

        print("\n2. Testing Authentication Module...")
        self.test_endpoint("/api/v1/auth/me", "GET")
        self.test_endpoint("/api/v1/auth/me", "PUT", json={"full_name": "Updated Name"})

        print("\n3. Testing Health Module...")
        self.test_endpoint("/api/v1/health", "GET", requires_auth=False)
        self.test_endpoint("/api/v1/health/ready", "GET", requires_auth=False)

        print("\n4. Testing User Management...")
        self.test_endpoint("/api/v1/users/profile", "GET")
        self.test_endpoint(
            "/api/v1/users/profile",
            "PUT",
            json={
                "age": 30,
                "gender": "male",
                "height": 175,
                "initial_weight": 80000,
                "target_weight": 70000,
                "activity_level": "moderate",
            },
        )

        print("\n5. Testing Health Data Management...")
        self.test_endpoint("/api/v1/health-data/records", "GET")
        self.test_endpoint(
            "/api/v1/health-data/records",
            "POST",
            json={"weight": 75000, "date": "2026-02-22", "notes": "Test weight record"},
        )

        print("\n6. Testing Habit System...")
        self.test_endpoint("/api/v1/habits/", "GET")
        self.test_endpoint(
            "/api/v1/habits/",
            "POST",
            json={
                "name": "Test Habit",
                "description": "Daily test habit",
                "category": "health",
                "frequency": "daily",
                "target_count": 1,
            },
        )

        print("\n7. Testing Nutrition System...")
        self.test_endpoint("/api/v1/nutrition/recommendations", "GET")
        self.test_endpoint("/api/v1/nutrition/calorie-target", "GET")

        print("\n8. Testing Dashboard...")
        self.test_endpoint("/api/v1/dashboard/overview", "GET")
        self.test_endpoint("/api/v1/dashboard/quick-stats", "GET")

        print("\n9. Testing AI Conversation System...")
        self.test_endpoint(
            "/api/v1/ai/chat",
            "POST",
            json={
                "message": "Hello, I need help with weight management",
                "role": "nutritionist",
            },
        )

        print("\n10. Testing Emotional Support...")
        self.test_endpoint("/api/v1/emotional-support/emotional-states", "GET")
        self.test_endpoint(
            "/api/v1/emotional-support/emotional-states",
            "POST",
            json={
                "mood": "happy",
                "energy_level": "high",
                "stress_level": 3,
                "notes": "Feeling good today",
            },
        )

        print("\n11. Testing Exercise Tracking...")
        self.test_endpoint("/api/v1/exercises/exercise-sessions", "GET")

        print("\n12. Testing Meal Tracking...")
        self.test_endpoint("/api/v1/meals/meals", "GET")

        print("\n13. Testing Gamification System...")
        self.test_endpoint("/api/v1/gamification/overview", "GET")
        self.test_endpoint("/api/v1/gamification/points", "GET")

        print("\n14. Testing Health Assessment...")
        self.test_endpoint("/api/v1/health-assessment/assessment", "POST", json={})

        print("\n15. Testing Scientific Visualization...")
        self.test_endpoint(
            "/api/v1/scientific-visualization/scientific-dashboard", "GET"
        )

        print("\n16. Testing Professional Fusion...")
        self.test_endpoint("/api/v1/professional-fusion/quick-check", "GET")

        print("\n17. Testing User Experience...")
        self.test_endpoint("/api/v1/user-experience/greeting", "GET")

        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")

        print(f"Total tests: {total}")
        print(f"Passed: {passed} ({passed / total * 100:.1f}%)")
        print(f"Failed: {failed} ({failed / total * 100:.1f}%)")
        print(f"Errors: {errors} ({errors / total * 100:.1f}%)")
        print(f"Skipped: {skipped} ({skipped / total * 100:.1f}%)")

        # Show failed tests
        if failed > 0 or errors > 0:
            print("\nFAILED/ERROR TESTS:")
            for result in self.results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(
                        f"  {result['method']} {result['endpoint']}: {result['details']}"
                    )

        return self.results


if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_comprehensive_tests()
