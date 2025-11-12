#!/usr/bin/env python3
"""
Demo script showing the SIEM package in action
"""

import sys
import os

# Add the src directory to path so it works without installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from realtime_siem import SIEMCore, ConfigManager
    from realtime_siem.detection import ThreatDetector
    from realtime_siem.parsers import LogParser
    from realtime_siem.alerts import AlertManager
    print("✅ Package imported successfully!")
except ImportError as e:
    print(f"❌ Package import failed: {e}")
    print("Make sure you run: pip install -e .")
    sys.exit(1)

def main():
    print("🚀 Real-Time SIEM System Demo")
    print("=" * 40)
    
    # Initialize the system
    config = ConfigManager()
    siem = SIEMCore(config)
    detector = ThreatDetector(config)
    parser = LogParser(config)
    alert_manager = AlertManager(config)
    
    print("SIEM System Initialized!")
    print(f"Version: {siem.__class__.__module__}")
    
    # Test with sample log messages
    sample_logs = [
        "User admin logged in successfully",
        "Login failed for user attacker",
        "System error: disk full",
        "Network scan detected from 10.0.0.1",
        "Database connection failed",
        "ERROR: Authentication service unavailable",
        "WARNING: Multiple failed login attempts"
    ]
    
    print("\n🔍 Analyzing sample logs...")
    for log in sample_logs:
        # Parse the log
        event = parser.parse(log)
        
        # Detect threats
        threats = detector.analyze_event(event)
        
        # Show results
        if threats:
            status = "⚠️ THREAT"
            print(f"{status}: {log}")
            for threat in threats:
                print(f"   └─ {threat.get('message', 'Threat detected')}")
                
                # Create alert for each threat
                alert = alert_manager.create_alert(threat, severity=threat.get('severity', 'medium'))
                print(f"      🚨 Alert created: {alert['alert_id']}")
        else:
            status = "✓ Normal"
            print(f"{status}: {log}")
    
    print("\n" + "=" * 40)
    print("🎉 Demo completed successfully!")
    print("\nYour SIEM package is working!")
    print("\nTo use it in other projects, run: pip install -e .")

if __name__ == "__main__":
    main()