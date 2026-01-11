"""
SQLite Database Interface Tools - BenchCraft AI
Corrected with Eager Loading to prevent DetachedInstanceErrors
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload
from models import Base, Employee, Project, Allocation, EmployeeSkill, EmployeeStatus, ProjectStatus
from config import Config
from typing import List, Dict, Optional

class SQLDatabaseTool:
    """Tool for SQLite database operations with eager loading for AI Agent compatibility"""
    
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
    
    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
    
    def get_employee(self, emp_id: int) -> Optional[Employee]:
        """Get employee by ID with skills eagerly loaded"""
        session = self.Session()
        try:
            return session.query(Employee).options(
                selectinload(Employee.skills)
            ).filter(Employee.id == emp_id).first()
        finally:
            session.close()
    
    def get_employees_by_ids(self, emp_ids: List[int]) -> List[Employee]:
        """Get multiple employees by IDs with skills eagerly loaded for the Matchmaker"""
        session = self.Session()
        try:
            # selectinload fixes the DetachedInstanceError by fetching skills 
            # before the session is closed.
            return session.query(Employee).options(
                selectinload(Employee.skills)
            ).filter(Employee.id.in_(emp_ids)).all()
        finally:
            session.close()
    
    def get_bench_employees(self) -> List[Employee]:
        """Get all employees currently on bench with their skill matrices"""
        session = self.Session()
        try:
            return session.query(Employee).options(
                selectinload(Employee.skills)
            ).filter(
                Employee.status == EmployeeStatus.BENCH
            ).all()
        finally:
            session.close()
    
    def get_project(self, proj_id: int) -> Optional[Project]:
        """Get project details by ID"""
        session = self.Session()
        try:
            return session.query(Project).filter(Project.id == proj_id).first()
        finally:
            session.close()
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects in the pipeline or active"""
        session = self.Session()
        try:
            return session.query(Project).all()
        finally:
            session.close()
    
    def create_allocation(self, emp_id: int, proj_id: int, start_date, end_date=None, billing_rate=None):
        """Create new allocation and update employee status atomically"""
        session = self.Session()
        try:
            allocation = Allocation(
                emp_id=emp_id,
                proj_id=proj_id,
                start_date=start_date,
                end_date=end_date,
                billing_rate=billing_rate,
                is_revealed=False
            )
            session.add(allocation)
            
            # Update employee status to ALLOCATED
            employee = session.query(Employee).filter(Employee.id == emp_id).first()
            if employee:
                employee.status = EmployeeStatus.ALLOCATED
            
            session.commit()
            # Refresh to ensure ID and relationships are accessible after commit
            session.refresh(allocation)
            return allocation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def reveal_allocation(self, allocation_id: int):
        """Mark allocation as revealed (Fairness override)"""
        session = self.Session()
        try:
            allocation = session.query(Allocation).filter(Allocation.id == allocation_id).first()
            if allocation:
                allocation.is_revealed = True
                session.commit()
        finally:
            session.close()
    
    def calculate_bench_burn(self) -> Dict:
        """Calculate total financial bench burn cost"""
        session = self.Session()
        try:
            # We don't necessarily need skills here, but we fetch them for consistency 
            # if the UI needs to show skills of high-cost bench resources
            bench_employees = session.query(Employee).filter(
                Employee.status == EmployeeStatus.BENCH
            ).all()
            
            total_monthly_cost = sum(emp.ctc_monthly for emp in bench_employees)
            return {
                'bench_count': len(bench_employees),
                'total_monthly_cost': total_monthly_cost,
                'employees': [
                    {
                        'id': emp.id,
                        'uuid': emp.uuid,
                        'ctc_monthly': emp.ctc_monthly,
                        'currency': emp.currency
                    }
                    for emp in bench_employees
                ]
            }
        finally:
            session.close()