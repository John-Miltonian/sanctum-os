#!/usr/bin/env python3
"""
Extract LSV Bible from Biblia Sacra et Ultra EPUB
Parses HTML files and populates the theology database
"""

import os
import re
import sqlite3
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Tuple, Optional

# Source directory
BIBLE_DIR = Path("/home/workspace/Christianity_Compilation/EXTRACTED/Biblia_Sacra/text")
DB_PATH = Path.home() / ".local/share/theology/theology.db"

# Book mapping from TOC
# Based on part0002.html TOC structure
BOOK_MAP = [
    # (book_name, testament, start_part_num, chapters)
    # Old Testament
    ("Genesis", "OT", 10, 50),
    ("Exodus", "OT", 61, 40),
    ("Leviticus", "OT", 102, 27),
    ("Numbers", "OT", 130, 36),
    ("Deuteronomy", "OT", 167, 34),
    ("Joshua", "OT", 202, 24),
    ("Judges", "OT", 227, 21),
    ("Ruth", "OT", 249, 4),
    ("1 Samuel", "OT", 254, 31),
    ("2 Samuel", "OT", 286, 24),
    ("1 Kings", "OT", 311, 22),
    ("2 Kings", "OT", 334, 25),
    ("1 Chronicles", "OT", 360, 29),
    ("2 Chronicles", "OT", 390, 36),
    ("Ezra", "OT", 427, 10),
    ("Nehemiah", "OT", 438, 13),
    ("Esther", "OT", 452, 10),
    ("Job", "OT", 463, 42),
    ("Psalms", "OT", 506, 150),
    ("Proverbs", "OT", 509, 31),
    ("Ecclesiastes", "OT", 541, 12),
    ("Song of Solomon", "OT", 554, 8),
    ("Isaiah", "OT", 563, 66),
    ("Jeremiah", "OT", 630, 52),
    ("Lamentations", "OT", 683, 5),
    ("Ezekiel", "OT", 689, 48),
    ("Daniel", "OT", 738, 14),
    ("Hosea", "OT", 751, 14),
    ("Joel", "OT", 766, 3),
    ("Amos", "OT", 770, 9),
    ("Obadiah", "OT", 780, 1),
    ("Jonah", "OT", 782, 4),
    ("Micah", "OT", 787, 7),
    ("Nahum", "OT", 795, 3),
    ("Habakkuk", "OT", 799, 3),
    ("Zephaniah", "OT", 803, 3),
    ("Haggai", "OT", 807, 2),
    ("Zechariah", "OT", 810, 14),
    ("Malachi", "OT", 825, 4),
    # New Testament
    ("Matthew", "NT", 830, 28),
    ("Mark", "NT", 859, 16),
    ("Luke", "NT", 876, 24),
    ("John", "NT", 901, 21),
    ("Acts", "NT", 923, 28),
    ("Romans", "NT", 952, 16),
    ("1 Corinthians", "NT", 969, 16),
    ("2 Corinthians", "NT", 986, 13),
    ("Galatians", "NT", 1000, 6),
    ("Ephesians", "NT", 1007, 6),
    ("Philippians", "NT", 1014, 4),
    ("Colossians", "NT", 1019, 4),
    ("1 Thessalonians", "NT", 1024, 5),
    ("2 Thessalonians", "NT", 1030, 3),
    ("1 Timothy", "NT", 1034, 6),
    ("2 Timothy", "NT", 1041, 4),
    ("Titus", "NT", 1046, 3),
    ("Philemon", "NT", 1050, 1),
    ("Hebrews", "NT", 1052, 13),
    ("James", "NT", 1066, 5),
    ("1 Peter", "NT", 1072, 5),
    ("2 Peter", "NT", 1078, 3),
    ("1 John", "NT", 1082, 5),
    ("2 John", "NT", 1088, 1),
    ("3 John", "NT", 1090, 1),
    ("Jude", "NT", 1092, 1),
    ("Revelation", "NT", 1094, 22),
]

