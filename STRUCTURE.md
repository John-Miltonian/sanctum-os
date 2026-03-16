# Sanctum OS - Complete Structure

```
arch-christian-rice/
├── AGENTS.md                          # Agent memory and context
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Main documentation
├── STRUCTURE.md                       # This file
│
├── install/
│   └── install.sh                     # Main installer script (~500 lines)
│                                      # Installs packages, deploys configs,
│                                      # extracts theology database
│
├── theology-db/                       # EMBEDDED THEOLOGICAL LIBRARY
│   ├── package_theology.py            # Creates embedded database
│   ├── theology.db                    # SQLite database (raw)
│   ├── theology_data_embedded.py      # Compressed, base85-encoded data
│   │                                  # (79 lines, ~4KB compressed)
│   └── extract_theology.py            # Extracts to ~/.local/share/theology/
│
├── scripts/                           # CLI TOOLS (in ~/.local/bin/)
│   ├── biblia                         # Bible CLI (search, read, daily verse)
│   │                                  # Features:
│   │                                  #   - List all books (OT/NT filter)
│   │                                  #   - Read chapters and verses
│   │                                  #   - Full-text search
│   │                                  #   - Daily verse rotation
│   │                                  #   - Colorized output (cardinal/gold)
│   │
│   ├── patres                         # Church Fathers CLI
│   │                                  # Features:
│   │                                  #   - List all Fathers by period
│   │                                  #   - List works by author
│   │                                  #   - Read patristic texts
│   │                                  #   - Search by author/content
│   │                                  #   - Random daily quotes
│   │
│   ├── sanctum-quote                  # Display theological quotes
│   │                                  # Daily rotation of Church Fathers quotes
│   │                                  # Formatted with theological colors
│   │
│   ├── sanctum-theme                  # Theme switcher
│   │                                  # sanctum: Cassock black, cardinal red, gold
│   │                                  # liturgy: Liturgical seasonal colors
│   │
│   └── sanctum-help                   # Help system
│       # Displays complete command reference and keybindings
│
├── config/                            # CONFIGURATION FILES
│   │                                  # All deployed to ~/.config/
│   │
│   ├── hypr/
│   │   └── hyprland.conf              # Window manager configuration
│   │                                  # Features:
│   │                                  #   - Biblical workspace naming (1-9)
│   │                                  #   - Sanctum color borders
│   │                                  #   - Mod+Return for terminal
│   │                                  #   - Mod+D for launcher
│   │                                  #   - Mod+T for daily scripture
│   │                                  #   - Window rules for apps
│   │                                  #   - Workspace auto-assignment
│   │
│   ├── kitty/
│   │   └── kitty.conf                 # Terminal configuration
│   │                                  # Features:
│   │                                  #   - Sanctum 16-color palette
│   │                                  #   - Cassock black background
│   │                                  #   - Aged parchment foreground
│   │                                  #   - Cardinal red for errors/alerts
│   │                                  #   - Byzantine gold for URLs
│   │                                  #   - 95% background opacity
│   │
│   ├── waybar/
│   │   ├── config                     # Status bar configuration
│   │   │                              # Modules:
│   │   │                              #   - Workspaces (1-9)
│   │   │                              #   - Window title
│   │   │                              #   - Custom theology quote
│   │   │                              #   - Custom biblia daily verse
│   │   │                              #   - Tray, network, audio
│   │   │                              #   - Battery, clock
│   │   │
│   │   └── style.css                  # Waybar styling
│   │                                  # Sanctum colors, red border bottom
│   │                                  # Cardinal red for active workspace
│   │                                  # Gold accents for theology module
│   │
│   ├── wofi/
│   │   ├── config                     # Launcher configuration
│   │   └── sanctum.css                # Launcher styling
│   │                                  # Dark background, red border
│   │                                  # Gold highlights for matches
│   │
│   ├── fastfetch/
│   │   └── config.jsonc               # System info display
│   │                                  # Custom ASCII art header
│   │                                  # Sanctum OS branding
│   │                                  # Theological footer quote
│   │
│   └── neofetch/
│       └── config.conf                # Legacy fetch config
│                                      # ASCII art with Sanctum colors
│
└── wallpapers/                          # THEOLOGICAL WALLPAPERS
    ├── sanctum-wallpaper-01.png       # Metatron's cube + cross
    ├── sanctum-wallpaper-02.png       # Golden halo circle
    └── sanctum-wallpaper-03.png       # Illuminated manuscript style

```

