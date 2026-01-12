"""
Comprehensive Database Re-initialization and Seeding Script
Generates enterprise-grade sample data for BenchCraft AI Resource Allocation System

This script:
1. Safely wipes all existing application data (preserving schema)
2. Generates realistic, enterprise-grade sample data
3. Covers all major features and workflows
4. Ensures data consistency and relational integrity
5. Creates sufficient volume for realistic demos

Run: python backend/seed_comprehensive.py
"""
import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from models import (
    Base, Employee, Project, EmployeeSkill, Allocation, RoleLevel, EmployeeStatus, ProjectStatus, ProjectType,
    Domain, EmployeeDomain, ProjectDomain, RateCard, PriorityScoring, DomainType, RateType, PriorityTier,
    Feedback360, BenchLedger, FinancialMetrics, AllocationFinancial, ProjectRateRequirements, ProjectRoleRequirements,
    RiskRegister, DomainPriority, PeriodType, RateNegotiationStatus, RiskType, RiskSeverity, RiskStatus
)
from tools.vector_db import ChromaSearchTool
from utils.employee_status import sync_employee_status

# ============================================================================
# REALISTIC DATA GENERATORS
# ============================================================================

# Enterprise-grade name pools
FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Kavita", "Rahul", "Anjali", "Vikram", "Sneha", "Arjun", "Divya",
    "Suresh", "Meera", "Karan", "Pooja", "Rohan", "Neha", "Aditya", "Shreya", "Nikhil", "Ananya",
    "Vivek", "Sanjana", "Ravi", "Kritika", "Manish", "Swati", "Gaurav", "Pallavi", "Deepak", "Richa",
    "Ankit", "Shruti", "Varun", "Aishwarya", "Harsh", "Isha", "Yash", "Tanvi", "Abhishek", "Sakshi",
    "Rishabh", "Anushka", "Kunal", "Mansi", "Siddharth", "Riya", "Prateek", "Juhi", "Mohit", "Kiran"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Singh", "Reddy", "Gupta", "Verma", "Mehta", "Jain", "Agarwal",
    "Malhotra", "Kapoor", "Chopra", "Bansal", "Shah", "Joshi", "Desai", "Iyer", "Nair", "Rao",
    "Krishnan", "Menon", "Nair", "Pillai", "Nambiar", "Iyer", "Subramanian", "Venkatesan", "Raman", "Sundaram"
]

# Comprehensive skill matrix
SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "Go", "Rust", "Scala", "Kotlin",
    # Frontend
    "React", "Angular", "Vue.js", "Next.js", "HTML5", "CSS3", "SASS", "Tailwind CSS", "Redux", "MobX",
    # Backend
    "Node.js", "Express", "Spring Boot", "Django", "Flask", "FastAPI", "ASP.NET", "Laravel", "Ruby on Rails",
    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "DynamoDB", "Oracle", "SQL Server",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", "GitLab CI/CD", "GitHub Actions",
    # Data & AI
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Data Science", "Pandas", "NumPy", "Scikit-learn",
    # Mobile
    "React Native", "Flutter", "iOS Development", "Android Development", "Swift", "Kotlin",
    # Other
    "GraphQL", "REST API", "Microservices", "Agile", "Scrum", "DevOps", "CI/CD", "System Design", "Architecture"
]

# Enterprise clients
CLIENTS = [
    "HDFC Bank", "ICICI Bank", "Axis Bank", "State Bank of India", "Kotak Mahindra Bank",
    "Reliance Industries", "Tata Consultancy Services", "Infosys", "Wipro", "Tech Mahindra",
    "Bharti Airtel", "Vodafone Idea", "Jio", "Adani Group", "Mahindra & Mahindra",
    "Larsen & Toubro", "HCL Technologies", "Cognizant", "Accenture", "Capgemini",
    "Amazon India", "Flipkart", "Paytm", "Razorpay", "Zomato", "Swiggy", "Ola", "Uber India"
]

# Industry domains
INDUSTRY_DOMAINS = [
    "FinTech", "Banking", "Insurance", "Healthcare", "Pharmaceuticals", "Retail", "E-commerce",
    "Telecom", "Manufacturing", "Automotive", "Aerospace", "Education", "Media & Entertainment",
    "Real Estate", "Energy", "Logistics", "Travel & Hospitality", "Government", "Non-Profit"
]

# Technical domains
TECHNICAL_DOMAINS = [
    "Cloud Architecture", "Machine Learning", "Data Engineering", "DevOps", "Security",
    "Mobile Development", "Web Development", "Blockchain", "IoT", "Cybersecurity"
]

# Business domains
BUSINESS_DOMAINS = [
    "Digital Transformation", "Customer Experience", "Supply Chain", "HR Technology",
    "Marketing Technology", "Sales Automation", "Business Intelligence", "Analytics"
]

# Project descriptions templates
PROJECT_DESCRIPTIONS = [
    "Enterprise digital banking platform with real-time payment processing, UPI/NEFT/RTGS integration, and compliance with RBI regulations. Microservices architecture on AWS with Kubernetes orchestration.",
    "E-commerce marketplace platform targeting Indian market with multi-vendor support, payment gateway integration (Razorpay, Paytm), inventory management, and order fulfillment systems.",
    "Cloud migration project moving legacy applications from on-premise to Azure. Containerization with Docker/Kubernetes, CI/CD pipeline automation, and infrastructure as code.",
    "Machine learning platform for fraud detection in financial transactions. Real-time processing using TensorFlow, data pipelines with Apache Kafka, and model serving infrastructure.",
    "Healthcare patient management system with Aadhaar integration, electronic health records, appointment scheduling, and telemedicine capabilities compliant with Indian healthcare regulations.",
    "5G network implementation project for telecom operator. Network infrastructure automation, OSS/BSS integration, and compliance with TRAI regulations.",
    "Omnichannel retail platform integrating online and offline channels. Inventory synchronization, POS integration, customer analytics, and supply chain optimization.",
    "Digital lending platform for NBFC with credit scoring algorithms, loan origination system, KYC/AML compliance, and loan management workflows.",
    "Online education platform with learning management system, video streaming, assessments, and student analytics. Integration with Indian education boards.",
    "IoT platform for smart manufacturing with sensor data collection, real-time monitoring, predictive maintenance, and industrial automation.",
    "Blockchain-based supply chain traceability system for pharmaceutical industry. Drug tracking, counterfeit prevention, and regulatory compliance.",
    "Customer data platform (CDP) for marketing automation. Data integration, segmentation, personalization engine, and campaign management.",
    "HR technology platform with recruitment, onboarding, performance management, payroll, and employee self-service portal.",
    "Business intelligence and analytics platform with data warehousing, ETL pipelines, dashboards, and reporting for executive decision-making.",
    "Cybersecurity platform with threat detection, incident response, vulnerability management, and compliance monitoring for financial services."
]

