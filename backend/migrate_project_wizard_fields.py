"""
Migration script to add new fields for Project Wizard
- project_code (String, unique)
- project_type (Enum: Fixed_Price, T&M, Retainer)
- billing_currency (String, default='USD')
- industry_domain (String)
- Update ProjectStatus enum to include ON_HOLD, CANCELLED
- Create project_role_requirements table
"""
import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent.parent / 'benchcraft.db'
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if project_code column exists
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add project_code if it doesn't exist
        if 'project_code' not in columns:
            print("Adding project_code column to projects table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN project_code TEXT UNIQUE")
            # Generate project_code for existing projects
            cursor.execute("SELECT id FROM projects WHERE project_code IS NULL")
            projects = cursor.fetchall()
            for (project_id,) in projects:
                # Get year from created date or use current year
                cursor.execute("SELECT start_date FROM projects WHERE id = ?", (project_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    year = result[0][:4]
                else:
                    from datetime import datetime
                    year = str(datetime.now().year)
                project_code = f"PROJ-{year}-{project_id}"
                cursor.execute("UPDATE projects SET project_code = ? WHERE id = ?", (project_code, project_id))
            print(f"Generated project_code for {len(projects)} existing projects")
        
        # Add project_type if it doesn't exist
        if 'project_type' not in columns:
            print("Adding project_type column to projects table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN project_type TEXT")
        
        # Add billing_currency if it doesn't exist
        if 'billing_currency' not in columns:
            print("Adding billing_currency column to projects table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN billing_currency TEXT DEFAULT 'USD'")
            # Set default for existing projects
            cursor.execute("UPDATE projects SET billing_currency = 'USD' WHERE billing_currency IS NULL")
        
        # Add industry_domain if it doesn't exist
        if 'industry_domain' not in columns:
            print("Adding industry_domain column to projects table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN industry_domain TEXT")
        
        # Note: SQLite doesn't support ALTER TABLE for enum changes
        # The enum values ON_HOLD and CANCELLED will work at the application level
        # Existing data with old enum values will continue to work
        
        # Create project_role_requirements table if it doesn't exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='project_role_requirements'
        """)
        if not cursor.fetchone():
            print("Creating project_role_requirements table...")
            cursor.execute("""
                CREATE TABLE project_role_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proj_id INTEGER NOT NULL,
                    role_name TEXT NOT NULL,
                    required_count INTEGER NOT NULL DEFAULT 1,
                    utilization_percentage INTEGER NOT NULL DEFAULT 100,
                    FOREIGN KEY (proj_id) REFERENCES projects (id)
                )
            """)
            print("Created project_role_requirements table")
        else:
            print("project_role_requirements table already exists")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
