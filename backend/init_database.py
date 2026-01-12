"""
Consolidated Database Initialization Script
Combines all migrations and seed data into a single script

This script:
1. Creates all database tables
2. Runs all migrations in the correct order
3. Seeds the database with sample data

Run this script once to set up a fresh database or update an existing one.
"""
import sys
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from models import Base

def create_all_tables(engine):
    """Create all database tables from models"""
    print("=" * 60)
    print("Step 1: Creating Database Tables")
    print("=" * 60)
    print()
    
    try:
        Base.metadata.create_all(engine)
        print("✓ All database tables created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def migrate_risk_register_table(conn):
    """Ensure risk_register table has correct schema"""
    print("\n" + "=" * 60)
    print("Step 2.1: Migrating risk_register Table")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    # Check if risk_register table exists
    if 'risk_register' not in inspector.get_table_names():
        print("Creating risk_register table...")
        try:
            conn.execute(text("""
                CREATE TABLE risk_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emp_id INTEGER NOT NULL,
                    project_id INTEGER,
                    risk_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    description TEXT,
                    mitigation_plan TEXT,
                    mitigation_owner_emp_id INTEGER,
                    identified_date DATE NOT NULL,
                    target_resolution_date DATE,
                    status VARCHAR(20) DEFAULT 'OPEN',
                    FOREIGN KEY (emp_id) REFERENCES employees(id),
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (mitigation_owner_emp_id) REFERENCES employees(id)
                )
            """))
            conn.commit()
            print("✓ Successfully created risk_register table")
        except Exception as e:
            print(f"ERROR: Failed to create risk_register table: {str(e)}")
            conn.rollback()
            return False
    else:
        print("risk_register table already exists")
        
        # Get existing columns
        columns = {col['name']: col for col in inspector.get_columns('risk_register')}
        
        # Check if project_id column exists
        if 'project_id' not in columns:
            # Check if proj_id exists (wrong column name)
            if 'proj_id' in columns:
                print("Found 'proj_id' column - renaming to 'project_id'...")
                try:
                    conn.execute(text("""
                        CREATE TABLE risk_register_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            emp_id INTEGER NOT NULL,
                            project_id INTEGER,
                            risk_type VARCHAR(50) NOT NULL,
                            severity VARCHAR(20) NOT NULL,
                            description TEXT,
                            mitigation_plan TEXT,
                            mitigation_owner_emp_id INTEGER,
                            identified_date DATE NOT NULL,
                            target_resolution_date DATE,
                            status VARCHAR(20) DEFAULT 'OPEN',
                            FOREIGN KEY (emp_id) REFERENCES employees(id),
                            FOREIGN KEY (project_id) REFERENCES projects(id),
                            FOREIGN KEY (mitigation_owner_emp_id) REFERENCES employees(id)
                        )
                    """))
                    
                    conn.execute(text("""
                        INSERT INTO risk_register_new 
                        (id, emp_id, project_id, risk_type, severity, description, mitigation_plan, 
                         mitigation_owner_emp_id, identified_date, target_resolution_date, status)
                        SELECT 
                            id, emp_id, proj_id, risk_type, severity, description, mitigation_plan,
                            mitigation_owner_emp_id, identified_date, target_resolution_date, status
                        FROM risk_register
                    """))
                    
                    conn.execute(text("DROP TABLE risk_register"))
                    conn.execute(text("ALTER TABLE risk_register_new RENAME TO risk_register"))
                    conn.commit()
                    print("✓ Successfully renamed proj_id to project_id")
                except Exception as e:
                    print(f"ERROR: Failed to rename column: {str(e)}")
                    conn.rollback()
                    return False
            else:
                print("Adding project_id column...")
                try:
                    conn.execute(text("ALTER TABLE risk_register ADD COLUMN project_id INTEGER"))
                    conn.commit()
                    print("✓ Successfully added project_id column")
                except Exception as e:
                    print(f"ERROR: Failed to add column: {str(e)}")
                    conn.rollback()
                    return False
        else:
            print("✓ project_id column already exists with correct name")
    
    return True

def migrate_project_wizard_fields(conn):
    """Add project wizard fields"""
    print("\n" + "=" * 60)
    print("Step 2.2: Migrating Project Wizard Fields")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'projects' not in inspector.get_table_names():
        print("ERROR: projects table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('projects')]
    
    # Add project_code
    if 'project_code' not in columns:
        print("Adding project_code column...")
        conn.execute(text("ALTER TABLE projects ADD COLUMN project_code TEXT UNIQUE"))
        # Generate project_code for existing projects
        result = conn.execute(text("SELECT id FROM projects WHERE project_code IS NULL"))
        projects = result.fetchall()
        for (project_id,) in projects:
            result = conn.execute(text("SELECT start_date FROM projects WHERE id = ?"), (project_id,))
            row = result.fetchone()
            if row and row[0]:
                year = str(row[0])[:4]
            else:
                year = str(date.today().year)
            project_code = f"PROJ-{year}-{project_id}"
            conn.execute(text("UPDATE projects SET project_code = ? WHERE id = ?"), (project_code, project_id))
        conn.commit()
        print(f"✓ Generated project_code for {len(projects)} existing projects")
    else:
        print("✓ project_code column already exists")
    
    # Add project_type
    if 'project_type' not in columns:
        print("Adding project_type column...")
        conn.execute(text("ALTER TABLE projects ADD COLUMN project_type TEXT"))
        conn.commit()
        print("✓ Added project_type column")
    else:
        print("✓ project_type column already exists")
    
    # Add billing_currency
    if 'billing_currency' not in columns:
        print("Adding billing_currency column...")
        conn.execute(text("ALTER TABLE projects ADD COLUMN billing_currency TEXT DEFAULT 'USD'"))
        conn.execute(text("UPDATE projects SET billing_currency = 'USD' WHERE billing_currency IS NULL"))
        conn.commit()
        print("✓ Added billing_currency column")
    else:
        print("✓ billing_currency column already exists")
    
    # Add industry_domain
    if 'industry_domain' not in columns:
        print("Adding industry_domain column...")
        conn.execute(text("ALTER TABLE projects ADD COLUMN industry_domain TEXT"))
        conn.commit()
        print("✓ Added industry_domain column")
    else:
        print("✓ industry_domain column already exists")
    
    # Create project_role_requirements table
    if 'project_role_requirements' not in inspector.get_table_names():
        print("Creating project_role_requirements table...")
        conn.execute(text("""
            CREATE TABLE project_role_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proj_id INTEGER NOT NULL,
                role_name TEXT NOT NULL,
                required_count INTEGER NOT NULL DEFAULT 1,
                utilization_percentage INTEGER NOT NULL DEFAULT 100,
                FOREIGN KEY (proj_id) REFERENCES projects (id)
            )
        """))
        conn.commit()
        print("✓ Created project_role_requirements table")
    else:
        print("✓ project_role_requirements table already exists")
    
    return True

def migrate_add_rate_card_id(conn):
    """Add rate_card_id to allocations"""
    print("\n" + "=" * 60)
    print("Step 2.3: Adding rate_card_id to Allocations")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'allocations' not in inspector.get_table_names():
        print("ERROR: allocations table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('allocations')]
    
    if 'rate_card_id' not in columns:
        print("Adding rate_card_id column...")
        conn.execute(text("ALTER TABLE allocations ADD COLUMN rate_card_id INTEGER"))
        conn.commit()
        print("✓ Added rate_card_id column")
    else:
        print("✓ rate_card_id column already exists")
    
    return True

def migrate_add_allocation_billable_percentage(conn):
    """Add allocation_percentage and billable_percentage to allocations"""
    print("\n" + "=" * 60)
    print("Step 2.4: Adding Allocation and Billable Percentage Fields")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'allocations' not in inspector.get_table_names():
        print("ERROR: allocations table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('allocations')]
    
    if 'allocation_percentage' not in columns:
        print("Adding allocation_percentage column...")
        conn.execute(text("""
            ALTER TABLE allocations 
            ADD COLUMN allocation_percentage INTEGER NOT NULL DEFAULT 100
        """))
        conn.commit()
        print("✓ Added allocation_percentage column")
    else:
        print("✓ allocation_percentage column already exists")
    
    if 'billable_percentage' not in columns:
        print("Adding billable_percentage column...")
        conn.execute(text("""
            ALTER TABLE allocations 
            ADD COLUMN billable_percentage INTEGER NOT NULL DEFAULT 100
        """))
        conn.commit()
        print("✓ Added billable_percentage column")
    else:
        print("✓ billable_percentage column already exists")
    
    # Migrate existing utilization data
    if 'utilization' in columns:
        print("Migrating existing utilization data to allocation_percentage...")
        result = conn.execute(text("""
            UPDATE allocations 
            SET allocation_percentage = COALESCE(utilization, 100)
            WHERE allocation_percentage = 100 AND utilization IS NOT NULL
        """))
        conn.commit()
        print(f"✓ Migrated {result.rowcount} records")
    
    return True

def migrate_add_shadow_and_internal_allocation(conn):
    """Add shadow resource and internal allocation fields"""
    print("\n" + "=" * 60)
    print("Step 2.5: Adding Shadow Resource and Internal Allocation Fields")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'allocations' not in inspector.get_table_names():
        print("ERROR: allocations table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('allocations')]
    
    # Add is_trainee
    if 'is_trainee' not in columns:
        print("Adding is_trainee column...")
        conn.execute(text("""
            ALTER TABLE allocations
            ADD COLUMN is_trainee BOOLEAN NOT NULL DEFAULT 0
        """))
        conn.commit()
        print("✓ Added is_trainee column")
    else:
        print("✓ is_trainee column already exists")
    
    # Add mentoring_primary_emp_id
    if 'mentoring_primary_emp_id' not in columns:
        print("Adding mentoring_primary_emp_id column...")
        conn.execute(text("""
            ALTER TABLE allocations
            ADD COLUMN mentoring_primary_emp_id INTEGER
        """))
        conn.commit()
        print("✓ Added mentoring_primary_emp_id column")
    else:
        print("✓ mentoring_primary_emp_id column already exists")
    
    # Add internal_allocation_percentage
    if 'internal_allocation_percentage' not in columns:
        print("Adding internal_allocation_percentage column...")
        conn.execute(text("""
            ALTER TABLE allocations
            ADD COLUMN internal_allocation_percentage INTEGER NOT NULL DEFAULT 100
        """))
        conn.commit()
        print("✓ Added internal_allocation_percentage column")
    else:
        print("✓ internal_allocation_percentage column already exists")
    
    # Set default values for existing records
    print("Setting default values for existing records...")
    result = conn.execute(text("""
        UPDATE allocations
        SET internal_allocation_percentage = COALESCE(allocation_percentage, utilization, 100)
        WHERE internal_allocation_percentage = 100 
        AND (allocation_percentage IS NOT NULL OR utilization IS NOT NULL)
    """))
    conn.commit()
    print(f"✓ Updated {result.rowcount} existing allocations")
    
    # Create indexes
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_allocations_is_trainee 
            ON allocations(is_trainee)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_allocations_mentoring_primary 
            ON allocations(mentoring_primary_emp_id)
        """))
        conn.commit()
        print("✓ Created indexes")
    except Exception as e:
        print(f"Note: Indexes may already exist: {e}")
    
    return True

def migrate_add_total_hours_in_period(conn):
    """Add total_hours_in_period to allocation_financials"""
    print("\n" + "=" * 60)
    print("Step 2.6: Adding total_hours_in_period to Allocation Financials")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'allocation_financials' not in inspector.get_table_names():
        print("ERROR: allocation_financials table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('allocation_financials')]
    
    if 'total_hours_in_period' not in columns:
        print("Adding total_hours_in_period column...")
        conn.execute(text("""
            ALTER TABLE allocation_financials 
            ADD COLUMN total_hours_in_period INTEGER DEFAULT 0
        """))
        conn.commit()
        print("✓ Added total_hours_in_period column")
    else:
        print("✓ total_hours_in_period column already exists")
    
    return True

def migrate_set_internal_allocation_percentage(conn):
    """Set internal_allocation_percentage = allocation_percentage for all allocations"""
    print("\n" + "=" * 60)
    print("Step 2.7: Setting Internal Allocation Percentage Values")
    print("=" * 60)
    
    inspector = inspect(conn)
    
    if 'allocations' not in inspector.get_table_names():
        print("ERROR: allocations table does not exist!")
        return False
    
    columns = [col['name'] for col in inspector.get_columns('allocations')]
    
    if 'internal_allocation_percentage' not in columns:
        print("ERROR: internal_allocation_percentage column does not exist!")
        print("Please run Step 2.5 first.")
        return False
    
    result = conn.execute(text("SELECT COUNT(*) FROM allocations"))
    total_count = result.fetchone()[0]
    print(f"Found {total_count} allocations in database")
    
    if total_count == 0:
        print("No allocations found. Skipping data migration.")
        return True
    
    print("Updating internal_allocation_percentage for all allocations...")
    result = conn.execute(text("""
        UPDATE allocations
        SET internal_allocation_percentage = COALESCE(
            allocation_percentage,
            utilization,
            100
        )
        WHERE internal_allocation_percentage IS NULL 
           OR internal_allocation_percentage != COALESCE(allocation_percentage, utilization, 100)
    """))
    updated_count = result.rowcount
    conn.commit()
    print(f"✓ Updated {updated_count} allocations")
    
    return True


def run_seed():
    """Run the seed script to populate database"""
    print("\n" + "=" * 60)
    print("Step 3: Seeding Database with Sample Data")
    print("=" * 60)
    print()
    
    try:
        # Import and run seed function
        from seed import seed_database
        seed_database()
        return True
    except Exception as e:
        print(f"ERROR: Failed to seed database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run all migrations and seeding"""
    print("=" * 60)
    print("BenchCraft AI - Consolidated Database Initialization")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Create all database tables")
    print("  2. Run all migrations in order")
    print("  3. Seed the database with sample data")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        return
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Create all tables
        if not create_all_tables(engine):
            print("\nERROR: Failed to create tables. Aborting.")
            return
        
        # Step 2: Run all migrations
        with engine.connect() as conn:
            migrations = [
                ("Risk Register Schema", lambda: migrate_risk_register_table(conn)),
                ("Project Wizard Fields", lambda: migrate_project_wizard_fields(conn)),
                ("Rate Card ID", lambda: migrate_add_rate_card_id(conn)),
                ("Allocation & Billable Percentage", lambda: migrate_add_allocation_billable_percentage(conn)),
                ("Shadow & Internal Allocation", lambda: migrate_add_shadow_and_internal_allocation(conn)),
                ("Total Hours in Period", lambda: migrate_add_total_hours_in_period(conn)),
                ("Set Internal Allocation Percentage", lambda: migrate_set_internal_allocation_percentage(conn)),
            ]
            
            for name, migration_func in migrations:
                try:
                    if not migration_func():
                        print(f"\nERROR: Migration '{name}' failed. Continuing with next migration...")
                except Exception as e:
                    print(f"\nERROR: Migration '{name}' failed with exception: {e}")
                    import traceback
                    traceback.print_exc()
                    print("Continuing with next migration...")
        
        # Sync employee statuses (requires session)
        print("\n" + "=" * 60)
        print("Step 2.8: Syncing Employee Statuses with Allocations")
        print("=" * 60)
        
        try:
            from utils.employee_status import sync_employee_status
            from models import Employee
            
            employees = session.query(Employee).all()
            total = len(employees)
            updated = 0
            
            print(f"Found {total} employees to check")
            
            for emp in employees:
                was_updated = sync_employee_status(emp, session)
                if was_updated:
                    updated += 1
            
            session.commit()
            
            print(f"✓ Total employees: {total}")
            print(f"✓ Statuses updated: {updated}")
            print(f"✓ Statuses already correct: {total - updated}")
        except Exception as e:
            session.rollback()
            print(f"ERROR: Failed to sync employee statuses: {e}")
            import traceback
            traceback.print_exc()
        
        # Step 3: Seed database
        seed_response = input("\nDo you want to seed the database with sample data? (yes/no): ")
        if seed_response.lower() in ['yes', 'y']:
            if not run_seed():
                print("\nWARNING: Seeding failed, but migrations completed successfully.")
        else:
            print("Skipping seed. Database is ready for use.")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Database initialization completed!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Restart the Flask server")
        print("  2. The database is ready for use")
        if seed_response.lower() not in ['yes', 'y']:
            print("  3. Run this script again with 'yes' to seed sample data")
        
    except Exception as e:
        print(f"\nERROR: Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    main()
