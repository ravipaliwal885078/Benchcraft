# Allocation Percentage Validation - Implementation Locations

This document lists all locations where allocation percentage validation has been implemented to ensure employees never exceed 100% total allocation.

## Validation Function

**Location:** `backend/utils/allocation_validator.py`

**Function:** `validate_allocation_percentage(session, employee_id, new_allocation_percentage, start_date, end_date, exclude_allocation_id=None)`

**Purpose:** Validates that adding/updating an allocation won't cause the total allocation_percentage for an employee to exceed 100% across all overlapping date ranges.

## Implementation Locations

### 1. Project Team Management (Primary Use Case)
**File:** `backend/routes/projects.py`  
**Function:** `update_project_team(project_id)`  
**Route:** `POST /api/v1/projects/<project_id>/team`  
**When:** When updating project team via "Update Team" button in Projects tab  
**Validation:** ✅ Implemented  
**Line:** ~346 (after parsing dates, before creating/updating allocation)

**How to Test:**
1. Go to Projects tab
2. Click "Manage Team" (Users icon) on any project
3. Try to add/update an employee with allocation_percentage that would cause total > 100%
4. Should see error message with employee name and current total

---

### 2. Employee Allocation via Employees Route
**File:** `backend/routes/employees.py`  
**Function:** `allocate_resource()`  
**Route:** `POST /api/v1/employees/allocate`  
**When:** When allocating an employee to a project from the employees section  
**Validation:** ✅ Implemented  
**Line:** ~597 (after parsing dates, before creating allocation)

**How to Test:**
1. Go to Employees tab
2. Allocate an employee to a project
3. Try to allocate the same employee to another project with overlapping dates
4. Should see validation error if total exceeds 100%

---

### 3. Resource Allocation via Resources Route
**File:** `backend/routes/resources.py`  
**Function:** `allocate_resource()`  
**Route:** `POST /api/v1/allocate`  
**When:** When allocating resources via the resource management API  
**Validation:** ✅ Implemented  
**Line:** ~105 (after parsing dates, before creating allocation)

**How to Test:**
1. Use the `/api/v1/allocate` endpoint
2. Try to allocate an employee with allocation_percentage that would exceed 100%
3. Should receive validation error

---

### 4. SQL Database Tool Allocation
**File:** `backend/tools/sql_db.py`  
**Function:** `create_allocation()`  
**When:** When creating allocations via the SQLDatabaseTool (used by agents)  
**Validation:** ✅ Implemented  
**Line:** ~75 (before creating allocation object)

**How to Test:**
1. This is used internally by agents
2. Any agent trying to create an allocation will be validated
3. Raises ValueError if validation fails

---

## Validation Logic

The validation function:
1. **Finds Overlapping Allocations:** Queries all allocations for the employee that overlap with the new/updated allocation's date range
2. **Excludes Current Allocation:** If updating, excludes the allocation being updated from the calculation
3. **Sums Allocation Percentages:** Adds up all allocation_percentage values from overlapping allocations
4. **Adds New Percentage:** Adds the new allocation_percentage to the total
5. **Checks Limit:** Returns error if total > 100%

**Date Overlap Logic:**
- Two date ranges overlap if: `start1 <= end2 AND start2 <= end1`
- `None` end_date is treated as far future (2099-12-31)

**Error Message Format:**
```
"Total allocation for {Employee Name} would be {total}%. Maximum allowed is 100%. Current overlapping allocations total {current}%."
```

---

## Frontend Validation (Optional Enhancement)

Currently, validation is only on the backend. For better UX, you could add frontend validation in:

**File:** `frontend/src/pages/Pipeline.jsx`  
**Function:** `handleTeamUpdate()`  
**Location:** Before calling `updateProjectTeam()` API

This would provide immediate feedback before the API call, but backend validation is the source of truth.

---

## Testing Checklist

To validate the implementation works correctly:

1. ✅ **Test in Projects Tab - Update Team:**
   - Open a project
   - Click "Manage Team"
   - Add employee with 50% allocation
   - Try to add same employee to another project with 60% allocation (should fail)
   - Try to add same employee with 50% allocation (should succeed)

2. ✅ **Test Overlapping Dates:**
   - Employee allocated 50% from Jan 1 - Jan 31
   - Try to allocate same employee 60% from Jan 15 - Feb 15 (should fail - overlaps)
   - Try to allocate same employee 50% from Feb 1 - Feb 28 (should succeed - no overlap)

3. ✅ **Test Update Scenario:**
   - Employee has 50% allocation on Project A
   - Employee has 50% allocation on Project B
   - Update Project A allocation to 60% (should fail - would be 110%)
   - Update Project A allocation to 40% (should succeed - would be 90%)

4. ✅ **Test Ongoing Allocations (end_date = None):**
   - Employee has ongoing 50% allocation (no end date)
   - Try to add another 60% allocation (should fail)
   - Try to add another 50% allocation (should fail)

---

## Known Limitations

1. **Date Range Overlap:** The validation checks for date overlaps, but doesn't handle partial overlaps (e.g., employee 50% allocated for first half of month, 60% for second half = valid, but both for full month = invalid)

2. **Concurrent Updates:** If two users try to update allocations simultaneously, there's a race condition. Consider adding database-level constraints or optimistic locking.

3. **Historical Allocations:** The validation only checks overlapping date ranges. Past allocations don't affect current/future allocations.

---

## Future Enhancements

1. Add frontend validation for immediate feedback
2. Add database constraint to enforce 100% limit
3. Add warning when allocation is close to 100% (e.g., > 90%)
4. Add visualization showing current allocation percentage in UI
5. Add bulk validation for multiple employees at once
