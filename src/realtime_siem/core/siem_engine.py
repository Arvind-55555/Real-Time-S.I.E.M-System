import logging
from typing import Dict, Any, Optional, List
from elasticsearch import Elasticsearch
from ..config.config_manager import ConfigManager
from ..parsers.log_parser import LogParser, SyslogParser, JSONParser
from .event_processor import EventProcessor
from .correlation_engine import CorrelationEngine
from ..detection.threat_detector import ThreatDetector
from ..alerts.alert_manager import AlertManager

logger = logging.getLogger(__name__)


class SIEMCore:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        self.es: Optional[Elasticsearch] = None
        self.parsers: Dict[str, Any] = {}
        self.event_processor = EventProcessor(self.config)
        self.correlation_engine = CorrelationEngine(self.config)
        self.threat_detector = ThreatDetector(self.config)
        self.alert_manager = AlertManager(self.config)
        self.is_running = False
        
        self._initialize_parsers()
        logger.info("SIEM Core initialized")

    def _initialize_parsers(self):
        self.parsers = {
            'syslog': SyslogParser(self.config),
            'json': JSONParser(self.config),
            'default': LogParser(self.config)
        }
        logger.debug(f"Initialized {len(self.parsers)} parsers")

    def connect_to_elasticsearch(self):
        try:
            es_host = self.config.get('elasticsearch.host', 'localhost')
            es_port = self.config.get('elasticsearch.port', 9200)
            
            self.es = Elasticsearch(
                hosts=[f"{es_host}:{es_port}"],
                verify_certs=False
            )
            
            if self.es.ping():
                logger.info(f"Connected to Elasticsearch at {es_host}:{es_port}")
            else:
                logger.error("Elasticsearch connection failed")
                self.es = None
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            self.es = None

    def process_log(self, log_line: str, log_type: str = 'default') -> Optional[Dict[str, Any]]:
        try:
            parser = self.parsers.get(log_type, self.parsers['default'])
            parsed_event = parser.parse(log_line)
            
            processed_event = self.event_processor.process(parsed_event)
            
            threats = self.threat_detector.detect(processed_event)
            
            if threats:
                processed_event['threats'] = threats
                for threat in threats:
                    self.alert_manager.create_alert(threat, processed_event)
            
            if self.es:
                self._index_event(processed_event)
            
            return processed_event
        except Exception as e:
            logger.error(f"Error processing log: {e}")
            return None

    def _index_event(self, event: Dict[str, Any]):
        try:
            index_name = self.config.get('elasticsearch.index', 'siem-events')
            self.es.index(index=index_name, document=event)
        except Exception as e:
            logger.error(f"Failed to index event: {e}")

    def start(self):
        self.connect_to_elasticsearch()
        self.is_running = True
        logger.info("SIEM Core started")

    def stop(self):
        self.is_running = False
        if self.es:
            self.es.close()
        logger.info("SIEM Core stopped")

    def get_stats(self) -> Dict[str, Any]:
        return {
            'is_running': self.is_running,
            'elasticsearch_connected': self.es is not None and self.es.ping() if self.es else False,
            'parsers': list(self.parsers.keys()),
            'alerts_count': len(self.alert_manager.alerts)
        }
