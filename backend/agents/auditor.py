"""
The Auditor Agent - Financial Constraint Checker
Validates allocations against budget and rules
"""
from agents.base_agent import BaseAgent
from tools.sql_db import SQLDatabaseTool
from models import EmployeeStatus
from typing import Dict, Tuple

class AuditorAgent(BaseAgent):
    """The Auditor - Finance Agent"""
    
    def __init__(self):
        self.db_tool = SQLDatabaseTool()
        super().__init__(
            role="Financial Auditor",
            goal="Validate allocations against budget constraints and business rules",
            backstory="You are a meticulous financial auditor ensuring all allocations comply with budget limits and employee availability."
        )
    
    def validate_allocation(self, emp_id: int, proj_id: int) -> Tuple[bool, str]:
        """
        Validate if allocation is allowed
        Returns (is_valid, reason)
        """
        employee = self.db_tool.get_employee(emp_id)
        project = self.db_tool.get_project(proj_id)
        
        if not employee:
            return False, "Employee not found"
        
        if not project:
            return False, "Project not found"
        
        # Check employee status
        if employee.status != EmployeeStatus.BENCH:
            return False, f"Employee is not on bench (current status: {employee.status.value})"
        
        # Check budget (simplified - in production, calculate remaining budget)
        if employee.ctc_monthly > project.budget_cap:
            return False, f"Employee CTC ({employee.ctc_monthly}) exceeds project budget cap ({project.budget_cap})"
        
        return True, "Allocation approved"