## Installation Flow

```
┌─────────────────┐
│  User runs      │
│  install.sh     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Install packages│
│ via pacman/yay  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract theology│
│ database        │
│ (embedded py →  │
│  ~/.local/...)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Copy configs to │
│ ~/.config/      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Copy scripts to │
│ ~/.local/bin/   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update PATH in  │
│ .bashrc/.zshrc  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sanctum OS      │
│ Ready!          │
└─────────────────┘
```

## Database Schema

```sql
-- Bible books
CREATE TABLE bible_books (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,          -- "Genesis", "John", etc.
    testament TEXT,            -- "OT" or "NT"
    chapters INTEGER           -- Number of chapters
);

-- Bible verses (73 books × ~1000 verses = ~73,000 rows)
CREATE TABLE bible_verses (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,           -- FK to bible_books
    chapter INTEGER,
    verse INTEGER,
    text TEXT                  -- Full verse text
);

-- Church Fathers writings
CREATE TABLE church_fathers (
    id INTEGER PRIMARY KEY,
    author TEXT,               -- "Augustine of Hippo"
    work TEXT,                 -- "Confessions"
    section TEXT,              -- "Book 1, Chapter 1"
    text TEXT                  -- Full text content
);

-- Full-text search (FTS5)
CREATE VIRTUAL TABLE bible_verses_fts USING fts5(text);
CREATE VIRTUAL TABLE church_fathers_fts USING fts5(text);
```

## Color Usage Map

| Element | Color | Hex | File |
|---------|-------|-----|------|
| Background | Cassock Black | `#0a0a0a` | kitty, waybar, wofi |
| Foreground | Aged Parchment | `#d4c4a8` | kitty, waybar |
| Active border | Cardinal Red | `#8b0000` | hyprland |
| Accent/Hover | Bright Cardinal | `#b22222` | waybar |
| Workspace active | Cardinal | `#8b0000` | waybar |
| Daily verse bg | Royal Purple | `#4a1942` | waybar |
| URLs/Links | Byzantine Gold | `#b8860b` | kitty |
| Highlights | Bright Gold | `#daa520` | kitty, wofi |
| Success | Olive Green | `#4a5d23` | kitty |
| Secondary | Marian Blue | `#1a3a5c` | waybar (theology) |

## Total Package Size

```
Component           Size
─────────────────────────────
Embedded database   ~4 KB
Scripts             ~20 KB
Configs             ~15 KB
Wallpapers          ~1.5 MB
Documentation       ~10 KB
─────────────────────────────
Total               ~1.8 MB
```

## Post-Installation Paths

```
~/.local/share/theology/
├── theology.db              # Extracted SQLite database
└── extract_theology.py      # Copy of extractor

~/.local/bin/
├── biblia                   # Bible CLI
├── patres                   # Fathers CLI
├── sanctum-quote            # Quote display
├── sanctum-theme            # Theme switcher
└── sanctum-help             # Help

~/.config/
├── hypr/hyprland.conf       # WM config
├── kitty/kitty.conf         # Terminal
├── waybar/                  # Status bar
├── wofi/                    # Launcher
├── fastfetch/               # Fetch config
└── neofetch/                # Legacy fetch

~/.local/share/wallpapers/sanctum-os/
├── sanctum-wallpaper-01.png
├── sanctum-wallpaper-02.png
└── sanctum-wallpaper-03.png
```

---

*Sanctum OS v1.0 - The Theological Computing Environment*
