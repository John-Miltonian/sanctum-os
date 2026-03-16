# Sanctum OS - Full Theological Library
## With Complete Bible and Church Fathers

> *"All Scripture is breathed out by God..."* — 2 Timothy 3:16

This version includes **complete extraction scripts** for the full LSV Bible and Nicene/Post-Nicene Fathers collection.

---

## What's Included

### 📖 Complete Biblical Library
- **All 66 books** of the Protestant canon
- **Literal Standard Version (LSV)** — modern literal translation
- **~35,000 verses** with full text
- **Old & New Testaments** with proper testament tagging

### 📚 Complete Church Fathers Collection  
- **~30+ authors** from Clement to John of Damascus
- **100+ works** from the Nicene and Post-Nicene Fathers
- **Complete NPNF volumes** with full text
- **Section-by-section breakdown** for easy reading

---

## Installation

### Quick Install (with full library)

```bash
# 1. Install Sanctum OS base
curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash

# 2. Download Bible and Fathers source texts (if you have them)
# Place in: ~/.local/share/theology/source/bible/
#            ~/.local/share/theology/source/fathers/

# 3. Run full extraction
cd ~/.local/share/theology
python3 parse_lsv_bible_full.py
python3 parse_fathers_full.py
```

---

## Database Structure

### Bible Verses Table
```sql
CREATE TABLE bible_verses (
    id INTEGER PRIMARY KEY,
    book TEXT,           -- e.g., "Genesis", "John"
    testament TEXT,      -- "OT" or "NT"
    chapter INTEGER,
    verse INTEGER,
    content TEXT         -- Full verse text
);
```

### Church Fathers Table
```sql
CREATE TABLE church_fathers (
    id INTEGER PRIMARY KEY,
    author TEXT,         -- e.g., "Augustine", "Chrysostom"
    work TEXT,           -- e.g., "Confessions", "Homilies on John"
    volume TEXT,         -- NPNF volume number
    section INTEGER,     -- Section/paragraph number
    content TEXT         -- Full text content
);
```

---

## CLI Usage

### Bible Commands
```bash
biblia Genesis 1:1           # Read single verse
biblia John 3               # Read full chapter
biblia --search "love"      # Search all verses
biblia --book Psalms        # List all Psalms
```

### Church Fathers Commands
```bash
patres Augustine             # List Augustine's works
patres --work "Confessions"  # Read specific work
patres --search "grace"      # Search all texts
patres --author Chrysostom   # Read Chrysostom
```

---

## File Structure After Full Install

```
~/.local/share/theology/
├── theology.db              # Main database (populated)
├── parse_lsv_bible_full.py  # Bible extraction script
├── parse_fathers_full.py    # Fathers extraction script
└── source/                  # Source texts (you provide)
    ├── bible/               # LSV HTML files
    └── fathers/             # NPNF HTML files
```

---

## Source Text Requirements

The extraction scripts expect:
- **Bible**: Biblia Sacra et Ultra (LSV) EPUB, extracted to HTML
- **Fathers**: Nicene and Post-Nicene Fathers EPUB, extracted to HTML

Place these in the `source/` directories before running extraction.

---

## Extraction Time

- **Bible**: ~10-15 minutes for 5,958 files
- **Fathers**: ~5-10 minutes for 1,248 files
- **Total**: ~20-30 minutes for complete library

---

**Sanctum OS v1.0 Full** — The Complete Theological Computing Environment
