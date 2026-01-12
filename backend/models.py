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
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ProjectType(enum.Enum):
    FIXED_PRICE = "Fixed_Price"
    T_AND_M = "T&M"
    RETAINER = "Retainer"


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
    allocations = relationship("Allocation", back_populates="employee", cascade="all, delete-orphan", foreign_keys="Allocation.emp_id")
    feedbacks = relationship("Feedback360", back_populates="employee", cascade="all, delete-orphan")
    bench_entries = relationship("BenchLedger", back_populates="employee", cascade="all, delete-orphan")
    domains = relationship("EmployeeDomain", back_populates="employee", cascade="all, delete-orphan")
    rate_cards = relationship("RateCard", back_populates="employee", cascade="all, delete-orphan", foreign_keys="RateCard.emp_id")
    priority_scores = relationship("PriorityScoring", back_populates="employee", cascade="all, delete-orphan")
    risks = relationship("RiskRegister", back_populates="employee", cascade="all, delete-orphan", foreign_keys="RiskRegister.emp_id")
    mitigation_owned_risks = relationship("RiskRegister", foreign_keys="RiskRegister.mitigation_owner_emp_id")
    trainee_allocations = relationship("Allocation", foreign_keys="Allocation.mentoring_primary_emp_id", back_populates="mentoring_primary")


