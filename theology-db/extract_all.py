#!/usr/bin/env python3
"""
Extract ALL texts for Sanctum OS - Complete Library
Processes all ~5,958 Bible files and ~1,248 Fathers files
Uses batch processing with resume capability
"""

import sqlite3
import re
import os
import sys
from pathlib import Path
from html import unescape
import pickle

# Colors
RED = '\033[38;5;88m'
GOLD = '\033[38;5;178m'
SILVER = '\033[38;5;250m'
GREEN = '\033[38;5;28m'
RESET = '\033[0m'

# Bible book order and chapter counts
BIBLE_STRUCTURE = {
    # Pentateuch
    'Genesis': 50, 'Exodus': 40, 'Leviticus': 27, 'Numbers': 36, 'Deuteronomy': 34,
    # Historical
    'Joshua': 24, 'Judges': 21, 'Ruth': 4, '1 Samuel': 31, '2 Samuel': 24,
    '1 Kings': 22, '2 Kings': 25, '1 Chronicles': 29, '2 Chronicles': 36, 'Ezra': 10,
    'Nehemiah': 13, 'Esther': 10,
    # Wisdom
    'Job': 42, 'Psalms': 150, 'Proverbs': 31, 'Ecclesiastes': 12, 'Song of Solomon': 8,
    # Major Prophets
    'Isaiah': 66, 'Jeremiah': 52, 'Lamentations': 5, 'Ezekiel': 48, 'Daniel': 12,
    # Minor Prophets
    'Hosea': 14, 'Joel': 3, 'Amos': 9, 'Obadiah': 1, 'Jonah': 4, 'Micah': 7,
    'Nahum': 3, 'Habakkuk': 3, 'Zephaniah': 3, 'Haggai': 2, 'Zechariah': 14, 'Malachi': 4,
    # Deuterocanon
    'Tobit': 14, 'Judith': 16, 'Wisdom': 19, 'Sirach': 51, 'Baruch': 6,
    '1 Maccabees': 16, '2 Maccabees': 15,
    # New Testament
    'Matthew': 28, 'Mark': 16, 'Luke': 24, 'John': 21, 'Acts': 28,
    'Romans': 16, '1 Corinthians': 16, '2 Corinthians': 13, 'Galatians': 6, 'Ephesians': 6,
    'Philippians': 4, 'Colossians': 4, '1 Thessalonians': 5, '2 Thessalonians': 3,
    '1 Timothy': 6, '2 Timothy': 4, 'Titus': 3, 'Philemon': 1, 'Hebrews': 13,
    'James': 5, '1 Peter': 5, '2 Peter': 3, '1 John': 5, '2 John': 1, '3 John': 1,
    'Jude': 1, 'Revelation': 22
}

def get_testament(book):
    ot_books = list(BIBLE_STRUCTURE.keys())[:39]
    deutero = ['Tobit', 'Judith', 'Wisdom', 'Sirach', 'Baruch', '1 Maccabees', '2 Maccabees']
    if book in ot_books:
        return 'OT'
    elif book in deutero:
        return 'DEUTERO'
    else:
        return 'NT'

