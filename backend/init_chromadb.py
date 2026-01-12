"""
ChromaDB Initialization Script
Clears and reinitializes ChromaDB vector store for BenchCraft AI

This script:
1. Clears all existing embeddings from ChromaDB
2. Optionally re-populates embeddings from existing employees in the database
3. Ensures ChromaDB is ready for semantic search operations

Run: python backend/init_chromadb.py
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from models import Employee
from tools.vector_db import ChromaSearchTool

def clear_chromadb():
    """Clear all existing data from ChromaDB collection"""
    print("=" * 60)
    print("Clearing ChromaDB Collection")
    print("=" * 60)
    print()
    
    try:
        vector_tool = ChromaSearchTool()
        
        # Get all existing IDs
        existing_data = vector_tool.collection.get()
        
        if existing_data and existing_data.get('ids'):
            num_embeddings = len(existing_data['ids'])
            print(f"Found {num_embeddings} existing embeddings in ChromaDB")
            
            # Delete all existing embeddings
            vector_tool.collection.delete(ids=existing_data['ids'])
            print(f"✓ Deleted {num_embeddings} embeddings from ChromaDB")
        else:
            print("✓ ChromaDB collection is already empty")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to clear ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False

def repopulate_chromadb():
    """Repopulate ChromaDB with embeddings from existing employees"""
    print("\n" + "=" * 60)
    print("Repopulating ChromaDB from Database")
    print("=" * 60)
    print()
    
    try:
        # Initialize database session
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Initialize ChromaDB
        vector_tool = ChromaSearchTool()
        
        # Get all employees
        employees = session.query(Employee).all()
        
        if not employees:
            print("⚠ No employees found in database. Skipping ChromaDB population.")
            print("   Run the seeding script first to create employees.")
            session.close()
            return True
        
        print(f"Found {len(employees)} employees in database")
        print("Generating embeddings...")
        print()
        
        success_count = 0
        error_count = 0
        
        for i, employee in enumerate(employees, 1):
            try:
                # Use bio_summary if available, otherwise generate a basic bio
                if employee.bio_summary:
                    bio = employee.bio_summary
                else:
                    # Generate basic bio from available data
                    skills = [s.skill_name for s in employee.skills[:5]]
                    skills_str = ', '.join(skills) if skills else 'software development'
                    bio = f"{employee.role_level} software engineer with expertise in {skills_str}. "
                    bio += f"Based in {employee.base_location or 'India'}. "
                    bio += f"Experienced in enterprise software development."
                
                # Add embedding to ChromaDB
                vector_tool.add_employee_embedding(employee.id, bio)
                success_count += 1
                
                if i % 10 == 0:
                    print(f"  Processed {i}/{len(employees)} employees...")
                    
            except Exception as e:
                error_count += 1
                print(f"  ⚠ Error processing employee {employee.id} ({employee.first_name} {employee.last_name}): {e}")
                continue
        
        session.close()
        
        print()
        print("=" * 60)
        print("ChromaDB Repopulation Complete")
        print("=" * 60)
        print(f"  ✓ Successfully added {success_count} embeddings")
        if error_count > 0:
            print(f"  ⚠ Failed to add {error_count} embeddings")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to repopulate ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        if 'session' in locals():
            session.close()
        return False

def verify_chromadb():
    """Verify ChromaDB is properly initialized"""
    print("\n" + "=" * 60)
    print("Verifying ChromaDB")
    print("=" * 60)
    print()
    
    try:
        vector_tool = ChromaSearchTool()
        
        # Get collection info
        existing_data = vector_tool.collection.get()
        
        if existing_data and existing_data.get('ids'):
            num_embeddings = len(existing_data['ids'])
            print(f"✓ ChromaDB is initialized with {num_embeddings} embeddings")
            
            # Test search functionality
            try:
                test_results = vector_tool.search("Python developer", top_k=3)
                print(f"✓ Search functionality verified ({len(test_results)} test results)")
            except Exception as search_error:
                print(f"⚠ Search test failed: {search_error}")
                print("   This may be due to missing GEMINI_API_KEY")
        else:
            print("⚠ ChromaDB collection is empty")
            print("   Run with --repopulate flag to populate from database")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to verify ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ChromaDB for BenchCraft AI')
    parser.add_argument(
        '--repopulate',
        action='store_true',
        help='Repopulate ChromaDB with embeddings from existing employees in database'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify ChromaDB status without clearing or repopulating'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("CHROMADB INITIALIZATION")
    print("BenchCraft AI Resource Allocation System")
    print("=" * 60)
    print()
    
    # Check if GEMINI_API_KEY is configured
    if not Config.GEMINI_API_KEY:
        print("⚠ WARNING: GEMINI_API_KEY not found in environment variables")
        print("   ChromaDB embeddings require Gemini API for vector generation")
        print("   Set GEMINI_API_KEY in backend/.env file")
        print()
        response = input("Continue anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted.")
            return False
    
    # Verify only mode
    if args.verify_only:
        return verify_chromadb()
    
    # Clear ChromaDB
    if not clear_chromadb():
        return False
    
    # Repopulate if requested
    if args.repopulate:
        if not repopulate_chromadb():
            return False
    else:
        print("\n" + "=" * 60)
        print("ChromaDB Cleared")
        print("=" * 60)
        print()
        print("ChromaDB collection has been cleared.")
        print("To repopulate with employee embeddings, run:")
        print("  python backend/init_chromadb.py --repopulate")
        print()
        print("Or run the comprehensive seeding script which will populate ChromaDB:")
        print("  python backend/seed_comprehensive.py")
    
    # Verify
    verify_chromadb()
    
    print("\n" + "=" * 60)
    print("SUCCESS: ChromaDB initialization completed!")
    print("=" * 60)
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
