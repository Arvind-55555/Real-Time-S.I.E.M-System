"""
Real-Time Security Information and Event Management System
A comprehensive SIEM solution for real-time security monitoring.
"""

__version__ = "0.1.0"
__author__ = "Arvind"
__email__ = "arvind.saane.111@gmail.com"

# Import core components
from .core.siem_engine import SIEMCore
from .config.config_manager import ConfigManager

__all__ = [
    "SIEMCore",
    "ConfigManager",
]