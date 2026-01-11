# Allocation and Billable Percentage Update

## Overview

Updated the data model to support the critical use case where **allocation percentage** and **billable percentage** are two separate concepts. This allows for more accurate tracking of employee utilization and revenue generation.

## Key Changes

### 1. Allocation Model Updates (`backend/models.py`)

**New Fields:**
- `allocation_percentage` (Integer, 0-100%): How much of employee's total time is allocated to this project
- `billable_percentage` (Integer, 0-100%): How much of that allocation is billable to the client

**Deprecated Field:**
- `utilization` (Integer): Kept for backward compatibility, but should use `allocation_percentage` instead

### 2. Supported Scenarios

The model now supports all the requested scenarios:

#### Scenario 1: Multiple Projects with Underutilization
```
PERSON    PROJECT    ALLOCATION    BILLABLE
Roopak    Novartis   50%           100%
Roopak    PwC        40%           100%
Result: 90% utilized (10% underutilized)
```

#### Scenario 2: Single Project Full Utilization
```
PERSON    PROJECT    ALLOCATION    BILLABLE
Roopak    Novartis   100%          100%
Result: Fully utilized on single project
```

#### Scenario 3: Partial Allocation Across Projects
```
PERSON    PROJECT    ALLOCATION    BILLABLE
Roopak    Novartis   50%           50%
Roopak    PwC        50%           50%
Result: 100% allocated, but only 50% billable on each
```

#### Scenario 4: Replacement/Resignation Scenario
```
PERSON    PROJECT    ALLOCATION    BILLABLE
Roopak    Novartis   100%          50%
Result: Employee allocated 100% but only 50% billable (replacement being searched)
```

### 3. Financial Calculations

The `AllocationFinancial` model has been updated to properly calculate revenue based on billable percentage:

- **Revenue Calculation:**
  - `billed_hours = (total_hours × allocation_percentage × billable_percentage) / 10000`
  - `revenue = billing_rate × billed_hours`

- **Cost Calculation:**
  - `utilized_hours = (total_hours × allocation_percentage) / 100`
  - `cost = cost_rate × utilized_hours`

- **Example:**
  - 160 hours/month, 50% allocation, 100% billable = 80 billable hours
  - 160 hours/month, 50% allocation = 80 utilized hours

### 4. Updated Files

1. **`backend/models.py`**
   - Added `allocation_percentage` and `billable_percentage` to `Allocation` model
   - Updated `AllocationFinancial` model with better documentation
   - Added comprehensive docstrings explaining the concepts

2. **`backend/seed.py`**
   - Updated to use new fields when creating allocations
   - Added realistic scenarios (partial allocations, replacement scenarios)

3. **`backend/routes/employees.py`**
   - Updated to return both `allocation_percentage` and `billable_percentage`
   - Maintains backward compatibility with `utilization` field

4. **`backend/routes/hr.py`**
   - Updated allocation report to include new fields

5. **`backend/routes/projects.py`**
   - Updated project view to use new fields

6. **`backend/migrate_add_allocation_billable_percentage.py`**
   - New migration script to add columns to existing database

## Database Migration

To apply the changes to an existing database:

```bash
cd backend
python migrate_add_allocation_billable_percentage.py
```

The migration will:
1. Add `allocation_percentage` column (default: 100)
2. Add `billable_percentage` column (default: 100)
3. Migrate existing `utilization` values to `allocation_percentage` if they exist
4. Set `billable_percentage` to 100 for all existing records

## API Response Changes

Allocation objects now return:
```json
{
  "allocation_percentage": 50,
  "billable_percentage": 100,
  "utilization": 50  // Backward compatibility
}
```

## Backward Compatibility

- The `utilization` field is still returned in API responses for backward compatibility
- Existing code reading `utilization` will continue to work
- New code should use `allocation_percentage` and `billable_percentage`

## Next Steps

1. Run the migration script
2. Restart the Flask server
3. Update frontend components to display both allocation and billable percentages
4. Consider adding validation to ensure allocation percentages don't exceed 100% across all active allocations (optional business rule)

## Business Logic Notes

- **Total Utilization**: Sum of `allocation_percentage` across all active allocations for an employee
  - < 100% = Underutilized
  - = 100% = Fully utilized
  - > 100% = Overallocated (should be flagged)

- **Revenue Impact**: Only `billable_percentage` of the allocation generates revenue
  - Example: 50% allocation, 100% billable = 50% of time generates revenue
  - Example: 100% allocation, 50% billable = 50% of time generates revenue (replacement scenario)
