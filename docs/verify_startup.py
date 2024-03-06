"""
Verify all components before starting the dashboard
"""
import sys

print("="*60)
print("Saudi eVisa Dashboard - Startup Verification")
print("="*60)
print()

errors = []
warnings = []

# Test 1: Config
print("[1/6] Checking configuration...")
try:
    from config import Config
    config = Config()
    
    # Check required attributes
    required = ['email', 'password', 'from_email', 'subject_filter', 'save_path', 'check_interval']
    for attr in required:
        if not hasattr(config, attr):
            errors.append(f"Config missing: {attr}")
        else:
            value = getattr(config, attr)
            if attr == 'check_interval':
                if value < 60:
                    warnings.append(f"check_interval too low: {value} (min: 60)")
    
    if not errors:
        print(f"   ✓ Config OK (interval: {config.check_interval}s)")
except Exception as e:
    errors.append(f"Config error: {e}")
    print(f"   ✗ Config failed: {e}")

print()

# Test 2: Database
print("[2/6] Checking database...")
try:
    from database import VisaDatabase
    db = VisaDatabase()
    records = db.get_all_records()
    print(f"   ✓ Database OK ({len(records)} records)")
except Exception as e:
    errors.append(f"Database error: {e}")
    print(f"   ✗ Database failed: {e}")

print()

# Test 3: Audio
print("[3/6] Checking audio system...")
try:
    from audio_announcer import announcer
    if announcer.enabled:
        print("   ✓ Audio enabled")
    else:
        warnings.append("Audio disabled (pyttsx3 not available)")
        print("   ⚠ Audio disabled")
except Exception as e:
    warnings.append(f"Audio error: {e}")
    print(f"   ⚠ Audio warning: {e}")

print()

# Test 4: Flask App
print("[4/6] Checking Flask app...")
try:
    from app import app, auto_monitor_active
    print("   ✓ Flask app loaded")
except Exception as e:
    errors.append(f"Flask error: {e}")
    print(f"   ✗ Flask failed: {e}")

print()

# Test 5: Templates
print("[5/6] Checking templates...")
try:
    import os
    if os.path.exists('templates/dashboard.html'):
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'chart.js' in content.lower():
                print("   ✓ Dashboard template OK")
            else:
                warnings.append("Chart.js not found in template")
                print("   ⚠ Chart.js missing")
    else:
        errors.append("Dashboard template not found")
        print("   ✗ Template missing")
except Exception as e:
    errors.append(f"Template error: {e}")
    print(f"   ✗ Template failed: {e}")

print()

# Test 6: Dependencies
print("[6/6] Checking dependencies...")
try:
    import pandas
    import openpyxl
    print("   ✓ Excel export ready")
except ImportError as e:
    warnings.append(f"Excel export unavailable: {e}")
    print(f"   ⚠ Excel warning: {e}")

print()
print("="*60)
print("Verification Summary")
print("="*60)
print()

if errors:
    print(f"❌ ERRORS ({len(errors)}):")
    for error in errors:
        print(f"   - {error}")
    print()

if warnings:
    print(f"⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"   - {warning}")
    print()

if not errors:
    print("✅ All critical checks passed!")
    print()
    print("Ready to start:")
    print("   python app.py")
    print()
    print("Dashboard will be available at:")
    print("   http://127.0.0.1:5000")
    print()
    sys.exit(0)
else:
    print("❌ Please fix errors before starting")
    print()
    sys.exit(1)
