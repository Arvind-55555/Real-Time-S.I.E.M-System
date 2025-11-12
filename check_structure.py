#!/usr/bin/env python3
"""
Check what files actually exist in the new structure
"""

import os
from pathlib import Path

def check_directory_structure():
    """Check what files were actually migrated"""
    base_dir = Path("src/realtime_siem")
    
    print("Current Package Structure:")
    print("=" * 50)
    
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(str(base_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f"{subindent}{file}")
    
    print("\n" + "=" * 50)
    
    # Check original directories
    print("\nOriginal directories (should be mostly empty now):")
    original_dirs = ['siem_core', 'threat_detection', 'log_parsers', 'alert_system', 'config']
    for dir_name in original_dirs:
        if os.path.exists(dir_name):
            files = [f for f in os.listdir(dir_name) if f.endswith('.py')]
            print(f"{dir_name}/: {len(files)} Python files")
            for file in files:
                print(f"  - {file}")

if __name__ == "__main__":
    check_directory_structure()