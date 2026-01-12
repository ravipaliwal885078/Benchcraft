"""
Migration script to sync all employee statuses with their actual allocations
This ensures stored status matches derived status from allocations
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from models import Employee, Base

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

def sync_all_employee_statuses():
    """Sync all employee statuses with their actual allocations"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        from utils.employee_status import sync_employee_status
        
        employees = session.query(Employee).all()
        total = len(employees)
        updated = 0
        
        print(f"Found {total} employees to check")
        print("=" * 60)
        
        for emp in employees:
            was_updated = sync_employee_status(emp, session)
            if was_updated:
                updated += 1
                print(f"✓ Updated {emp.first_name} {emp.last_name}: {emp.status.value}")
        
        session.commit()
        
        print("=" * 60)
        print(f"Total employees: {total}")
        print(f"Statuses updated: {updated}")
        print(f"Statuses already correct: {total - updated}")
        print("\nMigration completed successfully!")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: Sync Employee Statuses with Allocations")
    print("=" * 60)
    print()
    
    success = sync_all_employee_statuses()
    
    if not success:
        sys.exit(1)
