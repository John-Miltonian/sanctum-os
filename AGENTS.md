# Sanctum OS - Agent Memory

## Project Overview

Sanctum OS is a complete Arch Linux rice designed for theological scholars and those who want a reverent, scholarly computing environment. It includes the full Bible and Church Fathers' texts embedded directly in the system.

## Key Components

### Theological Database
- **Location**: `/home/workspace/arch-christian-rice/theology-db/`
- **Packager**: `package_theology.py` - Creates embedded database
- **Embedded Data**: `theology_data_embedded.py` - Compressed, base85-encoded
- **Extractor**: `extract_theology.py` - Extracts to `~/.local/share/theology/`

### CLI Tools
- **biblia** - Bible search and reading
- **patres** - Church Fathers access
- **sanctum-quote** - Daily theological quotes
- **sanctum-theme** - Color scheme switcher
- **sanctum-help** - Help system

### Desktop Environment
- **WM**: Hyprland (primary), Sway (alternative), i3 (X11)
- **Terminal**: Kitty with Sanctum colors
- **Status Bar**: Waybar with biblical workspace names
- **Launcher**: Wofi/Rofi with theological theme
- **Fetch**: Fastfetch/Neofetch with custom config

### Color Scheme
| Color | Hex | Symbolism |
|-------|-----|-----------|
| Background | `#0a0a0a` | Cassock black |
| Foreground | `#d4c4a8` | Aged parchment |
| Red | `#8b0000` | Cardinal red |
| Gold | `#b8860b` | Byzantine gold |

## Workspaces (Biblical Naming)
1. Genesis - Terminal
2. Exodus - Browser
3. Leviticus - Editor
4. Numbers - File manager
5. Deuteronomy - Documents
6. Psalms - Media
7. Proverbs - Communication
8. Gospels - Study
9. Revelation - System monitoring

## Installation Flow
1. `install.sh` installs packages via pacman and yay
2. Extracts theology database
3. Copies configs to `~/.config/`
4. Copies scripts to `~/.local/bin/`
5. Sets up keybindings

## Maintenance Notes
- Update theology database by re-running `package_theology.py`
- Add new Fathers by editing the sample_texts in the packager
- Colors defined in: kitty.conf, waybar/style.css, wofi/sanctum.css

## User Context
Josh (joshr) is working on:
- The Sacraments analog horror series
- The Custodia and the City of God theological fiction
- Grand Christian Library compilation

This rice complements their theological research and creative work.
