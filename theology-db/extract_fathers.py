#!/usr/bin/env python3
"""
Extract Church Fathers texts from EPUB
Parses the Nicene and Post-Nicene Fathers series
"""

import os
import re
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

# Source directory
FATHERS_DIR = Path("/home/workspace/Christianity_Compilation/EXTRACTED/Church_Fathers_Complete/text")
DB_PATH = Path.home() / ".local/share/theology/theology.db"

# Major Church Fathers and their approximate file ranges
# Based on the NPNF/PNF series structure
FATHERS_WORKS = [
    # (author, work_title, file_pattern, period)
    ("Clement of Rome", "First Epistle to the Corinthians", "part22*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Ephesians", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Magnesians", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Trallians", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Romans", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Philadelphians", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to the Smyrnaeans", "part23*.html", "Apostolic"),
    ("Ignatius of Antioch", "Epistle to Polycarp", "part23*.html", "Apostolic"),
    ("Polycarp of Smyrna", "Epistle to the Philippians", "part24*.html", "Apostolic"),
    ("Didache", "Teaching of the Twelve Apostles", "part21*.html", "Apostolic"),
    ("Barnabas", "Epistle of Barnabas", "part22*.html", "Apostolic"),
    ("Hermas", "The Shepherd of Hermas", "part25*.html", "Apostolic"),
    
    ("Justin Martyr", "First Apology", "part30*.html", "Apologetic"),
    ("Justin Martyr", "Second Apology", "part30*.html", "Apologetic"),
    ("Justin Martyr", "Dialogue with Trypho", "part31*.html", "Apologetic"),
    ("Irenaeus of Lyons", "Against Heresies", "part50*.html", "Apologetic"),
    ("Clement of Alexandria", "Exhortation to the Heathen", "part40*.html", "Alexandrian"),
    ("Clement of Alexandria", "The Instructor", "part40*.html", "Alexandrian"),
    ("Clement of Alexandria", "Stromata", "part41*.html", "Alexandrian"),
    ("Tertullian", "Apology", "part60*.html", "Western"),
    ("Tertullian", "On the Resurrection of the Flesh", "part61*.html", "Western"),
    ("Tertullian", "Against Praxeas", "part62*.html", "Western"),
    ("Origen", "De Principiis", "part70*.html", "Alexandrian"),
    ("Origen", "Against Celsus", "part71*.html", "Alexandrian"),
    ("Cyprian of Carthage", "Treatises", "part80*.html", "Western"),
    ("Cyprian of Carthage", "Letters", "part81*.html", "Western"),
    
    ("Athanasius of Alexandria", "On the Incarnation", "part100*.html", "Nicene"),
    ("Athanasius of Alexandria", "Deposition of Arius", "part101*.html", "Nicene"),
    ("Athanasius of Alexandria", "Life of St. Anthony", "part102*.html", "Nicene"),
    ("Athanasius of Alexandria", "Four Discourses Against the Arians", "part103*.html", "Nicene"),
    ("Athanasius of Alexandria", "On the Councils of Ariminum and Seleucia", "part104*.html", "Nicene"),
    ("Athanasius of Alexandria", "Tomas ad Antiochenos", "part105*.html", "Nicene"),
    ("Athanasius of Alexandria", "Letter to the Bishops of Egypt and Libya", "part106*.html", "Nicene"),
    ("Athanasius of Alexandria", "Apology to the Emperor", "part107*.html", "Nicene"),
    ("Athanasius of Alexandria", "Apology for His Flight", "part108*.html", "Nicene"),
    ("Athanasius of Alexandria", "History of the Arians", "part109*.html", "Nicene"),
    ("Athanasius of Alexandria", "Four Letters to Serapion", "part110*.html", "Nicene"),
    ("Athanasius of Alexandria", "Against the Arian Heresy", "part111*.html", "Nicene"),
    ("Athanasius of Alexandria", "On the Nicene Council", "part112*.html", "Nicene"),
    ("Athanasius of Alexandria", "Defense of the Nicene Definition", "part113*.html", "Nicene"),
    ("Athanasius of Alexandria", "On the Opinion of Dionysius", "part114*.html", "Nicene"),
    ("Athanasius of Alexandria", "On the Baptism of the Holy Spirit", "part115*.html", "Nicene"),
    ("Athanasius of Alexandria", "Letters", "part116*.html", "Nicene"),
    
    ("Basil of Caesarea", "On the Holy Spirit", "part200*.html", "Nicene"),
    ("Basil of Caesarea", "Letters and Select Works", "part201*.html", "Nicene"),
    ("Gregory of Nazianzus", "Theological Orations", "part210*.html", "Nicene"),
    ("Gregory of Nazianzus", "Sermons", "part211*.html", "Nicene"),
    ("Gregory of Nazianzus", "Letters", "part212*.html", "Nicene"),
    ("Gregory of Nyssa", "Dogmatic Treatises", "part220*.html", "Nicene"),
    ("Gregory of Nyssa", "Ascetical Works", "part221*.html", "Nicene"),
    ("Gregory of Nyssa", "Letters", "part222*.html", "Nicene"),
    ("John Chrysostom", "On the Priesthood", "part300*.html", "Nicene"),
    ("John Chrysostom", "Letters to the Fallen Theodore", "part301*.html", "Nicene"),
    ("John Chrysostom", "No One Can Harm the Man Who Does Not Harm Himself", "part302*.html", "Nicene"),
    ("John Chrysostom", "Letters to Olympias", "part303*.html", "Nicene"),
    ("John Chrysostom", "On the Priesthood", "part304*.html", "Nicene"),
    ("John Chrysostom", "Homilies on the Gospel of Matthew", "part305*.html", "Nicene"),
    ("John Chrysostom", "Homilies on the Gospel of John", "part306*.html", "Nicene"),
    ("John Chrysostom", "Homilies on the Acts of the Apostles", "part307*.html", "Nicene"),
    ("John Chrysostom", "Homilies on the Epistle to the Romans", "part308*.html", "Nicene"),
    ("John Chrysostom", "Homilies on First Corinthians", "part309*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Second Corinthians", "part310*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Ephesians", "part311*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Philippians", "part312*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Colossians", "part313*.html", "Nicene"),
    ("John Chrysostom", "Homilies on First Thessalonians", "part314*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Second Thessalonians", "part315*.html", "Nicene"),
    ("John Chrysostom", "Homilies on First Timothy", "part316*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Second Timothy", "part317*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Titus", "part318*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Philemon", "part319*.html", "Nicene"),
    ("John Chrysostom", "Homilies on Hebrews", "part320*.html", "Nicene"),
    ("Ambrose of Milan", "On the Christian Faith", "part400*.html", "Nicene"),
    ("Ambrose of Milan", "On the Holy Spirit", "part401*.html", "Nicene"),
    ("Ambrose of Milan", "On the Mysteries", "part402*.html", "Nicene"),
    ("Ambrose of Milan", "On the Sacraments", "part403*.html", "Nicene"),
    ("Ambrose of Milan", "On Repentance", "part404*.html", "Nicene"),
    ("Ambrose of Milan", "On the Duties of the Clergy", "part405*.html", "Nicene"),
    ("Ambrose of Milan", "Letters", "part406*.html", "Nicene"),
    
    ("Jerome", "Letters and Select Works", "part500*.html", "Post-Nicene"),
    ("Jerome", "Lives of the Hermits", "part501*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Confessions", "part600*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Letters", "part601*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Christian Doctrine", "part602*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Trinity", "part603*.html", "Post-Nicene"),
    ("Augustine of Hippo", "City of God", "part604*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Nature and Grace", "part605*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Grace and Free Will", "part606*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Rebuke and Grace", "part607*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Predestination of the Saints", "part608*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Gift of Perseverance", "part609*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Homilies on the Gospel of John", "part610*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Homilies on the First Epistle of John", "part611*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Homilies on Psalm 119", "part612*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Sermon on the Mount", "part613*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Homilies on the New Testament", "part614*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Our Lord's Sermon on the Mount", "part615*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Harmony of the Gospels", "part616*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Questions on the Gospels", "part617*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Homilies on the Old Testament", "part618*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Expositions on the Psalms", "part619*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Soliloquies", "part620*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Enarrations on the Psalms", "part621*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Reply to Faustus the Manichaean", "part622*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Contra Julianum", "part623*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Marriage and Concupiscence", "part624*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Against Two Letters of the Pelagians", "part625*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Soul and Its Origin", "part626*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Against the Priscillianists and Origenists", "part627*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Against the Epistle of Manichaeus", "part628*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Morals of the Catholic Church", "part629*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Morals of the Manichaeans", "part630*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Greatness of the Soul", "part631*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Teacher", "part632*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Free Will", "part633*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Usefulness of Belief", "part634*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Catechising of the Uninstructed", "part635*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Faith and the Creed", "part636*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Creed - A Sermon to Catechumens", "part637*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Continence", "part638*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Good of Marriage", "part639*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Holy Virginity", "part640*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Good of Widowhood", "part641*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Lying", "part642*.html", "Post-Nicene"),
    ("Augustine of Hippo", "Against Lying", "part643*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Work of Monks", "part644*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Patience", "part645*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Care to be Had for the Dead", "part646*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Punishment and Forgiveness of Sins", "part647*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Spirit and the Letter", "part648*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Faith and Works", "part649*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Seeing God", "part650*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Proceedings of Pelagius", "part651*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Grace of Christ", "part652*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Original Sin", "part653*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Perfection of Human Righteousness", "part654*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Proceedings of Pelagius", "part655*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On the Grace of Christ", "part656*.html", "Post-Nicene"),
    ("Augustine of Hippo", "On Original Sin", "part657*.html", "Post-Nicene"),
    
    ("Cyril of Jerusalem", "Catechetical Lectures", "part700*.html", "Post-Nicene"),
    ("Cyril of Alexandria", "Commentary on John", "part800*.html", "Post-Nicene"),
    ("Cyril of Alexandria", "Commentary on Luke", "part801*.html", "Post-Nicene"),
    ("Cyril of Alexandria", "On the Holy and Consubstantial Trinity", "part802*.html", "Post-Nicene"),
    ("Cyril of Alexandria", "Letters", "part803*.html", "Post-Nicene"),
    
    ("Leo the Great", "Letters and Sermons", "part900*.html", "Post-Nicene"),
    ("Leo the Great", "Tome", "part901*.html", "Post-Nicene"),
    
    ("Gregory the Great", "Pastoral Rule", "part1000*.html", "Post-Nicene"),
    ("Gregory the Great", "Dialogues", "part1001*.html", "Post-Nicene"),
    ("Gregory the Great", "Letters", "part1002*.html", "Post-Nicene"),
    
    ("John of Damascus", "Exact Exposition of the Orthodox Faith", "part1100*.html", "Post-Nicene"),
    ("John of Damascus", "On Heresies", "part1101*.html", "Post-Nicene"),
    ("John of Damascus", "On the Divine Images", "part1102*.html", "Post-Nicene"),
]

def clean_html_text(html: str) -> str:
    """Extract clean text from HTML"""
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Replace common entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    
    return text.strip()

def extract_text_from_file(file_path: Path, section_size: int = 1000) -> List[Tuple[str, str]]:
    """Extract text sections from an HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    # Clean the text
    full_text = clean_html_text(html)
    
    if not full_text:
        return []
    
    # Split into sections
    words = full_text.split()
    sections = []
    
    for i in range(0, len(words), section_size):
        section_words = words[i:i+section_size]
        section_text = ' '.join(section_words)
        section_name = f"Section {len(sections) + 1}"
        sections.append((section_name, section_text))
    
    return sections

def populate_fathers_db(db_path: Path):
    """Populate database with Church Fathers texts"""
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing Fathers data
    cursor.execute("DELETE FROM church_fathers")
    
    total_entries = 0
    
    for author, work_title, file_pattern, period in FATHERS_WORKS:
        # Find matching files
        matching_files = sorted(FATHERS_DIR.glob(file_pattern))
        
        if not matching_files:
            continue
        
        print(f"Processing {author} - {work_title} ({len(matching_files)} files)...")
        
        for file_path in matching_files:
            sections = extract_text_from_file(file_path)
            
            for section_name, text in sections:
                cursor.execute(
                    "INSERT INTO church_fathers (author, work, section, text) VALUES (?, ?, ?, ?)",
                    (author, work_title, section_name, text)
                )
                total_entries += 1
    
    conn.commit()
    conn.close()
    
    print(f"\nDone! Added {total_entries} entries from Church Fathers.")
    print(f"Database: {db_path}")

if __name__ == '__main__':
    # Ensure database exists
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        print("Run extract_theology.py first to create the database structure.")
        exit(1)
    
    populate_fathers_db(DB_PATH)
