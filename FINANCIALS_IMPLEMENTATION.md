# Financials & Domain Management Implementation

## Overview
This document describes the implementation of financial tracking and domain management features for the BenchCraft AI application, enabling HR/Project Allocation Managers to make data-driven decisions about resource allocation based on profitability and priority.

## New Features

### 1. Domain Management
- **Domains**: Business/Technical domains (FinTech, Healthcare, Retail, etc.)
- **Employee Domains**: Track employee expertise in specific domains with proficiency levels
- **Project Domains**: Link projects to required domains with priority levels

### 2. Rate Cards
- **Base Rate Cards**: Default hourly rates for employees
- **Domain-Specific Rates**: Higher rates for specific domain expertise (e.g., $100/hr for FinTech vs $50/hr base)
- **Historical Tracking**: Effective and expiry dates for rate changes
- **Rate Types**: BASE, DOMAIN_SPECIFIC, SKILL_SPECIFIC, PROJECT_SPECIFIC

### 3. Financial Metrics
- **Gross Margin Tracking**: Calculate and track gross margin percentage (target: 50%)
- **Allocation Financials**: Per-allocation financial tracking
- **Cost Calculations**: Employee hourly cost from monthly CTC
- **Revenue Tracking**: Estimated vs actual revenue and costs

### 4. Priority Scoring
- **Automated Priority Calculation**: Based on rate card values and bench duration
- **Priority Tiers**: CRITICAL, HIGH, MEDIUM, LOW
- **Alignment Optimization**: Higher rate card employees get priority for allocation

### 5. HR/Project Allocation Manager Report
- **Comprehensive Employee Report**: 
  - Employee name and status
  - Current project details
  - Project start and end dates
  - Alignment period
  - Current hourly pay (rate card)
  - Gross profit contribution
  - Gross margin percentage
  - Monthly profit estimates
  - Priority scores
  - Availability status
- **Proactive Planning**: Forecast availability at least 30 days in advance (configurable)
- **Filtering & Sorting**: By status, priority, margin, profit, or rate

## Database Schema Changes

### New Tables
1. **domains** - Domain master data
2. **employee_domains** - Employee domain expertise
3. **project_domains** - Project domain requirements
4. **rate_cards** - Rate card definitions
5. **financial_metrics** - Financial tracking
6. **allocation_financials** - Per-allocation financial details
7. **priority_scoring** - Priority calculation results
8. **project_rate_requirements** - Client rate expectations

### Modified Tables
- **allocations**: Added `rate_card_id` foreign key

## API Endpoints

### New Endpoint
- `GET /api/v1/hr/allocation-report`
  - Query Parameters:
    - `forecast_days` (default: 30): Number of days to look ahead
    - `include_bench` (default: true): Include employees on bench
  - Returns: Comprehensive allocation report with financial metrics

## Frontend Changes

### New Page
- **Allocation Report** (`/allocation-report`)
  - Interactive table with employee allocation details
  - Financial metrics display
  - Filtering and sorting capabilities
  - Summary cards with key metrics
  - Color-coded status indicators

### Navigation
- Added "Allocation Report" link to main navigation

## Usage

### Setting Up Rate Cards

1. Create domains first:
   ```python
   domain = Domain(
       domain_name="FinTech",
       domain_code="FINTECH",
       domain_type=DomainType.BUSINESS_DOMAIN
   )
   ```

2. Link employees to domains:
   ```python
   emp_domain = EmployeeDomain(
       emp_id=employee.id,
       domain_id=domain.id,
       proficiency=5,  # Expert level
       years_of_experience=5.0,
       is_primary_domain=True
   )
   ```

3. Create rate cards:
   ```python
   # Base rate
   base_rate = RateCard(
       emp_id=employee.id,
       hourly_rate=50.0,
       rate_type=RateType.BASE,
       effective_date=date.today()
   )
   
   # Domain-specific rate
   domain_rate = RateCard(
       emp_id=employee.id,
       domain_id=domain.id,
       hourly_rate=100.0,
       rate_type=RateType.DOMAIN_SPECIFIC,
       effective_date=date.today()
   )
   ```

### Viewing the Report

1. Navigate to `/allocation-report` in the frontend
2. Adjust forecast days (default: 30 days)
3. Filter by status (All, Allocated, Bench, Available)
4. Sort by Priority, Margin, Profit, or Rate
5. Review financial metrics and availability

## Calculation Logic

### Hourly Cost
```
hourly_cost = ctc_monthly / 160  # Assuming 160 working hours per month
```

### Gross Margin
```
gross_margin_percentage = ((billing_rate - cost_rate) / billing_rate) * 100
```

### Priority Score
Priority is calculated based on:
- Highest base rate card value
- Highest domain-specific rate value
- Days on bench
- Last allocation end date

## Database Migration

For existing databases, run:
```python
from tools.sql_db import SQLDatabaseTool
db_tool = SQLDatabaseTool()
db_tool.init_db()  # This will create new tables
```

**Note**: This will create new tables but won't migrate existing data. For production, consider using Alembic for proper migrations.

## Future Enhancements

1. **Automated Priority Calculation**: Background job to recalculate priority scores
2. **Rate Card Suggestions**: AI-powered rate card recommendations based on market data
3. **Margin Alerts**: Notifications when margins fall below target
4. **Historical Trends**: Track margin trends over time
5. **Export Functionality**: Export reports to Excel/PDF
6. **Bulk Operations**: Bulk rate card updates
7. **Rate Negotiation Workflow**: Track rate negotiations with clients

## Testing

To test the implementation:

1. **Backend**: 
   - Start the Flask server: `python backend/app.py`
   - Test endpoint: `GET http://localhost:5000/api/v1/hr/allocation-report`

2. **Frontend**:
   - Start the dev server: `npm run dev` (in frontend directory)
   - Navigate to `http://localhost:3000/allocation-report`

## Notes

- The system assumes 160 working hours per month for cost calculations
- Gross margin target is configurable (default: 50%)
- Rate cards support historical tracking with effective/expiry dates
- Priority scoring can be enhanced with additional factors
- The report supports proactive planning up to 90 days in advance
