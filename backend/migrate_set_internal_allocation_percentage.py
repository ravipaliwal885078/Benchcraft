"""
Migration script to set internal_allocation_percentage = allocation_percentage for all existing allocations.

This script:
1. Updates all Allocation records to set internal_allocation_percentage = allocation_percentage
2. Falls back to utilization if allocation_percentage doesn't exist
3. Defaults to 100 if neither exists
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import Config
except ImportError:
    print("ERROR: Could not import Config. Make sure you're running from the backend directory.")
    sys.exit(1)

def migrate():
    """Run the migration"""
    print("=" * 60)
    print("Migration: Set internal_allocation_percentage = allocation_percentage")
    print("=" * 60)
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        with engine.connect() as conn:
            # Check if internal_allocation_percentage column exists
            result = conn.execute(text("PRAGMA table_info(allocations)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'internal_allocation_percentage' not in columns:
                print("\nERROR: 'internal_allocation_percentage' column does not exist.")
                print("Please run 'backend/migrate_add_shadow_and_internal_allocation.py' first.")
                return
            
            # Check how many allocations exist
            result = conn.execute(text("SELECT COUNT(*) FROM allocations"))
            total_count = result.fetchone()[0]
            print(f"\n1. Found {total_count} allocations in database")
            
            if total_count == 0:
                print("\n   No allocations found. Nothing to migrate.")
                return
            
            print("\n2. Updating internal_allocation_percentage for all allocations...")
            print("   Setting internal_allocation_percentage = COALESCE(allocation_percentage, utilization, 100)")
            
            # Use SQL UPDATE for efficiency
            update_query = text("""
                UPDATE allocations
                SET internal_allocation_percentage = COALESCE(
                    allocation_percentage,
                    utilization,
                    100
                )
                WHERE internal_allocation_percentage IS NULL 
                   OR internal_allocation_percentage != COALESCE(allocation_percentage, utilization, 100)
            """)
            
            result = conn.execute(update_query)
            updated_count = result.rowcount
            conn.commit()
            
            print(f"   ✓ Updated {updated_count} allocations")
            
            # Verify the update
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN internal_allocation_percentage = COALESCE(allocation_percentage, utilization, 100) THEN 1 END) as matching
                FROM allocations
            """))
            stats = result.fetchone()
            total = stats[0]
            matching = stats[1]
            
            print(f"\n3. Verification:")
            print(f"   Total allocations: {total}")
            print(f"   Matching internal_allocation_percentage: {matching}")
            print(f"   Mismatched: {total - matching}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Migration completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Total allocations: {total_count}")
        print(f"  - Allocations updated: {updated_count}")
        print(f"  - Allocations already correct: {total_count - updated_count}")
        print(f"\nAll allocations now have internal_allocation_percentage set to")
        print(f"match their allocation_percentage (or utilization) values.")
        
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    migrate()
