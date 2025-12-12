"""Main threat detection engine"""

from .rules_engine import RulesEngine
from .anomaly_detector import AnomalyDetector

class ThreatDetector:
    """Main threat detection engine"""
    
    def __init__(self, config=None):
        self.config = config
        # Initialize with simple implementations
        self.rules_engine = RulesEngine(config)
        self.anomaly_detector = AnomalyDetector(config)
        
    def detect(self, event):
        """Detect threats in a single event"""
        return self.analyze_event(event)
    
    def analyze_event(self, event):
        """Analyze a single event for threats"""
        threats = []
        
        # Rule-based detection
        rule_threats = self.rules_engine.check_rules(event)
        threats.extend(rule_threats)
        
        # Anomaly detection
        anomaly_threats = self.anomaly_detector.detect_anomalies(event)
        threats.extend(anomaly_threats)
        
        # Basic rule checking as fallback
        if not threats and self._check_basic_rules(event):
            threats.append({
                "type": "basic_rule",
                "event": event,
                "severity": "medium",
                "message": "Basic rule triggered"
            })
        
        return threats
    
    def _check_basic_rules(self, event):
        """Check basic rules - to be expanded later"""
        message = str(event.get("message", "")).lower()
        suspicious_terms = ["error", "failed", "unauthorized", "attack", "malware"]
        
        return any(term in message for term in suspicious_terms)