"""
Test script for new features
"""
import sys

print("="*50)
print("Testing New Features")
print("="*50)
print()

# Test 1: Audio Announcer
print("[1/5] Testing Audio Announcer...")
try:
    from audio_announcer import announcer
    print("✓ Audio announcer module loaded")
    
    if announcer.enabled:
        print("✓ Audio engine initialized")
        announcer.announce("Test announcement")
        print("✓ Test announcement queued")
    else:
        print("⚠️ Audio disabled (pyttsx3 not available)")
except Exception as e:
    print(f"❌ Audio test failed: {e}")

print()

# Test 2: Database
print("[2/5] Testing Database...")
try:
    from database import VisaDatabase
    db = VisaDatabase()
    records = db.get_all_records()
    print(f"✓ Database connected: {len(records)} records")
except Exception as e:
    print(f"❌ Database test failed: {e}")

print()

# Test 3: Flask App
print("[3/5] Testing Flask App...")
try:
    from app import app, auto_monitor_active
    print("✓ Flask app loaded")
    print(f"✓ Auto-monitor status: {auto_monitor_active}")
except Exception as e:
    print(f"❌ Flask test failed: {e}")

print()

# Test 4: Excel Export
print("[4/5] Testing Excel Export...")
try:
    import pandas as pd
    import openpyxl
    print("✓ pandas installed")
    print("✓ openpyxl installed")
    print("✓ Excel export ready")
except Exception as e:
    print(f"❌ Excel test failed: {e}")
    print("   Run: pip install pandas openpyxl")

print()

# Test 5: Chart.js (check if template exists)
print("[5/5] Testing Dashboard Template...")
try:
    import os
    if os.path.exists('templates/dashboard.html'):
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'chart.js' in content.lower():
                print("✓ Dashboard template exists")
                print("✓ Chart.js included")
            else:
                print("⚠️ Chart.js not found in template")
    else:
        print("❌ Dashboard template not found")
except Exception as e:
    print(f"❌ Template test failed: {e}")

print()
print("="*50)
print("Test Summary")
print("="*50)
print()
print("Next Steps:")
print("1. Run: python app.py")
print("2. Open: http://127.0.0.1:5000")
print("3. Check auto-monitor status")
print("4. Test audio announcements")
print("5. Try sorting and filtering")
print("6. Export records to Excel")
print()
print("For issues, check NEW_FEATURES_GUIDE.md")
print()
