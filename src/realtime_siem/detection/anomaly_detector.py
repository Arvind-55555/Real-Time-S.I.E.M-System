import logging
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(self, config=None):
        self.config = config
        self.event_counts = defaultdict(int)
        self.baseline_window = timedelta(hours=1)
        self.anomaly_threshold_multiplier = 3.0
        self.event_history = []
        self.max_history = 10000
    
    def detect_anomalies(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        anomalies = []
        
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        if self._check_frequency_anomaly(event):
            anomalies.append({
                "type": "frequency_anomaly",
                "event": event,
                "severity": "high",
                "message": "Unusual event frequency detected",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if self._check_rare_event(event):
            anomalies.append({
                "type": "rare_event",
                "event": event,
                "severity": "medium",
                "message": "Rare event type detected",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if self._check_unusual_time(event):
            anomalies.append({
                "type": "unusual_time",
                "event": event,
                "severity": "medium",
                "message": "Event occurred at unusual time",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        if self._check_data_volume_anomaly(event):
            anomalies.append({
                "type": "data_volume_anomaly",
                "event": event,
                "severity": "high",
                "message": "Unusual data volume detected",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return anomalies
    
    def _check_frequency_anomaly(self, event: Dict[str, Any]) -> bool:
        event_type = event.get('type', 'unknown')
        source_ip = event.get('source_ip', 'unknown')
        key = f"{event_type}_{source_ip}"
        
        self.event_counts[key] += 1
        
        recent_events = [e for e in self.event_history 
                        if e.get('type') == event_type and 
                        e.get('source_ip') == source_ip]
        
        if len(recent_events) > 20:
            avg_rate = len(recent_events) / max(len(self.event_history), 1)
            current_rate = self.event_counts[key] / max(len(self.event_history), 1)
            
            if current_rate > avg_rate * self.anomaly_threshold_multiplier:
                return True
        
        return False
    
    def _check_rare_event(self, event: Dict[str, Any]) -> bool:
        event_type = event.get('type', 'unknown')
        type_events = [e for e in self.event_history if e.get('type') == event_type]
        
        if len(self.event_history) > 100 and len(type_events) < 3:
            return True
        
        return False
    
    def _check_unusual_time(self, event: Dict[str, Any]) -> bool:
        timestamp = event.get('timestamp')
        if not timestamp:
            return False
        
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = event_time.hour
            
            if hour < 6 or hour > 22:
                event_type = event.get('type', '')
                if event_type in ['login', 'file_access', 'database_query']:
                    return True
        except Exception:
            pass
        
        return False
    
    def _check_data_volume_anomaly(self, event: Dict[str, Any]) -> bool:
        bytes_sent = event.get('bytes_sent', 0)
        bytes_received = event.get('bytes_received', 0)
        
        total_bytes = bytes_sent + bytes_received
        
        if total_bytes > 100 * 1024 * 1024:
            return True
        
        if bytes_sent > 0:
            historical_bytes = [e.get('bytes_sent', 0) for e in self.event_history 
                              if e.get('bytes_sent', 0) > 0]
            if historical_bytes:
                avg_bytes = sum(historical_bytes) / len(historical_bytes)
                if bytes_sent > avg_bytes * self.anomaly_threshold_multiplier:
                    return True
        
        return False
    
    def reset_baseline(self):
        self.event_counts.clear()
        self.event_history.clear()
        logger.info("Anomaly detector baseline reset")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_events_tracked': len(self.event_history),
            'unique_event_patterns': len(self.event_counts),
            'max_history': self.max_history,
            'threshold_multiplier': self.anomaly_threshold_multiplier
        }
