#!/usr/bin/env python3
"""
SIEM Demo Script - Demonstrates system functionality with sample data
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager
from realtime_siem.utils.helpers import setup_logging

# Sample log data
SAMPLE_LOGS = [
    # Successful login
    '{"timestamp": "2025-12-12T10:00:00Z", "user": "alice", "action": "login", "status": "success", "source_ip": "10.0.1.50"}',
    
    # Failed login attempts (should trigger alert)
    '{"timestamp": "2025-12-12T10:01:00Z", "user": "admin", "action": "login", "status": "failed", "failed_logins": 8, "source_ip": "203.0.113.1"}',
    
    # Suspicious IP (should trigger alert)
    '{"timestamp": "2025-12-12T10:02:00Z", "user": "bob", "action": "file_access", "source_ip": "192.0.2.1", "file": "/etc/passwd"}',
    
    # Large data transfer (should trigger alert)
    '{"timestamp": "2025-12-12T10:03:00Z", "user": "charlie", "action": "upload", "bytes_sent": 150000000, "destination": "external.server.com"}',
    
    # Privilege escalation
    '{"timestamp": "2025-12-12T10:04:00Z", "user": "dave", "action": "sudo", "command": "su root"}',
    
    # Unusual time access
    '{"timestamp": "2025-12-12T02:30:00Z", "user": "eve", "action": "database_query", "type": "login", "source_ip": "10.0.2.100"}',
    
    # Syslog messages
    '<134>Dec 12 10:05:15 server1 sshd[12345]: Failed password for invalid user admin from 203.0.113.50 port 22 ssh2',
    '<134>Dec 12 10:06:20 server2 kernel: iptables: DROPPED IN=eth0 OUT= SRC=192.0.2.100 DST=10.0.0.1',
    
    # Generic log
    'ERROR: Unauthorized access attempt detected from 198.51.100.1 to resource /admin/users',
    'WARNING: Multiple failed authentication attempts from user "hacker"',
]

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_event(event, index):
    print(f"\n[Event {index+1}] ID: {event.get('event_id', 'N/A')}")
    print(f"  Type: {event.get('type', 'unknown')}")
    print(f"  Message: {event.get('message', 'N/A')[:60]}...")
    
    if 'threats' in event and event['threats']:
        print(f"  ⚠️  THREATS DETECTED: {len(event['threats'])}")
        for threat in event['threats']:
            severity = threat.get('severity', 'unknown').upper()
            threat_type = threat.get('type', threat.get('rule_name', 'unknown'))
            print(f"     [{severity}] {threat_type}")

def print_stats(stats):
    print(f"\n📊 System Statistics:")
    print(f"  Running: {stats.get('is_running', False)}")
    print(f"  Elasticsearch: {'Connected' if stats.get('elasticsearch_connected') else 'Disconnected'}")
    print(f"  Parsers: {', '.join(stats.get('parsers', []))}")
    print(f"  Total Alerts: {stats.get('alerts_count', 0)}")

def main():
    print_header("SIEM SYSTEM DEMONSTRATION")
    
    print("\n🚀 Initializing SIEM System...")
    setup_logging()
    
    config = ConfigManager()
    siem = SIEMCore(config)
    siem.start()
    
    print("✓ SIEM initialized successfully")
    
    print_header("PROCESSING SAMPLE LOGS")
    
    print(f"\n📥 Processing {len(SAMPLE_LOGS)} sample log entries...\n")
    
    processed_events = []
    
    for i, log in enumerate(SAMPLE_LOGS):
        # Determine log type
        if log.strip().startswith('{'):
            log_type = 'json'
        elif log.strip().startswith('<'):
            log_type = 'syslog'
        else:
            log_type = 'default'
        
        # Process log
        result = siem.process_log(log, log_type)
        
        if result:
            processed_events.append(result)
            print_event(result, i)
        
        time.sleep(0.1)  # Small delay for readability
    
    print_header("DETECTION SUMMARY")
    
    # Count threats by severity
    threat_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    total_threats = 0
    
    for event in processed_events:
        if 'threats' in event:
            for threat in event['threats']:
                severity = threat.get('severity', 'low')
                threat_counts[severity] = threat_counts.get(severity, 0) + 1
                total_threats += 1
    
    print(f"\n🎯 Total Threats Detected: {total_threats}")
    print(f"  Critical: {threat_counts['critical']}")
    print(f"  High: {threat_counts['high']}")
    print(f"  Medium: {threat_counts['medium']}")
    print(f"  Low: {threat_counts['low']}")
    
    # Alert details
    alerts = siem.alert_manager.get_alerts()
    print(f"\n🚨 Active Alerts: {len(alerts)}")
    
    for i, alert in enumerate(alerts[:5], 1):  # Show first 5
        print(f"\n  Alert {i}:")
        print(f"    ID: {alert['alert_id']}")
        print(f"    Severity: {alert['severity'].upper()}")
        print(f"    Status: {alert['status']}")
        print(f"    Time: {alert['timestamp']}")
    
    if len(alerts) > 5:
        print(f"\n  ... and {len(alerts) - 5} more alerts")
    
    print_header("SYSTEM STATISTICS")
    print_stats(siem.get_stats())
    
    # Component stats
    print(f"\n📈 Component Statistics:")
    print(f"  Events Processed: {siem.event_processor.get_stats()['processed_count']}")
    print(f"  Rules Loaded: {siem.threat_detector.rules_engine.get_stats()['total_rules']}")
    print(f"  Correlation History: {siem.correlation_engine.get_stats()['history_size']} events")
    print(f"  Anomaly Patterns: {siem.threat_detector.anomaly_detector.get_stats()['unique_event_patterns']}")
    
    print_header("DEMO COMPLETE")
    print("\n✓ SIEM demonstration completed successfully!")
    print("\nNext steps:")
    print("  1. Review the alerts above")
    print("  2. Check logs/siem.log for detailed logging")
    print("  3. Connect to Elasticsearch to view indexed events")
    print("  4. Customize detection rules in config/detection_rules.yaml")
    print("  5. Run real-time monitoring with scripts/monitor.py\n")
    
    siem.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
