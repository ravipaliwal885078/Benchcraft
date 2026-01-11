"""
SQLAlchemy Database Models for BenchCraft AI
Comprehensive data-rich schema as per specification
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class RoleLevel(enum.Enum):
    JR = "Jr"
    MID = "Mid"
    SR = "Sr"
    LEAD = "Lead"
    PRINCIPAL = "Principal"


class EmployeeStatus(enum.Enum):
    BENCH = "BENCH"
    ALLOCATED = "ALLOCATED"
    NOTICE_PERIOD = "NOTICE_PERIOD"


class ProjectStatus(enum.Enum):
    PIPELINE = "PIPELINE"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class Employee(Base):
    """The Resource - 360° metadata with PII"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role_level = Column(Enum(RoleLevel), nullable=False)
    ctc_monthly = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    base_location = Column(String)
    visa_status = Column(String)
    remote_pref = Column(Boolean, default=False)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.BENCH)
    joined_date = Column(Date)
    bio_summary = Column(Text)
    
    # Relationships
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    allocations = relationship("Allocation", back_populates="employee", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback360", back_populates="employee", cascade="all, delete-orphan")
    bench_entries = relationship("BenchLedger", back_populates="employee", cascade="all, delete-orphan")


class Project(Base):
    """The Demand - Active Projects and Sales Pipeline"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    client_name = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # Vector Source - JD/Scope
    budget_cap = Column(Float, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PIPELINE)
    probability = Column(Integer, default=0)  # 0-100 for Pipeline
    tech_stack = Column(String)  # Comma-separated tags
    
    # Relationships
    allocations = relationship("Allocation", back_populates="project", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback360", back_populates="project", cascade="all, delete-orphan")


class Allocation(Base):
    """The Ledger - Links Employees to Projects"""
    __tablename__ = 'allocations'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    billing_rate = Column(Float)
    is_revealed = Column(Boolean, default=False)  # Fairness Flag
    utilization = Column(Integer, default=100)  # Percentage
    
    # Relationships
    employee = relationship("Employee", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")


class EmployeeSkill(Base):
    """Granular Skill Matrix - 360° Skill Tracking"""
    __tablename__ = 'employee_skills'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    skill_name = Column(String, nullable=False)
    proficiency = Column(Integer, nullable=False)  # 1 (Novice) to 5 (Expert)
    last_used = Column(Date)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="skills")


class Feedback360(Base):
    """Qualitative Performance History"""
    __tablename__ = 'feedback_360'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    feedback = Column(Text)
    tags = Column(String)  # Comma-separated tags like "Delivery", "Innovation"
    
    # Relationships
    employee = relationship("Employee", back_populates="feedbacks")
    project = relationship("Project", back_populates="feedbacks")


class BenchLedger(Base):
    """Financial Audit - Tracks exact cost of bench time"""
    __tablename__ = 'bench_ledger'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    reason = Column(String)  # "Project End", "Hired", etc.
    cost_incurred = Column(Float)  # Calculated: Days * (CTC/30)
    
    # Relationships
    employee = relationship("Employee", back_populates="bench_entries")
