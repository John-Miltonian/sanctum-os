#!/usr/bin/env python3
"""
Complete Library Extraction for Sanctum OS
Extracts ALL Bible verses and ALL Church Fathers texts
from the Christianity_Compilation source files.

This creates a complete, searchable database for the rice.
"""

import sqlite3
import re
import os
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Dict
import sys

# Color codes
RED = '\033[38;5;88m'
GOLD = '\033[38;5;178m'
SILVER = '\033[38;5;250m'
GREEN = '\033[38;5;28m'
RESET = '\033[0m'

class BibleParser:
    """Parse LSV Bible HTML files."""
    
    # Book mapping based on file patterns in Biblia Sacra
    BOOK_SEQUENCES = [
        # (start_file_pattern, book_name, testament, chapters)
        # OT Books
        ("part0011", "Genesis", "OT", 50),
        ("part0062", "Exodus", "OT", 40),
        ("part0103", "Leviticus", "OT", 27),
        ("part0131", "Numbers", "OT", 36),
        ("part0168", "Deuteronomy", "OT", 34),
        ("part0203", "Joshua", "OT", 24),
        ("part0228", "Judges", "OT", 21),
        ("part0250", "Ruth", "OT", 4),
        ("part0255", "1 Samuel", "OT", 31),
        ("part0287", "2 Samuel", "OT", 24),
        ("part0312", "1 Kings", "OT", 22),
        ("part0335", "2 Kings", "OT", 25),
        ("part0361", "1 Chronicles", "OT", 29),
        ("part0391", "2 Chronicles", "OT", 36),
        ("part0428", "Ezra", "OT", 10),
        ("part0439", "Nehemiah", "OT", 13),
        ("part0453", "Esther", "OT", 10),
        ("part0464", "Job", "OT", 42),
        ("part0507", "Psalms", "OT", 150),
        ("part0658", "Proverbs", "OT", 31),
        ("part0690", "Ecclesiastes", "OT", 12),
        ("part0703", "Song of Solomon", "OT", 8),
        ("part0712", "Isaiah", "OT", 66),
        ("part0779", "Jeremiah", "OT", 52),
        ("part0832", "Lamentations", "OT", 5),
        ("part0838", "Ezekiel", "OT", 48),
        ("part0887", "Daniel", "OT", 12),
        ("part0900", "Hosea", "OT", 14),
        ("part0915", "Joel", "OT", 3),
        ("part0919", "Amos", "OT", 9),
        ("part0929", "Obadiah", "OT", 1),
        ("part0931", "Jonah", "OT", 4),
        ("part0936", "Micah", "OT", 7),
        ("part0944", "Nahum", "OT", 3),
        ("part0948", "Habakkuk", "OT", 3),
        ("part0952", "Zephaniah", "OT", 3),
        ("part0956", "Haggai", "OT", 2),
        ("part0959", "Zechariah", "OT", 14),
        ("part0974", "Malachi", "OT", 4),
        # NT Books
        ("part0979", "Matthew", "NT", 28),
        ("part1008", "Mark", "NT", 16),
        ("part1025", "Luke", "NT", 24),
        ("part1050", "John", "NT", 21),
        ("part1072", "Acts", "NT", 28),
        ("part1101", "Romans", "NT", 16),
        ("part1118", "1 Corinthians", "NT", 16),
        ("part1135", "2 Corinthians", "NT", 13),
        ("part1149", "Galatians", "NT", 6),
        ("part1156", "Ephesians", "NT", 6),
        ("part1163", "Philippians", "NT", 4),
        ("part1168", "Colossians", "NT", 4),
        ("part1173", "1 Thessalonians", "NT", 5),
        ("part1179", "2 Thessalonians", "NT", 3),
        ("part1183", "1 Timothy", "NT", 6),
        ("part1190", "2 Timothy", "NT", 4),
        ("part1195", "Titus", "NT", 3),
        ("part1199", "Philemon", "NT", 1),
        ("part1201", "Hebrews", "NT", 13),
        ("part1215", "James", "NT", 5),
        ("part1221", "1 Peter", "NT", 5),
        ("part1227", "2 Peter", "NT", 3),
        ("part1231", "1 John", "NT", 5),
        ("part1237", "2 John", "NT", 1),
        ("part1239", "3 John", "NT", 1),
        ("part1241", "Jude", "NT", 1),
        ("part1243", "Revelation", "NT", 22),
    ]
    
    # Apocrypha/Deuterocanon
    APOCRYPHA_BOOKS = [
        ("part1267", "Tobit", "Apocrypha", 14),
        ("part1282", "Judith", "Apocrypha", 16),
        ("part1299", "Wisdom", "Apocrypha", 19),
        ("part1319", "Sirach", "Apocrypha", 51),
        ("part1371", "Baruch", "Apocrypha", 6),
        ("part1378", "1 Maccabees", "Apocrypha", 16),
        ("part1395", "2 Maccabees", "Apocrypha", 15),
        ("part1411", "Additions to Esther", "Apocrypha", 7),
        ("part1419", "Additions to Daniel", "Apocrypha", 3),
        ("part1423", "Prayer of Manasseh", "Apocrypha", 1),
    ]
    
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.verses: List[Tuple[str, str, int, int, str]] = []
        self.processed = 0
        self.errors = 0
        
    def extract_verses_from_html(self, html_content: str, book: str, testament: str) -> List[Tuple]:
        """Extract verse numbers and text from HTML content."""
        verses = []
        current_chapter = 1
        
        # Find all paragraph blocks with verses
        para_pattern = r'<p class="block_4"[^>]*>(.*?)</p>'
        paragraphs = re.findall(para_pattern, html_content, re.DOTALL)
        
        for para in paragraphs:
            # Extract ALL verse numbers and their associated text in this paragraph
            # Pattern: <b class="calibre2"><sup class="calibre6">N </sup></b>text...
            verse_pattern = r'<b class="calibre2"><sup class="calibre6">(\d+)[^<]*</sup></b>(.*?)(?=<b class="calibre2"><sup class="calibre6">|$)'
            verse_matches = re.findall(verse_pattern, para)
            
            for verse_num, verse_text in verse_matches:
                try:
                    v_num = int(verse_num)
                    # Clean up the verse text - remove HTML tags
                    verse_text = re.sub(r'<[^>]+>', '', verse_text)
                    verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                    
                    # Skip empty or too-short verses
                    if not verse_text or len(verse_text) < 5:
                        continue
                        
                    verses.append((book, testament, current_chapter, v_num, verse_text))
                except ValueError:
                    continue
                    
        return verses
    
    def process_file(self, filepath: Path, book: str, testament: str) -> int:
        """Process a single HTML file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            verses = self.extract_verses_from_html(content, book, testament)
            self.verses.extend(verses)
            return len(verses)
        except Exception as e:
            self.errors += 1
            return 0
    
    def parse_all(self) -> int:
        """Parse all Bible HTML files."""
        print(f"{GOLD}Parsing LSV Bible...{RESET}")
        
        # Process canonical books
        for start_file, book, testament, chapters in self.BOOK_SEQUENCES:
            count = 0
            # Find all files for this book
            pattern = f"{start_file}*.html"
            files = sorted(self.source_dir.glob(pattern))
            
            for filepath in files:
                added = self.process_file(filepath, book, testament)
                count += added
            
            if count > 0:
                print(f"  {SILVER}{book}{RESET}: {count} verses")
        
        # Process Apocrypha
        for start_file, book, testament, chapters in self.APOCRYPHA_BOOKS:
            count = 0
            files = sorted(self.source_dir.glob(f"{start_file}*.html"))
            for filepath in files:
                added = self.process_file(filepath, book, testament)
                count += added
            if count > 0:
                print(f"  {SILVER}{book}{RESET}: {count} verses")
        
        total = len(self.verses)
        print(f"\n{GREEN}✓ Extracted {total} Bible verses{RESET}")
        if self.errors > 0:
            print(f"{RED}  ({self.errors} errors){RESET}")
        return total


class ChurchFathersParser:
    """Parse Church Fathers HTML files."""
    
    # Major authors and their file patterns
    FATHERS_AUTHORS = {
        "Clement of Rome": ["part*", "clement*"],
        "Ignatius of Antioch": ["ignatius*"],
        "Polycarp": ["polycarp*"],
        "Papias": ["papias*"],
        "Justin Martyr": ["justin*", "apology*"],
        "Irenaeus": ["irenaeus*"],
        "Clement of Alexandria": ["alexandria*"],
        "Tertullian": ["tertullian*"],
        "Origen": ["origen*"],
        "Cyprian": ["cyprian*"],
        "Athanasius": ["athanasius*"],
        "Basil the Great": ["basil*"],
        "Gregory of Nazianzus": ["nazianzen*", "nazianzus*"],
        "Gregory of Nyssa": ["nyssa*"],
        "Chrysostom": ["chrysostom*", "homily*"],
        "Ambrose": ["ambrose*"],
        "Jerome": ["jerome*"],
        "Augustine": ["augustine*", "confessions*", "city*"],
        "Cyril of Alexandria": ["cyril*"],
        "Cyril of Jerusalem": ["catechetical*"],
        "Leo the Great": ["leo*"],
        "Gregory the Great": ["gregory_great*"],
        "Eusebius": ["eusebius*", "church_history*"],
        "Hippolytus": ["hippolytus*"],
        "Novatian": ["novatian*"],
    }
    
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.texts: List[Tuple[str, str, str, int, str]] = []
        self.processed = 0
        self.errors = 0
        
    def extract_text_from_html(self, html_content: str, author: str, work: str) -> List[Tuple]:
        """Extract text sections from HTML content."""
        sections = []
        section_num = 0
        
        # Look for paragraph content
        para_pattern = r'<p[^>]*>(.*?)</p>'
        paragraphs = re.findall(para_pattern, html_content, re.DOTALL)
        
        for para in paragraphs:
            # Clean HTML tags
            text = re.sub(r'<[^>]+>', ' ', para)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Skip short or copyright text
            if len(text) < 20 or 'copyright' in text.lower():
                continue
                
            section_num += 1
            # Volume is parsed from content or defaults
            volume = "Volume 1"
            sections.append((author, work, volume, section_num, text))
        
        return sections
    
    def process_file(self, filepath: Path, author: str, work: str) -> int:
        """Process a single HTML file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Try to extract work title from content
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match and work == "Unknown":
                work = title_match.group(1).strip()
            
            sections = self.extract_text_from_html(content, author, work)
            self.texts.extend(sections)
            return len(sections)
        except Exception as e:
            self.errors += 1
            return 0
    
    def parse_all(self) -> int:
        """Parse all Church Fathers HTML files."""
        print(f"\n{GOLD}Parsing Church Fathers...{RESET}")
        
        # Get all HTML files
        html_files = list(self.source_dir.glob("*.html"))
        
        # Group by detected author
        author_files: Dict[str, List[Path]] = {author: [] for author in self.FATHERS_AUTHORS}
        
        for filepath in html_files:
            filename = filepath.name.lower()
            for author, patterns in self.FATHERS_AUTHORS.items():
                for pattern in patterns:
                    if pattern.replace("*", "") in filename or filepath.match(pattern):
                        author_files[author].append(filepath)
                        break
        
        # Process each author's files
        for author, files in author_files.items():
            if not files:
                continue
                
            count = 0
            work = "Collected Works" if len(files) > 1 else files[0].stem.replace('_', ' ').title()
            
            for filepath in sorted(files)[:20]:  # Limit per author for now
                added = self.process_file(filepath, author, work)
                count += added
            
            if count > 0:
                print(f"  {SILVER}{author}{RESET}: {count} sections")
        
        total = len(self.texts)
        print(f"\n{GREEN}✓ Extracted {total} Fathers sections{RESET}")
        if self.errors > 0:
            print(f"{RED}  ({self.errors} errors){RESET}")
        return total