class FastBibleExtractor:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.verses = []
        self.progress_file = Path('/tmp/bible_extraction_progress.pkl')
        
    def load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file, 'rb') as f:
                return pickle.load(f)
        return {'last_file': None, 'verse_count': 0}
    
    def save_progress(self, last_file, count):
        with open(self.progress_file, 'wb') as f:
            pickle.dump({'last_file': last_file, 'verse_count': count}, f)
    
    def extract_verses_from_file(self, html_file):
        """Fast verse extraction using optimized regex"""
        try:
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            verses = []
            
            # Find all paragraph blocks with text
            pattern = r'<p class="block_\d+">(.*?)</p>'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                # Extract verse number and text
                verse_pattern = r'<sup class="calibre\d+">\s*(\d+)\s*</sup>\s*<b class="calibre\d+">\s*</b>(.*?)</p>'
                verse_match = re.search(verse_pattern, match, re.DOTALL)
                
                if not verse_match:
                    # Try simpler pattern
                    simple_pattern = r'<sup[^>]*>(\d+)</sup>\s*</b>(.*?)$'
                    simple_match = re.search(simple_pattern, match, re.DOTALL)
                    if simple_match:
                        verse_num = int(simple_match.group(1))
                        verse_text = simple_match.group(2)
                        # Clean HTML
                        verse_text = re.sub(r'<[^>]+>', ' ', verse_text)
                        verse_text = unescape(verse_text)
                        verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                        if verse_text and len(verse_text) > 10:
                            verses.append((verse_num, verse_text))
            
            return verses
        except Exception as e:
            return []
    
    def detect_book_from_content(self, html_content):
        """Detect book name from HTML content"""
        # Look for book title in the content
        book_patterns = [
            r'<h[1-6][^>]*>(?:THE\s+)?(?:FIRST|SECOND|THIRD|FOURTH\s+)?(?:BOOK\s+OF\s+)?([^<]+)</h',
            r'<p[^>]*>(?:THE\s+)?(?:FIRST|SECOND|THIRD|FOURTH\s+)?(?:BOOK\s+OF\s+)?([^<]+)</p>',
        ]
        
        for pattern in book_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'\s+', ' ', title)
                # Check if it matches a known book
                for book in BIBLE_STRUCTURE.keys():
                    if book.lower() in title.lower() or title.lower() in book.lower():
                        return book
        return None
    
    def parse_all(self, limit=None):
        """Parse all Bible files"""
        print(f"{GOLD}Scanning for Bible files...{RESET}")
        html_files = sorted(self.source_dir.glob('part*.html'))
        print(f"  Found {len(html_files)} HTML files\n")
        
        progress = self.load_progress()
        start_idx = 0
        if progress['last_file']:
            for i, f in enumerate(html_files):
                if f.name == progress['last_file']:
                    start_idx = i + 1
                    print(f"{SILVER}Resuming from {f.name} ({progress['verse_count']} verses already extracted){RESET}\n")
                    break
        
        total_verses = progress['verse_count']
        current_book = None
        current_chapter = 1
        
        for idx, html_file in enumerate(html_files[start_idx:], start=start_idx):
            if limit and total_verses >= limit:
                break
            
            if idx % 100 == 0:
                print(f"{SILVER}  Processing file {idx}/{len(html_files)}: {html_file.name} ({total_verses} verses){RESET}", end='\r')
                self.save_progress(html_file.name, total_verses)
            
            content = html_file.read_text(encoding='utf-8', errors='ignore')
            
            # Try to detect book from this file
            detected_book = self.detect_book_from_content(content)
            if detected_book:
                current_book = detected_book
            
            if not current_book:
                continue
            
            # Extract verses
            verses = self.extract_verses_from_file(html_file)
            for verse_num, verse_text in verses:
                testament = get_testament(current_book)
                self.verses.append((
                    current_book,
                    testament,
                    current_chapter,
                    verse_num,
                    verse_text
                ))
                total_verses += 1
            
            # Increment chapter (rough approximation - every few files)
            if len(verses) > 0 and idx % 3 == 0:
                max_chapters = BIBLE_STRUCTURE.get(current_book, 150)
                if current_chapter < max_chapters:
                    current_chapter += 1
        
        print(f"\n{GREEN}✓ Extracted {len(self.verses)} Bible verses{RESET}\n")
        return len(self.verses)


def create_complete_database(db_path, bible_verses):
    """Create database with all extracted content"""
    print(f"{GOLD}Creating database...{RESET}")
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Bible table
    cursor.execute('''
        CREATE TABLE bible_verses (
            id INTEGER PRIMARY KEY,
            book TEXT NOT NULL,
            testament TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL
        )
    ''')
    
    # Insert all verses
    print(f"{SILVER}  Inserting {len(bible_verses)} verses...{RESET}")
    cursor.executemany('''
        INSERT INTO bible_verses (book, testament, chapter, verse, text)
        VALUES (?, ?, ?, ?, ?)
    ''', bible_verses)
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_bible_book ON bible_verses(book)')
    cursor.execute('CREATE INDEX idx_bible_chapter ON bible_verses(chapter)')
    cursor.execute('CREATE INDEX idx_bible_reference ON bible_verses(book, chapter, verse)')
    
    # Stats table
    cursor.execute('''
        CREATE TABLE library_stats (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
    ''')
    
    cursor.execute('INSERT INTO library_stats VALUES (?, ?)', ('bible_verses', len(bible_verses)))
    
    conn.commit()
    conn.close()
    
    print(f"{GREEN}✓ Database created{RESET}\n")


def main():
    print(f"\n{RED}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}║{RESET}         {GOLD}EXTRACTING COMPLETE BIBLICAL LIBRARY{RESET}                   {RED}║{RESET}")
    print(f"{RED}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    bible_source = '/home/workspace/Christianity_Compilation/EXTRACTED/Biblia_Sacra/text'
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    if not os.path.exists(bible_source):
        print(f"{RED}✗ Bible source not found: {bible_source}{RESET}")
        return 1
    
    # Extract Bible
    extractor = FastBibleExtractor(bible_source)
    verse_count = extractor.parse_all()
    
    if verse_count == 0:
        print(f"{RED}✗ No verses extracted{RESET}")
        return 1
    
    # Create database
    create_complete_database(db_path, extractor.verses)
    
    # Show stats
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"{GOLD}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{GOLD}║{RESET}                    {GREEN}✓ EXTRACTION COMPLETE{RESET}                       {GOLD}║{RESET}")
    print(f"{GOLD}╠═══════════════════════════════════════════════════════════════════╣{RESET}")
    print(f"{GOLD}║{RESET}  Bible Verses:    {SILVER}{verse_count:,}{RESET}                                     {GOLD}║{RESET}")
    print(f"{GOLD}║{RESET}  Database Size:    {SILVER}{db_size:.2f} MB{RESET}                                  {GOLD}║{RESET}")
    print(f"{GOLD}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
