"""
SQLAlchemy Database Models for BenchCraft AI
Comprehensive data-rich schema as per specification
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime, date

Base = declarative_base()


class RoleLevel(enum.Enum):
    JR = "JR"
    MID = "MID"
    SR = "SR"
    LEAD = "LEAD"
    PRINCIPAL = "PRINCIPAL"




class EmployeeStatus(enum.Enum):
    BENCH = "BENCH"
    ALLOCATED = "ALLOCATED"
    NOTICE_PERIOD = "NOTICE_PERIOD"


class ProjectStatus(enum.Enum):
    PIPELINE = "PIPELINE"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class DomainType(enum.Enum):
    BUSINESS_DOMAIN = "BUSINESS_DOMAIN"
    TECHNICAL_DOMAIN = "TECHNICAL_DOMAIN"
    INDUSTRY_VERTICAL = "INDUSTRY_VERTICAL"


class RateType(enum.Enum):
    BASE = "BASE"
    DOMAIN_SPECIFIC = "DOMAIN_SPECIFIC"
    SKILL_SPECIFIC = "SKILL_SPECIFIC"
    PROJECT_SPECIFIC = "PROJECT_SPECIFIC"


class PriorityTier(enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DomainPriority(enum.Enum):
    MANDATORY = "MANDATORY"
    PREFERRED = "PREFERRED"
    NICE_TO_HAVE = "NICE_TO_HAVE"


class PeriodType(enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    PROJECT_LIFETIME = "PROJECT_LIFETIME"


class RateNegotiationStatus(enum.Enum):
    OPEN = "OPEN"
    NEGOTIATING = "NEGOTIATING"
    AGREED = "AGREED"
    REJECTED = "REJECTED"


class RiskType(enum.Enum):
    NOTICE_PERIOD = "NOTICE_PERIOD"
    CRITICAL_ROLE = "CRITICAL_ROLE"
    SINGLE_POINT_FAILURE = "SINGLE_POINT_FAILURE"
    SKILL_GAP = "SKILL_GAP"
    PERFORMANCE = "PERFORMANCE"


class RiskSeverity(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskStatus(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"
    ACCEPTED = "ACCEPTED"


class Employee(Base):
    """The Resource - 360° metadata with PII"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role_level = Column(String(20), nullable=False)
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
    domains = relationship("EmployeeDomain", back_populates="employee", cascade="all, delete-orphan")
    rate_cards = relationship("RateCard", back_populates="employee", cascade="all, delete-orphan", foreign_keys="RateCard.emp_id")
    priority_scores = relationship("PriorityScoring", back_populates="employee", cascade="all, delete-orphan")
    risks = relationship("RiskRegister", back_populates="employee", cascade="all, delete-orphan", foreign_keys="RiskRegister.emp_id")
    mitigation_owned_risks = relationship("RiskRegister", foreign_keys="RiskRegister.mitigation_owner_emp_id")


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
    domains = relationship("ProjectDomain", back_populates="project", cascade="all, delete-orphan")
    rate_requirements = relationship("ProjectRateRequirements", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("RiskRegister", back_populates="project", cascade="all, delete-orphan")


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
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id'), nullable=True)  # Link to rate card used (nullable for backward compatibility)
    
    # Relationships
    employee = relationship("Employee", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")
    rate_card = relationship("RateCard", foreign_keys=[rate_card_id], lazy='select')
    financials = relationship("AllocationFinancial", back_populates="allocation", cascade="all, delete-orphan", uselist=False)


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


# ============================================================================
# Financials & Domain Management Models
# ============================================================================

class Domain(Base):
    """Business/Technical Domains"""
    __tablename__ = 'domains'
    
    id = Column(Integer, primary_key=True)
    domain_name = Column(String, nullable=False)  # FinTech, Healthcare, Retail, etc.
    domain_code = Column(String, unique=True)  # Unique identifier
    domain_type = Column(Enum(DomainType), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_date = Column(Date, default=date.today)
    
    # Relationships
    employee_domains = relationship("EmployeeDomain", back_populates="domain", cascade="all, delete-orphan")
    project_domains = relationship("ProjectDomain", back_populates="domain", cascade="all, delete-orphan")
    rate_cards = relationship("RateCard", back_populates="domain", cascade="all, delete-orphan")
    rate_requirements = relationship("ProjectRateRequirements", back_populates="domain", cascade="all, delete-orphan")


class EmployeeDomain(Base):
    """Employee Domain Expertise"""
    __tablename__ = 'employee_domains'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    proficiency = Column(Integer, nullable=False)  # 1-Novice to 5-Expert
    years_of_experience = Column(Float, default=0.0)
    first_exposure_date = Column(Date)
    last_used_date = Column(Date)
    is_primary_domain = Column(Boolean, default=False)
    notes = Column(Text)
    last_updated = Column(Date, default=date.today)
    
    # Relationships
    employee = relationship("Employee", back_populates="domains")
    domain = relationship("Domain", back_populates="employee_domains")


class ProjectDomain(Base):
    """Project Domain Requirements"""
    __tablename__ = 'project_domains'
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    priority = Column(Enum(DomainPriority), default=DomainPriority.PREFERRED)
    weight = Column(Integer, default=5)  # Importance 1-10
    requirements = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="domains")
    domain = relationship("Domain", back_populates="project_domains")


class RateCard(Base):
    """Rate Cards - Base and Domain-Specific Rates"""
    __tablename__ = 'rate_cards'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    domain_id = Column(Integer, ForeignKey('domains.id'))  # Nullable - null means base rate
    skill_id = Column(Integer)  # Nullable - for skill-specific rates (future)
    hourly_rate = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)  # Null for current rates
    rate_type = Column(Enum(RateType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_by_emp_id = Column(Integer, ForeignKey('employees.id'))
    created_date = Column(Date, default=date.today)
    notes = Column(Text)
    
    # Relationships
    employee = relationship("Employee", back_populates="rate_cards", foreign_keys=[emp_id])
    domain = relationship("Domain", back_populates="rate_cards")
    created_by = relationship("Employee", foreign_keys=[created_by_emp_id])
    allocations = relationship("Allocation", foreign_keys="Allocation.rate_card_id", overlaps="rate_card")
    allocation_financials = relationship("AllocationFinancial", back_populates="rate_card", cascade="all, delete-orphan")


class FinancialMetrics(Base):
    """Financial Metrics - Gross Margin Tracking"""
    __tablename__ = 'financial_metrics'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'))  # Nullable - null means company-wide
    proj_id = Column(Integer, ForeignKey('projects.id'))  # Nullable - null means company-wide
    target_gross_margin_percentage = Column(Float, default=50.0)  # Target margin e.g. 50%
    actual_gross_margin_percentage = Column(Float)  # Calculated margin
    total_revenue = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    gross_profit = Column(Float, default=0.0)
    period_start_date = Column(Date)
    period_end_date = Column(Date)
    period_type = Column(Enum(PeriodType), default=PeriodType.MONTHLY)
    calculated_date = Column(Date, default=date.today)
    notes = Column(Text)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[emp_id])
    project = relationship("Project", foreign_keys=[proj_id])


class AllocationFinancial(Base):
    """Financial Details per Allocation"""
    __tablename__ = 'allocation_financials'
    
    id = Column(Integer, primary_key=True)
    allocation_id = Column(Integer, ForeignKey('allocations.id'), nullable=False, unique=True)
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id'), nullable=False)
    billing_rate = Column(Float, nullable=False)  # Actual rate charged to client
    cost_rate = Column(Float)  # Employee cost per hour (CTC/working_hours)
    gross_margin_percentage = Column(Float)  # Calculated margin for this allocation
    estimated_revenue = Column(Float, default=0.0)
    actual_revenue = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    billed_hours = Column(Integer, default=0)
    utilized_hours = Column(Integer, default=0)
    last_calculated_date = Column(Date, default=date.today)
    notes = Column(Text)
    
    # Relationships
    allocation = relationship("Allocation", back_populates="financials")
    rate_card = relationship("RateCard", back_populates="allocation_financials")


class PriorityScoring(Base):
    """Priority Scoring for Resource Alignment"""
    __tablename__ = 'priority_scoring'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False, unique=True)
    priority_score = Column(Float, nullable=False)  # Calculated priority score
    base_rate_card_value = Column(Float)  # Highest base rate card
    max_domain_rate_value = Column(Float)  # Highest domain-specific rate
    days_on_bench = Column(Integer, default=0)
    last_allocation_end_date = Column(Date)
    calculated_date = Column(Date, default=date.today)
    priority_tier = Column(Enum(PriorityTier), default=PriorityTier.MEDIUM)
    calculation_factors = Column(Text)  # JSON or text of factors
    
    # Relationships
    employee = relationship("Employee", back_populates="priority_scores")


class ProjectRateRequirements(Base):
    """Project Rate Requirements"""
    __tablename__ = 'project_rate_requirements'
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    domain_id = Column(Integer, ForeignKey('domains.id'))  # Nullable - for domain-specific rates
    min_acceptable_rate = Column(Float)
    max_acceptable_rate = Column(Float)
    preferred_rate = Column(Float)
    rate_negotiation_status = Column(Enum(RateNegotiationStatus), default=RateNegotiationStatus.OPEN)
    rate_notes = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="rate_requirements")
    domain = relationship("Domain", back_populates="rate_requirements")


class RiskRegister(Base):
    """Risk Register - Track Employee and Project Risks"""
    __tablename__ = 'risk_register'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'))  # Nullable - risk may not be project-specific
    risk_type = Column(Enum(RiskType), nullable=False)
    severity = Column(Enum(RiskSeverity), nullable=False)
    description = Column(Text)
    mitigation_plan = Column(Text)
    mitigation_owner_emp_id = Column(Integer, ForeignKey('employees.id'))  # Who is responsible for mitigation
    identified_date = Column(Date, nullable=False, default=date.today)
    target_resolution_date = Column(Date)
    status = Column(Enum(RiskStatus), default=RiskStatus.OPEN)
    
    # Relationships
    employee = relationship("Employee", back_populates="risks", foreign_keys=[emp_id])
    project = relationship("Project", back_populates="risks", foreign_keys=[project_id])
    mitigation_owner = relationship("Employee", foreign_keys=[mitigation_owner_emp_id], overlaps="mitigation_owned_risks")