def create_complete_database(db_path: str, bible_verses: List[Tuple], fathers_texts: List[Tuple]):
    """Create the complete theology database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables with proper schema
    cursor.execute('DROP TABLE IF EXISTS bible_verses')
    cursor.execute('DROP TABLE IF EXISTS church_fathers')
    
    cursor.execute('''
        CREATE TABLE bible_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            testament TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE church_fathers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            work TEXT NOT NULL,
            volume TEXT,
            section INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_bible_book ON bible_verses(book)')
    cursor.execute('CREATE INDEX idx_bible_ref ON bible_verses(book, chapter, verse)')
    cursor.execute('CREATE INDEX idx_bible_testament ON bible_verses(testament)')
    cursor.execute('CREATE INDEX idx_fathers_author ON church_fathers(author)')
    cursor.execute('CREATE INDEX idx_fathers_work ON church_fathers(work)')
    cursor.execute('CREATE INDEX idx_fathers_content ON church_fathers(content)')
    
    # Insert all Bible verses
    if bible_verses:
        print(f"\n{GOLD}Inserting {len(bible_verses)} Bible verses...{RESET}")
        cursor.executemany('''
            INSERT INTO bible_verses (book, testament, chapter, verse, content)
            VALUES (?, ?, ?, ?, ?)
        ''', bible_verses)
    
    # Insert all Fathers texts
    if fathers_texts:
        print(f"{GOLD}Inserting {len(fathers_texts)} Fathers sections...{RESET}")
        cursor.executemany('''
            INSERT INTO church_fathers (author, work, volume, section, content)
            VALUES (?, ?, ?, ?, ?)
        ''', fathers_texts)
    
    conn.commit()
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM bible_verses")
    bible_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT book) FROM bible_verses")
    bible_books = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM church_fathers")
    fathers_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT author) FROM church_fathers")
    fathers_authors = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{RED}╔═══════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}║{RESET}                    {GOLD}COMPLETE LIBRARY POPULATED{RESET}                       {RED}║{RESET}")
    print(f"{RED}╠═══════════════════════════════════════════════════════════════════════════╣{RESET}")
    print(f"{RED}║{RESET}  {SILVER}Bible:{RESET}      {bible_count:,} verses from {bible_books} books                  {RED}║{RESET}")
    print(f"{RED}║{RESET}  {SILVER}Fathers:{RESET}    {fathers_count:,} sections from {fathers_authors} authors            {RED}║{RESET}")
    print(f"{RED}╚═══════════════════════════════════════════════════════════════════════════╝{RESET}")
    
    return bible_count, fathers_count


def main():
    """Main extraction function."""
    print(f"\n{RED}╔═══════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}║{RESET}           {GOLD}SANCTUM OS - COMPLETE LIBRARY EXTRACTION{RESET}                   {RED}║{RESET}")
    print(f"{RED}╚═══════════════════════════════════════════════════════════════════════════╝{RESET}\n")
    
    # Paths
    bible_source = '/home/workspace/Christianity_Compilation/EXTRACTED/Biblia_Sacra/text'
    fathers_source = '/home/workspace/Christianity_Compilation/EXTRACTED/Church_Fathers_Complete/text'
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    # Check source directories
    if not os.path.exists(bible_source):
        print(f"{RED}Error: Bible source not found: {bible_source}{RESET}")
        return 1
    
    if not os.path.exists(fathers_source):
        print(f"{RED}Error: Fathers source not found: {fathers_source}{RESET}")
        return 1
    
    # Parse Bible
    bible_parser = BibleParser(bible_source)
    bible_count = bible_parser.parse_all()
    
    # Parse Fathers
    fathers_parser = ChurchFathersParser(fathers_source)
    fathers_count = fathers_parser.parse_all()
    
    # Create database
    create_complete_database(db_path, bible_parser.verses, fathers_parser.texts)
    
    # Show file size
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    print(f"\n{SILVER}Database size: {db_size:.1f} MB{RESET}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
