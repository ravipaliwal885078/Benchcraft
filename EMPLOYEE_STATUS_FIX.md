# Employee Status Fix - Derived from Allocations

## Problem
Employee status was showing as "ALLOCATED" in some displays even when the employee had no active allocations or projects. This was because:
1. Status was stored as a static database field (`employee.status`)
2. This field could get out of sync with actual allocations
3. Status was returned directly from the database without checking actual allocations

## Solution
Created utility functions to **derive employee status from actual allocations** rather than relying on the stored status field.

## Changes Made

### 1. Created Utility Functions (`backend/utils/employee_status.py`)

**`get_derived_employee_status(employee, session, today)`**
- Derives status from actual allocations
- Rules:
  - **ALLOCATED**: Has active allocations (start_date <= today AND (end_date is None OR end_date >= today))
  - **NOTICE_PERIOD**: Preserves special status (overrides allocation status)
  - **BENCH**: No active allocations
- Filters out pure trainee allocations (is_trainee=True with 0% allocation)

**`get_current_allocation(employee, session, today)`**
- Gets the current active allocation for an employee
- Prefers non-trainee allocations
- Returns None if no active allocations

**`sync_employee_status(employee, session)`**
- Syncs stored status field with derived status
- Can be called after allocation changes to keep database in sync

### 2. Updated Employee Routes (`backend/routes/employees.py`)

- **`get_employees()`**: Now returns derived status instead of stored status
- **`get_employee()`**: Uses derived status
- **Status filter**: Now filters by derived status (not stored status)
- **Allocation creation**: Automatically syncs status after creating allocation

### 3. Updated HR Routes (`backend/routes/hr.py`)

- **`get_pending_profiles()`**: Filters by derived status
- **`get_allocation_report()`**: Uses derived status
- **`verify_profile()`**: Syncs status instead of forcing to ALLOCATED

### 4. Updated Resource Routes (`backend/routes/resources.py`)

- **`allocate_resource()`**: Syncs status after allocation instead of forcing to ALLOCATED

### 5. Updated SQL DB Tool (`backend/tools/sql_db.py`)

- **`create_allocation()`**: Syncs status after creating allocation

### 6. Created Migration Script (`backend/migrate_sync_employee_status.py`)

- Script to sync all employee statuses with their actual allocations
- Run this once to fix existing data

## How It Works

### Status Derivation Logic

```python
# 1. Check if employee is in NOTICE_PERIOD (special status)
if employee.status == EmployeeStatus.NOTICE_PERIOD:
    return EmployeeStatus.NOTICE_PERIOD

# 2. Find active allocations
active_allocations = allocations where:
    - start_date <= today
    - end_date is None OR end_date >= today

# 3. Filter out pure trainee allocations
real_allocations = active_allocations where:
    - NOT is_trainee OR
    - is_trainee BUT has allocation_percentage > 0

# 4. Determine status
if real_allocations exist:
    return ALLOCATED
else:
    return BENCH
```

### Current Allocation Logic

```python
# Prefers non-trainee allocations
# Returns first non-trainee active allocation
# Falls back to trainee allocation if that's all they have
```

## API Response Changes

Employee objects now return:
```json
{
  "status": "ALLOCATED",  // Derived from allocations
  "stored_status": "ALLOCATED",  // Original database value (for reference)
  "current_allocation": {
    "project_name": "...",
    "project_id": 123,
    ...
  }
}
```

## Migration Steps

1. **Run the sync migration** (optional but recommended):
   ```bash
   cd backend
   python migrate_sync_employee_status.py
   ```

2. **Restart the Flask server** to load the new utility functions

3. **Test the changes**:
   - Check employee list - status should match actual allocations
   - Check employee profile - status should be correct
   - Create/update allocations - status should sync automatically

## Benefits

1. **Accurate Status**: Status always reflects actual allocations
2. **Automatic Sync**: Status updates automatically when allocations change
3. **Consistent Display**: All endpoints return the same derived status
4. **Backward Compatible**: Still includes `stored_status` for reference

## Edge Cases Handled

- ✅ Expired allocations (end_date < today) → BENCH
- ✅ Future allocations (start_date > today) → BENCH
- ✅ Trainee-only allocations (0% allocation) → BENCH
- ✅ Multiple allocations → ALLOCATED if any are active
- ✅ NOTICE_PERIOD status → Preserved (special case)
- ✅ No allocations → BENCH

## Files Modified

- ✅ `backend/utils/employee_status.py` (new)
- ✅ `backend/routes/employees.py`
- ✅ `backend/routes/hr.py`
- ✅ `backend/routes/resources.py`
- ✅ `backend/tools/sql_db.py`
- ✅ `backend/migrate_sync_employee_status.py` (new)
