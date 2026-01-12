# Data Model Extension: Shadow Resource Tracking and Internal vs Client Allocation

## Overview

Extended the BenchCraft AI data model to support:
1. **Shadow Resource Tracking**: Trainee/mentoring relationships where resources shadow primary employees
2. **Internal vs Client Allocation Differentiation**: Track actual internal work vs what's reported to clients

## Changes Made

### 1. Allocation Model Extensions (`backend/models.py`)

#### New Fields Added:

```python
# Shadow Resource Tracking
is_trainee = Column(Boolean, default=False, nullable=False)
# Indicates if this allocation is for a trainee/shadow resource
# Trainees are NEVER billable to the client

mentoring_primary_emp_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
# References the employee.id of the primary resource being shadowed
# NULL if is_trainee=False
# Must reference an active allocation on the same project if is_trainee=True

# Internal vs Client Allocation Tracking
internal_allocation_percentage = Column(Integer, nullable=False, default=100)
# Actual percentage of employee's time spent on this project internally
# Range: 0-100%
# Can be LESS than allocation_percentage (over-billing scenario)
# Can be MORE than allocation_percentage (under-billing scenario)
```

#### New Relationships:

**In Employee model:**
```python
trainee_allocations = relationship("Allocation", 
                                   foreign_keys="Allocation.mentoring_primary_emp_id",
                                   back_populates="mentoring_primary")
```

**In Allocation model:**
```python
mentoring_primary = relationship("Employee", 
                                foreign_keys=[mentoring_primary_emp_id],
                                back_populates="trainee_allocations")
```

### 2. Updated Financial Calculation Formulas

#### For PRIMARY Resources (is_trainee=False):
- **Revenue Calculation:**
  - `billed_hours = (total_hours × allocation_percentage × billable_percentage) / 10000`
  - `revenue = billing_rate × billed_hours`
  
- **Cost Calculation:**
  - `cost_hours = (total_hours × internal_allocation_percentage) / 100`
  - `cost = cost_rate × cost_hours`
  - **Note:** Cost is based on ACTUAL internal work, not client-reported allocation

- **Gross Margin:**
  - `gross_margin = (revenue - cost) / revenue × 100 if revenue > 0 else 0`

#### For TRAINEE Resources (is_trainee=True):
- **Revenue Calculation:**
  - `revenue = $0` (trainees are NEVER billable)
  - `billed_hours = 0`

- **Cost Calculation:**
  - `cost_hours = (total_hours × internal_allocation_percentage) / 100`
  - `cost = cost_rate × cost_hours`
  - Pure training investment (cost center)

### 3. Validation Rules

Added comprehensive validation functions in `backend/models.py`:

1. **is_trainee validation:**
   - If `is_trainee=True`, then `billable_percentage` MUST be 0
   - If `is_trainee=True`, then `mentoring_primary_emp_id` MUST NOT be NULL
   - If `is_trainee=True`, then `billing_rate` should be 0 or NULL

2. **mentoring_primary_emp_id validation:**
   - Must reference a valid employee ID
   - Cannot reference self (emp_id)

3. **internal_allocation_percentage validation:**
   - Must be between 0 and 100
   - Can be different from `allocation_percentage` (over/under-billing scenarios)

### 4. Example Query Functions

Added helper functions in `backend/models.py`:

- `get_trainees_for_project(session, project_id)`: Find all trainee/shadow resources for a project
- `get_employee_financial_summary(session, employee_id)`: Calculate total cost vs revenue for an employee
- `get_over_billed_allocations(session, project_id)`: Identify over-billed allocations (efficiency scenarios)
- `get_under_billed_allocations(session, project_id)`: Identify under-billed allocations
- `get_shadow_resources_and_mentors(session, project_id)`: Find shadow resources and their mentors

### 5. Updated Seed Script (`backend/seed.py`)

- Added logic to create trainee allocations (5% chance)
- Added logic to create over-billing/under-billing scenarios (20% chance)
- Updated financial calculations to use `internal_allocation_percentage` for cost
- Trainees automatically find primary resources to shadow on the same project

### 6. Migration Script (`backend/migrate_add_shadow_and_internal_allocation.py`)

