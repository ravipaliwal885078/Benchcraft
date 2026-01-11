"""
Migration script to add total_hours_in_period column to allocation_financials table
Run this once to update existing database schema
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from config import Config

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

def migrate_allocation_financials_table():
    """Add total_hours_in_period column to allocation_financials table if it doesn't exist"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # Check if allocation_financials table exists
        if 'allocation_financials' not in inspector.get_table_names():
            print("ERROR: allocation_financials table does not exist!")
            return False
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns('allocation_financials')]
        
        # Check if total_hours_in_period already exists
        if 'total_hours_in_period' in columns:
            print("✓ total_hours_in_period column already exists in allocation_financials table")
            return True
        
        # Add the column
        try:
            print("Adding total_hours_in_period column to allocation_financials table...")
            conn.execute(text('ALTER TABLE allocation_financials ADD COLUMN total_hours_in_period INTEGER DEFAULT 0'))
            conn.commit()
            print("✓ Successfully added total_hours_in_period column to allocation_financials table")
            return True
        except Exception as e:
            print(f"ERROR: Failed to add column: {str(e)}")
            conn.rollback()
            return False

if __name__ == '__main__':
    print("Running migration: Add total_hours_in_period to allocation_financials table")
    print("=" * 60)
    success = migrate_allocation_financials_table()
    print("=" * 60)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed. Please check the error messages above.")
        sys.exit(1)
