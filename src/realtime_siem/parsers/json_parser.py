"""JSON parser module"""

class JSONParser:
    """Parses JSON log messages"""
    
    def __init__(self, config=None):
        self.config = config
    
    def parse(self, log_line):
        """Parse a JSON log line"""
        import json
        try:
            parsed = json.loads(log_line)
            parsed["type"] = "json"
            return parsed
        except json.JSONDecodeError:
            return {"message": log_line.strip(), "type": "json", "error": "parse_failed"}