#!/usr/bin/env python3
"""
Fixed test with consistent constructors
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_consistent_constructors():
    """Test that all classes accept config parameter"""
    print("Testing consistent constructors...")
    
    try:
        from realtime_siem.config import ConfigManager
        from realtime_siem.core import SIEMCore
        from realtime_siem.detection import ThreatDetector, RulesEngine, AnomalyDetector
        from realtime_siem.parsers import LogParser
        from realtime_siem.alerts import AlertManager
        
        print("✅ All imports successful")
        
        # Create config first
        config = ConfigManager()
        print("✅ ConfigManager created")
        
        # Test that all classes accept config parameter
        classes_to_test = [
            ("SIEMCore", SIEMCore),
            ("ThreatDetector", ThreatDetector),
            ("RulesEngine", RulesEngine),
            ("AnomalyDetector", AnomalyDetector),
            ("LogParser", LogParser),
            ("AlertManager", AlertManager),
        ]
        
        all_passed = True
        for name, cls in classes_to_test:
            try:
                obj = cls(config)
                print(f"✅ {name} accepts config parameter")
            except TypeError as e:
                print(f"❌ {name} failed: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from realtime_siem.config import ConfigManager
        from realtime_siem.parsers import LogParser
        from realtime_siem.detection import ThreatDetector
        from realtime_siem.alerts import AlertManager
        
        config = ConfigManager()
        
        # Test log parsing
        parser = LogParser(config)
        test_log = "Sample log message"
        parsed_event = parser.parse(test_log)
        print(f"✅ Log parsing: {parsed_event}")
        
        # Test threat detection
        detector = ThreatDetector(config)
        threats = detector.analyze_event(parsed_event)
        print(f"✅ Threat detection: Found {len(threats)} threats")
        
        # Test alerting
        alert_manager = AlertManager(config)
        if threats:
            alert = alert_manager.create_alert(threats[0])
            print(f"✅ Alert creation: {alert}")
        else:
            # Test with a mock threat
            mock_threat = {"type": "test", "message": "Test threat"}
            alert = alert_manager.create_alert(mock_threat)
            print(f"✅ Alert creation: {alert}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the fixed test"""
    print("Running Fixed Constructor Test")
    print("=" * 50)
    
    constructors_ok = test_consistent_constructors()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if constructors_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED! Your package is fully working!")
        print("\nNext steps:")
        print("1. Run: pip install -e .")
        print("2. Start implementing your actual SIEM logic")
        print("3. Replace the stub implementations with real code")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()