# config.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'siem',
    'user': 'siem_user',
    'password': 'password'
}

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}