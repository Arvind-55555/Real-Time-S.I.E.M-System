import logging
from datetime import datetime
from typing import Any, Dict


def get_timestamp() -> str:
    return datetime.utcnow().isoformat()


def setup_logging(level: int = logging.INFO, log_file: str = None):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )


def validate_ip(ip_address: str) -> bool:
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    
    parts = ip_address.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    sensitive_keys = ['password', 'secret', 'token', 'api_key', 'credential']
    sanitized = data.copy()
    
    for key in sanitized:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = '***REDACTED***'
    
    return sanitized
