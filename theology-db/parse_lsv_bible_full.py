#!/usr/bin/env python3
"""
Parse LSV Bible from Biblia Sacra et Ultra - FULL VERSION
Extracts all 66 books with complete verse-by-verse text
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class LSVBibleParser:
    """Parse the Literal Standard Version (LSV) Bible from HTML files."""
    
    # Book canonical order with approximate file ranges
    LSV_BOOKS = [
        ('Genesis', 1, 50),
        ('Exodus', 1, 40),
        ('Leviticus', 1, 27),
        ('Numbers', 1, 36),
        ('Deuteronomy', 1, 34),
        ('Joshua', 1, 24),
        ('Judges', 1, 21),
        ('Ruth', 1, 4),
        ('1 Samuel', 1, 31),
        ('2 Samuel', 1, 24),
        ('1 Kings', 1, 22),
        ('2 Kings', 1, 25),
        ('1 Chronicles', 1, 29),
        ('2 Chronicles', 1, 36),
        ('Ezra', 1, 10),
        ('Nehemiah', 1, 13),
        ('Esther', 1, 10),
        ('Job', 1, 42),
        ('Psalms', 1, 150),
        ('Proverbs', 1, 31),
        ('Ecclesiastes', 1, 12),
        ('Song of Solomon', 1, 8),
        ('Isaiah', 1, 66),
        ('Jeremiah', 1, 52),
        ('Lamentations', 1, 5),
        ('Ezekiel', 1, 48),
        ('Daniel', 1, 12),
        ('Hosea', 1, 14),
        ('Joel', 1, 3),
        ('Amos', 1, 9),
        ('Obadiah', 1, 1),
        ('Jonah', 1, 4),
        ('Micah', 1, 7),
        ('Nahum', 1, 3),
        ('Habakkuk', 1, 3),
        ('Zephaniah', 1, 3),
        ('Haggai', 1, 2),
        ('Zechariah', 1, 14),
        ('Malachi', 1, 4),
        ('Matthew', 1, 28),
        ('Mark', 1, 16),
        ('Luke', 1, 24),
        ('John', 1, 21),
        ('Acts', 1, 28),
        ('Romans', 1, 16),
        ('1 Corinthians', 1, 16),
        ('2 Corinthians', 1, 13),
        ('Galatians', 1, 6),
        ('Ephesians', 1, 6),
        ('Philippians', 1, 4),
        ('Colossians', 1, 4),
        ('1 Thessalonians', 1, 5),
        ('2 Thessalonians', 1, 3),
        ('1 Timothy', 1, 6),
        ('2 Timothy', 1, 4),
        ('Titus', 1, 3),
        ('Philemon', 1, 1),
        ('Hebrews', 1, 13),
        ('James', 1, 5),
        ('1 Peter', 1, 5),
        ('2 Peter', 1, 3),
        ('1 John', 1, 5),
        ('2 John', 1, 1),
        ('3 John', 1, 1),
        ('Jude', 1, 1),
        ('Revelation', 1, 22),
    ]
    
    def __init__(self, text_dir: str):
        self.text_dir = Path(text_dir)
        self.html_files = sorted(self.text_dir.glob('part*.html'))
    
    def identify_book(self, html_file: Path) -> Optional[str]:
        """Identify which book an HTML file belongs to by examining content."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove HTML tags temporarily for searching
            text = re.sub(r'<[^>]+>', ' ', content)
            
            # Look for book titles in various patterns
            for book_name, _, _ in self.LSV_BOOKS:
                # Pattern 1: "THE BOOK OF GENESIS"
                if re.search(rf'BOOK OF {re.escape(book_name.upper())}', text):
                    return book_name
                # Pattern 2: Just the book name as a header
                if re.search(rf'\b{re.escape(book_name)}\b', text[:5000]):
                    # Check it's not just a reference
                    if text[:5000].count(book_name) >= 2:
                        return book_name
        except Exception:
            pass
        return None
    
    def parse_book(self, html_file: Path, book_name: str) -> List[Dict]:
        """Parse a single book HTML file."""
        verses = []
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {html_file}: {e}")
            return verses
        
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # Find all paragraph tags with verse content
        # LSV uses <p class="block_5"> for verses typically
        verse_pattern = re.compile(r'<p[^>]*class="[^"]*block[^"]*"[^>]*>(.*?)</p>', re.DOTALL)
        
        chapter_num = 1
        
        for match in verse_pattern.finditer(content):
            verse_html = match.group(1)
            
            # Extract text content
            text = re.sub(r'<[^>]+>', ' ', verse_html)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Skip empty or copyright lines
            if not text or len(text) < 5:
                continue
            if 'Covenant Press' in text or 'copyright' in text.lower():
                continue
            
            # Skip if it's just a number (chapter marker)
            if text.isdigit():
                chapter_num = int(text)
                continue
            
            # Try to extract verse number and text
            # Pattern: "16 And God said..." or "1 In the beginning..."
            verse_match = re.match(r'^(\d+)\s+(.+)$', text)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2)
                
                # Clean up verse text
                verse_text = verse_text.strip()
                
                # Determine testament
                if book_name in ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
                                 '1 Corinthians', '2 Corinthians', 'Galatians',
                                 'Ephesians', 'Philippians', 'Colossians',
                                 '1 Thessalonians', '2 Thessalonians', '1 Timothy',
                                 '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
                                 'James', '1 Peter', '2 Peter', '1 John', '2 John',
                                 '3 John', 'Jude', 'Revelation']:
                    testament = 'NT'
                else:
                    testament = 'OT'
                
                verses.append({
                    'book': book_name,
                    'testament': testament,
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'content': verse_text
                })
        
        return verses
    
    def extract_all_books(self) -> List[Dict]:
        """Extract all books from the LSV Bible."""
        all_verses = []
        processed_books = set()
        
        print(f"Scanning {len(self.html_files)} HTML files...")
        
        for html_file in sorted(self.html_files):
            book_name = self.identify_book(html_file)
            if book_name and book_name not in processed_books:
                print(f"  Processing {book_name}...")
                verses = self.parse_book(html_file, book_name)
                all_verses.extend(verses)
                if verses:
                    processed_books.add(book_name)
        
        return all_verses
    
    def populate_database(self, db_path: str):
        """Populate SQLite database with all Bible verses."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing Bible data
        cursor.execute("DELETE FROM bible_verses")
        
        verses = self.extract_all_books()
        
        print(f"\nInserting {len(verses)} verses into database...")
        
        # Insert in batches for efficiency
        batch_size = 1000
        for i in range(0, len(verses), batch_size):
            batch = verses[i:i+batch_size]
            cursor.executemany('''
                INSERT INTO bible_verses (book, testament, chapter, verse, content)
                VALUES (?, ?, ?, ?, ?)
            ''', [(v['book'], v['testament'], v['chapter'], v['verse'], v['content']) for v in batch])
            conn.commit()
        
        conn.close()
        
        print(f"✓ Inserted {len(verses)} verses")
        
        # Print summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT testament, COUNT(*) FROM bible_verses GROUP BY testament")
        for testament, count in cursor.fetchall():
            print(f"  {testament}: {count} verses")
        cursor.execute("SELECT COUNT(DISTINCT book) FROM bible_verses")
        book_count = cursor.fetchone()[0]
        print(f"  Total books: {book_count}")
        conn.close()

if __name__ == '__main__':
    import sys
    
    bible_dir = '/home/workspace/Christianity_Compilation/EXTRACTED/Biblia_Sacra/text'
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    if not os.path.exists(bible_dir):
        print(f"Error: Bible directory not found: {bible_dir}")
        sys.exit(1)
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        print("Run 'python3 package_theology.py' first to create the database structure.")
        sys.exit(1)
    
    parser = LSVBibleParser(bible_dir)
    parser.populate_database(db_path)
    print("\n✓ Bible extraction complete!")
