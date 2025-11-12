"""Utility functions"""

def get_timestamp():
    """Get current timestamp"""
    from datetime import datetime
    return datetime.now().isoformat()

def setup_logging():
    """Setup basic logging"""
    import logging
    logging.basicConfig(level=logging.INFO)