# Efficient Testing Guide

## Goal
Eliminate all inefficient workflows in testing and create a streamlined, efficient testing infrastructure.

## Problems We're Solving
1. **Repeated user registration** - Testing API without token, then registering user, then getting token
2. **Machine slowdowns** - Restart procedures leaving processes running
3. **Inefficient workflows** - Testing without proper setup, then fixing, then retesting
4. **No fixed test users** - Creating new users for every test run

## Solutions Implemented

### 1. Fixed Test Users System
**Always use these fixed test users - NEVER register new users for testing:**

| Purpose | Email | Password | Username |
|---------|-------|----------|----------|
| Default | `test.user@example.com` | `TestPassword123!` | `testuser` |
| Nutrition | `nutrition.test@example.com` | `NutritionTest123!` | `nutritiontest` |
| Habit | `habit.test@example.com` | `HabitTest123!` | `habittest` |
| Admin | `admin.test@example.com` | `AdminTest123!` | `admintest` |

**Usage:**
```python
# Direct approach (recommended)
import requests

token = get_direct_token()  # From test_direct_token.py
headers = {"Authorization": f"Bearer {token}"}

# Or use test_users module
from app.core.test_users import get_test_token
token = get_test_token(db, "nutrition")
```

### 2. Efficient Restart Procedures
**ALWAYS kill processes before restarting:**

```bash
# Use the efficient restart script
./restart_efficient.sh

# Or the simple version
./restart_simple.sh
```

**Key features:**
- Kills all processes on port 8000
- Kills Python backend processes
- Waits for proper cleanup
- Starts fresh with PID tracking
- Verifies backend is healthy

### 3. Direct Token Acquisition
**NEVER test API without token first:**

```python
# BAD - Inefficient workflow
response = requests.get("/api/endpoint")  # Fails: 401
# Register user...
# Get token...
# Test again...

# GOOD - Efficient workflow
token = get_direct_token()  # Gets token immediately
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("/api/endpoint", headers=headers)  # Works!
```

### 4. Centralized Test Resources
**Use these centralized modules:**

- `backend/app/core/test_users.py` - Test user management
- `backend/app/core/test_resources.py` - Test data and fixtures
- `backend/app/core/qwen_config.py` - Qwen API configuration
- `test_direct_token.py` - Simple token acquisition
- `test_efficient.py` - Efficient testing tools

## Workflow Rules

### Rule 1: Always Start with Token
**NEVER** test API endpoints without authentication first. Always:
1. Get token from fixed test user
2. Use token in all API calls
3. Save token for reuse in same session

### Rule 2: Use Efficient Restart
**NEVER** restart backend without killing processes first:
1. Run `./restart_efficient.sh`
2. Wait for "Backend started successfully" message
3. Verify with `curl http://localhost:8000/api/v1/health`

### Rule 3: Never Register New Users
**NEVER** create new users during testing:
1. Use fixed test users only
2. If user doesn't exist, script will register it once
3. Token is cached for 30 minutes

### Rule 4: Document Everything
**ALWAYS** document patterns in project context:
1. Run `/bmad-bmm-generate-project-context` regularly
2. Update documentation when patterns change
3. Share efficient workflows with team

## Quick Reference Commands

### Restart Backend
```bash
cd /Users/felix/bmad
./restart_efficient.sh      # Full featured restart
./restart_simple.sh         # Quick restart
```

### Get Test Token
```bash
cd /Users/felix/bmad
python test_direct_token.py  # Gets token and saves to test_token.txt
```

### Test API
```bash
# With saved token
export TEST_TOKEN=$(cat test_token.txt)
curl -H "Authorization: Bearer $TEST_TOKEN" http://localhost:8000/api/v1/users/me

# Or use test script
python test_efficient.py
```

### Check Backend Health
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/users/me -H "Authorization: Bearer $TOKEN"
```

## Common Issues and Solutions

### Issue: "Cannot connect to server"
**Solution:**
```bash
./restart_efficient.sh  # Kills processes and restarts
```

### Issue: "401 Unauthorized"
**Solution:**
```bash
python test_direct_token.py  # Gets fresh token
export TEST_TOKEN=$(cat test_token.txt)
```

### Issue: "Machine slowing down"
**Solution:**
```bash
./restart_efficient.sh  # Kills leftover processes
pkill -f "uvicorn"      # Force kill if needed
pkill -f "python.*backend"
```

### Issue: "User already exists"
**Solution:**
- Use fixed test users only
- Script handles registration automatically
- Clean up with: `python -c "from app.core.test_users import test_user_manager; import app.core.database; db = app.core.database.SessionLocal(); test_user_manager.cleanup_test_users(db)"`

## Best Practices

1. **Token Reuse**: Save token to file and reuse in same testing session
2. **Health Checks**: Always check backend health before testing
3. **Log Monitoring**: Watch logs with `tail -f backend/backend.log`
4. **Clean State**: Use efficient restart to ensure clean state
5. **Fixed Data**: Use test_resources.py for consistent test data

## Files Created

### Core Infrastructure
- `backend/app/core/test_users.py` - Fixed test user management
- `backend/app/core/test_resources.py` - Test data and fixtures
- `backend/app/core/qwen_config.py` - Centralized Qwen API config

### Testing Tools
- `test_direct_token.py` - Simple direct token acquisition
- `test_efficient.py` - Efficient testing utilities
- `test_simple_efficient.py` - Simplified testing approach

### Restart Scripts
- `restart_efficient.sh` - Full-featured restart with process killing
- `restart_simple.sh` - Quick restart script

### Documentation
- `docs/EFFICIENT_TESTING_GUIDE.md` - This guide
- `docs/INFRASTRUCTURE_QUICK_REFERENCE.md` - Quick reference
- Updated project context via BMAD workflow

## Next Steps

1. **Update all existing tests** to use fixed test users
2. **Train team members** on efficient workflows
3. **Monitor performance** and optimize further
4. **Regularly update** project context with new patterns

## Success Metrics

- ✅ No more "test API → no token → register → get token" workflow
- ✅ Backend restarts cleanly without machine slowdowns
- ✅ Fixed test users available for all testing
- ✅ Token acquisition is simple and direct
- ✅ All patterns documented in project context

---

**Remember:** Efficiency is not optional. Follow these patterns to save time and avoid frustration.