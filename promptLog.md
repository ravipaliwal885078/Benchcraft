# Prompt Log - BenchCraft AI Development

This file maintains a log of all user prompts and requirements during the development and enhancement of the BenchCraft AI application.

---

## 2026-01-11 - Financials & Domain Management Extension

### Initial Requirement: Data Model Extension for Financials

**Original Prompt:**
> This is the data model. I need to extend the data model for financials part. For providing the updated DDL, please maintain the same consistency. The use case is: While managing a resource, a company maintains a gross margin of lets say 50%. For every resource, when he is billed on a project, a certain amount of payable is received on his behalf based on his skills and experience known as rate card. That rate card is what defines what the employee is giving the company. Based on which the package of the employee is calculated, and where his interests lies when it comes to alignment managemnt for best returns. This should also take priority into consideration like, if there is an employee A (rate card 50$ per hour) and employee B (80$ per hour). Based on this, the priority becomes that we align employee B as soon as he gets free or his project is ending. Now it should also take into consideration that if lets say another project is coming and is willing to pay 100$ per hour for employee A since his domain is related to the needs of the latest project. For this, we will have to manage the domains of the employee as well which currently is not in the data model. Please make these amendements. Only share the delta of the structure.

**Deliverable**: Provide only the delta/extensions to the existing data model structure, maintaining consistency with the current schema design.

---

### Implementation Request: HR/Project Allocation Manager Report

**Original Prompt:**
> Here's a clearer, more professional rephrased version of your prompt: An HR (Project Allocation Manager) report is generated containing details such as employee name, current project, project start and end dates, employee project alignment period, current hourly pay, gross profit contribution, and related metrics. This report provides insights into each employee's profitability and availability, enabling proactive planning at least one month in advance to maximize resource utilization and returns. according to the plan, update in the existing application to have the new features discussed.

**Implementation Scope**: Integrate this feature into the existing application architecture, ensuring it leverages the newly implemented financial and domain management data models.

---

### Error Resolution: Database Schema Migration

