# Database Changes for Employees Page Enhancement

## Overview
This document outlines the database schema changes required to support the enhanced Employees page with risk management and skills functionality.

## Required Changes

### 1. Risk Register Table (MISSING - Needs to be added)

The RISK_REGISTER table is defined in the ER diagram but not implemented in models.py. This table is required for the "Raise Risk" functionality.

**Table: risk_register**

```sql
CREATE TABLE risk_register (
    id INTEGER PRIMARY KEY,
    emp_id INTEGER NOT NULL,
    project_id INTEGER,
    risk_type VARCHAR(50) NOT NULL,  -- NOTICE_PERIOD, CRITICAL_ROLE, SINGLE_POINT_FAILURE, SKILL_GAP, PERFORMANCE
    severity VARCHAR(20) NOT NULL,     -- LOW, MEDIUM, HIGH, CRITICAL
    description TEXT,
    mitigation_plan TEXT,
    mitigation_owner_emp_id INTEGER,
    identified_date DATE NOT NULL,
    target_resolution_date DATE,
    status VARCHAR(20) DEFAULT 'OPEN',  -- OPEN, IN_PROGRESS, MITIGATED, CLOSED, ACCEPTED
    FOREIGN KEY (emp_id) REFERENCES employees(id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (mitigation_owner_emp_id) REFERENCES employees(id)
);
```

**Enums Required:**
- RiskType: NOTICE_PERIOD, CRITICAL_ROLE, SINGLE_POINT_FAILURE, SKILL_GAP, PERFORMANCE
- RiskSeverity: LOW, MEDIUM, HIGH, CRITICAL
- RiskStatus: OPEN, IN_PROGRESS, MITIGATED, CLOSED, ACCEPTED

### 2. Skills Table (MISSING - Needs to be added)

The ER diagram shows a SKILLS table, but currently skills are stored as strings in employee_skills. For better skill management, we should add a SKILLS master table.

**Table: skills**

```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),  -- TECHNICAL, DOMAIN, SOFT_SKILL, TOOL, FRAMEWORK, LANGUAGE
    description TEXT,
    is_certifiable BOOLEAN DEFAULT 0,
    market_demand_score INTEGER DEFAULT 5  -- 1-10
);
```

**Note**: This is optional but recommended for better skill standardization.

### 3. Employee Model Updates

**No changes needed** - The Employee model already has all required fields.

### 4. Allocation Model Updates

**Already updated** - The `rate_card_id` column has been added (migration required).

### 5. Rate Card Display

**No changes needed** - RateCard model already exists and supports base and domain-specific rates.

## Migration Script

A migration script will be created to:
1. Add RISK_REGISTER table
2. Add SKILLS table (optional but recommended)
3. Update employee_skills to reference skills.id (if SKILLS table is added)

## Summary

**Required Changes:**
- ✅ **COMPLETED**: RiskRegister model added to models.py (RISK_REGISTER table will be created on next DB init)
- ⚠️ Add SKILLS master table (OPTIONAL but recommended for better skill management)
- ✅ Rate card support already exists (migration for rate_card_id column needed)

**Implementation Status:**
- ✅ RiskRegister model with all required enums (RiskType, RiskSeverity, RiskStatus) added to models.py
- ✅ Employee model updated with risks relationship
- ✅ Project model updated with risks relationship
- ✅ Backend routes for skills and risk management created
- ✅ Frontend components for Add Skills and Raise Risk modals created
- ✅ Employee list endpoint enhanced to include allocation, skills, and rate card data

**No Changes Needed:**
- Employee table structure
- Allocation table (rate_card_id migration pending)
- Employee skills table structure (unless SKILLS master table is added)

**Next Steps:**
1. Run database migration/initialization to create RISK_REGISTER table
2. Test the new functionality
3. Optionally add SKILLS master table for better skill standardization
