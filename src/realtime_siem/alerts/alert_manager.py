import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertManager:
    def __init__(self, config=None):
        self.config = config
        self.alerts: List[Dict[str, Any]] = []
        self.alert_counter = 0
    
    def create_alert(self, threat: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
        self.alert_counter += 1
        alert = {
            "alert_id": f"alert_{self.alert_counter}_{int(datetime.utcnow().timestamp())}",
            "threat": threat,
            "event": event,
            "severity": threat.get('severity', 'medium'),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "open"
        }
        self.alerts.append(alert)
        logger.warning(f"Alert created: {alert['alert_id']} - {threat.get('type', 'unknown')}")
        return alert
    
    def get_alerts(self, severity: str = None, status: str = None) -> List[Dict[str, Any]]:
        filtered = self.alerts
        if severity:
            filtered = [a for a in filtered if a.get('severity') == severity]
        if status:
            filtered = [a for a in filtered if a.get('status') == status]
        return filtered
    
    def close_alert(self, alert_id: str):
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['status'] = 'closed'
                alert['closed_at'] = datetime.utcnow().isoformat()
                logger.info(f"Alert closed: {alert_id}")
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_alerts': len(self.alerts),
            'open_alerts': len([a for a in self.alerts if a['status'] == 'open']),
            'closed_alerts': len([a for a in self.alerts if a['status'] == 'closed']),
            'severity_distribution': self._get_severity_distribution()
        }
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        distribution = {}
        for alert in self.alerts:
            severity = alert.get('severity', 'unknown')
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution
