"""Clear database and reprocess all PDFs with improved OCR"""
import os
import sqlite3
from datetime import datetime

def clear_database():
    """Clear all records from the database"""
    db_path = 'visa_records.db'
    
    if not os.path.exists(db_path):
        print("✓ Database doesn't exist yet")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get count before deletion
        cursor.execute("SELECT COUNT(*) FROM visa_records")
        count = cursor.fetchone()[0]
        
        # Delete all records
        cursor.execute("DELETE FROM visa_records")
        conn.commit()
        
        print(f"✓ Cleared {count} records from database")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM visa_records")
        remaining = cursor.fetchone()[0]
        print(f"✓ Database now has {remaining} records")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Error clearing database: {e}")

def main():
    print("\n" + "="*80)
    print("CLEAR DATABASE AND PREPARE FOR REPROCESSING")
    print("="*80)
    print()
    
    # Confirm action
    print("⚠ WARNING: This will delete ALL records from the database!")
    print("  The database will be repopulated when you:")
    print("  1. Run the Flask app: python app.py")
    print("  2. Click 'Scan & Extract Existing PDFs' button")
    print("  3. Or click 'Retry Extraction' button")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n✗ Operation cancelled")
        return
    
    print()
    print("Step 1: Clearing database...")
    clear_database()
    
    print()
    print("="*80)
    print("✓ DATABASE CLEARED SUCCESSFULLY")
    print("="*80)
    print()
    print("Next steps:")
    print("  1. Start the Flask app: python app.py")
    print("  2. Open dashboard: http://127.0.0.1:5000")
    print("  3. Click 'Scan & Extract Existing PDFs' to reprocess all PDFs")
    print("     (This will use the improved OCR extraction)")
    print()

if __name__ == "__main__":
    main()
