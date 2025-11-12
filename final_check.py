#!/usr/bin/env python3
"""
Final check of the package setup
"""

import sys
import os

print("🔍 Final Package Setup Check")
print("=" * 50)

# Check 1: Python path
print("1. Python path includes src/:")
src_in_path = any('src' in path for path in sys.path)
print(f"   {'✅' if src_in_path else '❌'} src/ is in Python path")

# Check 2: Import package
print("2. Package import:")
try:
    sys.path.insert(0, 'src')
    import realtime_siem
    print(f"   ✅ realtime_siem imported (version: {realtime_siem.__version__})")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")

# Check 3: Module imports
print("3. Module imports:")
modules = ['core', 'detection', 'parsers', 'alerts', 'config']
all_modules_ok = True
for module in modules:
    try:
        __import__(f'realtime_siem.{module}')
        print(f"   ✅ realtime_siem.{module}")
    except ImportError as e:
        print(f"   ❌ realtime_siem.{module}: {e}")
        all_modules_ok = False

# Check 4: Class creation
print("4. Class instantiation:")
if all_modules_ok:
    try:
        from realtime_siem.config import ConfigManager
        from realtime_siem.core import SIEMCore
        config = ConfigManager()
        siem = SIEMCore(config)
        print("   ✅ ConfigManager and SIEMCore created")
    except Exception as e:
        print(f"   ❌ Object creation failed: {e}")
        all_modules_ok = False

print("\n" + "=" * 50)
if all_modules_ok:
    print("🎉 PACKAGE SETUP IS COMPLETE AND WORKING!")
    print("\nYou can now:")
    print("1. Use the package in your projects")
    print("2. Continue developing the SIEM logic")
    print("3. Create releases and publish to PyPI")
else:
    print("❌ Some checks failed. Please review the errors above.")