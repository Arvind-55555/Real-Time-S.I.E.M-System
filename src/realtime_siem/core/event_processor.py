import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EventProcessor:
    def __init__(self, config=None):
        self.config = config
        self.processed_count = 0
    
    def process(self, event: Dict[str, Any]) -> Dict[str, Any]:
        self.processed_count += 1
        
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat()
        
        if 'event_id' not in event:
            event['event_id'] = f"evt_{self.processed_count}_{int(datetime.utcnow().timestamp())}"
        
        event['processed'] = True
        event['processed_at'] = datetime.utcnow().isoformat()
        
        event = self._enrich_event(event)
        event = self._normalize_event(event)
        
        logger.debug(f"Event processed: {event.get('event_id')}")
        return event
    
    def _enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        if 'source_ip' in event:
            event['ip_type'] = self._classify_ip(event['source_ip'])
        
        if 'user' in event and event['user'] == 'root':
            event['privileged_user'] = True
        
        return event
    
    def _classify_ip(self, ip: str) -> str:
        if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
            return 'private'
        elif ip.startswith('127.'):
            return 'loopback'
        else:
            return 'public'
    
    def _normalize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        if 'msg' in event and 'message' not in event:
            event['message'] = event['msg']
        
        if 'src_ip' in event and 'source_ip' not in event:
            event['source_ip'] = event['src_ip']
        
        if 'dst_ip' in event and 'destination_ip' not in event:
            event['destination_ip'] = event['dst_ip']
        
        return event
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'processed_count': self.processed_count
        }
