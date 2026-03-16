#!/usr/bin/env python3
"""
Sanctum OS Theology Database Extractor
Extracts the embedded Bible and Church Fathers database
"""

import os
import sys
import gzip
import base64
import sqlite3
from pathlib import Path

DATA_FILE = Path(__file__).parent / "theology_data_embedded.py"
OUTPUT_DIR = Path.home() / ".local/share/theology"
DB_PATH = OUTPUT_DIR / "theology.db"

def extract_database():
    """Extract the compressed database to the user's home directory"""
    print("Extracting Sanctum Theology Database...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Import the embedded data
    sys.path.insert(0, str(Path(__file__).parent))
    import theology_data_embedded as data
    
    # Reconstruct the compressed data
    encoded = ''.join(data.THEOLOGY_DATA_CHUNKS)
    compressed = base64.b85decode(encoded)
    
    # Decompress
    db_data = gzip.decompress(compressed)
    
    # Write to destination
    with open(DB_PATH, 'wb') as f:
        f.write(db_data)
    
    print(f"Database extracted to: {DB_PATH}")
    print(f"Size: {len(db_data):,} bytes")
    
    # Verify database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM bible_books")
    bible_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bible_verses")
    bible_verses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM church_fathers")
    fathers_texts = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Bible books: {bible_books}")
    print(f"Bible verses: {bible_verses}")
    print(f"Church Fathers texts: {fathers_texts}")
    print("Extraction complete!")
    
    return DB_PATH

if __name__ == "__main__":
    extract_database()
