#!/usr/bin/env python3
"""
Parse Church Fathers from Nicene & Post-Nicene Fathers - FULL VERSION
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict

class ChurchFathersParser:
    """Parse Church Fathers writings from HTML files."""
    
    def __init__(self, text_dir: str):
        self.text_dir = Path(text_dir)
        self.html_files = sorted(self.text_dir.glob('*.html'))
        
        # Major authors in the collection
        self.KNOWN_AUTHORS = {
            'Eusebius', 'Athanasius', 'Basil', 'Gregory of Nazianzus',
            'Gregory of Nyssa', 'Chrysostom', 'Jerome', 'Augustine',
            'Cyprian', 'Ambrose', 'Leo', 'Gregory the Great',
            'Cyril of Jerusalem', 'Epiphanius', 'Hilary', 'Clement',
            'Ignatius', 'Polycarp', 'Irenaeus', 'Justin Martyr',
            'Tertullian', 'Origen', 'Novatian', 'Cyprian'
        }
    
    def identify_author_and_work(self, html_file: Path) -> tuple:
        """Identify author and work from HTML file."""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from HTML
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                # Clean up title
                title = re.sub(r'\s+', ' ', title).strip()
                
                # Try to identify author from title
                author = "Unknown"
                for known in self.KNOWN_AUTHORS:
                    if known.lower() in title.lower():
                        author = known
                        break
                
                # Extract work name
                work = title
                if author != "Unknown":
                    work = title.replace(author, '').strip()
                
                return author, work
        except Exception:
            pass
        
        # Fallback to filename
        filename = html_file.stem
        return "Unknown", filename
    
    def parse_file(self, html_file: Path) -> List[Dict]:
        """Parse a single HTML file."""
        texts = []
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {html_file}: {e}")
            return texts
        
        # Remove script and style tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # Get author and work
        author, work = self.identify_author_and_work(html_file)
        
        # Extract text content from paragraphs
        # NPNF uses various paragraph styles
        para_pattern = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
        
        section_num = 0
        for match in para_pattern.finditer(content):
            para_html = match.group(1)
            
            # Clean HTML tags
            text = re.sub(r'<[^>]+>', ' ', para_html)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Skip empty or copyright lines
            if not text or len(text) < 10:
                continue
            if 'copyright' in text.lower() or 'zebra' in text.lower():
                continue
            
            section_num += 1
            texts.append({
                'author': author,
                'work': work,
                'volume': self.extract_volume(html_file),
                'section': section_num,
                'content': text
            })
        
        return texts
    
    def extract_volume(self, html_file: Path) -> str:
        """Extract volume number from filename."""
        # NPNF files often have volume numbers in name
        match = re.search(r'vol(\d+)', html_file.name, re.IGNORECASE)
        if match:
            return f"Volume {match.group(1)}"
        return "Unknown"
    
    def extract_all_texts(self) -> List[Dict]:
        """Extract all texts from all HTML files."""
        all_texts = []
        
        print(f"Scanning {len(self.html_files)} HTML files...")
        
        for html_file in self.html_files:
            texts = self.parse_file(html_file)
            if texts:
                author = texts[0]['author']
                work = texts[0]['work']
                print(f"  {author} - {work}: {len(texts)} sections")
                all_texts.extend(texts)
        
        return all_texts
    
    def populate_database(self, db_path: str):
        """Populate SQLite database with all texts."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM church_fathers")
        
        texts = self.extract_all_texts()
        
        print(f"\nInserting {len(texts)} sections into database...")
        
        # Insert in batches
        batch_size = 500
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            cursor.executemany('''
                INSERT INTO church_fathers (author, work, volume, section, content)
                VALUES (?, ?, ?, ?, ?)
            ''', [(t['author'], t['work'], t['volume'], t['section'], t['content']) for t in batch])
            conn.commit()
        
        conn.close()
        
        print(f"✓ Inserted {len(texts)} sections")
        
        # Print summary
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT author, COUNT(*) FROM church_fathers GROUP BY author ORDER BY COUNT(*) DESC")
        print(f"\nTop authors by section count:")
        for author, count in cursor.fetchall()[:15]:
            print(f"  {author}: {count}")
        cursor.execute("SELECT COUNT(DISTINCT author) FROM church_fathers")
        author_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT work) FROM church_fathers")
        work_count = cursor.fetchone()[0]
        print(f"\nTotal authors: {author_count}, Total works: {work_count}")
        conn.close()

if __name__ == '__main__':
    import sys
    
    fathers_dir = '/home/workspace/Christianity_Compilation/EXTRACTED/Church_Fathers_Complete/text'
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    if not os.path.exists(fathers_dir):
        print(f"Error: Church Fathers directory not found: {fathers_dir}")
        sys.exit(1)
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        print("Run 'python3 package_theology.py' first.")
        sys.exit(1)
    
    parser = ChurchFathersParser(fathers_dir)
    parser.populate_database(db_path)
    print("\n✓ Church Fathers extraction complete!")
