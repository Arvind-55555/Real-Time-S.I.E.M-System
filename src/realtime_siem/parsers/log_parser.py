import logging
import re
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LogParser:
    def __init__(self, config=None):
        self.config = config
    
    def parse(self, log_line: str) -> Dict[str, Any]:
        return {
            "message": log_line.strip(),
            "type": "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }


class SyslogParser(LogParser):
    def __init__(self, config=None):
        super().__init__(config)
        self.rfc3164_pattern = re.compile(
            r'^<(?P<priority>\d+)>(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<hostname>\S+)\s+(?P<process>\S+?)(\[(?P<pid>\d+)\])?:\s*(?P<message>.*)$'
        )
        self.rfc5424_pattern = re.compile(
            r'^<(?P<priority>\d+)>(?P<version>\d+)\s+(?P<timestamp>\S+)\s+'
            r'(?P<hostname>\S+)\s+(?P<appname>\S+)\s+(?P<procid>\S+)\s+'
            r'(?P<msgid>\S+)\s+(?P<structured_data>\S+)\s*(?P<message>.*)$'
        )
    
    def parse(self, log_line: str) -> Dict[str, Any]:
        log_line = log_line.strip()
        
        rfc5424_match = self.rfc5424_pattern.match(log_line)
        if rfc5424_match:
            return self._parse_rfc5424(rfc5424_match, log_line)
        
        rfc3164_match = self.rfc3164_pattern.match(log_line)
        if rfc3164_match:
            return self._parse_rfc3164(rfc3164_match, log_line)
        
        return {
            'message': log_line,
            'raw_message': log_line,
            'type': 'syslog',
            'timestamp': datetime.utcnow().isoformat(),
            'parse_status': 'unknown_format'
        }
    
    def _parse_rfc3164(self, match: re.Match, raw_line: str) -> Dict[str, Any]:
        priority = int(match.group('priority'))
        facility = priority >> 3
        severity = priority & 0x07
        
        event = {
            'type': 'syslog',
            'format': 'RFC3164',
            'priority': priority,
            'facility': facility,
            'severity': severity,
            'timestamp': match.group('timestamp'),
            'hostname': match.group('hostname'),
            'process': match.group('process'),
            'pid': match.group('pid'),
            'message': match.group('message'),
            'raw_message': raw_line
        }
        return event
    
    def _parse_rfc5424(self, match: re.Match, raw_line: str) -> Dict[str, Any]:
        priority = int(match.group('priority'))
        facility = priority >> 3
        severity = priority & 0x07
        
        event = {
            'type': 'syslog',
            'format': 'RFC5424',
            'priority': priority,
            'facility': facility,
            'severity': severity,
            'version': match.group('version'),
            'timestamp': match.group('timestamp'),
            'hostname': match.group('hostname'),
            'appname': match.group('appname'),
            'procid': match.group('procid'),
            'msgid': match.group('msgid'),
            'structured_data': match.group('structured_data'),
            'message': match.group('message'),
            'raw_message': raw_line
        }
        return event


class JSONParser(LogParser):
    def __init__(self, config=None):
        super().__init__(config)
    
    def parse(self, log_line: str) -> Dict[str, Any]:
        import json
        try:
            parsed = json.loads(log_line)
            if not isinstance(parsed, dict):
                parsed = {'value': parsed}
            parsed['type'] = 'json'
            if 'timestamp' not in parsed:
                parsed['timestamp'] = datetime.utcnow().isoformat()
            return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON log: {e}")
            return {
                'message': log_line.strip(),
                'raw_message': log_line,
                'type': 'json',
                'parse_status': 'failed',
                'timestamp': datetime.utcnow().isoformat()
            }
