import logging
import re
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RulesEngine:
    def __init__(self, config=None, rules_file: Optional[str] = None):
        self.config = config
        self.rules: List[Dict[str, Any]] = []
        self.rules_file = rules_file
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 10000
        
        if rules_file:
            self.load_rules_from_file(rules_file)
        else:
            self._load_default_rules()
        
        logger.info(f"RulesEngine initialized with {len(self.rules)} rules")

    def _load_default_rules(self):
        self.rules = [
            {
                "name": "multiple_failed_logins",
                "description": "Detect multiple failed login attempts",
                "condition": "failed_logins > 5",
                "severity": "high",
                "field": "failed_logins",
                "threshold": 5,
                "operator": ">"
            },
            {
                "name": "suspicious_ip",
                "description": "Detect connections from suspicious IP addresses",
                "condition": "source_ip in blacklist",
                "severity": "medium",
                "field": "source_ip",
                "blacklist": ["192.0.2.1", "198.51.100.1", "203.0.113.1"]
            },
            {
                "name": "privilege_escalation",
                "description": "Detect privilege escalation attempts",
                "condition": "action == 'sudo' or action == 'su'",
                "severity": "high",
                "field": "action",
                "values": ["sudo", "su"]
            },
            {
                "name": "data_exfiltration",
                "description": "Detect large data transfers",
                "condition": "bytes_sent > 1000000",
                "severity": "critical",
                "field": "bytes_sent",
                "threshold": 1000000,
                "operator": ">"
            }
        ]

    def load_rules_from_file(self, rules_file: str):
        try:
            path = Path(rules_file)
            if not path.exists():
                logger.error(f"Rules file not found: {rules_file}")
                self._load_default_rules()
                return
            
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
            if 'rules' in data:
                self.rules = data['rules']
                self._process_rules()
                logger.info(f"Loaded {len(self.rules)} rules from {rules_file}")
            else:
                logger.warning(f"No rules found in {rules_file}, loading defaults")
                self._load_default_rules()
        except Exception as e:
            logger.error(f"Error loading rules from file: {e}")
            self._load_default_rules()

    def _process_rules(self):
        for rule in self.rules:
            if 'condition' in rule:
                condition = rule['condition']
                
                if '>' in condition:
                    parts = condition.split('>')
                    rule['field'] = parts[0].strip().replace('event.', '')
                    rule['operator'] = '>'
                    threshold_str = parts[1].strip().split()[0]
                    rule['threshold'] = int(threshold_str) if threshold_str.isdigit() else threshold_str
                
                elif '<' in condition:
                    parts = condition.split('<')
                    rule['field'] = parts[0].strip().replace('event.', '')
                    rule['operator'] = '<'
                    threshold_str = parts[1].strip().split()[0]
                    rule['threshold'] = int(threshold_str) if threshold_str.isdigit() else threshold_str
                
                elif '==' in condition:
                    parts = condition.split('==')
                    rule['field'] = parts[0].strip().replace('event.', '')
                    rule['operator'] = '=='
                    rule['value'] = parts[1].strip().strip('"').strip("'")
                
                elif 'in' in condition:
                    parts = condition.split('in')
                    rule['field'] = parts[0].strip().replace('event.', '')
                    rule['operator'] = 'in'

    def check_rules(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        for rule in self.rules:
            try:
                if self._evaluate_rule(rule, event):
                    violation = {
                        'rule_name': rule.get('name', 'unknown'),
                        'description': rule.get('description', ''),
                        'severity': rule.get('severity', 'medium'),
                        'matched_condition': rule.get('condition', ''),
                        'event': event,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    violations.append(violation)
                    logger.warning(f"Rule violation detected: {rule['name']}")
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('name', 'unknown')}: {e}")
        
        return violations

    def _evaluate_rule(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        field = rule.get('field')
        operator = rule.get('operator')
        
        if not field or field not in event:
            return False
        
        event_value = event[field]
        
        if operator == '>':
            threshold = rule.get('threshold', 0)
            return float(event_value) > float(threshold) if self._is_numeric(event_value) else False
        
        elif operator == '<':
            threshold = rule.get('threshold', 0)
            return float(event_value) < float(threshold) if self._is_numeric(event_value) else False
        
        elif operator == '==':
            return str(event_value) == str(rule.get('value', ''))
        
        elif operator == 'in':
            blacklist = rule.get('blacklist', [])
            values = rule.get('values', [])
            check_list = blacklist or values
            return event_value in check_list
        
        elif operator == 'regex':
            pattern = rule.get('pattern', '')
            return bool(re.match(pattern, str(event_value)))
        
        return False

    def _is_numeric(self, value) -> bool:
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def add_rule(self, rule: Dict[str, Any]):
        self.rules.append(rule)
        self._process_rules()
        logger.info(f"Added new rule: {rule.get('name', 'unknown')}")

    def remove_rule(self, rule_name: str):
        self.rules = [r for r in self.rules if r.get('name') != rule_name]
        logger.info(f"Removed rule: {rule_name}")

    def get_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule.get('name') == rule_name:
                return rule
        return None

    def reload_rules(self):
        if self.rules_file:
            self.load_rules_from_file(self.rules_file)
        else:
            self._load_default_rules()
        logger.info("Rules reloaded")

    def get_stats(self) -> Dict[str, Any]:
        severity_counts = {}
        for rule in self.rules:
            severity = rule.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_rules': len(self.rules),
            'severity_distribution': severity_counts,
            'rules_file': self.rules_file
        }
