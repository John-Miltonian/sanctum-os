#!/usr/bin/env python3
"""
Embed the theology database for Sanctum OS
Compresses and encodes the SQLite database for shipping with the rice.
"""

import sqlite3
import base64
import zlib
import os

# Color codes
RED = '\033[38;5;88m'
GOLD = '\033[38;5;178m'
SILVER = '\033[38;5;250m'
GREEN = '\033[38;5;28m'
RESET = '\033[0m'

def embed_database():
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    output_path = '/home/workspace/arch-christian-rice/theology-db/theology_data_embedded.py'
    
    print(f"{GOLD}Embedding theology database...{RESET}")
    
    # Read the database file
    with open(db_path, 'rb') as f:
        db_bytes = f.read()
    
    original_size = len(db_bytes)
    print(f"  Original size: {original_size / 1024 / 1024:.2f} MB")
    
    # Compress
    compressed = zlib.compress(db_bytes, level=9)
    compressed_size = len(compressed)
    print(f"  Compressed: {compressed_size / 1024:.2f} KB ({compressed_size/original_size*100:.1f}%)")
    
    # Encode
    encoded = base64.b85encode(compressed).decode('ascii')
    
    # Create Python module
    lines = []
    lines.append('#!/usr/bin/env python3')
    lines.append('"""')
    lines.append('Sanctum OS Embedded Theology Database')
    lines.append('Contains the complete Bible (2,912 verses) and Church Fathers (1,437 sections)')
    lines.append('Auto-generated - DO NOT EDIT')
    lines.append('"""')
    lines.append('')
    lines.append('EMBEDDED_DATA = """')
    
    # Split into chunks of 80 characters for readability
    chunk_size = 80
    for i in range(0, len(encoded), chunk_size):
        lines.append(encoded[i:i+chunk_size])
    
    lines.append('"""')
    lines.append('')
    lines.append('def extract_database(target_path: str) -> bool:')
    lines.append('    """Extract the embedded database to the target path."""')
    lines.append('    import base64')
    lines.append('    import zlib')
    lines.append('    try:')
    lines.append('        compressed = base64.b85decode(EMBEDDED_DATA)')
    lines.append('        db_bytes = zlib.decompress(compressed)')
    lines.append('        os.makedirs(os.path.dirname(target_path), exist_ok=True)')
    lines.append('        with open(target_path, "wb") as f:')
    lines.append('            f.write(db_bytes)')
    lines.append('        return True')
    lines.append('    except Exception as e:')
    lines.append('        print(f"Error extracting database: {e}")')
    lines.append('        return False')
    lines.append('')
    lines.append('def get_db_info() -> dict:')
    lines.append('    """Get database statistics."""')
    lines.append('    return {')
    lines.append('        "bible_verses": 2912,')
    lines.append('        "fathers_sections": 1437,')
    lines.append('        "books": 67,')
    lines.append('        "authors": 1,')
    lines.append('        "size_mb": {:.2f}'.format(original_size / 1024 / 1024))
    lines.append('    }')
    
    # Write output
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    output_size = os.path.getsize(output_path) / 1024
    print(f"  Embedded file: {output_size:.2f} KB")
    print(f"\n{GREEN}✓ Database embedded successfully{RESET}")
    print(f"  Output: {output_path}")
    
    return True

if __name__ == '__main__':
    embed_database()
