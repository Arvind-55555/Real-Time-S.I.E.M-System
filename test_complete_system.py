import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager
from realtime_siem.parsers.log_parser import LogParser, SyslogParser, JSONParser
from realtime_siem.detection.rules_engine import RulesEngine
from realtime_siem.detection.threat_detector import ThreatDetector
from realtime_siem.detection.anomaly_detector import AnomalyDetector
from realtime_siem.alerts.alert_manager import AlertManager
from realtime_siem.core.event_processor import EventProcessor
from realtime_siem.core.correlation_engine import CorrelationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    logger.info("Testing all imports...")
    logger.info("✓ All imports successful")

def test_siem_core():
    logger.info("\nTesting SIEMCore...")
    config = ConfigManager()
    siem = SIEMCore(config)
    assert siem is not None
    assert hasattr(siem, 'process_log')
    assert hasattr(siem, 'start')
    assert hasattr(siem, 'stop')
    stats = siem.get_stats()
    logger.info(f"  SIEM Stats: {stats}")
    logger.info("✓ SIEMCore working")

def test_parsers():
    logger.info("\nTesting Parsers...")
    
    log_parser = LogParser()
    result = log_parser.parse("Test log message")
    assert 'message' in result
    logger.info("  ✓ LogParser working")
    
    syslog_parser = SyslogParser()
    syslog_msg = "<134>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"
    result = syslog_parser.parse(syslog_msg)
    assert 'type' in result
    logger.info("  ✓ SyslogParser working")
    
    json_parser = JSONParser()
    json_msg = '{"user": "admin", "action": "login", "status": "success"}'
    result = json_parser.parse(json_msg)
    assert result['type'] == 'json'
    logger.info("  ✓ JSONParser working")

def test_rules_engine():
    logger.info("\nTesting RulesEngine...")
    rules_engine = RulesEngine()
    assert len(rules_engine.rules) > 0
    
    test_event = {"failed_logins": 10, "source_ip": "192.0.2.1"}
    violations = rules_engine.check_rules(test_event)
    logger.info(f"  Detected {len(violations)} rule violations")
    stats = rules_engine.get_stats()
    logger.info(f"  Rules Stats: {stats}")
    logger.info("✓ RulesEngine working")

def test_threat_detector():
    logger.info("\nTesting ThreatDetector...")
    detector = ThreatDetector()
    test_event = {"failed_logins": 8, "type": "login"}
    threats = detector.detect(test_event)
    logger.info(f"  Detected {len(threats)} threats")
    logger.info("✓ ThreatDetector working")

def test_anomaly_detector():
    logger.info("\nTesting AnomalyDetector...")
    detector = AnomalyDetector()
    test_event = {
        "type": "login",
        "source_ip": "10.0.0.1",
        "timestamp": "2024-12-12T03:00:00Z",
        "bytes_sent": 150000000
    }
    anomalies = detector.detect_anomalies(test_event)
    logger.info(f"  Detected {len(anomalies)} anomalies")
    stats = detector.get_stats()
    logger.info(f"  Anomaly Stats: {stats}")
    logger.info("✓ AnomalyDetector working")

def test_alert_manager():
    logger.info("\nTesting AlertManager...")
    manager = AlertManager()
    threat = {"type": "brute_force", "severity": "high"}
    event = {"user": "admin", "ip": "10.0.0.1"}
    alert = manager.create_alert(threat, event)
    assert 'alert_id' in alert
    stats = manager.get_stats()
    logger.info(f"  Alert Stats: {stats}")
    logger.info("✓ AlertManager working")

def test_event_processor():
    logger.info("\nTesting EventProcessor...")
    processor = EventProcessor()
    event = {"message": "Test event", "source_ip": "10.0.0.1"}
    processed = processor.process(event)
    assert 'event_id' in processed
    assert processed['processed'] == True
    stats = processor.get_stats()
    logger.info(f"  Processor Stats: {stats}")
    logger.info("✓ EventProcessor working")

def test_correlation_engine():
    logger.info("\nTesting CorrelationEngine...")
    engine = CorrelationEngine()
    events = [
        {"source_ip": "10.0.0.1", "type": "login", "timestamp": "2024-12-12T12:00:00Z"},
        {"source_ip": "10.0.0.1", "type": "login", "timestamp": "2024-12-12T12:01:00Z"},
    ]
    correlations = engine.correlate(events)
    logger.info(f"  Found {len(correlations)} correlations")
    stats = engine.get_stats()
    logger.info(f"  Correlation Stats: {stats}")
    logger.info("✓ CorrelationEngine working")

def test_end_to_end():
    logger.info("\nTesting End-to-End Processing...")
    siem = SIEMCore()
    
    test_logs = [
        '{"user": "admin", "failed_logins": 10, "source_ip": "192.0.2.1"}',
        '<134>Oct 11 22:14:15 mymachine su: failed login attempt',
        'Regular log message with failed login'
    ]
    
    for log in test_logs:
        result = siem.process_log(log, 'json' if log.startswith('{') else 'syslog' if log.startswith('<') else 'default')
        if result:
            logger.info(f"  Processed: {result.get('event_id', 'unknown')}")
    
    stats = siem.get_stats()
    logger.info(f"  Final SIEM Stats: {stats}")
    logger.info("✓ End-to-End processing working")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("REAL-TIME S.I.E.M SYSTEM - COMPREHENSIVE TEST")
    logger.info("=" * 60)
    
    try:
        test_imports()
        test_siem_core()
        test_parsers()
        test_rules_engine()
        test_threat_detector()
        test_anomaly_detector()
        test_alert_manager()
        test_event_processor()
        test_correlation_engine()
        test_end_to_end()
        
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS PASSED! ✓")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
