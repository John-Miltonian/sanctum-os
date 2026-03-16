# Sanctum OS - Quick Start Guide

## First Steps After Installation

### 1. Verify Installation

Open a terminal and run:
```bash
sanctum-help
```

You should see the Sanctum OS header and help menu.

### 2. Check the Database

```bash
biblia --list
patres --list
```

This confirms the theological library is working.

### 3. Set Wallpaper

```bash
# For Hyprland
hyprpaper ~/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png

# Or use your preferred wallpaper setter
feh --bg-scale ~/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png
```

### 4. Key Commands to Learn

| Command | What it does |
|---------|--------------|
| `Mod+D` | Open application menu |
| `Mod+Return` | Open terminal |
| `Mod+1-9` | Switch workspaces |
| `Mod+Q` | Close window |
| `biblia --daily` | Daily scripture |
| `patres --random` | Random Father quote |
| `sanctum-quote` | Display quote |

### 5. Daily Use

**Morning devotion:**
```bash
biblia --daily
```

**Study session:**
```bash
patres --read Augustine
biblia Genesis 1
```

**Random inspiration:**
```bash
sanctum-quote
```

### 6. Customization

Edit configs in `~/.config/`:
- `hypr/hyprland.conf` - Window manager
- `kitty/kitty.conf` - Terminal
- `waybar/config` - Status bar

### 7. Troubleshooting

**Database not found:**
```bash
python3 ~/.local/share/theology/extract_theology.py
```

**Colors not applied:**
```bash
sanctum-theme sanctum
```

**Commands not found:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 8. Advanced Usage

**Search the Bible:**
```bash
biblia --search "love"
biblia --search "grace" --limit 50
```

**Read specific passages:**
```bash
biblia John 3:16
biblia Psalm 23
biblia "1 Corinthians" 13
```

**Access Church Fathers:**
```bash
patres --works Athanasius
patres --read Augustine --work "Confessions"
patres --search "Trinity" --author Augustine
```

### 9. Integration Ideas

Add to your shell startup (`.bashrc` or `.zshrc`):
```bash
# Daily verse on login
biblia --daily

# Random quote every hour
# (use cron or systemd timer for this)
```

### 10. Next Steps

- Explore all 9 biblical workspaces
- Customize the keybindings in `hyprland.conf`
- Add your own wallpapers
- Contribute to the Fathers database

---

*Dominus vobiscum*
