---
project_name: bmad
user_name: Felix
date: '2026-02-23'
sections_completed: ['technology_stack', 'code_patterns', 'api_conventions', 'database_patterns', 'testing_rules', 'naming_conventions']
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | ^3.11 | Runtime |
| FastAPI | ^0.109.0 | Web Framework |
| SQLAlchemy | ^2.0.23 | ORM |
| Pydantic | ^2.5.0 | Data Validation |
| Uvicorn | ^0.24.0 | ASGI Server |
| bcrypt | ^1.7.4 | Password Hashing |
| python-jose | ^3.3.0 | JWT Tokens |
| structlog | ^23.2.0 | Structured Logging |
| redis | ^5.0.1 | Caching |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ^7.4.3 | Testing |
| pytest-asyncio | ^0.21.1 | Async Testing |
| pytest-cov | ^4.1.0 | Coverage |
| black | ^23.11.0 | Formatting |
| isort | ^5.12.0 | Import Sorting |
| mypy | ^1.7.0 | Type Checking |
| factory-boy | ^3.3.0 | Test Factories |

### Configuration Files

- `pyproject.toml` - 项目配置 (Poetry)
- `pytest.ini` - 测试配置
- `mypy.ini` - 类型检查配置

---

## Critical Implementation Rules

### 1. API Endpoint Conventions

**File Location:** `app/api/v1/endpoints/`

**Pattern:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Endpoint description in Chinese"""
    # Implementation
    return user
```

**Rules:**
- Always use `status_code=status.HTTP_201_CREATED` for POST creating resources
- Use Chinese docstrings for endpoints
- Import models as `UserModel` to avoid confusion with schemas
- Use `Depends(get_db)` for database session injection
- Always validate input with Pydantic schemas

### 2. Service Layer Pattern

**File Location:** `app/services/`

**Pattern:**
```python
import structlog
from sqlalchemy.orm import Session

logger = structlog.get_logger()

def create_user(db: Session, user_data: dict):
    """Create a new user"""
    logger.info("Creating user", email=user_data.get("email"))
    # Implementation
    return user
```

**Rules:**
- Use `structlog.get_logger()` for logging
- Functions should accept `db: Session` as first parameter
- Use snake_case for function names
- Always log important operations

### 3. Database Model Conventions

**File Location:** `app/models/`

**Pattern:**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    health_records = relationship("HealthRecord", back_populates="user")
```

**Rules:**
- Use `func.now()` for server-side timestamps
- Always define `__tablename__` explicitly
- Use relationships with `back_populates`
- Use String(255) for email fields
- Use Integer for IDs

### 4. Pydantic Schema Conventions

**File Location:** `app/schemas/`

**Pattern:**
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator("password")
    def validate_password_strength(cls, v):
        # Custom validation
        return v
    
    class Config:
        from_attributes = True
```

**Rules:**
- Use `EmailStr` for email fields
- Use `Field()` with validation constraints
- Use `@validator` for complex validation
- Always set `class Config: from_attributes = True` for ORM compatibility
- Use Optional[] for nullable fields

### 5. Authentication Pattern

**Token Creation:**
```python
from app.services.auth_service import create_access_token
from datetime import timedelta

access_token = create_access_token(
    data={"sub": str(user_id), "email": user.email, "user_id": user_id},
    expires_delta=timedelta(minutes=30)
)
```

**Token Verification:**
```python
from app.api.v1.endpoints.auth import get_current_active_user

@router.get("/protected")
async def protected_endpoint(current_user: UserModel = Depends(get_current_active_user)):
    return {"user_id": current_user.id}
```

**Rules:**
- Token must contain: `sub` (user_id), `email`, `user_id`
- Use `get_current_active_user` dependency for protected endpoints
- Always verify user is active

### 6. Testing Conventions

**File Location:** `tests/`

**Pattern:**
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_example(client):
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

**Rules:**
- Use fixtures for test setup
- Override database with `app.dependency_overrides`
- Use unique data (UUID) to avoid conflicts
- Test both success and failure cases
- Use real database (SQLite) for integration tests

### 7. Weight Unit Convention

**Important:** This project uses **grams** for weight, not kilograms!

```python
# Correct - in grams
weight = 70000  # 70kg = 70000g

# Incorrect - in kilograms  
weight = 70  # Wrong!
```

**Fields using grams:**
- `initial_weight` - grams
- `target_weight` - grams
- `weight` in HealthRecord - grams

---

## Code Organization

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/     # API route handlers
│   ├── core/                   # Config, database, middleware
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── main.py                # FastAPI app
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── test_*.py              # Test files
│   └── factories.py           # Test data factories
└── pyproject.toml
```

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `auth_service.py` |
| Classes | PascalCase | `class UserService` |
| Functions | snake_case | `def get_user_by_email()` |
| Variables | snake_case | `user_email` |
| Constants | UPPER_SNAKE_CASE | `MAX_LOGIN_ATTEMPTS` |
| Database Tables | plural snake_case | `users`, `health_records` |
| API Routes | kebab-case | `/api/v1/user-profile` |

---

## Import Organization (isort)

```python
# Standard library
from datetime import datetime
from typing import Optional

# Third-party
import structlog
from fastapi import APIRouter
from sqlalchemy.orm import Session

# Local application
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
```

Order: Standard library → Third-party → Local application

---

## Error Handling

**API Error Response:**
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail={"error": "validation_error", "message": "Email already registered"}
)
```

**Logging Errors:**
```python
logger.error("Operation failed", error=str(e), user_id=user_id)
```

---

## Database Session Management

**Always use dependency injection:**
```python
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Never create sessions directly in endpoints!**

---

## Weight Measurement Units (CRITICAL)

This is a weight management app, so units are crucial:

| Field | Unit | Example |
|-------|------|---------|
| weight | grams | 70000 = 70kg |
| height | centimeters | 170 = 170cm |
| calories | kcal | 2000 = 2000kcal |
| sleep_hours | hours | 7.5 = 7.5 hours |

---

## Previous Test Quality Review

**Last Review Date:** 2026-02-23
**Quality Score:** 72/100 (C - 良好)

**Key Findings:**
- ✅ Real database testing implemented
- ✅ Good fixture architecture in conftest.py
- ✅ Tests use UUID for unique data
- ⚠️ Some performance tests need optimization
- ⚠️ Missing some edge case tests

**Test Priorities:**
- `@pytest.mark.p0` - Core functionality (registration, login)
- `@pytest.mark.p1` - Important features
- `@pytest.mark.p2` - Performance tests

---

## Notes for AI Agents

1. **Always use grams for weight** - This is the most common mistake
2. **Use Chinese for documentation** - Project documentation is in Chinese
3. **Test with real database** - Don't use mocks for integration tests
4. **Use structlog for logging** - Not print statements
5. **Follow isort order** - Organize imports correctly
6. **Use Pydantic v2** - Not v1

---

_Last updated: 2026-02-23_
