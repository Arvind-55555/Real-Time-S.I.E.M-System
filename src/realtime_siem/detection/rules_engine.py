# In src/realtime_siem/detection/rules_engine.py
def load_real_rules(self):
    self.rules = [
        {
            "name": "multiple_failed_logins",
            "condition": "event.auth_attempts > 5",
            "severity": "high"
        },
        {
            "name": "suspicious_ip", 
            "condition": "event.source_ip in suspicious_ips",
            "severity": "medium"
        }
    ]