class VerseExtractor(HTMLParser):
    """Extract verses from Bible chapter HTML"""
    
    def __init__(self):
        super().__init__()
        self.verses: List[Tuple[int, str]] = []
        self.current_verse: Optional[int] = None
        self.current_text: List[str] = []
        self.in_verse_sup = False
        self.in_text = False
        self.text_content: List[str] = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Look for verse number in <sup class="calibre6">
        if tag == 'sup' and attrs_dict.get('class') == 'calibre6':
            self.in_verse_sup = True
            
        # Look for text content in <span class="text_2"> or other text elements
        if tag in ['span', 'p']:
            self.in_text = True
            
    def handle_endtag(self, tag):
        if tag == 'sup':
            self.in_verse_sup = False
        if tag in ['span', 'p']:
            self.in_text = False
            
    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
            
        # Check if this is a verse number
        if self.in_verse_sup:
            # Try to parse as verse number
            match = re.match(r'^(\d+)\s*$', text)
            if match:
                # Save previous verse if exists
                if self.current_verse is not None:
                    verse_text = ' '.join(self.current_text).strip()
                    if verse_text:
                        self.verses.append((self.current_verse, verse_text))
                
                # Start new verse
                self.current_verse = int(match.group(1))
                self.current_text = []
        elif self.current_verse is not None:
            # This is text content for current verse
            # Clean up text
            text = text.replace('\n', ' ').strip()
            if text:
                self.current_text.append(text)
                
    def get_verses(self) -> List[Tuple[int, str]]:
        """Return extracted verses"""
        # Don't forget the last verse
        if self.current_verse is not None and self.current_text:
            verse_text = ' '.join(self.current_text).strip()
            if verse_text:
                self.verses.append((self.current_verse, verse_text))
        return self.verses

def clean_verse_text(text: str) -> str:
    """Clean up verse text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    text = re.sub(r'"\s+', '"', text)
    text = re.sub(r'\s+"', '"', text)
    return text.strip()

def extract_chapter(file_path: Path) -> List[Tuple[int, str]]:
    """Extract verses from a chapter HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    # Find the chapter content - between <h2> and next <div> or </body>
    # The verses are in <p class="block_4">
    
    # Simple regex approach for now
    # Find all verse patterns: <sup class="calibre6">N </sup> followed by text
    verses = []
    
    # Find chapter content
    chapter_match = re.search(r'<h2[^>]*>CHAPTER\s+(\d+)</h2>', html, re.IGNORECASE)
    if not chapter_match:
        return []
    
    chapter_num = int(chapter_match.group(1))
    
    # Extract verse content
    # Look for pattern: <b class="calibre2"><sup class="calibre6">N </sup></b>text
    verse_pattern = r'<b class="calibre2"><sup class="calibre6">(\d+)\s*</sup></b>(.*?)(?=<b class="calibre2"><sup class="calibre6">|\s*</p>)'
    
    for match in re.finditer(verse_pattern, html, re.DOTALL):
        verse_num = int(match.group(1))
        verse_html = match.group(2)
        
        # Clean HTML tags from text
        # Remove span tags but keep content
        text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', verse_html)
        # Remove other tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up
        text = clean_verse_text(text)
        
        if text:
            verses.append((verse_num, text))
    
    return verses

def populate_bible_db(db_path: Path):
    """Populate database with LSV Bible"""
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing Bible data
    cursor.execute("DELETE FROM bible_verses")
    cursor.execute("DELETE FROM bible_books")
    
    # Insert books
    print("Inserting Bible books...")
    for book_name, testament, start_part, chapters in BOOK_MAP:
        cursor.execute(
            "INSERT INTO bible_books (name, testament, chapters) VALUES (?, ?, ?)",
            (book_name, testament, chapters)
        )
    
    # Get book ID mapping
    cursor.execute("SELECT id, name FROM bible_books")
    book_ids = {name: id for id, name in cursor.fetchall()}
    
    # Extract verses for each book
    total_verses = 0
    for book_name, testament, start_part, chapters in BOOK_MAP:
        book_id = book_ids[book_name]
        print(f"Processing {book_name} ({chapters} chapters)...")
        
        for chapter in range(1, chapters + 1):
            # Calculate part number
            # Each chapter is typically in its own file
            part_num = start_part + chapter
            file_path = BIBLE_DIR / f"part{part_num:04d}.html"
            
            if not file_path.exists():
                # Some chapters might be split
                # Try with _split suffix
                for suffix in ['', '_split_000', '_split_001', '_split_002']:
                    test_path = BIBLE_DIR / f"part{part_num:04d}{suffix}.html"
                    if test_path.exists():
                        file_path = test_path
                        break
            
            if file_path.exists():
                verses = extract_chapter(file_path)
                for verse_num, verse_text in verses:
                    cursor.execute(
                        "INSERT INTO bible_verses (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
                        (book_id, chapter, verse_num, verse_text)
                    )
                    total_verses += 1
            else:
                print(f"  Warning: Missing file for {book_name} {chapter}")
    
    conn.commit()
    conn.close()
    
    print(f"\nDone! Added {total_verses} verses.")
    print(f"Database: {db_path}")

if __name__ == '__main__':
    # Ensure database exists
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        print("Run extract_theology.py first to create the database structure.")
        exit(1)
    
    populate_bible_db(DB_PATH)
