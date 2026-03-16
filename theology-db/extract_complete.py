#!/usr/bin/env python3
"""
Extract ALL Bible verses from Biblia Sacra et Ultra
Each chapter = 1 HTML file with all verses in one <p> tag
"""

import sqlite3
import re
import os
import sys
from pathlib import Path
from html import unescape

# Colors
RED = '\033[38;5;88m'
GOLD = '\033[38;5;178m'
SILVER = '\033[38;5;250m'
GREEN = '\033[38;5;28m'
RESET = '\033[0m'

# Testament detection
OT_BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 
    'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles',
    '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
    'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations',
    'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah',
    'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi']

DEUTERO_BOOKS = ['Tobit', 'Judith', 'Wisdom', 'Sirach', 'Baruch', 
    '1 Maccabees', '2 Maccabees', 'Additions to Esther', 'Prayer of Azariah',
    'Susanna', 'Bel and the Dragon', 'Letter of Jeremiah', '1 Esdras',
    '2 Esdras', 'Prayer of Manasseh', '3 Maccabees', '4 Maccabees']

def get_testament(book):
    if book in OT_BOOKS:
        return 'OT'
    elif book in DEUTERO_BOOKS:
        return 'DEUTERO'
    else:
        return 'NT'

class BibleExtractor:
    def __init__(self, source_dir):
        self.source_dir = Path(source_dir)
        self.verses = []
        self.book_order = self._build_book_order()
        
    def _build_book_order(self):
        """Build mapping of book names to order"""
        all_books = OT_BOOKS + DEUTERO_BOOKS + [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', 
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
            'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
            'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
            'Jude', 'Revelation'
        ]
        return {book: idx for idx, book in enumerate(all_books)}
    
    def extract_chapter_verses(self, html_content):
        """Extract all verses from a chapter HTML file"""
        # Find the main content paragraph
        pattern = r'<p class="block_4">(.*?)</p>'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            return []
        
        content = match.group(1)
        verses = []
        
        # Pattern for verse markers: <b class="calibre2"><sup class="calibre6">N </sup></b>
        # Split content by verse markers and rebuild verses
        verse_pattern = r'<b class="calibre2"><sup class="calibre6">(\d+)\s*</sup></b>'
        
        # Find all verse positions
        parts = re.split(verse_pattern, content)
        
        # parts[0] is text before first verse number
        # parts[1] is first verse number, parts[2] is text after
        # parts[3] is second verse number, parts[4] is text after, etc.
        
        if len(parts) >= 3:
            for i in range(1, len(parts), 2):
                if i < len(parts) and i+1 < len(parts):
                    verse_num = parts[i]
                    verse_text = parts[i+1]
                    
                    # Clean up HTML
                    verse_text = re.sub(r'<[^>]+>', ' ', verse_text)
                    verse_text = unescape(verse_text)
                    verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                    
                    # Remove trailing partial verse markers
                    verse_text = re.sub(r'<b.*$', '', verse_text)
                    verse_text = verse_text.strip()
                    
                    if verse_text and len(verse_text) > 5:
                        try:
                            verses.append((int(verse_num), verse_text))
                        except ValueError:
                            pass
        
        return verses
    
    def detect_book_from_file(self, html_file, html_content):
        """Determine book from filename patterns and content"""
        filename = html_file.name
        
        # Known file ranges for major books (approximate)
        part_num = int(re.search(r'part(\d+)', filename).group(1)) if re.search(r'part(\d+)', filename) else 0
        
        # Rough mapping based on file numbering
        # part0010-0011 = Genesis (intro + ch 1)
        # part0011-0061 = Genesis ch 1-50
        # part0061-0101 = Exodus ch 1-40
        # etc.
        
        book_ranges = [
            (10, 61, 'Genesis'),  # parts 10-60 = Genesis
            (61, 101, 'Exodus'),  # parts 61-100 = Exodus
            (101, 128, 'Leviticus'),  # parts 101-127 = Leviticus
            (128, 164, 'Numbers'),  # parts 128-163 = Numbers
            (164, 198, 'Deuteronomy'),  # parts 164-197 = Deuteronomy
            (198, 222, 'Joshua'),  # parts 198-221 = Joshua
            (222, 243, 'Judges'),  # parts 222-242 = Judges
            (243, 247, 'Ruth'),  # parts 243-246 = Ruth
            (247, 278, '1 Samuel'),  # parts 247-277 = 1 Samuel
            (278, 302, '2 Samuel'),  # parts 278-301 = 2 Samuel
            (302, 324, '1 Kings'),  # parts 302-323 = 1 Kings
            (324, 349, '2 Kings'),  # parts 324-348 = 2 Kings
            (349, 378, '1 Chronicles'),  # parts 349-377 = 1 Chronicles
            (378, 414, '2 Chronicles'),  # parts 378-413 = 2 Chronicles
            (414, 424, 'Ezra'),  # parts 414-423 = Ezra
            (424, 437, 'Nehemiah'),  # parts 424-436 = Nehemiah
            (437, 447, 'Esther'),  # parts 437-446 = Esther
            (447, 489, 'Job'),  # parts 447-488 = Job
            (489, 639, 'Psalms'),  # parts 489-638 = Psalms
            (639, 670, 'Proverbs'),  # parts 639-669 = Proverbs
            (670, 682, 'Ecclesiastes'),  # parts 670-681 = Ecclesiastes
            (670, 682, 'Ecclesiastes'),  # parts 670-681 = Ecclesiastes
            (682, 690, 'Song of Solomon'),  # parts 682-689 = Song of Solomon
            (690, 756, 'Isaiah'),  # parts 690-755 = Isaiah
            (756, 808, 'Jeremiah'),  # parts 756-807 = Jeremiah
            (808, 813, 'Lamentations'),  # parts 808-812 = Lamentations
            (813, 861, 'Ezekiel'),  # parts 813-860 = Ezekiel
            (861, 873, 'Daniel'),  # parts 861-872 = Daniel
            # Minor prophets combined
            (873, 887, 'Hosea'),  # parts 873-886 = Hosea
            (887, 890, 'Joel'),  # parts 887-889 = Joel
            (890, 899, 'Amos'),  # parts 890-898 = Amos
            (899, 900, 'Obadiah'),  # part 899 = Obadiah
            (900, 904, 'Jonah'),  # parts 900-903 = Jonah
            (904, 911, 'Micah'),  # parts 904-910 = Micah
            (911, 914, 'Nahum'),  # parts 911-913 = Nahum
            (914, 917, 'Habakkuk'),  # parts 914-916 = Habakkuk
            (917, 920, 'Zephaniah'),  # parts 917-919 = Zephaniah
            (920, 922, 'Haggai'),  # parts 920-921 = Haggai
            (922, 936, 'Zechariah'),  # parts 922-935 = Zechariah
            (936, 940, 'Malachi'),  # parts 936-939 = Malachi
            # New Testament
            (2000, 2028, 'Matthew'),  # parts 2000-2027 = Matthew
            (2028, 2044, 'Mark'),  # parts 2028-2043 = Mark
            (2044, 2068, 'Luke'),  # parts 2044-2067 = Luke
            (2068, 2089, 'John'),  # parts 2068-2088 = John
            (2089, 2117, 'Acts'),  # parts 2089-2116 = Acts
            (2117, 2133, 'Romans'),  # parts 2117-2132 = Romans
            (2133, 2149, '1 Corinthians'),  # parts 2133-2148 = 1 Corinthians
            (2149, 2162, '2 Corinthians'),  # parts 2149-2161 = 2 Corinthians
            (2162, 2168, 'Galatians'),  # parts 2162-2167 = Galatians
            (2168, 2174, 'Ephesians'),  # parts 2168-2173 = Ephesians
            (2174, 2178, 'Philippians'),  # parts 2174-2177 = Philippians
            (2178, 2182, 'Colossians'),  # parts 2178-2181 = Colossians
            (2182, 2187, '1 Thessalonians'),  # parts 2182-2186 = 1 Thessalonians
            (2187, 2190, '2 Thessalonians'),  # parts 2187-2189 = 2 Thessalonians
            (2190, 2196, '1 Timothy'),  # parts 2190-2195 = 1 Timothy
            (2196, 2200, '2 Timothy'),  # parts 2196-2199 = 2 Timothy
            (2200, 2203, 'Titus'),  # parts 2200-2202 = Titus
            (2203, 2204, 'Philemon'),  # part 2203 = Philemon
            (2204, 2217, 'Hebrews'),  # parts 2204-2216 = Hebrews
            (2217, 2222, 'James'),  # parts 2217-2221 = James
            (2222, 2227, '1 Peter'),  # parts 2222-2226 = 1 Peter
            (2227, 2230, '2 Peter'),  # parts 2227-2229 = 2 Peter
            (2230, 2235, '1 John'),  # parts 2230-2234 = 1 John
            (2235, 2236, '2 John'),  # part 2235 = 2 John
            (2236, 2237, '3 John'),  # part 2236 = 3 John
            (2237, 2238, 'Jude'),  # part 2237 = Jude
            (2238, 2260, 'Revelation'),  # parts 2238-2259 = Revelation
        ]
        
        for start, end, book in book_ranges:
            if start <= part_num < end:
                return book
        
        # Check for deuterocanonical books (usually numbered differently)
        # These are scattered through the files
        
        return None
    
    def parse_all(self):
        """Parse all Bible HTML files"""
        print(f"{GOLD}Scanning for Bible files...{RESET}")
        html_files = sorted(self.source_dir.glob('part*.html'))
        print(f"  Found {len(html_files)} HTML files\n")
        
        total_verses = 0
        current_book = None
        current_chapter = 1
        
        for idx, html_file in enumerate(html_files):
            if idx % 500 == 0:
                print(f"{SILVER}  Processing {idx}/{len(html_files)} ({total_verses} verses){RESET}", end='\r')
            
            try:
                content = html_file.read_text(encoding='utf-8', errors='ignore')
            except:
                continue
            
            # Detect book
            book = self.detect_book_from_file(html_file, content)
            if book:
                current_book = book
            
            if not current_book:
                continue
            
            # Extract verses from this chapter
            verses = self.extract_chapter_verses(content)
            
            if verses:
                # Estimate chapter number based on file position within book
                testament = get_testament(current_book)
                
                for verse_num, verse_text in verses:
                    self.verses.append((
                        current_book,
                        testament,
                        current_chapter,
                        verse_num,
                        verse_text
                    ))
                    total_verses += 1
                
                # Increment chapter for next file
                current_chapter += 1
        
        print(f"\n{GREEN}✓ Extracted {total_verses} Bible verses from {len(self.verses)} entries{RESET}\n")
        return total_verses


