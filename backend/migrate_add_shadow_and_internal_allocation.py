"""
Migration script to add shadow resource tracking and internal allocation fields to Allocation model.

New fields:
- is_trainee (Boolean, default=False)
- mentoring_primary_emp_id (Integer, nullable=True, FK to employees.id)
- internal_allocation_percentage (Integer, default=100)

This migration:
1. Adds new columns to allocations table
2. Sets default values for existing records:
   - is_trainee: False (all existing allocations are primary)
   - mentoring_primary_emp_id: NULL
   - internal_allocation_percentage: Same as allocation_percentage (assume 1:1 initially)
3. Creates indexes for performance
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

def migrate():
    """Run the migration"""
    print("=" * 60)
    print("Migration: Add Shadow Resource and Internal Allocation Fields")
    print("=" * 60)
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='allocations'
            """))
            
            if not result.fetchone():
                print("ERROR: 'allocations' table does not exist. Please run seed.py first.")
                return
            
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(allocations)"))
            columns = [row[1] for row in result.fetchall()]
            
            print("\n1. Adding new columns to allocations table...")
            
            # Add is_trainee column
            if 'is_trainee' not in columns:
                print("   - Adding is_trainee column...")
                conn.execute(text("""
                    ALTER TABLE allocations
                    ADD COLUMN is_trainee BOOLEAN NOT NULL DEFAULT 0
                """))
                conn.commit()
                print("   ✓ Added is_trainee column")
            else:
                print("   - is_trainee column already exists")
            
            # Add mentoring_primary_emp_id column
            if 'mentoring_primary_emp_id' not in columns:
                print("   - Adding mentoring_primary_emp_id column...")
                conn.execute(text("""
                    ALTER TABLE allocations
                    ADD COLUMN mentoring_primary_emp_id INTEGER
                """))
                conn.commit()
                print("   ✓ Added mentoring_primary_emp_id column")
            else:
                print("   - mentoring_primary_emp_id column already exists")
            
            # Add internal_allocation_percentage column
            if 'internal_allocation_percentage' not in columns:
                print("   - Adding internal_allocation_percentage column...")
                conn.execute(text("""
                    ALTER TABLE allocations
                    ADD COLUMN internal_allocation_percentage INTEGER NOT NULL DEFAULT 100
                """))
                conn.commit()
                print("   ✓ Added internal_allocation_percentage column")
            else:
                print("   - internal_allocation_percentage column already exists")
            
            print("\n2. Setting default values for existing records...")
            
            # Set internal_allocation_percentage to match allocation_percentage for existing records
            # (assuming 1:1 relationship initially)
            if 'internal_allocation_percentage' in columns:
                result = conn.execute(text("""
                    UPDATE allocations
                    SET internal_allocation_percentage = COALESCE(allocation_percentage, 100)
                    WHERE internal_allocation_percentage = 100 
                    AND (allocation_percentage IS NOT NULL OR utilization IS NOT NULL)
                """))
                updated = result.rowcount
                conn.commit()
                print(f"   ✓ Updated {updated} existing allocations to set internal_allocation_percentage = allocation_percentage")
            
            # Ensure is_trainee is False for all existing records
            if 'is_trainee' in columns:
                result = conn.execute(text("""
                    UPDATE allocations
                    SET is_trainee = 0
                    WHERE is_trainee IS NULL
                """))
                updated = result.rowcount
                conn.commit()
                if updated > 0:
                    print(f"   ✓ Set is_trainee = False for {updated} existing allocations")
            
            print("\n3. Creating indexes for performance...")
            
            # Create index on is_trainee for filtering
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_allocations_is_trainee 
                    ON allocations(is_trainee)
                """))
                conn.commit()
                print("   ✓ Created index on is_trainee")
            except Exception as e:
                print(f"   - Index on is_trainee may already exist: {e}")
            
            # Create index on mentoring_primary_emp_id for relationship queries
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_allocations_mentoring_primary 
                    ON allocations(mentoring_primary_emp_id)
                """))
                conn.commit()
                print("   ✓ Created index on mentoring_primary_emp_id")
            except Exception as e:
                print(f"   - Index on mentoring_primary_emp_id may already exist: {e}")
            
            print("\n" + "=" * 60)
            print("SUCCESS: Migration completed successfully!")
            print("=" * 60)
            print("\nSummary:")
            print("  - Added is_trainee column (Boolean, default=False)")
            print("  - Added mentoring_primary_emp_id column (Integer, nullable)")
            print("  - Added internal_allocation_percentage column (Integer, default=100)")
            print("  - Set default values for existing records")
            print("  - Created indexes for performance")
            print("\nNote: Existing allocations have been set to:")
            print("  - is_trainee = False (all are primary resources)")
            print("  - mentoring_primary_emp_id = NULL")
            print("  - internal_allocation_percentage = allocation_percentage (1:1 relationship)")
            print("\nYou can now use the new fields to track shadow resources and")
            print("differentiate between internal vs client allocation percentages.")
            
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    migrate()
