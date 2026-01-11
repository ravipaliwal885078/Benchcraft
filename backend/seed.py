"""
Seed script to populate database with dummy data and ChromaDB embeddings
Generates 20 employees and 5 projects as per specification
"""
import sys
from pathlib import Path
from datetime import date, timedelta
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import (
    Base, Employee, Project, EmployeeSkill, Allocation, RoleLevel, EmployeeStatus, ProjectStatus, ProjectType,
    Domain, EmployeeDomain, ProjectDomain, RateCard, PriorityScoring, DomainType, RateType, PriorityTier,
    Feedback360, BenchLedger, FinancialMetrics, AllocationFinancial, ProjectRateRequirements, ProjectRoleRequirements,
    RiskRegister, DomainPriority, PeriodType, RateNegotiationStatus, RiskType, RiskSeverity, RiskStatus
)
from config import Config
from tools.vector_db import ChromaSearchTool
from tools.sql_db import SQLDatabaseTool

# Sample data
FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Sage", "River",
               "Blake", "Cameron", "Dakota", "Emery", "Finley", "Harper", "Hayden", "Jamie", "Kai", "Logan"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]

SKILLS = ["Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Azure", "Docker", "Kubernetes", "SQL",
          "MongoDB", "PostgreSQL", "Machine Learning", "Data Science", "DevOps", "CI/CD", "Agile", "Scrum",
          "Microservices", "REST API", "GraphQL", "TypeScript", "Angular", "Vue.js", "Spring Boot", "Django",
          "Flask", "FastAPI", "TensorFlow", "PyTorch"]

LOCATIONS = ["New York", "London", "San Francisco", "Amsterdam", "Bangalore", "Singapore", "Toronto", "Sydney"]

CLIENTS = ["Acme Corp", "TechGlobal", "FinanceFirst", "HealthTech Solutions", "RetailMax", "AeroSystems", "KLM Airlines"]

PROJECT_DESCRIPTIONS = [
    "Senior Python developer needed for FinTech platform. Experience with microservices, AWS, and real-time payment processing required.",
    "Full-stack JavaScript developer for e-commerce platform. React, Node.js, and MongoDB expertise essential.",
    "Cloud architect for enterprise migration to Azure. Kubernetes and containerization experience required.",
    "Data scientist for machine learning project. Python, TensorFlow, and experience with large datasets.",
    "DevOps engineer for CI/CD pipeline automation. Docker, Kubernetes, and infrastructure as code experience needed.",
    "Aviation industry expert for airline management system. Experience with legacy systems and modern cloud architecture.",
    "Healthcare technology specialist for patient management platform. HIPAA compliance and security expertise required."
]

# Domain data
DOMAINS = [
    {"name": "FinTech", "code": "FINTECH", "type": DomainType.BUSINESS_DOMAIN},
    {"name": "Healthcare", "code": "HEALTHCARE", "type": DomainType.BUSINESS_DOMAIN},
    {"name": "Retail", "code": "RETAIL", "type": DomainType.BUSINESS_DOMAIN},
    {"name": "Aviation", "code": "AVIATION", "type": DomainType.INDUSTRY_VERTICAL},
    {"name": "Cloud Architecture", "code": "CLOUD", "type": DomainType.TECHNICAL_DOMAIN},
    {"name": "Machine Learning", "code": "ML", "type": DomainType.TECHNICAL_DOMAIN},
    {"name": "E-commerce", "code": "ECOMMERCE", "type": DomainType.BUSINESS_DOMAIN},
]

def generate_bio(role_level, skills_list):
    """Generate a realistic bio summary"""
    level_desc = {
        RoleLevel.JR: "junior",
        RoleLevel.MID: "mid-level",
        RoleLevel.SR: "senior",
        RoleLevel.LEAD: "lead",
        RoleLevel.PRINCIPAL: "principal"
    }
    
    bio = f"{level_desc.get(role_level, 'experienced')} software engineer with expertise in {', '.join(skills_list[:3])}. "
    bio += f"Strong background in software development and system architecture. "
    bio += f"Proven track record of delivering high-quality solutions in agile environments."
    
    return bio

