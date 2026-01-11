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

from models import Base, Employee, Project, EmployeeSkill, RoleLevel, EmployeeStatus, ProjectStatus
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
        for i in range(20):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            role_level = random.choice(list(RoleLevel))
            
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
                email=f"{first_name.lower()}.{last_name.lower()}@benchcraft.ai",
                role_level=role_level,
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
        
        # Create 5 projects
        print("\nCreating projects...")
        projects = []
        for i in range(5):
            client = random.choice(CLIENTS)
            description = random.choice(PROJECT_DESCRIPTIONS)
            
            # Extract tech stack from description
            tech_stack_list = []
            for skill in SKILLS:
                if skill.lower() in description.lower():
                    tech_stack_list.append(skill)
            tech_stack = ", ".join(tech_stack_list[:5]) if tech_stack_list else "Python, JavaScript"
            
            project = Project(
                client_name=client,
                project_name=f"{client} Platform",
                description=description,
                budget_cap=random.randint(50000, 200000),
                start_date=date.today() + timedelta(days=random.randint(-30, 30)),
                end_date=date.today() + timedelta(days=random.randint(90, 365)),
                status=random.choice([ProjectStatus.PIPELINE, ProjectStatus.ACTIVE]),
                probability=random.randint(50, 100) if i < 2 else 100,
                tech_stack=tech_stack
            )
            
            session.add(project)
            projects.append(project)
            print(f"  Created project {i+1}/5: {client} Platform")
        
        session.commit()
        print("\n✅ Database seeded successfully!")
        print(f"   - {len(employees)} employees created")
        print(f"   - {len(projects)} projects created")
        print(f"   - ChromaDB embeddings generated")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    seed_database()
