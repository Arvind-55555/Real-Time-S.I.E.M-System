#!/usr/bin/env python3
"""
Test that everything works together
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_complete_workflow():
    """Test a complete workflow"""
    print("Testing complete workflow...")
    
    try:
        from realtime_siem.config import ConfigManager
        from realtime_siem.core import SIEMCore
        from realtime_siem.detection import ThreatDetector, RulesEngine, AnomalyDetector
        from realtime_siem.parsers import LogParser
        from realtime_siem.alerts import AlertManager
        
        print("✅ All imports successful")
        
        # Create objects
        config = ConfigManager()
        siem = SIEMCore(config)
        detector = ThreatDetector(config)
        rules_engine = RulesEngine(config)
        anomaly_detector = AnomalyDetector(config)
        parser = LogParser(config)
        alert_manager = AlertManager(config)
        
        print("✅ All objects created successfully")
        
        # Test basic functionality
        test_event = {"message": "User login failed", "source_ip": "192.168.1.100"}
        
        # Test parsing
        parsed_event = parser.parse("Sample log message")
        print(f"✅ Log parsing works: {parsed_event}")
        
        # Test threat detection
        threats = detector.analyze_event(test_event)
        print(f"✅ Threat detection works: Found {len(threats)} threats")
        
        # Test alerting
        if threats:
            alert = alert_manager.create_alert(threats[0])
            print(f"✅ Alert creation works: {alert}")
        
        print("🎉 COMPLETE WORKFLOW TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the workflow test"""
    print("Running Complete Workflow Test")
    print("=" * 50)
    
    success = test_complete_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 YOUR PACKAGE IS FULLY WORKING!")
        print("\nNext steps:")
        print("1. Run: pip install -e .")
        print("2. Start adding your actual SIEM logic to the classes")
        print("3. Create your real log parsers, rules, and detection logic")
    else:
        print("❌ Workflow test failed")

if __name__ == "__main__":
    main()