def seed_database():
    """Main seeding function"""
    print("Initializing database...")
    
    # Initialize database
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Initialize ChromaDB
    print("Initializing ChromaDB...")
    vector_tool = ChromaSearchTool()
    
    try:
        # Create 20 employees
        print("Creating employees...")
        employees = []
        used_emails = set()  # Track used emails to ensure uniqueness
        
        for i in range(20):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            role_level = random.choice(list(RoleLevel))
            
            # Generate unique email
            base_email = f"{first_name.lower()}.{last_name.lower()}@benchcraft.ai"
            email = base_email
            counter = 1
            while email in used_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{counter}@benchcraft.ai"
                counter += 1
            used_emails.add(email)
            
            # Assign skills (3-7 skills per employee)
            num_skills = random.randint(3, 7)
            employee_skills = random.sample(SKILLS, num_skills)
            
            # Generate bio
            bio = generate_bio(role_level, employee_skills)
            
            # Calculate CTC based on role level
            ctc_base = {
                RoleLevel.JR: 5000,
                RoleLevel.MID: 8000,
                RoleLevel.SR: 12000,
                RoleLevel.LEAD: 15000,
                RoleLevel.PRINCIPAL: 20000
            }
            ctc_monthly = ctc_base[role_level] + random.randint(-500, 2000)
            
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,  # Use unique email
                role_level=role_level.value,  # Store enum value as string
                ctc_monthly=ctc_monthly,
                currency="USD",
                base_location=random.choice(LOCATIONS),
                visa_status=random.choice(["Citizen", "H1B", "Green Card", "Work Permit"]),
                remote_pref=random.choice([True, False]),
                status=random.choice([EmployeeStatus.BENCH, EmployeeStatus.ALLOCATED]),
                joined_date=date.today() - timedelta(days=random.randint(30, 1000)),
                bio_summary=bio
            )
            
            session.add(employee)
            session.flush()  # Get the ID
            
            # Add skills
            for skill_name in employee_skills:
                skill = EmployeeSkill(
                    emp_id=employee.id,
                    skill_name=skill_name,
                    proficiency=random.randint(2, 5),
                    last_used=date.today() - timedelta(days=random.randint(0, 365)),
                    is_verified=random.choice([True, False])
                )
                session.add(skill)
            
            # Add to ChromaDB
            vector_tool.add_employee_embedding(employee.id, bio)
            
            employees.append(employee)
            print(f"  Created employee {i+1}/20: {first_name} {last_name} ({role_level.value})")
        
        # Create domains
        print("\nCreating domains...")
        domains = []
        for domain_data in DOMAINS:
            domain = Domain(
                domain_name=domain_data["name"],
                domain_code=domain_data["code"],
                domain_type=domain_data["type"],
                description=f"{domain_data['name']} domain expertise",
                is_active=True
            )
            session.add(domain)
            session.flush()
            domains.append(domain)
            print(f"  Created domain: {domain_data['name']}")
        
        # Create 5 projects
        print("\nCreating projects...")
        projects = []
        industry_domains = ["FinTech", "Healthcare", "Retail", "Manufacturing", "Telecom", "Education", "Other"]
        project_types = list(ProjectType)
        currencies = ["INR", "USD", "EUR"]
        statuses = [ProjectStatus.PIPELINE, ProjectStatus.ACTIVE, ProjectStatus.ON_HOLD, ProjectStatus.CLOSED]
        
        for i in range(5):
            client = random.choice(CLIENTS)
            description = random.choice(PROJECT_DESCRIPTIONS)
            
            # Extract tech stack from description
            tech_stack_list = []
            for skill in SKILLS:
                if skill.lower() in description.lower():
                    tech_stack_list.append(skill)
            tech_stack = ", ".join(tech_stack_list[:5]) if tech_stack_list else "Python, JavaScript"
            
            # Select random industry domain based on client/project type
            industry_domain = random.choice(industry_domains)
            # Match industry domain to client if possible
            if "Finance" in client or "FinTech" in description:
                industry_domain = "FinTech"
            elif "Health" in client or "Healthcare" in description:
                industry_domain = "Healthcare"
            elif "Retail" in client or "e-commerce" in description.lower():
                industry_domain = "Retail"
            
            project = Project(
                client_name=client,
                project_name=f"{client} Platform",
                description=description,
                budget_cap=random.randint(50000, 200000),
                billing_currency=random.choice(currencies),
                project_type=random.choice(project_types),
                industry_domain=industry_domain,
                start_date=date.today() + timedelta(days=random.randint(-30, 30)),
                end_date=date.today() + timedelta(days=random.randint(90, 365)),
                status=random.choice(statuses),
                probability=random.randint(50, 100) if i < 2 else 100,
                tech_stack=tech_stack
            )
            
            session.add(project)
            session.flush()  # Flush to get the project.id
            
            # Generate project_code: PROJ-<Year>-<PrimaryKey>
            current_year = date.today().year
            project.project_code = f"PROJ-{current_year}-{project.id}"
            
            projects.append(project)
            print(f"  Created project {i+1}/5: {client} Platform (Code: {project.project_code})")
        
        # Create employee domains (assign 1-3 domains per employee)
        print("\nCreating employee domains...")
        for employee in employees:
            num_domains = random.randint(1, 3)
            employee_domains_list = random.sample(domains, min(num_domains, len(domains)))
            
            for idx, domain in enumerate(employee_domains_list):
                emp_domain = EmployeeDomain(
                    emp_id=employee.id,
                    domain_id=domain.id,
                    proficiency=random.randint(3, 5),
                    years_of_experience=random.uniform(1.0, 8.0),
                    first_exposure_date=date.today() - timedelta(days=random.randint(100, 2000)),
                    last_used_date=date.today() - timedelta(days=random.randint(0, 180)),
                    is_primary_domain=(idx == 0)  # First domain is primary
                )
                session.add(emp_domain)
        
        # Create rate cards for employees
        print("\nCreating rate cards...")
        rate_cards_map = {}  # Map employee_id to rate_card_id
        for employee in employees:
            # Calculate base hourly rate (typically 2-3x hourly cost for 50% margin)
            hourly_cost = employee.ctc_monthly / 160.0  # Assuming 160 working hours/month
            base_rate = hourly_cost * random.uniform(2.0, 3.0)  # 50-66% margin
            
            # Create base rate card
            base_rate_card = RateCard(
                emp_id=employee.id,
                domain_id=None,  # Base rate
                hourly_rate=round(base_rate, 2),
                currency="USD",
                effective_date=date.today() - timedelta(days=30),
                expiry_date=None,
                rate_type=RateType.BASE,
                is_active=True
            )
            session.add(base_rate_card)
            session.flush()
            rate_cards_map[employee.id] = base_rate_card.id
            
            # Create 1-2 domain-specific rate cards (higher rates)
            employee_domains = session.query(EmployeeDomain).filter(EmployeeDomain.emp_id == employee.id).all()
            if employee_domains:
                selected_domains = random.sample(employee_domains, min(2, len(employee_domains)))
                for emp_domain in selected_domains:
                    domain_rate = base_rate * random.uniform(1.1, 1.5)  # 10-50% premium
                    domain_rate_card = RateCard(
                        emp_id=employee.id,
                        domain_id=emp_domain.domain_id,
                        hourly_rate=round(domain_rate, 2),
                        currency="USD",
                        effective_date=date.today() - timedelta(days=20),
                        expiry_date=None,
                        rate_type=RateType.DOMAIN_SPECIFIC,
                        is_active=True
                    )
                    session.add(domain_rate_card)
        
        # Create allocations (assign some employees to projects)
        print("\nCreating allocations...")
        active_projects = [p for p in projects if p.status == ProjectStatus.ACTIVE]
        allocated_employees = []
        
        for project in active_projects[:3]:  # Allocate to first 3 active projects
            num_allocations = random.randint(2, 5)
            available_employees = [e for e in employees if e.id not in allocated_employees]
            
            if not available_employees:
                break
                
            selected_employees = random.sample(available_employees, min(num_allocations, len(available_employees)))
            
            for employee in selected_employees:
                # Get employee's rate card
                rate_card_id = rate_cards_map.get(employee.id)
                
                # Calculate allocation dates
                alloc_start = project.start_date + timedelta(days=random.randint(0, 10))
                alloc_end = project.end_date - timedelta(days=random.randint(0, 30)) if project.end_date else None
                
                # Get rate from rate card
                rate_card = session.query(RateCard).filter(RateCard.id == rate_card_id).first()
                billing_rate = rate_card.hourly_rate if rate_card else None
                
                # Create allocation with allocation_percentage and billable_percentage
                # Most allocations are 100% allocation and 100% billable
                # Some scenarios: partial allocation, or allocation > billable (replacement scenario)
                allocation_pct = random.choice([50, 80, 100, 100, 100])  # Bias towards 100%
                billable_pct = random.choice([50, 80, 100, 100, 100])  # Bias towards 100%
                
                # Special case: if allocation is 100% but billable is 50%, simulate replacement scenario
                if allocation_pct == 100 and random.random() < 0.1:  # 10% chance
                    billable_pct = 50
                
                allocation = Allocation(
                    emp_id=employee.id,
                    proj_id=project.id,
                    start_date=alloc_start,
                    end_date=alloc_end,
                    billing_rate=billing_rate,
                    is_revealed=random.choice([True, False]),
                    allocation_percentage=allocation_pct,
                    billable_percentage=billable_pct,
                    rate_card_id=rate_card_id
                )
                session.add(allocation)
                session.flush()  # Flush to get allocation.id
                
                # Create AllocationFinancial for each allocation
                if billing_rate and rate_card_id:
                    # Calculate financial metrics
                    total_hours = 160  # Monthly hours
                    utilized_hours = int((total_hours * allocation_pct) / 100)
                    billed_hours = int((total_hours * allocation_pct * billable_pct) / 10000)
                    cost_rate = employee.ctc_monthly / 160.0
                    estimated_revenue = billing_rate * billed_hours
                    estimated_cost = cost_rate * utilized_hours
                    gross_margin = ((estimated_revenue - estimated_cost) / estimated_revenue * 100) if estimated_revenue > 0 else 0
                    
                    alloc_financial = AllocationFinancial(
                        allocation_id=allocation.id,
                        rate_card_id=rate_card_id,
                        billing_rate=billing_rate,
                        cost_rate=round(cost_rate, 2),
                        gross_margin_percentage=round(gross_margin, 2),
                        estimated_revenue=round(estimated_revenue, 2),
                        estimated_cost=round(estimated_cost, 2),
                        billed_hours=billed_hours,
                        utilized_hours=utilized_hours,
                        total_hours_in_period=total_hours
                    )
                    session.add(alloc_financial)
                
                # Update employee status
                employee.status = EmployeeStatus.ALLOCATED
                allocated_employees.append(employee.id)
        
        # Create project domains (assign 1-2 domains per project)
        print("\nCreating project domains...")
        for project in projects:
            num_domains = random.randint(1, 2)
            project_domains_list = random.sample(domains, min(num_domains, len(domains)))
            
            for domain in project_domains_list:
                proj_domain = ProjectDomain(
                    proj_id=project.id,
                    domain_id=domain.id,
                    priority=random.choice(list(DomainPriority)),
                    weight=random.randint(5, 10),
                    requirements=f"Requires expertise in {domain.domain_name} domain"
                )
                session.add(proj_domain)
        
        # Create project role requirements (for some projects)
        print("\nCreating project role requirements...")
        role_names = ["Architect", "Project Manager", "Senior Developer", "Developer", 
                     "Business Analyst", "QA Engineer", "Tech Lead", "Designer"]
        for project in projects[:3]:  # Add role requirements to first 3 projects
            num_roles = random.randint(2, 4)
            selected_roles = random.sample(role_names, min(num_roles, len(role_names)))
            
            for role_name in selected_roles:
                # Use role defaults
                role_defaults = {
                    "Architect": {"utilization": 25, "max": 50},
                    "Project Manager": {"utilization": 20, "max": 99},
                    "Senior Developer": {"utilization": 100, "max": 100},
                    "Developer": {"utilization": 100, "max": 100},
                    "Business Analyst": {"utilization": 50, "max": 100},
                    "QA Engineer": {"utilization": 50, "max": 99},
                    "Tech Lead": {"utilization": 75, "max": 100},
                    "Designer": {"utilization": 75, "max": 100}
                }
                defaults = role_defaults.get(role_name, {"utilization": 100, "max": 100})
                
                role_req = ProjectRoleRequirements(
                    proj_id=project.id,
                    role_name=role_name,
                    required_count=random.randint(1, 3),
                    utilization_percentage=defaults["utilization"]
                )
                session.add(role_req)
        
        # Create project rate requirements
        print("\nCreating project rate requirements...")
        for project in projects[:2]:  # Add rate requirements to first 2 projects
            # Select 1-2 domains for rate requirements
            project_domains = session.query(ProjectDomain).filter(ProjectDomain.proj_id == project.id).all()
            if project_domains:
                selected_domains = random.sample(project_domains, min(2, len(project_domains)))
                for proj_domain in selected_domains:
                    # Get average rate for this domain
                    domain_rates = session.query(RateCard).filter(
                        RateCard.domain_id == proj_domain.domain_id,
                        RateCard.is_active == True
                    ).all()
                    if domain_rates:
                        avg_rate = sum([r.hourly_rate for r in domain_rates]) / len(domain_rates)
                        # Get domain name
                        domain_obj = session.query(Domain).filter(Domain.id == proj_domain.domain_id).first()
                        domain_name = domain_obj.domain_name if domain_obj else "Unknown"
                        rate_req = ProjectRateRequirements(
                            proj_id=project.id,
                            domain_id=proj_domain.domain_id,
                            min_acceptable_rate=round(avg_rate * 0.8, 2),
                            max_acceptable_rate=round(avg_rate * 1.2, 2),
                            preferred_rate=round(avg_rate, 2),
                            rate_negotiation_status=random.choice(list(RateNegotiationStatus)),
                            rate_notes=f"Rate requirements for {domain_name} domain"
                        )
                        session.add(rate_req)
        
        # Create feedback entries
        print("\nCreating feedback entries...")
        feedback_tags = ["Delivery", "Innovation", "Communication", "Technical Excellence", "Leadership", "Problem Solving"]
        for project in active_projects[:2] if active_projects else []:  # Add feedback for first 2 active projects
            project_allocations = session.query(Allocation).filter(Allocation.proj_id == project.id).all()
            if project_allocations:
                # Create 1-2 feedback entries per project
                num_feedbacks = random.randint(1, 2)
                selected_allocations = random.sample(project_allocations, min(num_feedbacks, len(project_allocations)))
                
                for allocation in selected_allocations:
                    feedback = Feedback360(
                        emp_id=allocation.emp_id,
                        proj_id=project.id,
                        rating=random.randint(3, 5),
                        feedback=f"Strong performance on {project.project_name}. Demonstrated excellent technical skills and collaboration.",
                        tags=", ".join(random.sample(feedback_tags, random.randint(2, 4)))
                    )
                    session.add(feedback)
        
        # Create bench ledger entries
        print("\nCreating bench ledger entries...")
        bench_employees = [e for e in employees if e.status == EmployeeStatus.BENCH]
        for employee in bench_employees[:5]:  # Create bench entries for first 5 bench employees
            # Check if employee has previous allocation
            last_allocation = session.query(Allocation).filter(
                Allocation.emp_id == employee.id
            ).order_by(Allocation.end_date.desc()).first()
            
            if last_allocation and last_allocation.end_date:
                bench_start = last_allocation.end_date
                bench_end = None  # Ongoing bench
                days_on_bench = (date.today() - bench_start).days
            else:
                bench_start = date.today() - timedelta(days=random.randint(1, 60))
                bench_end = None
                days_on_bench = (date.today() - bench_start).days
            
            cost_per_day = employee.ctc_monthly / 30.0
            cost_incurred = cost_per_day * days_on_bench
            
            bench_entry = BenchLedger(
                emp_id=employee.id,
                start_date=bench_start,
                end_date=bench_end,
                reason="Project End",
                cost_incurred=round(cost_incurred, 2)
            )
            session.add(bench_entry)
        
        # Create financial metrics
        print("\nCreating financial metrics...")
        # Company-wide metrics
        company_metrics = FinancialMetrics(
            emp_id=None,
            proj_id=None,
            target_gross_margin_percentage=50.0,
            actual_gross_margin_percentage=random.uniform(45.0, 55.0),
            total_revenue=random.uniform(500000, 2000000),
            total_cost=random.uniform(250000, 1000000),
            gross_profit=0.0,  # Will be calculated
            period_start_date=date.today().replace(day=1),
            period_end_date=date.today(),
            period_type=PeriodType.MONTHLY
        )
        company_metrics.gross_profit = company_metrics.total_revenue - company_metrics.total_cost
        session.add(company_metrics)
        
        # Project-specific metrics
        for project in active_projects[:2] if active_projects else []:
            project_metrics = FinancialMetrics(
                emp_id=None,
                proj_id=project.id,
                target_gross_margin_percentage=50.0,
                actual_gross_margin_percentage=random.uniform(40.0, 60.0),
                total_revenue=random.uniform(50000, 200000),
                total_cost=random.uniform(25000, 100000),
                gross_profit=0.0,
                period_start_date=project.start_date,
                period_end_date=date.today(),
                period_type=PeriodType.PROJECT_LIFETIME
            )
            project_metrics.gross_profit = project_metrics.total_revenue - project_metrics.total_cost
            session.add(project_metrics)
        
        # Create risk register entries
        print("\nCreating risk register entries...")
        risk_types = list(RiskType)
        risk_severities = list(RiskSeverity)
        risk_statuses = list(RiskStatus)
        
        # Create risks for some employees
        for employee in employees[:5]:  # First 5 employees
            if random.random() < 0.3:  # 30% chance of having a risk
                risk = RiskRegister(
                    emp_id=employee.id,
                    project_id=random.choice([p.id for p in active_projects]) if active_projects and random.random() < 0.7 else None,
                    risk_type=random.choice(risk_types),
                    severity=random.choice(risk_severities),
                    description=f"Risk identified for {employee.first_name} {employee.last_name}: {random.choice(['Notice period risk', 'Skill gap identified', 'Performance concerns', 'Critical role dependency'])}",
                    mitigation_plan=f"Mitigation plan: {random.choice(['Cross-training', 'Backup resource', 'Performance improvement plan', 'Knowledge transfer'])}",
                    mitigation_owner_emp_id=random.choice([e.id for e in employees if e.id != employee.id]) if len(employees) > 1 else None,
                    identified_date=date.today() - timedelta(days=random.randint(1, 30)),
                    target_resolution_date=date.today() + timedelta(days=random.randint(30, 90)),
                    status=random.choice(risk_statuses)
                )
                session.add(risk)
        
        # Create priority scores for all employees
        print("\nCreating priority scores...")
        for employee in employees:
            # Get base rate card
            base_rate_card = session.query(RateCard).filter(
                RateCard.emp_id == employee.id,
                RateCard.rate_type == RateType.BASE
            ).first()
            
            base_rate_value = base_rate_card.hourly_rate if base_rate_card else 0
            
            # Get max domain rate
            domain_rates = session.query(RateCard).filter(
                RateCard.emp_id == employee.id,
                RateCard.rate_type == RateType.DOMAIN_SPECIFIC
            ).all()
            max_domain_rate = max([r.hourly_rate for r in domain_rates]) if domain_rates else base_rate_value
            
            # Calculate days on bench
            last_allocation = session.query(Allocation).filter(
                Allocation.emp_id == employee.id
            ).order_by(Allocation.end_date.desc()).first()
            
            days_on_bench = 0
            last_allocation_end = None
            if employee.status == EmployeeStatus.BENCH:
                if last_allocation and last_allocation.end_date:
                    days_on_bench = (date.today() - last_allocation.end_date).days
                    last_allocation_end = last_allocation.end_date
                else:
                    days_on_bench = random.randint(1, 60)
            
            # Calculate priority score (higher rate + days on bench = higher priority)
            priority_score = (max_domain_rate * 0.7) + (base_rate_value * 0.3) + (days_on_bench * 0.5)
            
            # Determine priority tier
            if priority_score >= 150:
                tier = PriorityTier.CRITICAL
            elif priority_score >= 100:
                tier = PriorityTier.HIGH
            elif priority_score >= 50:
                tier = PriorityTier.MEDIUM
            else:
                tier = PriorityTier.LOW
            
            priority = PriorityScoring(
                emp_id=employee.id,
                priority_score=round(priority_score, 2),
                base_rate_card_value=round(base_rate_value, 2),
                max_domain_rate_value=round(max_domain_rate, 2),
                days_on_bench=days_on_bench,
                last_allocation_end_date=last_allocation_end,
                priority_tier=tier
            )
            session.add(priority)
        
        session.commit()
        print("\nSUCCESS: Database seeded successfully!")
        print(f"   - {len(employees)} employees created")
        print(f"   - {len(projects)} projects created")
        print(f"   - {len(domains)} domains created")
        print(f"   - Employee domains assigned")
        print(f"   - Project domains assigned")
        print(f"   - Rate cards created")
        print(f"   - Allocations created")
        print(f"   - Allocation financials created")
        print(f"   - Project role requirements created")
        print(f"   - Project rate requirements created")
        print(f"   - Feedback entries created")
        print(f"   - Bench ledger entries created")
        print(f"   - Financial metrics created")
        print(f"   - Risk register entries created")
        print(f"   - Priority scores calculated")
        print(f"   - ChromaDB embeddings generated")
        
    except Exception as e:
        session.rollback()
        print(f"\nERROR: Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    seed_database()
