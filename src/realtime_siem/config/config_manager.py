import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration management for SIEM system
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        return yaml.safe_load(f)
                    elif self.config_path.endswith('.json'):
                        return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'log_level': 'INFO',
            'elasticsearch': {
                'host': 'localhost',
                'port': 9200,
                'index': 'siem-events'
            },
            'detection': {
                'rules_path': 'config/detection_rules.yaml',
                'enable_anomaly_detection': True
            },
            'alerts': {
                'email_enabled': False,
                'slack_enabled': False,
                'webhook_enabled': True
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value