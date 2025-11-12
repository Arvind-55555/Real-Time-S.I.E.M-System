#!/usr/bin/env python3
"""
Migration script to help move existing code to new package structure
"""

import os
import shutil
from pathlib import Path

# Mapping of old paths to new paths
MAPPING = {
    'siem_core/': 'src/realtime_siem/core/',
    'threat_detection/': 'src/realtime_siem/detection/',
    'log_parsers/': 'src/realtime_siem/parsers/',
    'alert_system/': 'src/realtime_siem/alerts/',
    'config/': 'src/realtime_siem/config/',
}

def migrate_file(old_path, new_path):
    """Migrate a single file with import updates"""
    if not os.path.exists(old_path):
        return
    
    # Create destination directory
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    
    # Read and update imports
    with open(old_path, 'r') as f:
        content = f.read()
    
    # Update import paths
    for old_import, new_import in MAPPING.items():
        old_module = old_import.replace('/', '.')
        new_module = new_import.replace('src/', '').replace('/', '.')
        content = content.replace(f'from {old_module}', f'from {new_module}')
        content = content.replace(f'import {old_module}', f'import {new_module}')
    
    # Write updated content
    with open(new_path, 'w') as f:
        f.write(content)
    
    print(f"Migrated: {old_path} → {new_path}")

def main():
    """Main migration function"""
    print("Starting migration to package structure...")
    
    # Create new directory structure
    for new_path in MAPPING.values():
        os.makedirs(new_path, exist_ok=True)
    
    # Migrate files
    for old_dir, new_dir in MAPPING.items():
        if os.path.exists(old_dir):
            for file in os.listdir(old_dir):
                if file.endswith('.py') and file != '__init__.py':
                    old_path = os.path.join(old_dir, file)
                    new_path = os.path.join(new_dir, file)
                    migrate_file(old_path, new_path)
    
    print("Migration completed!")

if __name__ == "__main__":
    main()