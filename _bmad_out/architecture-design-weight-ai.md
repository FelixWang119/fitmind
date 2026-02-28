# 体重管理 AI 助手 - 架构设计文档 (简化版)

**版本**: 1.0  
**日期**: 2026-02-27  
**项目**: Brownfield 优化项目  
**范围**: 新增/扩展模块架构设计

---

## 📋 目录

1. [系统架构图](#1-system-architecture-diagram)
2. [数据模型 ER 图](#2-data-model-er-diagram)
3. [API 端点列表](#3-api-endpoints)
4. [技术选型](#4-technology-selection)
5. [数据迁移策略](#5-data-migration-strategy)
6. [性能考虑](#6-performance-considerations)
7. [安全风险识别](#7-security-risks)

---

## 1. System Architecture Diagram

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐                              │
│  │   Web App    │  │  Mobile App  │                              │
│  │  (React)     │  │              │                              │
│  └──────┬───────┘  └──────────────┘                              │
└─────────┼────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                      API Gateway                                 │
│              FastAPI Router (v1/v2)                              │
└─────────┬────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │
│  │ User Service│ │Goal Service │ │Exercise Svc │                 │
│  └─────────────┘ └─────────────┘ └─────────────┘                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │
│  │Nutrition Svc│ │Memory Service│ │Notification│                 │
│  └─────────────┘ └─────────────┘ └─────────────┘                 │
└─────────┬────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                       Data Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │PostgreSQL   │  │PostgreSQL   │  │   Redis     │               │
│  │  (Main)     │  │+ pgvector   │  │   (Cache)   │               │
│  └─────────────┘  └─────────────┘  └─────────────┘               │
└─────────┬────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                        AI Layer                                  │
│  ┌─────────────┐  ┌─────────────┐                                │
│  │  Qwen AI    │  │BGE-Small-ZH │                                │
│  └─────────────┘  └─────────────┘                                │
└──────────────────────────────────────────────────────────────────┘
```

### New Module Architecture

```
User Profile Extension (P0)
├── UserProfile Model (17 fields)
├── Profile Schema (v2)
└── Profile API v2

Goal System (P0)
├── UserGoal Model
├── GoalProgress Model
└── GoalHistory Model

Calorie Balance (P0)
├── Meal Record Integration
├── Exercise Check-in Integration
└── Real-time Calculator

AI Memory Integration (P1)
├── Profile → UnifiedMemory
├── Vector Search (pgvector)
└── AI Conversation Reference

Push Notifications (P1)
├── Real-time Push (per meal/exercise)
├── Daily Digest (8PM)
└── Weekly Report (Monday)
```

---

## 2. Data Model ER Diagram

### New and Extended Tables

```
┌─────────────┐
│   USER      │ (扩展到 17 字段)
│             │
│ id          │
│ email       │
│ current_weight     # NEW
│ waist_circumference # NEW
│ hip_circumference  # NEW
│ body_fat_percentage # NEW
│ muscle_mass        # NEW
│ ... (17 total)     │
└──────┬──────┘
       │
       │ 1:N
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌─────────────┐   ┌─────────────┐
│USER_PROFILE │   │USER_GOAL    │ # NEW
│             │   │             │
│id           │   │id           │
│user_id      │   │user_id      │
│...          │   │goal_type    │
└─────────────┘   │current_val  │
                  │target_val    │
                  │...           │
                  └──────┬──────┘
                         │
                         │ 1:N
                         │
                         ▼
                  ┌─────────────┐
                  │GOAL_PROGRESS│ # NEW
                  │             │
                  │id           │
                  │goal_id      │
                  │value        │
                  │streak_count │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │GOAL_HISTORY │ # NEW
                  │             │
                  │id           │
                  │goal_id      │
                  │change_type  │
                  │previous_state│
                  │new_state    │
                  └─────────────┘

EXERCISE_CHECKIN
┌─────────────────────┐
│id                   │
│user_id              │
│exercise_type        │
│duration_minutes     │
│calories_burned      │
│...                  │
└─────────────────────┘

MEAL
┌─────────────────────┐
│id                   │
│user_id              │
│calories             │
│protein              │
│carbs                │
│fat                  │
│...                  │
└─────────────────────┘

UNIFIED_MEMORY (with pgvector)
┌─────────────────────┐
│id                   │
│user_id              │
│memory_type          │
│content_summary      │
│embedding (768 dim)  │ # NEW: pgvector
│source_type          │
│...                  │
└─────────────────────┘
```

### Key Fields

**USER (17 字段)**

```
Current 6 fields:
- age, gender, height, initial_weight, target_weight, activity_level

New 11 fields:
- current_weight (int)
- waist_circumference (int)
- hip_circumference (int)
- body_fat_percentage (float)
- muscle_mass (int)
- bone_density (float)
- metabolism_rate (float)
- health_conditions (json)
- medications (json)
- allergies (json)
- sleep_quality (string)
```

**USER_GOAL**

```
- goal_type: 'weight'|'exercise'|'diet'|'habit'
- current_value: 70.5
- target_value: 65.0
- unit: 'kg'|'minutes'|'kcal'|'ml'
- start_date, target_date
- predicted_date (AI calculated)
- status: 'active'|'completed'|'paused'
- progress_percentage: 65.5
```

**GOAL_PROGRESS**

```
- goal_id
- recorded_date
- value: 68.2
- daily_target_met: true
- streak_count: 5
```

---

## 3. API Endpoints

### New Endpoints (v2.0)

| Method | Endpoint | Priority |
|--------|----------|----------|
| GET | `/api/v2/users/me/profile` | P0 |
| PUT | `/api/v2/users/me/profile` | P0 |
| GET | `/api/v2/goals` | P0 |
| POST | `/api/v2/goals` | P0 |
| POST | `/api/v2/goals/{id}/progress` | P0 |
| GET | `/api/v2/calorie-balance/today` | P0 |
| GET | `/api/v2/exercise/checkins` | P0 |
| POST | `/api/v2/exercise/checkins` | P0 |
| GET | `/api/v2/achievements` | P1 |

### Extended Endpoints (v1.0 → v2.0)

| Method | Endpoint | Change |
|--------|----------|--------|
| GET | `/api/v1/users/me` | Expand to 17 fields |
| PUT | `/api/v1/users/me` | Accept 17 fields |

### API Versioning Strategy

```
/api/v1/     # Original API (backward compatible)
/api/v2/     # New API (profile, goals, calorie)
/api/latest  # Auto-redirect
```

---

## 4. Technology Selection

### Frontend

| Component | Library | Reason |
|-----------|---------|--------|
| UI Framework | Ant Design | Already in use |
| Charts | Chart.js | Lightweight, mature |
| State | Zustand | Already in use |

### Backend

| Service | Technology | Reason |
|---------|------------|--------|
| Web Frame | FastAPI | Already in use |
| ORM | SQLAlchemy | Already in use |
| Vector DB | pgvector | Simplified infra, native PG |

### Why pgvector?

✅ Simplified infrastructure (no extra DB)  
✅ Native PostgreSQL integration  
✅ Hybrid search support (vector + SQL)  
✅ Cost-effective  

### Why Chart.js?

✅ Lightweight (<20KB)  
✅ TypeScript friendly  
✅ Responsive  
✅ Already in use  

---

## 5. Data Migration Strategy

### Migration Steps

**Step 1: Backup Database**
```bash
pg_dump -U weight_ai_user weight_ai_db > backup/weight_ai_$(date).sql.gz
```

**Step 2: Add Extended Profile Fields**
```python
op.add_column("users", Column("current_weight", Integer))
op.add_column("users", Column("waist_circumference", Integer))
op.add_column("users", Column("health_conditions", Text))  # JSON
# ... (11 new fields total)
```

**Step 3: Create New Tables**
```python
op.create_table("user_goals", ...)
op.create_table("goal_progress", ...)
op.create_table("goal_history", ...)
```

**Step 4: Backfill Data**
```python
# Generate default goals for existing users
INSERT INTO user_goals (user_id, goal_type, current_value, ...)
SELECT id, 'weight', initial_weight/1000.0, ...
FROM users WHERE id NOT IN (SELECT user_id FROM user_goals);
```

**Step 5: Validate & Rollout**
- Row count verification
- Sample data check
- Production deployment

### Unit Conversion

```
CRITICAL: Weight Units
Database:  grams (70000)
Frontend:  kilograms (70.0)
Conversion: frontend * 1000 = backend
```

---

## 6. Performance Considerations

### Caching Strategy

| Data | TTL | Reason |
|------|-----|--------|
| User Profile | 300s | Infrequent changes |
| Calorie Balance | 120s | Real-time needed |
| Exercise Types | 1 day | Static data |
| Goal Statistics | 60s | Frequent updates |

### Redis Implementation

```python
@cache_result(ttl=60)
def get_calorie_balance(user_id: int):
    # ... calculation logic
```

### Database Indexing

```sql
-- Critical Indexes
CREATE INDEX idx_user_goals_user_type ON user_goals (user_id, goal_type);
CREATE INDEX idx_goal_progress_goal_date ON goal_progress (goal_id, recorded_date);
CREATE INDEX idx_unified_memory_embedding ON unified_memory 
    USING ivfflat (embedding vector_cosine_ops);
```

### Calculation Strategies

| Calculation | Strategy |
|-------------|----------|
| BMR/TDEE | Cached (30min) |
| Calorie Balance | Cached (2min) + Real-time |
| Goal Progress | Real-time |
| Exercise Calories | Real-time |

---

## 7. Security Risks

### Threat Matrix

| Threat | Severity | Mitigation |
|--------|----------|------------|
| Data Breach | 🔴 High | AES-256 encryption |
| Unauthorized Access | 🔴 High | RBAC + OAuth2 |
| SQL Injection | 🟡 Medium | SQLAlchemy ORM |
| XSS | 🟡 Medium | Content Security Policy |

### Encryption Example

```python
from cryptography.fernet import Fernet

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()
```

### Access Control

```python
def get_current_user_permissions(current_user: User) -> list:
    permissions = []
    if current_user.is_superuser:
        permissions = [p.value for p in Permission]
    else:
        permissions = ["read:health", "write:health"]
    return permissions
```

### Audit Logging

```python
class AuditLog(Base):
    action = Column(String(100))  # 'profile.update'
    old_value = Column(Text)  # JSON
    new_value = Column(Text)  # JSON
    ip_address = Column(String(50))
```

---

## ✅ Next Steps

1. Review architecture with team
2. Create Epic/Story breakdown
3. Implement User Profile Extension (P0)
4. Write unit and integration tests
5. Deploy to staging environment

---

**Document Status**: ✅ Draft Complete  
**Maintainer**: BMAD Architect Agent  
**Date**: 2026-02-27