def create_database(db_path, verses):
    """Create SQLite database"""
    print(f"{GOLD}Creating database...{RESET}")
    
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    print(f"{SILVER}  Inserting {len(verses)} verses...{RESET}")
    cursor.executemany('''
        INSERT INTO bible_verses (book, testament, chapter, verse, text)
        VALUES (?, ?, ?, ?, ?)
    ''', verses)
    
    cursor.execute('CREATE INDEX idx_bible_reference ON bible_verses(book, chapter, verse)')
    cursor.execute('CREATE INDEX idx_bible_testament ON bible_verses(testament)')
    
    cursor.execute('''
        CREATE TABLE library_stats (key TEXT PRIMARY KEY, value INTEGER)
    ''')
    cursor.execute('INSERT INTO library_stats VALUES (?, ?)', ('bible_verses', len(verses)))
    
    conn.commit()
    conn.close()
    
    print(f"{GREEN}✓ Database created{RESET}\n")


def main():
    print(f"\n{RED}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}║{RESET}       {GOLD}EXTRACTING COMPLETE BIBLICAL LIBRARY v2{RESET}                 {RED}║{RESET}")
    print(f"{RED}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    bible_source = '/home/workspace/Christianity_Compilation/EXTRACTED/Biblia_Sacra/text'
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    if not os.path.exists(bible_source):
        print(f"{RED}✗ Bible source not found{RESET}")
        return 1
    
    extractor = BibleExtractor(bible_source)
    count = extractor.parse_all()
    
    if count == 0:
        print(f"{RED}✗ No verses extracted{RESET}")
        return 1
    
    create_database(db_path, extractor.verses)
    
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"{GOLD}╔═══════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{GOLD}║{RESET}                 {GREEN}✓ COMPLETE EXTRACTION DONE{RESET}                      {GOLD}║{RESET}")
    print(f"{GOLD}╠═══════════════════════════════════════════════════════════════════╣{RESET}")
    print(f"{GOLD}║{RESET}  Total Verses:   {SILVER}{count:,}{RESET}                                  {GOLD}║{RESET}")
    print(f"{GOLD}║{RESET}  Database Size:   {SILVER}{db_size:.2f} MB{RESET}                               {GOLD}║{RESET}")
    print(f"{GOLD}╚═══════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