class Project(Base):
    """The Demand - Active Projects and Sales Pipeline"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    project_code = Column(String, unique=True)  # Auto-generated: PROJ-<Year>-<PrimaryKey>
    client_name = Column(String, nullable=False)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # Vector Source - JD/Scope
    budget_cap = Column(Float, nullable=False)
    billing_currency = Column(String, default='USD')  # INR, USD, EUR
    project_type = Column(Enum(ProjectType))  # Fixed_Price, T&M, Retainer
    industry_domain = Column(String)  # FinTech, Healthcare, Retail, Manufacturing, Telecom, Education, Other
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
    role_requirements = relationship("ProjectRoleRequirements", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("RiskRegister", back_populates="project", cascade="all, delete-orphan")


class Allocation(Base):
    """
    The Ledger - Links Employees to Projects
    
    Supports multiple simultaneous allocations per employee with shadow resource tracking
    and internal vs client allocation differentiation.
    
    Key Concepts:
    - allocation_percentage: How much of employee's total time is allocated to this project (0-100%)
      - This is what is REPORTED to the client
      - Sum across all active allocations should ideally be 100% (fully utilized)
      - Can be < 100% if underutilized, or > 100% if overallocated
    - internal_allocation_percentage: Actual percentage of employee's time spent on this project internally (0-100%)
      - This is the ACTUAL internal utilization
      - Can be LESS than allocation_percentage (over-billing scenario - employee billed more than actual work)
      - Can be MORE than allocation_percentage (under-billing scenario - employee works more than billed)
      - Used for cost calculations (what company pays employee)
    - billable_percentage: How much of the allocation is billable to the client (0-100%)
      - Can be different from allocation_percentage
      - Example: Employee allocated 100% but only 50% billable (during resignation/replacement)
      - Example: Employee allocated 50% and 100% billable (full billing on partial allocation)
    - is_trainee: Indicates if this allocation is for a trainee/shadow resource
      - Trainees are NEVER billable to the client (billable_percentage must be 0)
      - Trainees contribute to cost but not revenue
      - Must have a mentoring_primary_emp_id if is_trainee=True
    - mentoring_primary_emp_id: References the primary resource being shadowed
      - Only used when is_trainee=True
      - Must reference an active allocation on the same project
      - Cannot reference self (emp_id)
    
    Financial Calculation Scenarios:
    
    1. Standard Allocation (Primary Resource):
       - is_trainee: False
       - internal_allocation_percentage: 50%
       - allocation_percentage: 50% (reported to client)
       - billable_percentage: 100%
       - Billed hours: (total_hours × allocation_percentage × billable_percentage) / 10000
       - Cost hours: (total_hours × internal_allocation_percentage) / 100
       - Revenue: billing_rate × billed_hours
       - Cost: cost_rate × cost_hours
    
    2. Over-billed Resource (Efficiency Scenario):
       - is_trainee: False
       - internal_allocation_percentage: 25% (actually works 25%)
       - allocation_percentage: 75% (client billed for 75%)
       - billable_percentage: 100%
       - Billed hours: (160 × 75 × 100) / 10000 = 120 hours
       - Cost hours: (160 × 25) / 100 = 40 hours
       - Higher margin due to efficiency (more revenue, less cost)
    
    3. Trainee/Shadow Resource:
       - is_trainee: True
       - mentoring_primary_emp_id: 123 (primary resource ID)
       - internal_allocation_percentage: 100%
       - allocation_percentage: 0% (not reported to client)
       - billable_percentage: 0% (never billable)
       - Billed hours: 0 (trainees never billable)
       - Cost hours: (160 × 100) / 100 = 160 hours
       - Revenue: $0
       - Cost: cost_rate × 160 hours (pure training investment)
    
    4. Multiple Projects:
       - Employee can have different internal vs client allocations across projects
       - Total internal_allocation_percentage should ideally sum to 100%
       - Total allocation_percentage can exceed 100% (over-billing scenario)
    
    Validation Rules:
    - If is_trainee=True: billable_percentage MUST be 0, mentoring_primary_emp_id MUST NOT be NULL
    - If is_trainee=True: billing_rate should be 0 or NULL
    - mentoring_primary_emp_id must reference valid employee with active allocation on same project
    - mentoring_primary_emp_id cannot reference self (emp_id)
    - internal_allocation_percentage must be between 0 and 100
    """
    __tablename__ = 'allocations'
    
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # Null means ongoing allocation
    billing_rate = Column(Float)  # Hourly rate charged to client
    is_revealed = Column(Boolean, default=False)  # Fairness Flag - whether employee knows their rate
    
    # Allocation and Billable Percentages
    allocation_percentage = Column(Integer, nullable=False, default=100)  # How much of employee's time allocated (0-100%) - reported to client
    billable_percentage = Column(Integer, nullable=False, default=100)  # How much of allocation is billable (0-100%)
    
    # Internal vs Client Allocation Tracking
    internal_allocation_percentage = Column(Integer, nullable=False, default=100)  # Actual percentage of employee's time spent internally (0-100%)
    
    # Shadow Resource Tracking
    is_trainee = Column(Boolean, default=False, nullable=False)  # Indicates if this allocation is for a trainee/shadow resource
    mentoring_primary_emp_id = Column(Integer, ForeignKey('employees.id'), nullable=True)  # References the primary resource being shadowed
    
    # Legacy field for backward compatibility (deprecated - use allocation_percentage)
    utilization = Column(Integer)  # Deprecated: Use allocation_percentage instead
    
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id'), nullable=True)  # Link to rate card used
    
    # Relationships
    employee = relationship("Employee", back_populates="allocations", foreign_keys=[emp_id])
    project = relationship("Project", back_populates="allocations")
    rate_card = relationship("RateCard", foreign_keys=[rate_card_id], lazy='select')
    financials = relationship("AllocationFinancial", back_populates="allocation", cascade="all, delete-orphan", uselist=False)
    mentoring_primary = relationship("Employee", foreign_keys=[mentoring_primary_emp_id], back_populates="trainee_allocations")


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
    """
    Financial Details per Allocation
    
    Updated calculation formulas to support shadow resources and internal vs client allocation:
    
    For PRIMARY Resources (is_trainee=False):
    - Revenue Calculation:
      - Revenue = billing_rate × billed_hours
      - billed_hours = (total_hours × allocation_percentage × billable_percentage) / 10000
      - Example: 160 hours/month, 50% allocation (reported), 100% billable = 80 billable hours
    
    - Cost Calculation:
      - Cost = cost_rate × cost_hours
      - cost_hours = (total_hours × internal_allocation_percentage) / 100
      - Example: 160 hours/month, 25% internal allocation = 40 cost hours
      - Note: Cost is based on ACTUAL internal work, not client-reported allocation
    
    - Gross Margin:
      - gross_margin = (revenue - cost) / revenue × 100 if revenue > 0 else 0
    
    For TRAINEE Resources (is_trainee=True):
    - Revenue Calculation:
      - Revenue = $0 (trainees are NEVER billable)
      - billed_hours = 0
    
    - Cost Calculation:
      - Cost = cost_rate × cost_hours
      - cost_hours = (total_hours × internal_allocation_percentage) / 100
      - Example: 160 hours/month, 100% internal allocation = 160 cost hours
      - Pure training investment (cost center)
    
    Key Differences:
    - billed_hours: Based on allocation_percentage (what client sees)
    - cost_hours: Based on internal_allocation_percentage (actual internal work)
    - This allows tracking over-billing (internal < allocation) and under-billing (internal > allocation)
    """
    __tablename__ = 'allocation_financials'
    
    id = Column(Integer, primary_key=True)
    allocation_id = Column(Integer, ForeignKey('allocations.id'), nullable=False, unique=True)
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id'), nullable=False)
    billing_rate = Column(Float, nullable=False)  # Actual rate charged to client
    cost_rate = Column(Float)  # Employee cost per hour (CTC/working_hours)
    gross_margin_percentage = Column(Float)  # Calculated margin for this allocation
    
    # Revenue tracking (based on billable percentage)
    estimated_revenue = Column(Float, default=0.0)  # Estimated revenue from billable hours
    actual_revenue = Column(Float, default=0.0)  # Actual revenue from billable hours
    
    # Cost tracking (based on allocation percentage)
    estimated_cost = Column(Float, default=0.0)  # Estimated cost from allocated hours
    actual_cost = Column(Float, default=0.0)  # Actual cost from allocated hours
    
    # Hours tracking
    billed_hours = Column(Integer, default=0)  # Hours billable to client (allocation × billable %)
    utilized_hours = Column(Integer, default=0)  # Hours allocated (allocation %)
    total_hours_in_period = Column(Integer, default=0)  # Total working hours in the period (e.g., 160/month)
    
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


class ProjectRoleRequirements(Base):
    """Project Role Requirements - Team Structure Planning"""
    __tablename__ = 'project_role_requirements'
    
    id = Column(Integer, primary_key=True)
    proj_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    role_name = Column(String, nullable=False)  # Architect, Project Manager, Senior Developer, etc.
    required_count = Column(Integer, nullable=False, default=1)
    utilization_percentage = Column(Integer, nullable=False, default=100)  # 0-100%
    
    # Relationships
    project = relationship("Project", back_populates="role_requirements")


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


# ============================================================================
# Validation Functions for Allocation Model
# ============================================================================

from sqlalchemy import event
from sqlalchemy.orm import Session

def validate_allocation(allocation):
    """
    Validate Allocation model fields according to business rules.
    
    Validation Rules:
    1. If is_trainee=True: billable_percentage MUST be 0
    2. If is_trainee=True: mentoring_primary_emp_id MUST NOT be NULL
    3. If is_trainee=True: billing_rate should be 0 or NULL
    4. mentoring_primary_emp_id cannot reference self (emp_id)
    5. internal_allocation_percentage must be between 0 and 100
    6. allocation_percentage must be between 0 and 100
    7. billable_percentage must be between 0 and 100
    """
    errors = []
    
    # Validate internal_allocation_percentage range
    if allocation.internal_allocation_percentage < 0 or allocation.internal_allocation_percentage > 100:
        errors.append("internal_allocation_percentage must be between 0 and 100")
    
    # Validate allocation_percentage range
    if allocation.allocation_percentage < 0 or allocation.allocation_percentage > 100:
        errors.append("allocation_percentage must be between 0 and 100")
    
    # Validate billable_percentage range
    if allocation.billable_percentage < 0 or allocation.billable_percentage > 100:
        errors.append("billable_percentage must be between 0 and 100")
    
    # Validate trainee rules
    if allocation.is_trainee:
        if allocation.billable_percentage != 0:
            errors.append("Trainee allocations must have billable_percentage = 0")
        
        if allocation.mentoring_primary_emp_id is None:
            errors.append("Trainee allocations must have a mentoring_primary_emp_id")
        
        if allocation.mentoring_primary_emp_id == allocation.emp_id:
            errors.append("Trainee cannot mentor themselves (mentoring_primary_emp_id cannot equal emp_id)")
        
        if allocation.billing_rate and allocation.billing_rate != 0:
            errors.append("Trainee allocations should have billing_rate = 0 or NULL")
    
    if errors:
        raise ValueError("Allocation validation failed: " + "; ".join(errors))
    
    return True


@event.listens_for(Allocation, 'before_insert')
@event.listens_for(Allocation, 'before_update')
def validate_allocation_event(mapper, connection, target):
    """SQLAlchemy event listener to validate Allocation before insert/update"""
    validate_allocation(target)


# ============================================================================
# Example Query Functions
# ============================================================================

def get_trainees_for_project(session: Session, project_id: int):
    """
    Find all trainee/shadow resources for a specific project.
    
    Example usage:
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        trainees = get_trainees_for_project(session, project_id=1)
    """
    return session.query(Allocation).filter(
        Allocation.proj_id == project_id,
        Allocation.is_trainee == True
    ).all()


def get_employee_financial_summary(session: Session, employee_id: int):
    """
    Calculate total cost vs revenue for an employee across all active projects.
    
    Returns dict with:
    - total_revenue: Sum of all billed revenue
    - total_cost: Sum of all cost based on internal allocation
    - gross_margin: Calculated margin percentage
    - allocations: List of allocation details
    
    Example usage:
        summary = get_employee_financial_summary(session, employee_id=123)
        print(f"Total Revenue: ${summary['total_revenue']}")
        print(f"Total Cost: ${summary['total_cost']}")
        print(f"Gross Margin: {summary['gross_margin']}%")
    """
    from datetime import date
    
    allocations = session.query(Allocation).filter(
        Allocation.emp_id == employee_id,
        (Allocation.end_date.is_(None)) | (Allocation.end_date >= date.today())
    ).all()
    
    total_revenue = 0.0
    total_cost = 0.0
    allocation_details = []
    
    for alloc in allocations:
        # Get financial details if available
        if alloc.financials:
            total_revenue += alloc.financials.actual_revenue or 0.0
            total_cost += alloc.financials.actual_cost or 0.0
            allocation_details.append({
                'project_id': alloc.proj_id,
                'allocation_id': alloc.id,
                'revenue': alloc.financials.actual_revenue or 0.0,
                'cost': alloc.financials.actual_cost or 0.0,
                'is_trainee': alloc.is_trainee
            })
    
    gross_margin = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_margin': gross_margin,
        'allocations': allocation_details
    }


def get_over_billed_allocations(session: Session, project_id: int = None):
    """
    Identify over-billed allocations where internal_allocation < allocation_percentage.
    These represent efficiency scenarios where employee works less than billed.
    
    Example usage:
        over_billed = get_over_billed_allocations(session, project_id=1)
        for alloc in over_billed:
            print(f"Employee {alloc.emp_id}: Billed {alloc.allocation_percentage}%, Actual {alloc.internal_allocation_percentage}%")
    """
    query = session.query(Allocation).filter(
        Allocation.is_trainee == False,
        Allocation.internal_allocation_percentage < Allocation.allocation_percentage
    )
    
    if project_id:
        query = query.filter(Allocation.proj_id == project_id)
    
    return query.all()


def get_under_billed_allocations(session: Session, project_id: int = None):
    """
    Identify under-billed allocations where internal_allocation > allocation_percentage.
    These represent scenarios where employee works more than billed.
    
    Example usage:
        under_billed = get_under_billed_allocations(session, project_id=1)
        for alloc in under_billed:
            print(f"Employee {alloc.emp_id}: Billed {alloc.allocation_percentage}%, Actual {alloc.internal_allocation_percentage}%")
    """
    query = session.query(Allocation).filter(
        Allocation.is_trainee == False,
        Allocation.internal_allocation_percentage > Allocation.allocation_percentage
    )
    
    if project_id:
        query = query.filter(Allocation.proj_id == project_id)
    
    return query.all()


def get_shadow_resources_and_mentors(session: Session, project_id: int):
    """
    Find all shadow resources and their primary mentors for a project.
    
    Returns list of dicts with:
    - trainee: Allocation object for trainee
    - mentor: Employee object for primary mentor
    - mentor_allocation: Allocation object for mentor's allocation
    
    Example usage:
        shadows = get_shadow_resources_and_mentors(session, project_id=1)
        for shadow in shadows:
            print(f"Trainee: {shadow['trainee'].employee.first_name}")
            print(f"Mentor: {shadow['mentor'].first_name}")
    """
    trainees = session.query(Allocation).filter(
        Allocation.proj_id == project_id,
        Allocation.is_trainee == True
    ).all()
    
    results = []
    for trainee_alloc in trainees:
        if trainee_alloc.mentoring_primary_emp_id:
            mentor = session.query(Employee).filter(
                Employee.id == trainee_alloc.mentoring_primary_emp_id
            ).first()
            
            mentor_alloc = session.query(Allocation).filter(
                Allocation.emp_id == trainee_alloc.mentoring_primary_emp_id,
                Allocation.proj_id == project_id,
                Allocation.is_trainee == False
            ).first()
            
            results.append({
                'trainee': trainee_alloc,
                'mentor': mentor,
                'mentor_allocation': mentor_alloc
            })
    
    return results
