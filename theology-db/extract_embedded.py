#!/usr/bin/env python3
"""
Extract embedded theology database for Sanctum OS
This script extracts the embedded database to the user's home directory
"""

import sys
import os

# Add the theology-db directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the embedded data module
try:
    import theology_data_embedded
except ImportError:
    print("Error: theology_data_embedded.py not found")
    sys.exit(1)

def main():
    """Extract the database to the user's home directory"""
    output_dir = os.path.expanduser("~/.local/share/theology")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "theology.db")
    
    try:
        theology_data_embedded.extract_database(output_path)
        print(f"✓ Database extracted to: {output_path}")
        return 0
    except Exception as e:
        print(f"Error extracting database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
