#!/usr/bin/env python3
"""
Sanctum OS Theology Database Packager
Packages the Bible and Church Fathers' texts into an embeddable format
"""

import os
import json
import gzip
import base64
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
import re

# Source directories
SOURCE_DIR = Path("/home/workspace/Christianity_Compilation")
OUTPUT_DIR = Path(__file__).parent

class TheologyPackager:
    def __init__(self):
        self.books: Dict[str, Dict] = {}
        self.fathers: Dict[str, Dict] = {}
        self.verses_index: List[Tuple[str, int, str, str]] = []  # (book, chapter, verse, text)
        self.fathers_index: List[Tuple[str, str, str]] = []  # (author, work, text)
        
    def find_bible_texts(self) -> List[Path]:
        """Find all Bible text files in the compilation"""
        bible_dirs = [
            SOURCE_DIR / "EXTRACTED_CONTENT" / "Biblia_Sacra",
            SOURCE_DIR / "PART_02_Old_Testament",
            SOURCE_DIR / "PART_06_New_Testament",
            SOURCE_DIR / "PART_03_Apocrypha_Deuterocanon",
            SOURCE_DIR / "EXTRACTED" / "Biblia_Sacra",
        ]
        
        bible_files = []
        for bible_dir in bible_dirs:
            if bible_dir.exists():
                # Look for text, html, and pdf files
                for ext in ['*.txt', '*.html', '*.md', '*.json']:
                    bible_files.extend(bible_dir.rglob(ext))
        
        return bible_files
    
    def find_fathers_texts(self) -> List[Path]:
        """Find all Church Fathers texts"""
        fathers_dirs = [
            SOURCE_DIR / "EXTRACTED_CONTENT" / "Church_Fathers_Complete",
            SOURCE_DIR / "EXTRACTED" / "Church_Fathers_Complete",
        ]
        
        fathers_files = []
        for fathers_dir in fathers_dirs:
            if fathers_dir.exists():
                for ext in ['*.txt', '*.html', '*.md', '*.pdf']:
                    fathers_files.extend(fathers_dir.rglob(ext))
        
        return fathers_files
    
    def create_compressed_archive(self):
        """Create a compressed base64-encoded archive of all texts"""
        print("Scanning for theological texts...")
        
        bible_files = self.find_bible_texts()
        fathers_files = self.find_fathers_texts()
        
        print(f"Found {len(bible_files)} Bible files")
        print(f"Found {len(fathers_files)} Church Fathers files")
        
        # Create SQLite database for structured search
        db_path = OUTPUT_DIR / "theology.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bible_books (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                testament TEXT,
                chapters INTEGER,
                verses INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bible_verses (
                id INTEGER PRIMARY KEY,
                book_id INTEGER,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                FOREIGN KEY (book_id) REFERENCES bible_books(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS church_fathers (
                id INTEGER PRIMARY KEY,
                author TEXT,
                work TEXT,
                section TEXT,
                text TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS bible_verses_fts USING fts5(
                text, 
                content='bible_verses',
                content_rowid='id'
            )
        ''')
        
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS church_fathers_fts USING fts5(
                text,
                content='church_fathers',
                content_rowid='id'
            )
        ''')
        
        # Process Bible texts
        print("Processing Biblical texts...")
        self._process_bible_files(cursor, bible_files)
        
        # Process Church Fathers texts
        print("Processing Patristic texts...")
        self._process_fathers_files(cursor, fathers_files)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON bible_verses(book_id, chapter)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fathers_author ON church_fathers(author)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fathers_work ON church_fathers(work)")
        
        conn.commit()
        conn.close()
        
        print(f"Database created: {db_path}")
        
        # Compress the database
        with open(db_path, 'rb') as f:
            db_data = f.read()
        
        compressed = gzip.compress(db_data, compresslevel=9)
        encoded = base64.b85encode(compressed).decode('ascii')
        
        # Split into chunks for embedding
        chunk_size = 80
        chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
        
        # Write the embedded data file
        embedded_py = OUTPUT_DIR / "theology_data_embedded.py"
        with open(embedded_py, 'w') as f:
            f.write('"""\n')
            f.write('Sanctum OS Embedded Theology Database\n')
            f.write('Compressed, encoded Bible and Church Fathers texts\n')
            f.write('This file is auto-generated - DO NOT EDIT\n')
            f.write('"""\n\n')
            f.write(f'CHUNK_COUNT = {len(chunks)}\n')
            f.write(f'ORIGINAL_SIZE = {len(db_data)}\n')
            f.write(f'COMPRESSED_SIZE = {len(compressed)}\n\n')
            f.write('THEOLOGY_DATA_CHUNKS = [\n')
            for chunk in chunks:
                f.write(f'    "{chunk}",\n')
            f.write(']\n')
        
        print(f"Embedded data created: {embedded_py}")
        print(f"Original size: {len(db_data):,} bytes")
        print(f"Compressed size: {len(compressed):,} bytes")
        print(f"Compression ratio: {len(compressed)/len(db_data)*100:.1f}%")
        
        # Create standalone extraction script
        extract_script = OUTPUT_DIR / "extract_theology.py"
        self._create_extraction_script(extract_script, len(chunks))
        
        return db_path
    
    def _process_bible_files(self, cursor, files: List[Path]):
        """Process Bible files and insert into database"""
        # Standard Bible book order and names
        bible_books = [
            # Old Testament
            ("Genesis", "OT", 50), ("Exodus", "OT", 40), ("Leviticus", "OT", 27),
            ("Numbers", "OT", 36), ("Deuteronomy", "OT", 34), ("Joshua", "OT", 24),
            ("Judges", "OT", 21), ("Ruth", "OT", 4), ("1 Samuel", "OT", 31),
            ("2 Samuel", "OT", 24), ("1 Kings", "OT", 22), ("2 Kings", "OT", 25),
            ("1 Chronicles", "OT", 29), ("2 Chronicles", "OT", 36), ("Ezra", "OT", 10),
            ("Nehemiah", "OT", 13), ("Tobit", "OT", 14), ("Judith", "OT", 16),
            ("Esther", "OT", 10), ("1 Maccabees", "OT", 16), ("2 Maccabees", "OT", 15),
            ("Job", "OT", 42), ("Psalms", "OT", 150), ("Proverbs", "OT", 31),
            ("Ecclesiastes", "OT", 12), ("Song of Solomon", "OT", 8),
            ("Wisdom", "OT", 19), ("Sirach", "OT", 51), ("Isaiah", "OT", 66),
            ("Jeremiah", "OT", 52), ("Lamentations", "OT", 5), ("Baruch", "OT", 6),
            ("Ezekiel", "OT", 48), ("Daniel", "OT", 14), ("Hosea", "OT", 14),
            ("Joel", "OT", 3), ("Amos", "OT", 9), ("Obadiah", "OT", 1),
            ("Jonah", "OT", 4), ("Micah", "OT", 7), ("Nahum", "OT", 3),
            ("Habakkuk", "OT", 3), ("Zephaniah", "OT", 3), ("Haggai", "OT", 2),
            ("Zechariah", "OT", 14), ("Malachi", "OT", 4),
            # New Testament
            ("Matthew", "NT", 28), ("Mark", "NT", 16), ("Luke", "NT", 24),
            ("John", "NT", 21), ("Acts", "NT", 28), ("Romans", "NT", 16),
            ("1 Corinthians", "NT", 16), ("2 Corinthians", "NT", 13),
            ("Galatians", "NT", 6), ("Ephesians", "NT", 6), ("Philippians", "NT", 4),
            ("Colossians", "NT", 4), ("1 Thessalonians", "NT", 5),
            ("2 Thessalonians", "NT", 3), ("1 Timothy", "NT", 6),
            ("2 Timothy", "NT", 4), ("Titus", "NT", 3), ("Philemon", "NT", 1),
            ("Hebrews", "NT", 13), ("James", "NT", 5), ("1 Peter", "NT", 5),
            ("2 Peter", "NT", 3), ("1 John", "NT", 5), ("2 John", "NT", 1),
            ("3 John", "NT", 1), ("Jude", "NT", 1), ("Revelation", "NT", 22),
        ]
        
        # Insert Bible books
        for name, testament, chapters in bible_books:
            cursor.execute(
                "INSERT OR IGNORE INTO bible_books (name, testament, chapters) VALUES (?, ?, ?)",
                (name, testament, chapters)
            )
        
        # Process each file for verse content
        # For now, create placeholder entries with sample verses
        # Full implementation would parse actual Bible files
        sample_verses = [
            ("Genesis", 1, 1, "In the beginning God created the heavens and the earth."),
            ("Genesis", 1, 2, "The earth was without form and void, and darkness was upon the face of the deep."),
            ("Genesis", 1, 3, "And God said, 'Let there be light'; and there was light."),
            ("John", 1, 1, "In the beginning was the Word, and the Word was with God, and the Word was God."),
            ("John", 1, 2, "He was in the beginning with God."),
            ("John", 1, 3, "All things were made through him, and without him was not anything made that was made."),
            ("John", 3, 16, "For God so loved the world that he gave his only Son, that whoever believes in him should not perish but have eternal life."),
        ]
        
        for book, chapter, verse, text in sample_verses:
            cursor.execute("SELECT id FROM bible_books WHERE name = ?", (book,))
            book_id = cursor.fetchone()
            if book_id:
                cursor.execute(
                    "INSERT INTO bible_verses (book_id, chapter, verse, text) VALUES (?, ?, ?, ?)",
                    (book_id[0], chapter, verse, text)
                )
    
    def _process_fathers_files(self, cursor, files: List[Path]):
        """Process Church Fathers files and insert into database"""
        # Major Church Fathers and their works
        fathers = [
            ("Clement of Rome", "First Epistle to the Corinthians", "c. 96 AD"),
            ("Ignatius of Antioch", "Epistle to the Ephesians", "c. 110 AD"),
            ("Ignatius of Antioch", "Epistle to the Magnesians", "c. 110 AD"),
            ("Ignatius of Antioch", "Epistle to the Trallians", "c. 110 AD"),
            ("Ignatius of Antioch", "Epistle to the Romans", "c. 110 AD"),
            ("Polycarp of Smyrna", "Epistle to the Philippians", "c. 110-140 AD"),
            ("Justin Martyr", "First Apology", "c. 155-157 AD"),
            ("Justin Martyr", "Second Apology", "c. 155-157 AD"),
            ("Justin Martyr", "Dialogue with Trypho", "c. 160 AD"),
            ("Irenaeus of Lyons", "Against Heresies", "c. 180 AD"),
            ("Clement of Alexandria", "Stromata", "c. 198-203 AD"),
            ("Clement of Alexandria", "Paedagogus", "c. 198 AD"),
            ("Tertullian", "Apology", "c. 197 AD"),
            ("Tertullian", "On the Resurrection of the Flesh", "c. 208 AD"),
            ("Origen", "On First Principles", "c. 230 AD"),
            ("Origen", "Against Celsus", "c. 248 AD"),
            ("Cyprian of Carthage", "On the Unity of the Church", "c. 251 AD"),
            ("Athanasius of Alexandria", "On the Incarnation", "c. 318 AD"),
            ("Athanasius of Alexandria", "Life of St. Anthony", "c. 360 AD"),
            ("Basil of Caesarea", "On the Holy Spirit", "c. 375 AD"),
            ("Gregory of Nazianzus", "Theological Orations", "c. 380 AD"),
            ("Gregory of Nyssa", "On the Making of Man", "c. 379 AD"),
            ("John Chrysostom", "On the Priesthood", "c. 391 AD"),
            ("Ambrose of Milan", "On the Mysteries", "c. 390 AD"),
            ("Jerome", "Vulgate Prologue", "c. 390 AD"),
            ("Augustine of Hippo", "Confessions", "c. 397-400 AD"),
            ("Augustine of Hippo", "City of God", "c. 413-426 AD"),
            ("Augustine of Hippo", "On the Trinity", "c. 400-420 AD"),
            ("Augustine of Hippo", "On Christian Doctrine", "c. 397 AD"),
            ("Cyril of Alexandria", "Commentary on John", "c. 425 AD"),
            ("Leo the Great", "Tome", "c. 449 AD"),
            ("Gregory the Great", "Pastoral Rule", "c. 590 AD"),
            ("Gregory the Great", "Dialogues", "c. 593 AD"),
            ("John of Damascus", "Exact Exposition of the Orthodox Faith", "c. 730 AD"),
        ]
        
        # Sample texts from Church Fathers
        sample_texts = [
            ("Clement of Rome", "First Epistle to the Corinthians", "Chapter 1", "The Church of God which sojourns in Rome to the Church of God which sojourns in Corinth, to those who are called and sanctified by the will of God through our Lord Jesus Christ."),
            ("Ignatius of Antioch", "Epistle to the Ephesians", "Chapter 1", "Ignatius, who is also called Theophorus, to the Church which is at Ephesus, in Asia, deservedly most happy, being blessed in the greatness and fullness of God the Father."),
            ("Justin Martyr", "First Apology", "Chapter 1", "To the Emperor Titus Aelius Adrianus Antoninus Pius Augustus Caesar, and to his son Verissimus the Philosopher, and to Lucius the Philosopher."),
            ("Irenaeus of Lyons", "Against Heresies", "Preface", "Inasmuch as certain men have set the truth aside, and bring in lying words and vain genealogies, which, as the apostle says, minister questions rather than godly edifying which is in faith."),
            ("Athanasius of Alexandria", "On the Incarnation", "Chapter 1", "In our former book we treated of the making of the world and the creation of all things in it, as the true faith teaches concerning these matters."),
            ("Augustine of Hippo", "Confessions", "Book 1, Chapter 1", "Great art Thou, O Lord, and greatly to be praised; great is Thy power, and of Thy wisdom there is no number."),
            ("Augustine of Hippo", "City of God", "Book 1, Chapter 1", "The glorious city of God is my theme in this work, which you, my dearest son Marcellinus, suggested."),
            ("John Chrysostom", "On the Priesthood", "Book 1", "I had many genuine friends at that time, who desired to deliver me from the temptations which beset me, and to withdraw me from my purpose."),
        ]
        
        for author, work, section, text in sample_texts:
            cursor.execute(
                "INSERT INTO church_fathers (author, work, section, text) VALUES (?, ?, ?, ?)",
                (author, work, section, text)
            )
    
    def _create_extraction_script(self, path: Path, chunk_count: int):
        """Create the extraction script that will be deployed to users"""
        script = f'''#!/usr/bin/env python3
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
    
    print(f"Database extracted to: {{DB_PATH}}")
    print(f"Size: {{len(db_data):,}} bytes")
    
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
    
    print(f"Bible books: {{bible_books}}")
    print(f"Bible verses: {{bible_verses}}")
    print(f"Church Fathers texts: {{fathers_texts}}")
    print("Extraction complete!")
    
    return DB_PATH

if __name__ == "__main__":
    extract_database()
'''
        
        with open(path, 'w') as f:
            f.write(script)
        
        os.chmod(path, 0o755)
        print(f"Extraction script created: {path}")

if __name__ == "__main__":
    packager = TheologyPackager()
    packager.create_compressed_archive()
