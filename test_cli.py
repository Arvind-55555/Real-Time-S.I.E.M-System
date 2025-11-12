#!/usr/bin/env python3
"""
Test the CLI functionality directly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from realtime_siem.main import cli
    print("✅ CLI module imported successfully!")
    print("You can run: python -m realtime_siem.main --help")
except ImportError as e:
    print(f"❌ CLI import failed: {e}")