"""
Script to reset and reseed the database
Deletes the database file and recreates all tables with seed data
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from tools.sql_db import SQLDatabaseTool
from seed import seed_database

def reset_database():
    """Reset the database by deleting it and recreating with seed data"""
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    
    print("=" * 60)
    print("RESETTING DATABASE")
    print("=" * 60)
    
    # Delete the database file if it exists
    if os.path.exists(db_path):
        print(f"Deleting existing database: {db_path}")
        os.remove(db_path)
        print("SUCCESS: Database file deleted")
    else:
        print(f"Database file not found: {db_path}")
    
    # Initialize database
    print("\nInitializing database...")
    db_tool = SQLDatabaseTool()
    db_tool.init_db()
    print("SUCCESS: Database initialized")
    
    # Seed database
    print("\nSeeding database...")
    seed_database()
    
    print("\n" + "=" * 60)
    print("SUCCESS: DATABASE RESET COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    try:
        reset_database()
    except Exception as e:
        print(f"\nERROR: Error resetting database: {e}")
        if "PermissionError" in str(type(e)) or "being used by another process" in str(e):
            print("\nNOTE: The database file is locked. Please stop the Flask server first!")
            print("  1. Stop the Flask backend server (Ctrl+C)")
            print("  2. Run this script again")
        import traceback
        traceback.print_exc()
        sys.exit(1)