**Original Prompt:**
> (sqlite3.OperationalError) no such column: allocations.rate_card_id [SQL: SELECT allocations.id AS allocations_id, allocations.emp_id AS allocations_emp_id, allocations.proj_id AS allocations_proj_id, allocations.start_date AS allocations_start_date, allocations.end_date AS allocations_end_date, allocations.billing_rate AS allocations_billing_rate, allocations.is_revealed AS allocations_is_revealed, allocations.utilization AS allocations_utilization, allocations.rate_card_id AS allocations_rate_card_id FROM allocations WHERE allocations.emp_id = ? AND allocations.start_date <= ? AND (allocations.end_date IS NULL OR allocations.end_date >= ?) LIMIT ? OFFSET ?] [parameters: (1, '2026-01-11', '2026-01-11', 1, 0)] (Background on this error at: https://sqlalche.me/e/20/e3q8) giving this error now. please update

**Resolution**: Created migration script to add `rate_card_id` column to allocations table.

---

### Error Resolution: Syntax Error in HR Routes

**Original Prompt:**
> Traceback (most recent call last): File "D:\GIT - BenchCraft\backend\app.py", line 16, in <module> from routes import resources, projects, dashboard, employees, documents, hr, rfp, search, training, risk, monitor File "D:\GIT - BenchCraft\backend\routes\hr.py", line 235 upcoming_allocations = session.query(Allocation).filter( ^^^^^^^^^^^^^^^^^^^^ SyntaxError: expected 'except' or 'finally' block getting this error now

**Resolution**: Fixed try/except block structure in HR routes file.

---

### Maintenance Request: Prompt Logging

**Original Prompt:**
> For all the earlier prompts and upcoming prompts, maintain a file promptLog.md in the root folder and always append the file with the prompts that i provide while enhancing its language.

**Resolution**: Created and maintaining `promptLog.md` file in root directory with all prompts and requirements.

---

## 2026-01-11 - Employees Page Enhancement

### Requirement: Comprehensive Employee Grid with Enhanced Actions

**Original Prompt:**
> Lets start with updating each and every page: Employees: 1: List of employees is not visible. 2: Make a employees grid, while mentioning details like his personal details, project allocation details, skills, status, rates. Add actions like add a new employee on top. Also, for each employee add actions for Edit Employee, Add Skills, and Raise Risk. For each action, if needed any DB changes, please update and share the DB first and then lets commit to it.

**Implementation Approach**: 
- First, review and document all required database changes
- Share the database migration plan for approval
- Then proceed with frontend and backend implementation
- Ensure all actions are functional and properly integrated with the existing system

**Implementation Status:**
✅ **COMPLETED**

1. **Database Changes:**
   - Added RiskRegister model to `backend/models.py` with all required enums (RiskType, RiskSeverity, RiskStatus)
   - Updated Employee and Project models with risk relationships
   - Documented all changes in `DB_CHANGES_EMPLOYEES_PAGE.md`

2. **Backend Enhancements:**
   - Enhanced `/api/v1/employees/` GET endpoint to include current allocation, skills, and rate card data
   - Created new routes for skills and risk management in `backend/routes/employees_skills_risks.py`
   - Registered new routes in `backend/app.py`

3. **Frontend Enhancements:**
   - Updated Employees page to use EmployeeList component
   - Completely rewrote EmployeeList with enhanced grid view showing all required details
   - Created AddSkillsModal and RaiseRiskModal components
   - Added action buttons: Add Employee, Edit, Add Skills, Raise Risk

**Next Steps:**
- Run database initialization to create RISK_REGISTER table
- Test all new functionality

---

### Bug Fix: RoleLevel Enum Access

**Original Prompt:**
> while adding employee, getting the below error on the role level dropdown. 'MID' is not a valid RoleLevel please check and update the model

**Root Cause:**
- The RoleLevel enum is defined with member names (JR, MID, SR, LEAD, PRINCIPAL) and string values ("JR", "MID", "SR", "LEAD", "PRINCIPAL")
- The frontend sends the member name (e.g., "MID")
- The backend was using `RoleLevel("MID")` which searches for a value of "MID"
- Python's Enum requires square brackets `[]` to access by member name: `RoleLevel["MID"]`

**Resolution:**
- Created `parse_role_level()` helper function for robust enum parsing
- Updated all routes to use the helper function
- Changed `role_level` column to store as plain string instead of enum
- Updated seed.py to store enum values as strings

**Files Modified:**
- `backend/routes/employees.py` - Fixed enum access and storage
- `backend/models.py` - Changed role_level to String(20)
- `backend/seed.py` - Updated to store strings

---

## 2026-01-11 - Allocation and Billable Percentage Enhancement

### Requirement: Separate Allocation and Billable Concepts

**Original Prompt:**
> does it support the use case where a single employee is allocated to multiple projects. The allocation and billable are 2 different concepts. For an example Project Manager as an employee is an entity which is always operating on multiple projects. He is allocated 50% lets say and to client he is billable 100%. So the scenarios are:
> 
> PERSON,PROJECT,ALLOCATION,BILLABLE
> Roopak,Novartis,50%,100%
> Roopak,PwC,40%,100%
> If this is the case then Roopak is underutilized by 10%.
> 
> PERSON,PROJECT,ALLOCATION,BILLABLE
> Roopak,Novartis,100%,100%
> Fully utilized on a single project
> 
> PERSON,PROJECT,ALLOCATION,BILLABLE
> Roopak,Novartis,50%,50%
> Roopak,PwC,50%,50%
> Partially divided in 2 projects
> 
> PERSON,PROJECT,ALLOCATION,BILLABLE
> Roopak,Novartis,100%,50%
> Scenario where the user is either on Resignation, and replacement is being searched. Hence with alignment with client, its at 50%.
> 
> If it does not handle, then update the data model in a way that it should. Since the allocation percent and defines full utilization and billable defines how much money he is able to generate.

**Implementation:**
- Updated `Allocation` model to include `allocation_percentage` and `billable_percentage` fields
- `allocation_percentage`: How much of employee's time is allocated to this project (0-100%)
- `billable_percentage`: How much of that allocation is billable to the client (0-100%)
- Updated `AllocationFinancial` model with documentation on revenue calculations
- Created migration script `migrate_add_allocation_billable_percentage.py`
- Updated all routes to return both fields with backward compatibility
- Updated frontend views (EmployeeView, ProjectView, EmployeeList, AllocationReport) to display both percentages

**Files Modified:**
- `backend/models.py` - Added new fields to Allocation model
- `backend/routes/employees.py` - Updated to return new fields
- `backend/routes/hr.py` - Updated allocation report
- `backend/routes/projects.py` - Updated project team view
- `backend/seed.py` - Updated to use new fields
- `frontend/src/pages/EmployeeView.jsx` - Display allocation and billable percentages
- `frontend/src/pages/ProjectView.jsx` - Display for team members
- `frontend/src/pages/EmployeeList.jsx` - Display in employee cards
- `frontend/src/pages/AllocationReport.jsx` - Display in report

**Documentation:**
- Created `ALLOCATION_BILLABLE_UPDATE.md` with comprehensive explanation

---

### Requirement: Full Width Page Layout

**Original Prompt:**
> There in not full width of page make it full width page the main content page of overall application

**Implementation:**
- Updated `frontend/src/App.jsx` to remove `max-w-7xl mx-auto` constraint from main content
- Changed to `w-full` for full width layout
- Maintained padding for proper spacing

**Files Modified:**
- `frontend/src/App.jsx` - Updated main content container

---

### Requirement: Allocation Table Explanation

**Original Prompt:**
> explain the allocation and related tables.

**Response:**
Provided comprehensive explanation of Allocation model and related tables including:
- Allocation table structure and relationships
- Employee, Project, RateCard, AllocationFinancial tables
- Domain, EmployeeDomain, ProjectDomain tables
- PriorityScoring, BenchLedger tables
- Data flow examples and business logic

---

### Requirement: Update Frontend Views with Allocation/Billable Percentages

**Original Prompt:**
> Update these details at the areas from where it makes sense. Like on Resource/Employee view where all his details are displayed. Projects page to be updated to display the employees working on the project and their allocation and billable amounts as well.

**Implementation:**
- Updated EmployeeView to show allocation and billable percentages in current allocation banner, timeline, and project history
- Updated ProjectView to display both percentages for each team member
- Updated EmployeeList to show percentages in current allocation cards
- Updated AllocationReport to display both percentages in project allocation column
- Added visual indicators (📊 for allocation, 💰 for billable, ⚠️ for partial billing scenarios)

**Files Modified:**
- `frontend/src/pages/EmployeeView.jsx` - Added allocation/billable display
- `frontend/src/pages/ProjectView.jsx` - Added for team members
- `frontend/src/pages/EmployeeList.jsx` - Added in employee cards
- `frontend/src/pages/AllocationReport.jsx` - Added in report

---

## 2026-01-11 - Projects Tab Enhancements

### Requirement: Project Management Actions

**Original Prompt:**
> Projects Tab:
> 1: When clicking on a Project Name, The details of the project will be displayed. The functionality is already created on "View Details"
> 2: Actions to be created:
> 2.1: Update Project
> 2.2: Add/Update Project Team (employees) in grid view with allocation % for every team member that we can update from a single screen

**Implementation:**
- Made project names clickable to navigate to project details
- Added "Update Project" button with modal for editing project details
- Added "Manage Team" button with grid modal for managing team allocations
- Created backend endpoints:
  - `POST /api/v1/projects` - Create new project
  - `PUT /api/v1/projects/<id>` - Update project
  - `POST /api/v1/projects/<id>/team` - Update team allocations
  - `DELETE /api/v1/projects/<id>/team/<allocation_id>` - Remove team member
- Team management modal supports:
  - Adding new team members
  - Updating allocation_percentage and billable_percentage
  - Setting billing rates
  - Removing team members
  - Bulk save functionality

**Files Modified:**
- `backend/routes/projects.py` - Added create, update project and team management endpoints
- `frontend/src/services/api.js` - Added API functions for project operations
- `frontend/src/pages/Pipeline.jsx` - Added modals and action buttons

---

### Bug Fix: Project View 500 Error

**Original Prompt:**
> Error. Its saying project not found. Please check and update.

**Root Cause:**
- Code was trying to access `alloc.employee.role_level.value` but `role_level` is stored as a string, not an enum
- Strings don't have a `.value` attribute, causing AttributeError and 500 error

**Resolution:**
- Updated `get_project` endpoint to use `alloc.employee.role_level` directly (string)
- Removed `.value` access since role_level is already a string in the database

**Files Modified:**
- `backend/routes/projects.py` - Fixed role_level access in get_project endpoint

---

### Maintenance Request: Update Prompt Log

**Original Prompt:**
> update the promptLog.md file from where you left and keep updating after each prompt executed. Also, remove **Enhanced Description:** and do not add them moving forward.

**Implementation:**
- Updated promptLog.md with all recent changes from allocation/billable enhancement onwards
- Removed all "Enhanced Description" sections from existing entries
- Will continue updating after each prompt going forward without adding enhanced descriptions

---

### UI Updates: Navigation and Tab Changes

**Original Prompt:**
> 1: Remove Canvas Tab
> 2: Rename marketplace tab to "Talent Search"
> 3: Project Tab:- The page heading contains the word Pipeline still. Please update the text to Projects.

**Implementation:**
- Removed Canvas tab from navigation menu and routes
- Renamed "Marketplace" tab to "Talent Search" in navigation
- Updated Pipeline page heading from "Pipeline" to "Projects"
- Updated Pipeline page subtitle to "Manage active projects and pipeline"

**Files Modified:**
- `frontend/src/App.jsx` - Removed Canvas import, route, and navigation link; renamed Marketplace to Talent Search
- `frontend/src/pages/Pipeline.jsx` - Updated page heading and subtitle

---

### Requirement: Allocation Percentage Validation

**Original Prompt:**
> Update the validations for employee allocation_percentage. This will never cross 100% for a specific employee. See the employee "Roopak Bhama". He is allocated with 150%. When acting on Project -> Update team, and anywhere else, make sure an employee never crosses the 100% mark. Also, provide me list from where i can do these changes for me to validate.

**Implementation:**
- Created validation utility function `validate_allocation_percentage()` in `backend/utils/allocation_validator.py`
- Validates that total allocation_percentage across all overlapping date ranges for an employee never exceeds 100%
- Added validation to all allocation creation/update endpoints:
  1. `POST /api/v1/projects/<id>/team` - Project team management
  2. `POST /api/v1/employees/allocate` - Employee allocation
  3. `POST /api/v1/allocate` - Resource allocation
  4. `SQLDatabaseTool.create_allocation()` - Agent allocation tool
- Validation checks for date range overlaps and sums allocation percentages
- Returns clear error messages with employee name and current total

**Files Modified:**
- `backend/utils/allocation_validator.py` - New validation utility (created)
- `backend/utils/__init__.py` - Package init file (created)
- `backend/routes/projects.py` - Added validation to update_project_team
- `backend/routes/employees.py` - Added validation to allocate_resource
- `backend/routes/resources.py` - Added validation to allocate_resource
- `backend/tools/sql_db.py` - Added validation to create_allocation

**Documentation:**
- Created `ALLOCATION_VALIDATION_LOCATIONS.md` with comprehensive list of all validation locations and testing instructions

---

### Enhancement: Frontend Validation and Project End Date Sync

**Original Prompt:**
> When adding allocation percentage in grid for action "Project -> Manage Team", It should give validation and does not let the user submit if the allocation percentage of an employee crosses 100% for a given date range. Also, if a project does not have an end date, and if it is updated, all the team members "End Date" will also be same as the updated project's end date. From any action, the total allocation percentage of the employee should not cross 100%. During allocation, it should confirm in the DB what the current state of employee is.

**Implementation:**
- Added frontend validation in `handleTeamUpdate()` that checks allocation percentages before submission
- Created new API endpoint `POST /api/v1/employees/<id>/allocation-check` to query current DB state for validation
- Frontend validation calls backend check endpoint to verify current allocation state from database
- Prevents form submission if any employee would exceed 100% allocation
- Updated project update endpoint to automatically sync team member end dates when project end date is updated
- If project end_date is set and team member has no end_date or end_date is after project end_date, it gets updated to match project end_date
- Backend validation already queries current DB state (confirmed)

**Files Modified:**
- `backend/routes/projects.py` - Added allocation-check endpoint, updated project update to sync team end dates
- `frontend/src/pages/Pipeline.jsx` - Added frontend validation in handleTeamUpdate
- `frontend/src/services/api.js` - Added checkEmployeeAllocation API function

**Validation Flow:**
1. User fills allocation percentages in Manage Team modal
2. On "Save" click, frontend validates each employee by calling backend check endpoint
3. Backend queries current DB state for employee's existing allocations
4. Calculates total allocation including new/updated allocation
5. If > 100%, shows error and prevents submission
6. If valid, proceeds with team update (backend validates again as safety check)

---

### Bug Fix: Allocation Report Updates and Validation

**Original Prompt:**
> When I update the project, its team, the updated details are not displayed on Allocation Report. Also display the allocation percentage of the employees. Validation for allocation percentage is still not working. please check.

**Issues Fixed:**
1. **Allocation Report not refreshing** - Added "Refresh Report" button to manually reload data
2. **Allocation percentage not displayed** - Added dedicated "Allocation %" column in the report table
3. **Backend allocation_percentage access** - Fixed helper functions to properly access allocation_percentage field
4. **Validation not working** - Enhanced frontend validation with better error handling and range checks

**Implementation:**
- Added helper functions `_get_allocation_percentage()` and `_get_billable_percentage()` in `backend/routes/hr.py` to safely access allocation fields
- Added "Refresh Report" button in Allocation Report header
- Added dedicated "Allocation %" column in Allocation Report table showing allocation and billable percentages
- Enhanced frontend validation in `handleTeamUpdate()` with:
  - Range validation (0-100%) before API call
  - Better error handling for API failures
  - More descriptive error messages with employee names

**Files Modified:**
- `backend/routes/hr.py` - Added helper functions for safe allocation_percentage access
- `frontend/src/pages/AllocationReport.jsx` - Added refresh button and Allocation % column
- `frontend/src/pages/Pipeline.jsx` - Enhanced validation with better error handling

---

### UX Improvement: Inline Grid Validation

**Original Prompt:**
> The validation should be displayed on the grid and not on the popup.

**Implementation:**
- Removed alert popup for validation errors
- Added inline validation errors displayed directly in the grid below each allocation_percentage input
- Validation runs on blur of the allocation_percentage field
- Errors are shown with red border and error message text
- Save button is disabled when validation errors exist
- Save button shows error count when disabled
- Validation errors clear when user modifies the field

**Features:**
- Real-time validation feedback in the grid
- Visual indicators (red border, error text) for invalid inputs
- "Validating..." indicator while checking with backend
- Save button disabled state with error count
- Errors clear automatically when user fixes the issue

**Files Modified:**
- `frontend/src/pages/Pipeline.jsx` - Added inline validation with state management and grid display

---

### Feature: Budget Consumed, Back Button Fix, and Performance Feedback Forms

**Original Prompt:**
> When we are on Projects Tab, The cards displaying the project details should also show the Budget Consumed beside the Budget. Also, when we are on Projects Summary/Dashboard, the back button link's title is "Back to Pipeline". It should be back to projects. Add 2 actions: 1: Performance Feedback - Project: Basic feedback form for Project Team 2: Performance Feedback - Employee: Basic feedback form for Employee. Once these details are captured, also show them on Project Summary and Employee Summary under Feedbacks section which is already created.

**Implementation:**
1. **Budget Consumed in Project Cards:**
   - Updated `get_projects()` endpoint to calculate budget consumed from allocations
   - Added `budget_consumed` field to project list response
   - Updated Pipeline.jsx to display budget consumed beside budget in project cards

2. **Back Button Fix:**
   - Changed "Back to Pipeline" to "Back to Projects" in ProjectView.jsx

3. **Performance Feedback - Project:**
   - Created `POST /api/v1/projects/<id>/feedback` endpoint
   - Added feedback form modal in ProjectView with:
     - Team member selection dropdown
     - Star rating (1-5)
     - Feedback text area
     - Tags input (comma-separated)
   - Added "Add Feedback" button in Performance Feedback section
   - Feedbacks automatically displayed in existing feedback section

4. **Performance Feedback - Employee:**
   - Created `POST /api/v1/employees/<id>/feedback` endpoint
   - Added feedback form modal in EmployeeView with:
     - Project selection dropdown
     - Star rating (1-5)
     - Feedback text area
     - Tags input (comma-separated)
   - Added "Add Feedback" button in Performance Feedback tab
   - Feedbacks automatically displayed in existing feedback section

**Files Modified:**
- `backend/routes/projects.py` - Added budget_consumed calculation and feedback endpoint
- `backend/routes/employees.py` - Added feedback endpoint
- `frontend/src/pages/Pipeline.jsx` - Added budget consumed display
- `frontend/src/pages/ProjectView.jsx` - Fixed back button, added feedback form
- `frontend/src/pages/EmployeeView.jsx` - Added feedback form
- `frontend/src/services/api.js` - Added createProjectFeedback and createEmployeeFeedback functions

**Budget Calculation:**
- Budget consumed = Sum of (billing_rate × 160 hours × allocation_percentage × billable_percentage) for all allocations
- This is a simplified monthly estimate - in production, would calculate based on actual hours worked

---

### Feature: Update Team Member Button in Project Summary

**Original Prompt:**
> On each project summary, under section Team Members, add a button for updating the team member.

**Implementation:**
- Added "Update" button to each team member card in ProjectView
- Created update modal for individual team member editing
- Modal includes:
  - Start Date and End Date fields
  - Allocation % and Billable % fields
  - Billing Rate field
  - Real-time validation for allocation percentage (prevents >100% total)
  - Error display for validation failures
- Uses same validation logic as Manage Team modal
- Updates team member via updateProjectTeam API

**Files Modified:**
- `frontend/src/pages/ProjectView.jsx` - Added update button, modal, and validation logic

---

### Feature: Manage Team Action in Project Summary

**Original Prompt:**
> Under Projects, Section "Team Members", just like Performance Feedback action, add action to add team members so that it gets easy for the user to update the team members just like how he can do from Projects card "Manage Team". This action is already created. just plug it on Project summary under team members section

**Implementation:**
- Added "Manage Team" button in Team Members section header (similar to "Add Feedback" button)
- Integrated the full Manage Team modal functionality from Pipeline.jsx into ProjectView
- Modal includes:
  - Add Team Member functionality
  - Grid view for all team members with editable fields
  - Inline validation for allocation percentages
  - Remove team member functionality
  - Save/Cancel buttons with error count display
- Reuses same validation logic and API endpoints as Pipeline Manage Team modal
- Automatically reloads project data after team updates

**Files Modified:**
- `frontend/src/pages/ProjectView.jsx` - Added Manage Team button, modal, and all team management functions

---

### Bug Fix: Project View 500 Error - Missing Database Columns

**Original Prompt:**
> The project dashboard after clicking on its name is not visible. Its throwing an error.

**Root Cause:**
- The `get_project` endpoint was trying to access `allocation_percentage` and `billable_percentage` columns
- These columns may not exist in the database if the migration hasn't been run yet
- SQLAlchemy fails when trying to query columns that don't exist in the database schema

**Resolution:**
- Added comprehensive error handling in `get_project` endpoint
- Wrapped allocation processing in try-except blocks
- Added fallback to query allocations directly if relationship access fails
- Safely handles missing columns by using defaults (100% for both percentages)
- Falls back to `utilization` field if `allocation_percentage` doesn't exist

**Files Modified:**
- `backend/routes/projects.py` - Added error handling for missing database columns

**Next Steps:**
- Run the migration script `migrate_add_allocation_billable_percentage.py` to add the new columns to the database
- After migration, the endpoint will work with the new fields

---

### UI Updates: Navigation and Tab Changes

**Original Prompt:**
> 1: Remove Canvas Tab
> 2: Rename marketplace tab to "Talent Search"
> 3: Project Tab:- The page heading contains the word Pipeline still. Please update the text to Projects.

**Implementation:**
- Removed Canvas tab from navigation menu and routes
- Renamed "Marketplace" tab to "Talent Search" in navigation
- Updated Pipeline page heading from "Pipeline" to "Projects"
- Updated Pipeline page subtitle to "Manage active projects and pipeline"

**Files Modified:**
- `frontend/src/App.jsx` - Removed Canvas import, route, and navigation link; renamed Marketplace to Talent Search
- `frontend/src/pages/Pipeline.jsx` - Updated page heading and subtitle

---