# Role names for project requirements
ROLE_NAMES = [
    "Solution Architect", "Technical Architect", "Enterprise Architect",
    "Project Manager", "Program Manager", "Scrum Master", "Product Owner",
    "Senior Developer", "Lead Developer", "Principal Developer",
    "Developer", "Junior Developer", "Associate Developer",
    "Business Analyst", "Senior Business Analyst", "Product Analyst",
    "QA Engineer", "Senior QA Engineer", "Test Lead", "Automation Engineer",
    "Tech Lead", "Engineering Manager", "Development Manager",
    "UI/UX Designer", "Product Designer", "Design Lead",
    "DevOps Engineer", "Site Reliability Engineer", "Cloud Engineer",
    "Data Engineer", "Data Scientist", "ML Engineer", "Data Architect",
    "Security Engineer", "Security Architect", "Compliance Officer"
]

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_bio(role_level, skills_list, domains_list):
    """Generate realistic bio summary"""
    level_desc = {
        "JR": "junior",
        "MID": "mid-level",
        "SR": "senior",
        "LEAD": "lead",
        "PRINCIPAL": "principal"
    }
    
    domain_str = f" with expertise in {', '.join(domains_list[:2])}" if domains_list else ""
    skills_str = ', '.join(skills_list[:4])
    
    bio = f"{level_desc.get(role_level, 'experienced')} software engineer{domain_str} with strong expertise in {skills_str}. "
    bio += f"Proven track record of delivering scalable solutions in enterprise environments. "
    bio += f"Experienced in agile methodologies and cross-functional collaboration. "
    bio += f"Passionate about technology innovation and continuous learning."
    
    return bio

def calculate_ctc(role_level):
    """Calculate realistic CTC based on role level (INR)"""
    base_ctc = {
        "JR": 40000,      # ~$500/month
        "MID": 80000,      # ~$1000/month
        "SR": 150000,     # ~$1800/month
        "LEAD": 250000,   # ~$3000/month
        "PRINCIPAL": 400000  # ~$4800/month
    }
    return base_ctc[role_level] + random.randint(-10000, 50000)

def calculate_hourly_rate(ctc_monthly, margin_multiplier=2.5):
    """Calculate hourly rate with margin"""
    hourly_cost = ctc_monthly / 160.0
    return hourly_cost * margin_multiplier

def get_role_level_distribution():
    """Return realistic role level distribution"""
    return {
        "JR": 0.15,      # 15%
        "MID": 0.30,     # 30%
        "SR": 0.35,      # 35%
        "LEAD": 0.15,    # 15%
        "PRINCIPAL": 0.05  # 5%
    }

def get_status_distribution():
    """Return realistic status distribution"""
    return {
        EmployeeStatus.BENCH: 0.20,           # 20% on bench
        EmployeeStatus.ALLOCATED: 0.75,        # 75% allocated
        EmployeeStatus.NOTICE_PERIOD: 0.05     # 5% on notice
    }

def get_project_status_distribution():
    """Return realistic project status distribution"""
    return {
        ProjectStatus.PIPELINE: 0.20,    # 20% pipeline
        ProjectStatus.ACTIVE: 0.50,      # 50% active
        ProjectStatus.ON_HOLD: 0.10,     # 10% on hold
        ProjectStatus.CLOSED: 0.15,       # 15% closed
        ProjectStatus.CANCELLED: 0.05     # 5% cancelled
    }

# ============================================================================
# MAIN SEEDING FUNCTION
# ============================================================================

