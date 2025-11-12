#!/usr/bin/env python3
"""
Fix import statements in migrated files
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix various import patterns
    patterns = [
        (r'from siem_core', 'from realtime_siem.core'),
        (r'from threat_detection', 'from realtime_siem.detection'),
        (r'from log_parsers', 'from realtime_siem.parsers'),
        (r'from alert_system', 'from realtime_siem.alerts'),
        (r'import siem_core', 'import realtime_siem.core'),
        (r'import threat_detection', 'import realtime_siem.detection'),
        (r'import log_parsers', 'import realtime_siem.parsers'),
        (r'import alert_system', 'import realtime_siem.alerts'),
    ]
    
    for old_pattern, new_pattern in patterns:
        content = re.sub(old_pattern, new_pattern, content)
    
    # Write fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed imports in: {file_path}")

def main():
    """Fix imports in all Python files"""
    src_dir = Path("src/realtime_siem")
    
    for py_file in src_dir.rglob("*.py"):
        fix_imports_in_file(py_file)
    
    print("Import fixing completed!")

if __name__ == "__main__":
    main()