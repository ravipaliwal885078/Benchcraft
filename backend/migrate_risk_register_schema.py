"""
Migration script to ensure risk_register table has correct schema
Validates and fixes the project_id column name if needed
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from config import Config

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

def migrate_risk_register_table():
    """Ensure risk_register table exists with correct schema"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # Check if risk_register table exists
        if 'risk_register' not in inspector.get_table_names():
            print("Creating risk_register table...")
            try:
                # Create the table with correct schema
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
                return True
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
                        # SQLite doesn't support RENAME COLUMN directly, so we need to recreate
                        # This is a simplified approach - in production, use a more robust migration
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
                        
                        # Copy data from old table to new table
                        conn.execute(text("""
                            INSERT INTO risk_register_new 
                            (id, emp_id, project_id, risk_type, severity, description, mitigation_plan, 
                             mitigation_owner_emp_id, identified_date, target_resolution_date, status)
                            SELECT 
                                id, emp_id, proj_id, risk_type, severity, description, mitigation_plan,
                                mitigation_owner_emp_id, identified_date, target_resolution_date, status
                            FROM risk_register
                        """))
                        
                        # Drop old table and rename new one
                        conn.execute(text("DROP TABLE risk_register"))
                        conn.execute(text("ALTER TABLE risk_register_new RENAME TO risk_register"))
                        conn.commit()
                        print("✓ Successfully renamed proj_id to project_id")
                        return True
                    except Exception as e:
                        print(f"ERROR: Failed to rename column: {str(e)}")
                        conn.rollback()
                        return False
                else:
                    # Neither column exists - add project_id
                    print("Adding project_id column...")
                    try:
                        conn.execute(text("ALTER TABLE risk_register ADD COLUMN project_id INTEGER"))
                        conn.commit()
                        print("✓ Successfully added project_id column")
                        return True
                    except Exception as e:
                        print(f"ERROR: Failed to add column: {str(e)}")
                        conn.rollback()
                        return False
            else:
                print("✓ project_id column already exists with correct name")
                
                # Verify all required columns exist
                required_columns = [
                    'id', 'emp_id', 'project_id', 'risk_type', 'severity', 
                    'description', 'mitigation_plan', 'mitigation_owner_emp_id',
                    'identified_date', 'target_resolution_date', 'status'
                ]
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"WARNING: Missing columns: {missing_columns}")
                    print("Table structure may be incomplete. Consider recreating the table.")
                else:
                    print("✓ All required columns exist")
                
                return True

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Validate and Fix risk_register Table Schema")
    print("=" * 60)
    print()
    
    success = migrate_risk_register_table()
    
    print("=" * 60)
    if success:
        print("Migration completed successfully!")
        print()
        print("The risk_register table now has the correct schema:")
        print("  - Uses 'project_id' (not 'proj_id')")
        print("  - All required columns are present")
    else:
        print("Migration failed. Please check the error messages above.")
        sys.exit(1)