def wipe_existing_data(session, engine):
    """Safely delete all data while preserving schema"""
    print("=" * 60)
    print("Wiping Existing Data")
    print("=" * 60)
    print()
    
    try:
        # Check which tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        print("Checking existing tables...")
        print(f"Found {len(existing_tables)} tables in database")
        print()
        
        # Delete in reverse dependency order, only if tables exist
        print("Deleting existing data...")
        
        # Define tables to delete in dependency order (child to parent)
        tables_to_delete = [
            ('AllocationFinancial', AllocationFinancial),
            ('RiskRegister', RiskRegister),
            ('Feedback360', Feedback360),
            ('BenchLedger', BenchLedger),
            ('PriorityScoring', PriorityScoring),
            ('ProjectRoleRequirements', ProjectRoleRequirements),
            ('ProjectRateRequirements', ProjectRateRequirements),
            ('ProjectDomain', ProjectDomain),
            ('EmployeeDomain', EmployeeDomain),
            ('EmployeeSkill', EmployeeSkill),
            ('Allocation', Allocation),
            ('RateCard', RateCard),
            ('FinancialMetrics', FinancialMetrics),
            ('Project', Project),
            ('Employee', Employee),
            ('Domain', Domain),
        ]
        
        deleted_count = 0
        skipped_count = 0
        
        for table_name, model_class in tables_to_delete:
            # Check if table exists (SQLAlchemy table name mapping)
            table_obj = model_class.__table__
            table_name_db = table_obj.name
            
            if table_name_db in existing_tables:
                try:
                    count = session.query(model_class).count()
                    if count > 0:
                        session.query(model_class).delete()
                        print(f"  ✓ Deleted {count} records from {table_name_db}")
                        deleted_count += 1
                    else:
                        print(f"  - {table_name_db} is empty (skipped)")
                        skipped_count += 1
                except Exception as e:
                    print(f"  ⚠ Warning: Could not delete from {table_name_db}: {e}")
                    session.rollback()
            else:
                print(f"  - {table_name_db} does not exist (skipped)")
                skipped_count += 1
        
        session.commit()
        print()
        print(f"✓ Data deletion complete: {deleted_count} tables cleaned, {skipped_count} tables skipped")
        return True
    except Exception as e:
        session.rollback()
        print(f"ERROR: Failed to wipe data: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_comprehensive():
    """Main comprehensive seeding function"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE DATABASE SEEDING")
    print("BenchCraft AI Resource Allocation System")
    print("=" * 60)
    print()
    
    # Initialize database
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    # Ensure all tables exist first
    print("Ensuring database tables exist...")
    Base.metadata.create_all(engine)
    print("✓ Database tables verified/created")
    print()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Initialize ChromaDB (clear existing embeddings)
    print("Initializing ChromaDB...")
    try:
        vector_tool = ChromaSearchTool()
        # Clear existing embeddings
        existing_data = vector_tool.collection.get()
        if existing_data and existing_data.get('ids'):
            vector_tool.collection.delete(ids=existing_data['ids'])
            print(f"  ✓ Cleared {len(existing_data['ids'])} existing embeddings from ChromaDB")
        else:
            print("  ✓ ChromaDB collection is ready")
    except Exception as e:
        print(f"  ⚠ Warning: Could not initialize ChromaDB: {e}")
        print("     Continuing with database seeding...")
        vector_tool = None
    
    try:
        # Step 1: Wipe existing data
        if not wipe_existing_data(session, engine):
            return False
        
        # Step 2: Create Domains
        print("\n" + "=" * 60)
        print("Creating Domains")
        print("=" * 60)
        domains_map = {}
        
        all_domains = []
        # Industry domains
        for domain_name in INDUSTRY_DOMAINS:
            domain = Domain(
                domain_name=domain_name,
                domain_code=domain_name.upper().replace(" ", "_").replace("&", "AND"),
                domain_type=DomainType.INDUSTRY_VERTICAL,
                description=f"{domain_name} industry expertise and domain knowledge",
                is_active=True,
                created_date=date.today() - timedelta(days=random.randint(30, 365))
            )
            session.add(domain)
            session.flush()
            domains_map[domain_name] = domain
            all_domains.append(domain)
            print(f"  ✓ Created domain: {domain_name}")
        
        # Technical domains
        for domain_name in TECHNICAL_DOMAINS:
            domain = Domain(
                domain_name=domain_name,
                domain_code=domain_name.upper().replace(" ", "_"),
                domain_type=DomainType.TECHNICAL_DOMAIN,
                description=f"{domain_name} technical expertise",
                is_active=True,
                created_date=date.today() - timedelta(days=random.randint(30, 365))
            )
            session.add(domain)
            session.flush()
            domains_map[domain_name] = domain
            all_domains.append(domain)
            print(f"  ✓ Created domain: {domain_name}")
        
        # Business domains
        for domain_name in BUSINESS_DOMAINS:
            domain = Domain(
                domain_name=domain_name,
                domain_code=domain_name.upper().replace(" ", "_"),
                domain_type=DomainType.BUSINESS_DOMAIN,
                description=f"{domain_name} business domain expertise",
                is_active=True,
                created_date=date.today() - timedelta(days=random.randint(30, 365))
            )
            session.add(domain)
            session.flush()
            domains_map[domain_name] = domain
            all_domains.append(domain)
            print(f"  ✓ Created domain: {domain_name}")
        
        session.commit()
        print(f"\n✓ Created {len(all_domains)} domains")
        
        # Step 3: Create Employees (80 employees for realistic volume)
        print("\n" + "=" * 60)
        print("Creating Employees")
        print("=" * 60)
        
        employees = []
        used_emails = set()
        role_dist = get_role_level_distribution()
        status_dist = get_status_distribution()
        
        num_employees = 80
        role_counts = {
            "JR": int(num_employees * role_dist["JR"]),
            "MID": int(num_employees * role_dist["MID"]),
            "SR": int(num_employees * role_dist["SR"]),
            "LEAD": int(num_employees * role_dist["LEAD"]),
            "PRINCIPAL": int(num_employees * role_dist["PRINCIPAL"])
        }
        
        role_levels_pool = []
        for role, count in role_counts.items():
            role_levels_pool.extend([role] * count)
        random.shuffle(role_levels_pool)
        
        for i in range(num_employees):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            role_level = role_levels_pool[i] if i < len(role_levels_pool) else random.choice(list(RoleLevel)).value
            
            # Generate unique email
            base_email = f"{first_name.lower()}.{last_name.lower()}@benchcraft.ai"
            email = base_email
            counter = 1
            while email in used_emails:
                email = f"{first_name.lower()}.{last_name.lower()}{counter}@benchcraft.ai"
                counter += 1
            used_emails.add(email)
            
            # Assign skills (5-10 skills per employee)
            num_skills = random.randint(5, 10)
            employee_skills = random.sample(SKILLS, num_skills)
            
            # Assign domains (1-3 domains per employee)
            num_domains = random.randint(1, 3)
            employee_domains_list = random.sample(all_domains, min(num_domains, len(all_domains)))
            
            # Generate bio
            domain_names = [d.domain_name for d in employee_domains_list]
            bio = generate_bio(role_level, employee_skills, domain_names)
            
            # Calculate CTC
            ctc_monthly = calculate_ctc(role_level)
            
            # Determine status (will be synced later based on allocations)
            # For now, assign initial status
            status = random.choices(
                list(status_dist.keys()),
                weights=list(status_dist.values())
            )[0]
            
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                role_level=role_level,
                ctc_monthly=ctc_monthly,
                currency="INR",
                base_location=random.choice(["Bangalore", "Hyderabad", "Pune", "Mumbai", "Chennai", "Delhi", "Gurgaon", "Noida"]),
                visa_status=random.choice(["Indian Citizen", "OCI", "Work Visa", "H1B", "L1"]),
                remote_pref=random.choice([True, False]),
                status=status,
                joined_date=date.today() - timedelta(days=random.randint(30, 2000)),
                bio_summary=bio
            )
            
            session.add(employee)
            session.flush()
            
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
            
            # Add domains
            for idx, domain in enumerate(employee_domains_list):
                emp_domain = EmployeeDomain(
                    emp_id=employee.id,
                    domain_id=domain.id,
                    proficiency=random.randint(3, 5),
                    years_of_experience=random.uniform(1.0, 10.0),
                    first_exposure_date=date.today() - timedelta(days=random.randint(100, 3000)),
                    last_used_date=date.today() - timedelta(days=random.randint(0, 180)),
                    is_primary_domain=(idx == 0)
                )
                session.add(emp_domain)
            
            # Add to ChromaDB (if available)
            if vector_tool:
                try:
                    vector_tool.add_employee_embedding(employee.id, bio)
                except Exception as e:
                    print(f"    ⚠ Warning: Could not add embedding for {first_name} {last_name}: {e}")
            
            employees.append(employee)
            if (i + 1) % 10 == 0:
                print(f"  Created {i+1}/{num_employees} employees...")
        
        session.commit()
        print(f"\n✓ Created {len(employees)} employees")
        
        # Step 4: Create Rate Cards
        print("\n" + "=" * 60)
        print("Creating Rate Cards")
        print("=" * 60)
        
        rate_cards_map = {}
        for employee in employees:
            # Base rate card
            hourly_cost = employee.ctc_monthly / 160.0
            base_rate = calculate_hourly_rate(employee.ctc_monthly, random.uniform(2.0, 3.5))
            
            base_rate_card = RateCard(
                emp_id=employee.id,
                domain_id=None,
                hourly_rate=round(base_rate, 2),
                currency="INR",
                effective_date=date.today() - timedelta(days=random.randint(30, 180)),
                expiry_date=None,
                rate_type=RateType.BASE,
                is_active=True
            )
            session.add(base_rate_card)
            session.flush()
            rate_cards_map[employee.id] = base_rate_card.id
            
            # Domain-specific rate cards (1-3 per employee)
            employee_domains = session.query(EmployeeDomain).filter(EmployeeDomain.emp_id == employee.id).all()
            if employee_domains:
                num_domain_rates = random.randint(1, min(3, len(employee_domains)))
                selected_domains = random.sample(employee_domains, num_domain_rates)
                
                for emp_domain in selected_domains:
                    domain_premium = random.uniform(1.15, 1.60)  # 15-60% premium
                    domain_rate = base_rate * domain_premium
                    
                    domain_rate_card = RateCard(
                        emp_id=employee.id,
                        domain_id=emp_domain.domain_id,
                        hourly_rate=round(domain_rate, 2),
                        currency="INR",
                        effective_date=date.today() - timedelta(days=random.randint(20, 150)),
                        expiry_date=None,
                        rate_type=RateType.DOMAIN_SPECIFIC,
                        is_active=True
                    )
                    session.add(domain_rate_card)
        
        session.commit()
        print(f"✓ Created rate cards for all employees")
        
        # Step 5: Create Projects (25 projects)
        print("\n" + "=" * 60)
        print("Creating Projects")
        print("=" * 60)
        
        projects = []
        status_dist = get_project_status_distribution()
        project_types = list(ProjectType)
        currencies = ["INR", "USD"]
        
        num_projects = 25
        status_counts = {
            ProjectStatus.PIPELINE: int(num_projects * status_dist[ProjectStatus.PIPELINE]),
            ProjectStatus.ACTIVE: int(num_projects * status_dist[ProjectStatus.ACTIVE]),
            ProjectStatus.ON_HOLD: int(num_projects * status_dist[ProjectStatus.ON_HOLD]),
            ProjectStatus.CLOSED: int(num_projects * status_dist[ProjectStatus.CLOSED]),
            ProjectStatus.CANCELLED: int(num_projects * status_dist[ProjectStatus.CANCELLED])
        }
        
        status_pool = []
        for status, count in status_counts.items():
            status_pool.extend([status] * count)
        random.shuffle(status_pool)
        
        for i in range(num_projects):
            client = random.choice(CLIENTS)
            description = random.choice(PROJECT_DESCRIPTIONS)
            status = status_pool[i] if i < len(status_pool) else random.choice(list(ProjectStatus))
            
            # Extract tech stack from description
            tech_stack_list = []
            for skill in SKILLS:
                if skill.lower() in description.lower():
                    tech_stack_list.append(skill)
            if not tech_stack_list:
                tech_stack_list = random.sample(SKILLS, random.randint(3, 6))
            tech_stack = ", ".join(tech_stack_list[:8])
            
            # Match industry domain to description
            industry_domain = "FinTech"
            if "healthcare" in description.lower() or "patient" in description.lower():
                industry_domain = "Healthcare"
            elif "retail" in description.lower() or "e-commerce" in description.lower():
                industry_domain = "Retail"
            elif "telecom" in description.lower() or "5g" in description.lower():
                industry_domain = "Telecom"
            elif "education" in description.lower() or "learning" in description.lower():
                industry_domain = "Education"
            elif "manufacturing" in description.lower() or "iot" in description.lower():
                industry_domain = "Manufacturing"
            else:
                industry_domain = random.choice(INDUSTRY_DOMAINS)
            
            # Calculate dates based on status
            if status == ProjectStatus.CLOSED:
                start_date = date.today() - timedelta(days=random.randint(180, 730))
                end_date = date.today() - timedelta(days=random.randint(1, 90))
            elif status == ProjectStatus.ACTIVE:
                start_date = date.today() - timedelta(days=random.randint(1, 180))
                end_date = date.today() + timedelta(days=random.randint(90, 365))
            elif status == ProjectStatus.PIPELINE:
                start_date = date.today() + timedelta(days=random.randint(30, 90))
                end_date = date.today() + timedelta(days=random.randint(180, 540))
            else:  # ON_HOLD or CANCELLED
                start_date = date.today() - timedelta(days=random.randint(30, 180))
                end_date = None if status == ProjectStatus.ON_HOLD else date.today() - timedelta(days=random.randint(1, 30))
            
            budget_cap = random.randint(5000000, 50000000)  # 50L to 5Cr INR
            
            project = Project(
                client_name=client,
                project_name=f"{client} {random.choice(['Digital', 'Enterprise', 'Cloud', 'AI', 'Platform'])} Project",
                description=description,
                budget_cap=budget_cap,
                billing_currency=random.choice(currencies),
                project_type=random.choice(project_types),
                industry_domain=industry_domain,
                start_date=start_date,
                end_date=end_date,
                status=status,
                probability=random.randint(50, 100) if status == ProjectStatus.PIPELINE else 100,
                tech_stack=tech_stack
            )
            
            session.add(project)
            session.flush()
            
            # Generate project_code
            current_year = date.today().year
            project.project_code = f"PROJ-{current_year}-{project.id:04d}"
            
            projects.append(project)
            print(f"  ✓ Created project: {project.project_code} - {project.project_name} ({status.value})")
        
        session.commit()
        print(f"\n✓ Created {len(projects)} projects")
        
        # Step 6: Create Project Domains and Requirements
        print("\n" + "=" * 60)
        print("Creating Project Domains and Requirements")
        print("=" * 60)
        
        for project in projects:
            # Project domains (1-3 per project)
            num_domains = random.randint(1, 3)
            project_domains_list = random.sample(all_domains, min(num_domains, len(all_domains)))
            
            for domain in project_domains_list:
                proj_domain = ProjectDomain(
                    proj_id=project.id,
                    domain_id=domain.id,
                    priority=random.choice(list(DomainPriority)),
                    weight=random.randint(5, 10),
                    requirements=f"Requires expertise in {domain.domain_name} domain"
                )
                session.add(proj_domain)
            
            # Project role requirements (for active and pipeline projects)
            if project.status in [ProjectStatus.ACTIVE, ProjectStatus.PIPELINE]:
                num_roles = random.randint(3, 6)
                selected_roles = random.sample(ROLE_NAMES, min(num_roles, len(ROLE_NAMES)))
                
                for role_name in selected_roles:
                    role_defaults = {
                        "Solution Architect": {"utilization": 25, "count": (1, 2)},
                        "Technical Architect": {"utilization": 30, "count": (1, 2)},
                        "Project Manager": {"utilization": 20, "count": (1, 1)},
                        "Senior Developer": {"utilization": 100, "count": (2, 5)},
                        "Developer": {"utilization": 100, "count": (3, 8)},
                        "Business Analyst": {"utilization": 50, "count": (1, 3)},
                        "QA Engineer": {"utilization": 50, "count": (1, 4)},
                        "Tech Lead": {"utilization": 75, "count": (1, 2)},
                        "DevOps Engineer": {"utilization": 50, "count": (1, 2)}
                    }
                    defaults = role_defaults.get(role_name, {"utilization": 100, "count": (1, 3)})
                    
                    role_req = ProjectRoleRequirements(
                        proj_id=project.id,
                        role_name=role_name,
                        required_count=random.randint(*defaults["count"]),
                        utilization_percentage=defaults["utilization"]
                    )
                    session.add(role_req)
            
            # Project rate requirements (for some projects)
            if project.status in [ProjectStatus.ACTIVE, ProjectStatus.PIPELINE] and random.random() < 0.6:
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
                            rate_req = ProjectRateRequirements(
                                proj_id=project.id,
                                domain_id=proj_domain.domain_id,
                                min_acceptable_rate=round(avg_rate * 0.75, 2),
                                max_acceptable_rate=round(avg_rate * 1.25, 2),
                                preferred_rate=round(avg_rate, 2),
                                rate_negotiation_status=random.choice(list(RateNegotiationStatus)),
                                rate_notes=f"Rate requirements for {proj_domain.domain.domain_name} domain"
                            )
                            session.add(rate_req)
        
        session.commit()
        print("✓ Created project domains and requirements")
        
        # Step 7: Create Allocations (Complex scenarios)
        print("\n" + "=" * 60)
        print("Creating Allocations")
        print("=" * 60)
        
        active_projects = [p for p in projects if p.status == ProjectStatus.ACTIVE]
        pipeline_projects = [p for p in projects if p.status == ProjectStatus.PIPELINE]
        closed_projects = [p for p in projects if p.status == ProjectStatus.CLOSED]
        
        allocated_employees = set()
        allocation_count = 0
        
        # Allocate to active projects (70% of employees)
        num_to_allocate = int(len(employees) * 0.70)
        employees_to_allocate = random.sample(employees, min(num_to_allocate, len(employees)))
        
        for project in active_projects:
            # Determine number of allocations for this project
            num_allocations = random.randint(3, 8)
            available_employees = [e for e in employees_to_allocate if e.id not in allocated_employees]
            
            if not available_employees:
                break
            
            selected_employees = random.sample(available_employees, min(num_allocations, len(available_employees)))
            
            for employee in selected_employees:
                rate_card_id = rate_cards_map.get(employee.id)
                rate_card = session.query(RateCard).filter(RateCard.id == rate_card_id).first()
                
                # Calculate dates
                alloc_start = project.start_date + timedelta(days=random.randint(0, 30))
                alloc_end = project.end_date - timedelta(days=random.randint(0, 30)) if project.end_date else None
                
                # Determine allocation scenario
                scenario = random.choices(
                    ["optimal", "over_allocated", "under_allocated", "partial", "trainee"],
                    weights=[0.50, 0.10, 0.10, 0.25, 0.05]
                )[0]
                
                if scenario == "optimal":
                    allocation_pct = 100
                    billable_pct = 100
                    internal_pct = 100
                    is_trainee = False
                elif scenario == "over_allocated":
                    allocation_pct = 100
                    billable_pct = 100
                    internal_pct = random.randint(70, 90)  # Works less than billed
                    is_trainee = False
                elif scenario == "under_allocated":
                    allocation_pct = random.randint(50, 80)
                    billable_pct = 100
                    internal_pct = allocation_pct + random.randint(10, 20)  # Works more than billed
                    is_trainee = False
                elif scenario == "partial":
                    allocation_pct = random.randint(30, 70)
                    billable_pct = 100
                    internal_pct = allocation_pct
                    is_trainee = False
                else:  # trainee
                    is_trainee = True
                    allocation_pct = 0
                    billable_pct = 0
                    internal_pct = 100
                
                billing_rate = rate_card.hourly_rate if rate_card and not is_trainee else 0
                mentoring_primary_emp_id = None
                
                # If trainee, find a primary resource
                if is_trainee:
                    primary_allocations = session.query(Allocation).filter(
                        Allocation.proj_id == project.id,
                        Allocation.is_trainee == False,
                        Allocation.emp_id != employee.id
                    ).all()
                    
                    if primary_allocations:
                        mentoring_primary_emp_id = random.choice(primary_allocations).emp_id
                    else:
                        is_trainee = False
                        allocation_pct = 100
                        billable_pct = 100
                        internal_pct = 100
                        billing_rate = rate_card.hourly_rate if rate_card else 0
                
                allocation = Allocation(
                    emp_id=employee.id,
                    proj_id=project.id,
                    start_date=alloc_start,
                    end_date=alloc_end,
                    billing_rate=billing_rate,
                    is_revealed=random.choice([True, False]) if not is_trainee else False,
                    allocation_percentage=allocation_pct,
                    billable_percentage=billable_pct,
                    internal_allocation_percentage=internal_pct,
                    is_trainee=is_trainee,
                    mentoring_primary_emp_id=mentoring_primary_emp_id,
                    rate_card_id=rate_card_id
                )
                session.add(allocation)
                session.flush()
                
                # Create AllocationFinancial
                total_hours = 160
                if is_trainee:
                    billed_hours = 0
                    cost_hours = int((total_hours * internal_pct) / 100)
                    estimated_revenue = 0.0
                else:
                    billed_hours = int((total_hours * allocation_pct * billable_pct) / 10000)
                    cost_hours = int((total_hours * internal_pct) / 100)
                    estimated_revenue = billing_rate * billed_hours if billing_rate else 0.0
                
                cost_rate = employee.ctc_monthly / 160.0
                estimated_cost = cost_rate * cost_hours
                gross_margin = ((estimated_revenue - estimated_cost) / estimated_revenue * 100) if estimated_revenue > 0 else 0
                
                alloc_financial = AllocationFinancial(
                    allocation_id=allocation.id,
                    rate_card_id=rate_card_id,
                    billing_rate=billing_rate if not is_trainee else 0,
                    cost_rate=round(cost_rate, 2),
                    gross_margin_percentage=round(gross_margin, 2),
                    estimated_revenue=round(estimated_revenue, 2),
                    estimated_cost=round(estimated_cost, 2),
                    actual_revenue=round(estimated_revenue * random.uniform(0.95, 1.05), 2),
                    actual_cost=round(estimated_cost * random.uniform(0.95, 1.05), 2),
                    billed_hours=billed_hours,
                    utilized_hours=cost_hours,
                    total_hours_in_period=total_hours
                )
                session.add(alloc_financial)
                
                allocated_employees.add(employee.id)
                allocation_count += 1
        
        # Allocate some employees to multiple projects (10% multi-project allocation)
        multi_project_employees = random.sample(
            [e for e in employees if e.id in allocated_employees],
            min(int(len(employees) * 0.10), len([e for e in employees if e.id in allocated_employees]))
        )
        
        for employee in multi_project_employees:
            # Find another active project
            existing_allocations = session.query(Allocation).filter(Allocation.emp_id == employee.id).all()
            existing_project_ids = {a.proj_id for a in existing_allocations}
            available_projects = [p for p in active_projects if p.id not in existing_project_ids]
            
            if available_projects:
                project = random.choice(available_projects)
                rate_card_id = rate_cards_map.get(employee.id)
                rate_card = session.query(RateCard).filter(RateCard.id == rate_card_id).first()
                
                # Partial allocation for second project
                allocation_pct = random.randint(20, 50)
                billable_pct = 100
                internal_pct = allocation_pct
                
                alloc_start = project.start_date + timedelta(days=random.randint(0, 30))
                alloc_end = project.end_date - timedelta(days=random.randint(0, 30)) if project.end_date else None
                
                allocation = Allocation(
                    emp_id=employee.id,
                    proj_id=project.id,
                    start_date=alloc_start,
                    end_date=alloc_end,
                    billing_rate=rate_card.hourly_rate if rate_card else 0,
                    is_revealed=random.choice([True, False]),
                    allocation_percentage=allocation_pct,
                    billable_percentage=billable_pct,
                    internal_allocation_percentage=internal_pct,
                    is_trainee=False,
                    rate_card_id=rate_card_id
                )
                session.add(allocation)
                session.flush()
                
                # Financials
                total_hours = 160
                billed_hours = int((total_hours * allocation_pct * billable_pct) / 10000)
                cost_hours = int((total_hours * internal_pct) / 100)
                estimated_revenue = rate_card.hourly_rate * billed_hours if rate_card else 0.0
                cost_rate = employee.ctc_monthly / 160.0
                estimated_cost = cost_rate * cost_hours
                gross_margin = ((estimated_revenue - estimated_cost) / estimated_revenue * 100) if estimated_revenue > 0 else 0
                
                alloc_financial = AllocationFinancial(
                    allocation_id=allocation.id,
                    rate_card_id=rate_card_id,
                    billing_rate=rate_card.hourly_rate if rate_card else 0,
                    cost_rate=round(cost_rate, 2),
                    gross_margin_percentage=round(gross_margin, 2),
                    estimated_revenue=round(estimated_revenue, 2),
                    estimated_cost=round(estimated_cost, 2),
                    actual_revenue=round(estimated_revenue * random.uniform(0.95, 1.05), 2),
                    actual_cost=round(estimated_cost * random.uniform(0.95, 1.05), 2),
                    billed_hours=billed_hours,
                    utilized_hours=cost_hours,
                    total_hours_in_period=total_hours
                )
                session.add(alloc_financial)
                allocation_count += 1
        
        # Create historical allocations for closed projects
        for project in closed_projects[:5]:  # First 5 closed projects
            num_allocations = random.randint(2, 5)
            available_employees = [e for e in employees if e.id not in allocated_employees]
            
            if not available_employees:
                available_employees = random.sample(employees, min(num_allocations, len(employees)))
            
            selected_employees = random.sample(available_employees, min(num_allocations, len(available_employees)))
            
            for employee in selected_employees:
                rate_card_id = rate_cards_map.get(employee.id)
                rate_card = session.query(RateCard).filter(RateCard.id == rate_card_id).first()
                
                alloc_start = project.start_date + timedelta(days=random.randint(0, 30))
                alloc_end = project.end_date - timedelta(days=random.randint(0, 30))
                
                allocation = Allocation(
                    emp_id=employee.id,
                    proj_id=project.id,
                    start_date=alloc_start,
                    end_date=alloc_end,
                    billing_rate=rate_card.hourly_rate if rate_card else 0,
                    is_revealed=True,
                    allocation_percentage=100,
                    billable_percentage=100,
                    internal_allocation_percentage=100,
                    is_trainee=False,
                    rate_card_id=rate_card_id
                )
                session.add(allocation)
                session.flush()
                
                # Financials
                total_hours = 160
                billed_hours = 160
                cost_hours = 160
                estimated_revenue = rate_card.hourly_rate * billed_hours if rate_card else 0.0
                cost_rate = employee.ctc_monthly / 160.0
                estimated_cost = cost_rate * cost_hours
                gross_margin = ((estimated_revenue - estimated_cost) / estimated_revenue * 100) if estimated_revenue > 0 else 0
                
                alloc_financial = AllocationFinancial(
                    allocation_id=allocation.id,
                    rate_card_id=rate_card_id,
                    billing_rate=rate_card.hourly_rate if rate_card else 0,
                    cost_rate=round(cost_rate, 2),
                    gross_margin_percentage=round(gross_margin, 2),
                    estimated_revenue=round(estimated_revenue, 2),
                    estimated_cost=round(estimated_cost, 2),
                    actual_revenue=round(estimated_revenue * random.uniform(0.95, 1.05), 2),
                    actual_cost=round(estimated_cost * random.uniform(0.95, 1.05), 2),
                    billed_hours=billed_hours,
                    utilized_hours=cost_hours,
                    total_hours_in_period=total_hours
                )
                session.add(alloc_financial)
                allocation_count += 1
        
        session.commit()
        print(f"✓ Created {allocation_count} allocations")
        
        # Step 8: Sync Employee Statuses
        print("\n" + "=" * 60)
        print("Syncing Employee Statuses")
        print("=" * 60)
        
        for employee in employees:
            sync_employee_status(employee, session)
        
        session.commit()
        print("✓ Synced all employee statuses")
        
        # Step 9: Create Bench Ledger Entries
        print("\n" + "=" * 60)
        print("Creating Bench Ledger Entries")
        print("=" * 60)
        
        bench_employees = [e for e in employees if e.status == EmployeeStatus.BENCH]
        for employee in bench_employees:
            # Check for last allocation
            last_allocation = session.query(Allocation).filter(
                Allocation.emp_id == employee.id
            ).order_by(Allocation.end_date.desc()).first()
            
            if last_allocation and last_allocation.end_date:
                bench_start = last_allocation.end_date
                days_on_bench = (date.today() - bench_start).days
            else:
                bench_start = date.today() - timedelta(days=random.randint(1, 90))
                days_on_bench = (date.today() - bench_start).days
            
            cost_per_day = employee.ctc_monthly / 30.0
            cost_incurred = cost_per_day * days_on_bench
            
            bench_entry = BenchLedger(
                emp_id=employee.id,
                start_date=bench_start,
                end_date=None,
                reason=random.choice(["Project End", "Hired", "Training", "Bench", "Between Projects"]),
                cost_incurred=round(cost_incurred, 2)
            )
            session.add(bench_entry)
        
        session.commit()
        print(f"✓ Created bench ledger entries for {len(bench_employees)} employees")
        
        # Step 10: Create Feedback Entries
        print("\n" + "=" * 60)
        print("Creating Feedback Entries")
        print("=" * 60)
        
        feedback_tags = ["Delivery", "Innovation", "Communication", "Technical Excellence", "Leadership", 
                        "Problem Solving", "Collaboration", "Quality", "Timeliness", "Client Satisfaction"]
        
        feedback_count = 0
        for project in active_projects + closed_projects[:5]:
            project_allocations = session.query(Allocation).filter(
                Allocation.proj_id == project.id,
                Allocation.is_trainee == False
            ).all()
            
            if project_allocations:
                # Create feedback for 30-50% of allocations
                num_feedbacks = max(1, int(len(project_allocations) * random.uniform(0.3, 0.5)))
                selected_allocations = random.sample(project_allocations, min(num_feedbacks, len(project_allocations)))
                
                for allocation in selected_allocations:
                    feedback = Feedback360(
                        emp_id=allocation.emp_id,
                        proj_id=project.id,
                        rating=random.randint(3, 5),
                        feedback=random.choice([
                            f"Strong performance on {project.project_name}. Demonstrated excellent technical skills and collaboration.",
                            f"Outstanding contribution to {project.project_name}. Consistently delivered high-quality work on time.",
                            f"Excellent team player on {project.project_name}. Proactive in problem-solving and knowledge sharing.",
                            f"Solid performance on {project.project_name}. Met all deliverables and exceeded expectations in some areas.",
                            f"Good work on {project.project_name}. Reliable and professional approach to project tasks."
                        ]),
                        tags=", ".join(random.sample(feedback_tags, random.randint(2, 5)))
                    )
                    session.add(feedback)
                    feedback_count += 1
        
        session.commit()
        print(f"✓ Created {feedback_count} feedback entries")
        
        # Step 11: Create Risk Register Entries
        print("\n" + "=" * 60)
        print("Creating Risk Register Entries")
        print("=" * 60)
        
        risk_count = 0
        # Create risks for 15-20% of employees
        employees_with_risks = random.sample(employees, int(len(employees) * random.uniform(0.15, 0.20)))
        
        for employee in employees_with_risks:
            # Determine risk type based on employee status
            if employee.status == EmployeeStatus.NOTICE_PERIOD:
                risk_type = RiskType.NOTICE_PERIOD
                severity = random.choice([RiskSeverity.HIGH, RiskSeverity.CRITICAL])
            elif employee.status == EmployeeStatus.ALLOCATED:
                risk_type = random.choice([RiskType.CRITICAL_ROLE, RiskType.SINGLE_POINT_FAILURE, RiskType.PERFORMANCE])
                severity = random.choice([RiskSeverity.MEDIUM, RiskSeverity.HIGH])
            else:
                risk_type = random.choice([RiskType.SKILL_GAP, RiskType.PERFORMANCE])
                severity = random.choice([RiskSeverity.LOW, RiskSeverity.MEDIUM])
            
            # Assign to project if allocated
            project_id = None
            if employee.status == EmployeeStatus.ALLOCATED:
                employee_allocations = session.query(Allocation).filter(
                    Allocation.emp_id == employee.id,
                    (Allocation.end_date.is_(None)) | (Allocation.end_date >= date.today())
                ).all()
                if employee_allocations:
                    project_id = random.choice(employee_allocations).proj_id
            
            # Mitigation owner (different employee)
            mitigation_owner_id = random.choice([e.id for e in employees if e.id != employee.id])
            
            risk_descriptions = {
                RiskType.NOTICE_PERIOD: f"{employee.first_name} {employee.last_name} has submitted resignation. Notice period ends in {random.randint(15, 90)} days.",
                RiskType.CRITICAL_ROLE: f"{employee.first_name} {employee.last_name} is in a critical role with no backup resource available.",
                RiskType.SINGLE_POINT_FAILURE: f"{employee.first_name} {employee.last_name} is the sole resource with specific domain knowledge required for project success.",
                RiskType.SKILL_GAP: f"Skill gap identified for {employee.first_name} {employee.last_name} in upcoming project requirements.",
                RiskType.PERFORMANCE: f"Performance concerns identified for {employee.first_name} {employee.last_name}. Requires monitoring and support."
            }
            
            mitigation_plans = {
                RiskType.NOTICE_PERIOD: "Initiate knowledge transfer sessions. Identify and onboard replacement resource. Cross-train backup team members.",
                RiskType.CRITICAL_ROLE: "Identify backup resource. Document critical processes. Create knowledge base. Plan for resource rotation.",
                RiskType.SINGLE_POINT_FAILURE: "Document domain knowledge. Train additional resources. Create backup plan. Reduce dependency.",
                RiskType.SKILL_GAP: "Provide targeted training. Assign mentor. Create learning plan. Consider upskilling vs hiring decision.",
                RiskType.PERFORMANCE: "Performance improvement plan. Regular check-ins. Provide additional support and resources. Set clear expectations."
            }
            
            risk = RiskRegister(
                emp_id=employee.id,
                project_id=project_id,
                risk_type=risk_type,
                severity=severity,
                description=risk_descriptions[risk_type],
                mitigation_plan=mitigation_plans[risk_type],
                mitigation_owner_emp_id=mitigation_owner_id,
                identified_date=date.today() - timedelta(days=random.randint(1, 60)),
                target_resolution_date=date.today() + timedelta(days=random.randint(30, 120)),
                status=random.choice([RiskStatus.OPEN, RiskStatus.IN_PROGRESS, RiskStatus.MITIGATED])
            )
            session.add(risk)
            risk_count += 1
        
        session.commit()
        print(f"✓ Created {risk_count} risk register entries")
        
        # Step 12: Create Priority Scores
        print("\n" + "=" * 60)
        print("Creating Priority Scores")
        print("=" * 60)
        
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
                    days_on_bench = random.randint(1, 90)
            
            # Calculate priority score
            priority_score = (max_domain_rate * 0.7) + (base_rate_value * 0.3) + (days_on_bench * 0.5)
            
            # Determine priority tier
            if priority_score >= 200:
                tier = PriorityTier.CRITICAL
            elif priority_score >= 150:
                tier = PriorityTier.HIGH
            elif priority_score >= 100:
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
        print("✓ Created priority scores for all employees")
        
        # Step 13: Create Financial Metrics
        print("\n" + "=" * 60)
        print("Creating Financial Metrics")
        print("=" * 60)
        
        # Company-wide metrics
        total_revenue = sum([
            af.actual_revenue for af in session.query(AllocationFinancial).all()
        ])
        total_cost = sum([
            af.actual_cost for af in session.query(AllocationFinancial).all()
        ])
        gross_profit = total_revenue - total_cost
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        company_metrics = FinancialMetrics(
            emp_id=None,
            proj_id=None,
            target_gross_margin_percentage=50.0,
            actual_gross_margin_percentage=round(gross_margin, 2),
            total_revenue=round(total_revenue, 2),
            total_cost=round(total_cost, 2),
            gross_profit=round(gross_profit, 2),
            period_start_date=date.today().replace(day=1),
            period_end_date=date.today(),
            period_type=PeriodType.MONTHLY
        )
        session.add(company_metrics)
        
        # Project-specific metrics
        for project in active_projects[:10]:
            project_allocations = session.query(Allocation).filter(Allocation.proj_id == project.id).all()
            if project_allocations:
                project_revenue = sum([
                    af.actual_revenue for af in session.query(AllocationFinancial).join(Allocation).filter(
                        Allocation.proj_id == project.id
                    ).all()
                ])
                project_cost = sum([
                    af.actual_cost for af in session.query(AllocationFinancial).join(Allocation).filter(
                        Allocation.proj_id == project.id
                    ).all()
                ])
                project_profit = project_revenue - project_cost
                project_margin = (project_profit / project_revenue * 100) if project_revenue > 0 else 0
                
                project_metrics = FinancialMetrics(
                    emp_id=None,
                    proj_id=project.id,
                    target_gross_margin_percentage=50.0,
                    actual_gross_margin_percentage=round(project_margin, 2),
                    total_revenue=round(project_revenue, 2),
                    total_cost=round(project_cost, 2),
                    gross_profit=round(project_profit, 2),
                    period_start_date=project.start_date,
                    period_end_date=date.today(),
                    period_type=PeriodType.PROJECT_LIFETIME
                )
                session.add(project_metrics)
        
        session.commit()
        print("✓ Created financial metrics")
        
        # Final Summary
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  ✓ {len(employees)} employees created")
        print(f"  ✓ {len(projects)} projects created")
        print(f"  ✓ {len(all_domains)} domains created")
        print(f"  ✓ {allocation_count} allocations created")
        print(f"  ✓ {feedback_count} feedback entries created")
        print(f"  ✓ {risk_count} risk register entries created")
        print(f"  ✓ Employee domains, skills, and rate cards assigned")
        print(f"  ✓ Project domains and requirements configured")
        print(f"  ✓ Bench ledger entries created")
        print(f"  ✓ Priority scores calculated")
        print(f"  ✓ Financial metrics generated")
        print(f"  ✓ ChromaDB embeddings generated")
        print()
        print("The database is now populated with enterprise-grade sample data!")
        print("All features are ready for demonstration.")
        
    except Exception as e:
        session.rollback()
        print(f"\nERROR: Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
    
    return True

if __name__ == '__main__':
    success = seed_comprehensive()
    sys.exit(0 if success else 1)