Created migration script to:
- Add new columns to existing database
- Set default values for existing records:
  - `is_trainee`: False (all existing allocations are primary)
  - `mentoring_primary_emp_id`: NULL
  - `internal_allocation_percentage`: Same as `allocation_percentage` (1:1 initially)
- Create indexes for performance

## Example Scenarios

### Scenario 1: Standard Allocation
**Employee:** John Doe  
**Project:** Novartis  
- `is_trainee`: False
- `internal_allocation_percentage`: 50%
- `allocation_percentage`: 50% (reported to client)
- `billable_percentage`: 100%
- `billing_rate`: $150/hr
- `total_hours`: 160/month

**Calculations:**
- Billed hours: (160 × 50 × 100) / 10000 = 80 hours
- Revenue: $150 × 80 = $12,000
- Cost hours: (160 × 50) / 100 = 80 hours
- Cost: (CTC hourly) × 80 hours

### Scenario 2: Over-billed Resource (Efficiency)
**Employee:** Jane Smith  
**Project:** PwC  
- `is_trainee`: False
- `internal_allocation_percentage`: 25% (actually works 25%)
- `allocation_percentage`: 75% (client billed for 75%)
- `billable_percentage`: 100%
- `billing_rate`: $200/hr
- `total_hours`: 160/month

**Calculations:**
- Billed hours: (160 × 75 × 100) / 10000 = 120 hours
- Revenue: $200 × 120 = $24,000
- Cost hours: (160 × 25) / 100 = 40 hours
- Cost: (CTC hourly) × 40 hours
- **Higher margin due to efficiency** (more revenue, less cost)

### Scenario 3: Trainee/Shadow Resource
**Employee:** Alex Trainee  
**Project:** Novartis  
- `is_trainee`: True
- `mentoring_primary_emp_id`: 123 (John Doe's employee ID)
- `internal_allocation_percentage`: 100%
- `allocation_percentage`: 0% (not reported to client)
- `billable_percentage`: 0%
- `total_hours`: 160/month

**Calculations:**
- Billed hours: 0 (trainees never billable)
- Revenue: $0
- Cost hours: (160 × 100) / 100 = 160 hours
- Cost: (CTC hourly) × 160 hours
- **Pure training investment** (cost center)

## Database Migration

To apply the changes to an existing database:

```bash
cd backend
python migrate_add_shadow_and_internal_allocation.py
```

The migration will:
1. Add `is_trainee` column (Boolean, default=False)
2. Add `mentoring_primary_emp_id` column (Integer, nullable)
3. Add `internal_allocation_percentage` column (Integer, default=100)
4. Set default values for existing records
5. Create indexes for performance

## Backward Compatibility

- All existing allocations will have:
  - `is_trainee = False` (primary resources)
  - `mentoring_primary_emp_id = NULL`
  - `internal_allocation_percentage = allocation_percentage` (1:1 relationship)
- Existing code will continue to work as `internal_allocation_percentage` defaults to same as `allocation_percentage`
- No breaking changes to existing API responses

## Files Modified

1. **`backend/models.py`**
   - Extended `Allocation` model with new fields
   - Added relationships in `Employee` and `Allocation`
   - Updated `AllocationFinancial` docstring with new formulas
   - Added validation functions
   - Added example query functions

2. **`backend/seed.py`**
   - Updated allocation creation to use new fields
   - Added trainee allocation generation
   - Updated financial calculations

3. **`backend/migrate_add_shadow_and_internal_allocation.py`** (NEW)
   - Migration script for database schema changes

## Next Steps

1. Run the migration script to update existing databases
2. Update any financial calculation code to use `internal_allocation_percentage` for cost calculations
3. Update frontend/API to support new fields in forms and displays
4. Consider adding UI for:
   - Marking allocations as trainee/shadow
   - Setting internal vs client allocation percentages
   - Viewing shadow resource relationships

## Validation

The model includes SQLAlchemy event listeners that automatically validate:
- Trainee rules (billable_percentage = 0, mentoring_primary_emp_id required)
- Range validations (0-100% for all percentage fields)
- Self-reference prevention (trainee cannot mentor themselves)

Validation errors will raise `ValueError` with descriptive messages before insert/update operations.
