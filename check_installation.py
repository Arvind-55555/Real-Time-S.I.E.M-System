#!/usr/bin/env python3
"""
Check if the package is properly installed
"""

import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTrying to import realtime_siem...")

try:
    import realtime_siem
    print("✅ realtime_siem imported successfully!")
    print(f"Version: {realtime_siem.__version__}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    
    # Try alternative import
    print("\nTrying alternative import from src...")
    sys.path.insert(0, 'src')
    try:
        import realtime_siem
        print("✅ realtime_siem imported from src successfully!")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")