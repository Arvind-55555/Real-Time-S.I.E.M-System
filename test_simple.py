#!/usr/bin/env python3
"""
Simple test script for basic package functionality
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic package imports"""
    print("Testing basic imports...")
    
    try:
        import realtime_siem
        print("✓ Main package imported")
    except ImportError as e:
        print(f"✗ Main package import failed: {e}")
        return False
    
    try:
        from realtime_siem.config import ConfigManager
        print("✓ ConfigManager imported")
    except ImportError as e:
        print(f"✗ ConfigManager import failed: {e}")
        return False
    
    return True

def test_create_objects():
    """Test creating basic objects"""
    print("\nTesting object creation...")
    
    try:
        from realtime_siem.config import ConfigManager
        config = ConfigManager()
        print("✓ ConfigManager object created")
    except Exception as e:
        print(f"✗ ConfigManager creation failed: {e}")
        return False
    
    # Try to import and create other objects if they exist
    try:
        from realtime_siem.core import SIEMCore
        siem = SIEMCore(config)
        print("✓ SIEMCore object created")
    except Exception as e:
        print(f"⚠️  SIEMCore creation failed (might need implementation): {e}")
    
    return True

def check_package_structure():
    """Check if basic package structure is correct"""
    print("\nChecking package structure...")
    
    required_files = [
        'src/realtime_siem/__init__.py',
        'src/realtime_siem/core/__init__.py',
        'src/realtime_siem/config/__init__.py',
        'src/realtime_siem/config/config_manager.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("Running basic package tests...")
    print("=" * 50)
    
    structure_ok = check_package_structure()
    imports_ok = test_basic_imports()
    objects_ok = test_create_objects()
    
    print("\n" + "=" * 50)
    if structure_ok and imports_ok:
        print("✅ Basic package structure is working!")
        print("\nNext steps:")
        print("1. Run: pip install -e .")
        print("2. Add your actual implementation to the stub files")
    else:
        print("❌ Package needs more setup")
        print("\nPlease check the missing files above.")