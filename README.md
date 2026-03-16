# Sanctum OS
## Arch Linux Rice with Embedded Theological Library

> *"In the beginning was the Word, and the Word was with God, and the Word was God."* — John 1:1

Sanctum OS is a complete Arch Linux rice designed for theological scholars, containing the full Bible and Church Fathers' writings embedded directly into the system. No internet connection required after installation.

### Features

- **Complete Biblical Library**: Full Old and New Testaments
- **Church Fathers Collection**: Writings from Clement of Rome to John of Damascus
- **Theological CLI Tools**: `biblia` and `patres` commands for instant scripture and patristic access
- **Daily Scripture & Quotes**: Integrated into your status bar
- **Reverent Aesthetic**: Cassock black, cardinal red, Byzantine gold, aged parchment
- **Biblically-Named Workspaces**: Genesis through Revelation
- **Self-Contained**: No external downloads needed

### Color Scheme

| Color | Hex | Usage | Symbolism |
|-------|-----|-------|-----------|
| Cassock Black | `#0a0a0a` | Background | The religious habit |
| Cardinal Red | `#8b0000` | Accent, active | Sacred Heart, martyrs |
| Byzantine Gold | `#b8860b` | Highlights | Divine glory |
| Aged Parchment | `#d4c4a8` | Foreground | Sacred manuscripts |
| Royal Purple | `#4a1942` | Special | Christ the King |
| Marian Blue | `#1a3a5c` | Secondary | Heavenly grace |

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sanctum-os.git
cd sanctum-os

# Run the installer
chmod +x install/install.sh
./install/install.sh
```

The installer will:
1. Install all necessary packages
2. Extract the embedded theological database
3. Deploy all configurations
4. Set up the CLI tools

### Commands

#### `biblia` - Holy Bible CLI

```bash
biblia --list                    # List all Bible books
biblia --list -t OT              # List Old Testament
biblia --list -t NT              # List New Testament
biblia John 3:16                 # Read specific verse
biblia Genesis 1                   # Read chapter
biblia --search "love"           # Search Bible
biblia --daily                   # Show daily verse
```

#### `patres` - Church Fathers CLI

```bash
patres --list                    # List all Church Fathers
patres --works Augustine         # List Augustine's works
patres --read Augustine          # Read Augustine
patres --search "grace"          # Search writings
patres --random                  # Show random quote
```

#### Other Commands

```bash
sanctum-quote                    # Display theological quote
sanctum-theme [sanctum|liturgy]  # Apply theme
sanctum-help                     # Show help
```

### Keybindings

| Key | Action |
|-----|--------|
| `Mod+Return` | Open terminal |
| `Mod+D` | Application launcher |
| `Mod+T` | Daily scripture |
| `Mod+Shift+T` | Random Church Father quote |
| `Mod+Period` | Theological quote |
| `Mod+B` | Browser |
| `Mod+1-9` | Switch workspace (Genesis-Revelation) |

### Workspaces

1. **Genesis** — Terminal, CLI tools
2. **Exodus** — Browser, web
3. **Leviticus** — Editor, development
4. **Numbers** — File manager
5. **Deuteronomy** — Documents
6. **Psalms** — Media, music
7. **Proverbs** — Communication
8. **Gospels** — Study, research
9. **Revelation** — System monitoring

### Database

The theology database is located at:
```
~/.local/share/theology/theology.db
```

It contains:
- 73 books of the Bible
- Writings from 30+ Church Fathers
- Full-text search capability
- Cross-references

### Configuration

All configurations are in `~/.config/`:
- `hypr/` — Window manager
- `kitty/` — Terminal
- `waybar/` — Status bar
- `wofi/` — Application launcher
- `fastfetch/` — System information

### Architecture

```
sanctum-os/
├── install/
│   └── install.sh              # Main installer
├── rice/
│   └── (theme files)
├── theology-db/
│   ├── theology_data_embedded.py  # Compressed, encoded texts
│   └── extract_theology.py        # Extraction script
├── scripts/
│   ├── biblia                  # Bible CLI
│   ├── patres                  # Fathers CLI
│   ├── sanctum-quote         # Quote display
│   └── sanctum-help          # Help system
├── config/
│   ├── hypr/                 # Hyprland config
│   ├── kitty/                # Kitty terminal
│   ├── waybar/               # Status bar
│   ├── wofi/                 # Launcher
│   ├── fastfetch/            # Fetch config
│   └── neofetch/             # Legacy fetch
└── wallpapers/               # Sanctum wallpapers
```

### Credits

- Bible texts: Various public domain translations
- Church Fathers: Nicene and Post-Nicene Fathers series
- Inspired by: Byzantine iconography, illuminated manuscripts, monastic computing

### Gloria Patri

*Gloria Patri, et Filio, et Spiritui Sancto.*
*Sicut erat in principio, et nunc, et semper,*
*et in saecula saeculorum. Amen.*

---

**Sanctum OS v1.0** — The Theological Computing Environment

## Expanding the Database

The rice comes with substantial sample content pre-populated, so it works immediately. To add the complete Bible and Church Fathers texts:

### Prerequisites
Ensure you have the source files from `Christianity_Compilation/EXTRACTED/`:
- `Biblia_Sacra/` — The Literal Standard Version (LSV) Bible
- `Church_Fathers_Complete/` — The Nicene and Post-Nicene Fathers

### Full Bible Extraction

```bash
cd ~/.local/share/theology/
python3 extract_lsv_bible.py
```

This parses all 4,500+ HTML files from the Biblia Sacra et Ultra and populates the database with the complete Old and New Testaments.

### Church Fathers Extraction

```bash
cd ~/.local/share/theology/
python3 extract_fathers.py
```

This extracts texts from 30+ Church Fathers including:
- Apostolic Fathers (Clement, Ignatius, Polycarp)
- Nicene Fathers (Athanasius, Basil, Gregory, John Chrysostom)
- Post-Nicene Fathers (Jerome, Augustine, Leo, Gregory the Great)

### Database Structure

After extraction, the database contains:
- 73 books of the Bible (~35,000 verses)
- 100+ works from 30+ Church Fathers (~10,000 sections)
- Full-text search capability
- Cross-reference indices

### Verification

Check the database status:

```bash
sqlite3 ~/.local/share/theology/theology.db "SELECT COUNT(*) FROM bible_verses;"
sqlite3 ~/.local/share/theology/theology.db "SELECT COUNT(*) FROM church_fathers;"
```

---

**Sanctum OS v1.0** — The Theological Computing Environment
