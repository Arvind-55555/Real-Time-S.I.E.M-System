#!/usr/bin/env python3
"""
Final test for the package structure
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_all_imports():
    """Test that all main components can be imported"""
    print("Testing all imports...")
    
    tests = [
        ("Main package", "import realtime_siem"),
        ("SIEMCore", "from realtime_siem.core import SIEMCore"),
        ("ConfigManager", "from realtime_siem.config import ConfigManager"),
        ("ThreatDetector", "from realtime_siem.detection import ThreatDetector"),
        ("LogParser", "from realtime_siem.parsers import LogParser"),
        ("AlertManager", "from realtime_siem.alerts import AlertManager"),
    ]
    
    all_passed = True
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {test_name}")
        except ImportError as e:
            print(f"❌ {test_name}: {e}")
            all_passed = False
    
    return all_passed

def test_object_creation():
    """Test creating objects from imported classes"""
    print("\nTesting object creation...")
    
    try:
        from realtime_siem.config import ConfigManager
        config = ConfigManager()
        print("✅ ConfigManager object created")
        
        from realtime_siem.core import SIEMCore
        siem = SIEMCore(config)
        print("✅ SIEMCore object created")
        
        from realtime_siem.detection import ThreatDetector
        detector = ThreatDetector(config)
        print("✅ ThreatDetector object created")
        
        return True
        
    except Exception as e:
        print(f"❌ Object creation failed: {e}")
        return False

def test_package_metadata():
    """Test package metadata"""
    print("\nTesting package metadata...")
    
    try:
        import realtime_siem
        print(f"✅ Version: {realtime_siem.__version__}")
        print(f"✅ Author: {realtime_siem.__author__}")
        return True
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Final Package Tests")
    print("=" * 50)
    
    imports_ok = test_all_imports()
    objects_ok = test_object_creation()
    metadata_ok = test_package_metadata()
    
    print("\n" + "=" * 50)
    if imports_ok and objects_ok and metadata_ok:
        print("🎉 ALL TESTS PASSED! Your package is working correctly.")
        print("\nNext steps:")
        print("1. Run: pip install -e .")
        print("2. Test the installation")
        print("3. Start implementing your actual SIEM logic")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()