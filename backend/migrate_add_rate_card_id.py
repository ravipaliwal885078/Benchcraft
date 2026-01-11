"""
Migration script to add rate_card_id column to allocations table
Run this once to update existing database schema
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from config import Config

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

def migrate_allocations_table():
    """Add rate_card_id column to allocations table if it doesn't exist"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # Check if allocations table exists
        if 'allocations' not in inspector.get_table_names():
            print("ERROR: allocations table does not exist!")
            return False
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns('allocations')]
        
        # Check if rate_card_id already exists
        if 'rate_card_id' in columns:
            print("✓ rate_card_id column already exists in allocations table")
            return True
        
        # Add the column
        try:
            print("Adding rate_card_id column to allocations table...")
            conn.execute(text('ALTER TABLE allocations ADD COLUMN rate_card_id INTEGER'))
            conn.commit()
            print("✓ Successfully added rate_card_id column to allocations table")
            return True
        except Exception as e:
            print(f"ERROR: Failed to add column: {str(e)}")
            conn.rollback()
            return False

if __name__ == '__main__':
    print("Running migration: Add rate_card_id to allocations table")
    print("=" * 60)
    success = migrate_allocations_table()
    print("=" * 60)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed. Please check the error messages above.")
        sys.exit(1)
