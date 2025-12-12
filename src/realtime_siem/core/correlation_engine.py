import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class CorrelationEngine:
    def __init__(self, config=None):
        self.config = config
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        self.correlation_window = timedelta(minutes=5)
    
    def correlate(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        correlations = []
        
        for event in events:
            self.event_history.append(event)
        
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]
        
        correlations.extend(self._correlate_by_source_ip())
        correlations.extend(self._correlate_by_user())
        correlations.extend(self._correlate_by_pattern())
        
        return correlations
    
    def _correlate_by_source_ip(self) -> List[Dict[str, Any]]:
        correlations = []
        ip_events = defaultdict(list)
        
        cutoff_time = datetime.utcnow() - self.correlation_window
        
        for event in self.event_history:
            if 'source_ip' in event:
                event_time = self._parse_timestamp(event.get('timestamp'))
                if event_time and event_time > cutoff_time:
                    ip_events[event['source_ip']].append(event)
        
        for ip, events in ip_events.items():
            if len(events) > 5:
                correlations.append({
                    'type': 'multiple_events_same_ip',
                    'source_ip': ip,
                    'event_count': len(events),
                    'events': events,
                    'severity': 'medium',
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return correlations
    
    def _correlate_by_user(self) -> List[Dict[str, Any]]:
        correlations = []
        user_events = defaultdict(list)
        
        cutoff_time = datetime.utcnow() - self.correlation_window
        
        for event in self.event_history:
            if 'user' in event:
                event_time = self._parse_timestamp(event.get('timestamp'))
                if event_time and event_time > cutoff_time:
                    user_events[event['user']].append(event)
        
        for user, events in user_events.items():
            if len(events) > 10:
                correlations.append({
                    'type': 'suspicious_user_activity',
                    'user': user,
                    'event_count': len(events),
                    'events': events,
                    'severity': 'high',
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return correlations
    
    def _correlate_by_pattern(self) -> List[Dict[str, Any]]:
        correlations = []
        
        failed_logins = [e for e in self.event_history if e.get('event_type') == 'failed_login']
        if len(failed_logins) > 5:
            correlations.append({
                'type': 'brute_force_pattern',
                'event_count': len(failed_logins),
                'severity': 'high',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return correlations
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        try:
            if isinstance(timestamp_str, str):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            return datetime.utcnow()
        except Exception:
            return datetime.utcnow()
    
    def clear_history(self):
        self.event_history.clear()
        logger.info("Correlation engine history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'history_size': len(self.event_history),
            'max_history_size': self.max_history_size,
            'correlation_window_minutes': int(self.correlation_window.total_seconds() / 60)
        }
