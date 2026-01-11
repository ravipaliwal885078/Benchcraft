"""
Migration Script: Add allocation_percentage and billable_percentage to allocations table

This migration adds two new columns to support the use case where:
- Allocation percentage: How much of employee's time is allocated to a project
- Billable percentage: How much of that allocation is billable to the client

These are separate concepts that allow scenarios like:
- Employee allocated 50% to Project A (100% billable) and 40% to Project B (100% billable) = 90% utilized
- Employee allocated 100% but only 50% billable (during resignation/replacement)
"""

import sqlite3
import os
from pathlib import Path

# Database path
db_path = Path(__file__).parent.parent / 'data' / 'benchcraft.db'

def migrate():
    """Add allocation_percentage and billable_percentage columns"""
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(allocations)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'allocation_percentage' not in columns:
            print("Adding allocation_percentage column...")
            cursor.execute("""
                ALTER TABLE allocations 
                ADD COLUMN allocation_percentage INTEGER NOT NULL DEFAULT 100
            """)
            print("SUCCESS: Added allocation_percentage column")
        else:
            print("allocation_percentage column already exists")
        
        if 'billable_percentage' not in columns:
            print("Adding billable_percentage column...")
            cursor.execute("""
                ALTER TABLE allocations 
                ADD COLUMN billable_percentage INTEGER NOT NULL DEFAULT 100
            """)
            print("SUCCESS: Added billable_percentage column")
        else:
            print("billable_percentage column already exists")
        
        # Migrate existing data: if utilization exists, use it for allocation_percentage
        if 'utilization' in columns:
            print("Migrating existing utilization data to allocation_percentage...")
            cursor.execute("""
                UPDATE allocations 
                SET allocation_percentage = COALESCE(utilization, 100)
                WHERE allocation_percentage = 100 AND utilization IS NOT NULL
            """)
            print("SUCCESS: Migrated utilization data")
        
        conn.commit()
        conn.close()
        
        print("\nMigration completed successfully!")
        return True
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Columns already exist. Migration may have been run before.")
            return True
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Add allocation_percentage and billable_percentage")
    print("=" * 60)
    print(f"Database: {db_path}\n")
    
    success = migrate()
    
    if success:
        print("\nNext steps:")
        print("1. Restart the Flask server")
        print("2. The new fields are now available in the Allocation model")
        print("3. Existing allocations will have allocation_percentage = utilization (if exists) or 100")
        print("4. All existing allocations will have billable_percentage = 100")
    else:
        print("\nMigration failed. Please check the error messages above.")
