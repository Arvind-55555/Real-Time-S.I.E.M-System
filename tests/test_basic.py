import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from realtime_siem import SIEMCore, ThreatDetector
from realtime_siem.config import ConfigManager

class TestPackageStructure(unittest.TestCase):
    
    def test_imports(self):
        """Test that all main components can be imported"""
        from realtime_siem.core import SIEMCore, EventProcessor
        from realtime_siem.detection import ThreatDetector, RulesEngine
        from realtime_siem.parsers import LogParser, SyslogParser
        from realtime_siem.alerts import AlertManager
        
        self.assertTrue(True)  # If we get here, imports work
    
    def test_config_manager(self):
        """Test configuration management"""
        config = ConfigManager()
        self.assertIsNotNone(config.get('log_level'))
    
    def test_package_version(self):
        """Test package version"""
        from realtime_siem import __version__
        self.assertIsInstance(__version__, str)

if __name__ == '__main__':
    unittest.main()