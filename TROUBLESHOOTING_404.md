# Troubleshooting 404 Error for Allocation Report

## Issue
Getting 404 error when accessing `/api/v1/hr/allocation-report`

## Solution Steps

### 1. Restart Flask Server
The most common cause is that the Flask server needs to be restarted to pick up the new route.

**Windows:**
```powershell
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
python app.py
```

**Or if using the PowerShell script:**
```powershell
.\start-backend.ps1
```

### 2. Verify Route Registration
Test if the HR blueprint is working by accessing:
```
GET http://localhost:5000/api/v1/hr/test
```

This should return: `{"message": "HR routes are working", "route": "/api/v1/hr/test"}`

### 3. Check for Import Errors
If the test route also returns 404, there might be an import error. Check the Flask server logs for any errors when starting.

Common issues:
- New models (RateCard, Domain, etc.) might not exist in database
- Database tables need to be created

### 4. Initialize Database Tables
If the new tables don't exist, create them:

```python
from tools.sql_db import SQLDatabaseTool
from models import Base
from sqlalchemy import create_engine
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
```

Or run:
```python
python -c "from tools.sql_db import SQLDatabaseTool; db = SQLDatabaseTool(); db.init_db()"
```

### 5. Verify Route Path
The route should be accessible at:
- Full path: `http://localhost:5000/api/v1/hr/allocation-report`
- With query params: `http://localhost:5000/api/v1/hr/allocation-report?forecast_days=30&include_bench=true`

### 6. Check Flask Logs
Look for any errors in the Flask console output when the server starts. Common errors:
- `ModuleNotFoundError`: Missing imports
- `AttributeError`: Model attributes not found
- `OperationalError`: Database table doesn't exist

## Quick Test

1. **Test HR blueprint:**
   ```bash
   curl http://localhost:5000/api/v1/hr/test
   ```

2. **Test allocation report:**
   ```bash
   curl "http://localhost:5000/api/v1/hr/allocation-report?forecast_days=30&include_bench=true"
   ```

## Expected Response

If working correctly, the allocation report should return:
```json
{
  "report_date": "2026-01-11",
  "forecast_days": 30,
  "forecast_date": "2026-02-10",
  "total_employees": 20,
  "employees": [...],
  "summary": {...}
}
```

## Still Not Working?

If the route still returns 404 after restarting:
1. Check that `backend/routes/hr.py` contains the `@bp.route('/allocation-report', methods=['GET'])` decorator
2. Verify `backend/app.py` imports and registers the HR blueprint
3. Check for any Python syntax errors in `backend/routes/hr.py`
4. Ensure all new model imports are correct
