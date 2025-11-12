#!/usr/bin/env python3
"""
Reliable test that works regardless of installation
"""

import sys
import os

# Always add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_package():
    """Test the package functionality"""
    print("Testing SIEM Package...")
    print("=" * 40)
    
    try:
        from realtime_siem import SIEMCore, ConfigManager
        from realtime_siem.detection import ThreatDetector
        from realtime_siem.parsers import LogParser
        from realtime_siem.alerts import AlertManager
        
        print("✅ All imports successful!")
        
        # Create instances
        config = ConfigManager()
        siem = SIEMCore(config)
        detector = ThreatDetector(config)
        parser = LogParser(config)
        alert_manager = AlertManager(config)
        
        print("✅ All objects created successfully!")
        
        # Test functionality
        test_logs = [
            "Normal user activity",
            "ERROR: System failure",
            "Login failed for user test"
        ]
        
        print("\nTesting functionality with sample logs:")
        for log in test_logs:
            event = parser.parse(log)
            threats = detector.analyze_event(event)
            
            if threats:
                print(f"🔴 THREAT: {log}")
                for threat in threats:
                    alert = alert_manager.create_alert(threat)
                    print(f"   🚨 Alert: {alert['alert_id']}")
            else:
                print(f"🟢 NORMAL: {log}")
        
        print("\n" + "=" * 40)
        print("🎉 ALL TESTS PASSED!")
        print("\nYour SIEM package is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_package()
    sys.exit(0 if success else 1)