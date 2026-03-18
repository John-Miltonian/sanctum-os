#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUM OS - ONE-SHOT INSTALLER (Sway/i3 Edition)
# curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
RESET='\033[0m'

echo -e "${RED}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███╗            ║
║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║            ║
║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║            ║
║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██�║╚██╔╝██║            ║
║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║            ║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"
echo -e "${GOLD}Sanctum OS v1.1 - The Theological Computing Environment${RESET}\n"
echo -e "${SILVER}Using Sway (Wayland) or i3 (X11) window manager${RESET}\n"

# Detect source location
if [ -f "./install/install.sh" ] && [ -d "./theology-db" ]; then
    SOURCE_DIR="$(pwd)"
    LOCAL_INSTALL=true
    echo -e "${SILVER}[*] Local install detected${RESET}"
else
    LOCAL_INSTALL=false
    SOURCE_DIR="$(mktemp -d)/sanctum-os"
    echo -e "${SILVER}[*] Downloading from GitHub...${RESET}"
    git clone --depth 1 https://github.com/John-Miltonian/sanctum-os.git "$SOURCE_DIR" 2>/dev/null || {
        curl -fsSL https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz | tar -xz -C /tmp
        SOURCE_DIR="/tmp/sanctum-os-main"
    }
fi

# Check distribution
if [ -f "/etc/arch-release" ] || [ -f "/etc/endeavouros-release" ]; then
    echo -e "${SILVER}[*] Arch-based system detected${RESET}"
    
    # Install packages
    echo -e "${SILVER}[*] Installing packages...${RESET}"
    
    # Core packages (official repos)
    sudo pacman -Syu --needed --noconfirm kitty sway i3-wm i3status dmenu waybar wofi swaylock swayidle 2>/dev/null || true
    sudo pacman -Syu --needed --noconfirm fastfetch neofetch zsh bash-completion sqlite python 2>/dev/null || true
    
    # Try AUR helper for starship
    if command -v yay &>/dev/null; then
        yay -S --needed --noconfirm starship 2>/dev/null || true
    elif command -v paru &>/dev/null; then
        paru -S --needed --noconfirm starship 2>/dev/null || true
    fi
    
    echo -e "${SILVER}[*] Package installation complete${RESET}"
else
    echo -e "${GOLD}[!] Non-Arch system - install manually:${RESET}"
    echo -e "  kitty, sway (or i3), waybar, wofi, sqlite, python"
fi

# Create directories
echo -e "${SILVER}[*] Setting up directories...${RESET}"
mkdir -p ~/.config/{kitty,sway,i3,waybar,wofi,fastfetch,neofetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers/sanctum-os}

# Copy configs
echo -e "${SILVER}[*] Installing configurations...${RESET}"
cp "$SOURCE_DIR/config/kitty/kitty.conf" ~/.config/kitty/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/config" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/style.css" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/config" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/sanctum.css" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/fastfetch/config.jsonc" ~/.config/fastfetch/ 2>/dev/null || true
cp "$SOURCE_DIR/config/neofetch/config.conf" ~/.config/neofetch/ 2>/dev/null || true

# Install Sway config (new)
cat > ~/.config/sway/config << 'SWAYCONFIG'
# Sanctum OS Sway Configuration
# Theological Computing Environment

set $mod Mod4
set $term kitty
set $menu wofi --show drun

# Font
font pango:Fira Code Nerd Font 11

# Window borders
default_border pixel 2
default_floating_border normal
hide_edge_borders none

# Colors - Sanctum Theme
# class                 border  backgr. text    indicator child_border
client.focused          #8b0000 #0a0a0a #d4c4a8 #b8860b   #8b0000
client.focused_inactive #333333 #0a0a0a #888888 #292929   #333333
client.unfocused        #333333 #0a0a0a #555555 #292929   #333333
client.urgent           #8b0000 #0a0a0a #ffffff #900000   #8b0000

# Gaps
gaps inner 8
gaps outer 4

# Startup
exec waybar
exec kitty --session ~/.config/kitty/sanctum-session.conf

# Key bindings
bindsym $mod+Return exec $term
bindsym $mod+d exec $menu
bindsym $mod+q kill
bindsym $mod+Shift+e exec swaynag -t warning -m 'Exit Sway?' -b 'Yes' 'swaymsg exit'

# Workspaces (Biblical naming)
bindsym $mod+1 workspace "1: Genesis"
bindsym $mod+2 workspace "2: Exodus"
bindsym $mod+3 workspace "3: Leviticus"
bindsym $mod+4 workspace "4: Numbers"
bindsym $mod+5 workspace "5: Deuteronomy"
bindsym $mod+6 workspace "6: Psalms"
bindsym $mod+7 workspace "7: Proverbs"
bindsym $mod+8 workspace "8: Gospels"
bindsym $mod+9 workspace "9: Revelation"

# Move windows
bindsym $mod+Shift+1 move container to workspace "1: Genesis"
bindsym $mod+Shift+2 move container to workspace "2: Exodus"
bindsym $mod+Shift+3 move container to workspace "3: Leviticus"
bindsym $mod+Shift+4 move container to workspace "4: Numbers"
bindsym $mod+Shift+5 move container to workspace "5: Deuteronomy"
bindsym $mod+Shift+6 move container to workspace "6: Psalms"
bindsym $mod+Shift+7 move container to workspace "7: Proverbs"
bindsym $mod+Shift+8 move container to workspace "8: Gospels"
bindsym $mod+Shift+9 move container to workspace "9: Revelation"

# Layout
bindsym $mod+b splith
bindsym $mod+v splitv
bindsym $mod+s layout stacking
bindsym $mod+w layout tabbed
bindsym $mod+e layout toggle split
bindsym $mod+f fullscreen
bindsym $mod+Shift+space floating toggle

# Focus
bindsym $mod+Left focus left
bindsym $mod+Down focus down
bindsym $mod+Up focus up
bindsym $mod+Right focus right

# Resize
bindsym $mod+r mode "resize"
mode "resize" {
    bindsym Left resize shrink width 10px
    bindsym Down resize grow height 10px
    bindsym Up resize shrink height 10px
    bindsym Right resize grow width 10px
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

# Wallpaper
output * bg ~/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png fill

# Idle
exec swayidle -w \
    timeout 300 'swaylock -f -c 0a0a0a' \
    timeout 600 'swaymsg "output * power off"' \
    resume 'swaymsg "output * power on"' \
    before-sleep 'swaylock -f -c 0a0a0a'
SWAYCONFIG

# Install i3 config (alternative)
cat > ~/.config/i3/config << 'I3CONFIG'
# Sanctum OS i3 Configuration
# X11 alternative to Sway

set $mod Mod4
set $term kitty
set $menu dmenu_run -fn "Fira Code Nerd Font-11" -nb "#0a0a0a" -nf "#d4c4a8" -sb "#8b0000" -sf "#ffffff"

# Font
font pango:Fira Code Nerd Font 11

# Window style
default_border pixel 2
default_floating_border normal
hide_edge_borders none

# Colors - Sanctum Theme
client.focused          #8b0000 #0a0a0a #d4c4a8 #b8860b
client.focused_inactive #333333 #0a0a0a #888888 #292929
client.unfocused        #333333 #0a0a0a #555555 #292929
client.urgent           #8b0000 #0a0a0a #ffffff #900000

# Gaps
gaps inner 8
gaps outer 4

# Startup
exec_always --no-startup-id ~/.local/bin/sanctum-quote
exec --no-startup-id feh --bg-scale ~/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png

# Key bindings
bindsym $mod+Return exec $term
bindsym $mod+d exec $menu
bindsym $mod+q kill
bindsym $mod+Shift+e exec "i3-nagbar -t warning -m 'Exit i3?' -B 'Yes' 'i3-msg exit'"

# Workspaces (Biblical naming)
bindsym $mod+1 workspace "1: Genesis"
bindsym $mod+2 workspace "2: Exodus"
bindsym $mod+3 workspace "3: Leviticus"
bindsym $mod+4 workspace "4: Numbers"
bindsym $mod+5 workspace "5: Deuteronomy"
bindsym $mod+6 workspace "6: Psalms"
bindsym $mod+7 workspace "7: Proverbs"
bindsym $mod+8 workspace "8: Gospels"
bindsym $mod+9 workspace "9: Revelation"

# Move windows
bindsym $mod+Shift+1 move container to workspace "1: Genesis"
bindsym $mod+Shift+2 move container to workspace "2: Exodus"
bindsym $mod+Shift+3 move container to workspace "3: Leviticus"
bindsym $mod+Shift+4 move container to workspace "4: Numbers"
bindsym $mod+Shift+5 move container to workspace "5: Deuteronomy"
bindsym $mod+Shift+6 move container to workspace "6: Psalms"
bindsym $mod+Shift+7 move container to workspace "7: Proverbs"
bindsym $mod+Shift+8 move container to workspace "8: Gospels"
bindsym $mod+Shift+9 move container to workspace "9: Revelation"

# Layout
bindsym $mod+b splith
bindsym $mod+v splitv
bindsym $mod+s layout stacking
bindsym $mod+w layout tabbed
bindsym $mod+e layout toggle split
bindsym $mod+f fullscreen
bindsym $mod+Shift+space floating toggle

# Focus
bindsym $mod+Left focus left
bindsym $mod+Down focus down
bindsym $mod+Up focus up
bindsym $mod+Right focus right

# Resize
bindsym $mod+r mode "resize"
mode "resize" {
    bindsym Left resize shrink width 10 px or 10 ppt
    bindsym Down resize grow height 10 px or 10 ppt
    bindsym Up resize shrink height 10 px or 10 ppt
    bindsym Right resize grow width 10 px or 10 ppt
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

# Custom scripts
bindsym $mod+Shift+b exec kitty -e ~/.local/bin/biblia
bindsym $mod+Shift+p exec kitty -e ~/.local/bin/patres
I3CONFIG

# Install scripts
echo -e "${SILVER}[*] Installing CLI tools...${RESET}"
cp "$SOURCE_DIR/scripts/biblia" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/patres" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-quote" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-help" ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true

# Extract theology database
echo -e "${SILVER}[*] Extracting theological library...${RESET}"
if [ -f "$SOURCE_DIR/theology-db/extract_embedded.py" ]; then
    python3 "$SOURCE_DIR/theology-db/extract_embedded.py" 2>/dev/null || echo -e "${GOLD}[!] DB extraction skipped${RESET}"
fi

# Install wallpapers
echo -e "${SILVER}[*] Installing wallpapers...${RESET}"
cp "$SOURCE_DIR/wallpapers/"*.png ~/.local/share/wallpapers/sanctum-os/ 2>/dev/null || true

# Update wallpaper path in sway config
sed -i "s|bg .* fill|bg $HOME/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png fill|" ~/.config/sway/config 2>/dev/null || true

# PATH setup
if ! grep -q "\.local/bin" ~/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi
if ! grep -q "\.local/bin" ~/.zshrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# Cleanup
if [ "$LOCAL_INSTALL" = false ]; then
    rm -rf "$SOURCE_DIR" 2>/dev/null || true
fi

# Final message
echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║                  SANCTUM OS INSTALLED                             ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║           HOW TO START SANCTUM OS                                  ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${SILVER}From a TTY (not from a terminal window):${RESET}"
echo ""
echo -e "  ${RED}1.${RESET} Log out of your current session"
echo -e "  ${RED}2.${RESET} Press ${GOLD}Ctrl+Alt+F3${RESET} to open a TTY"
echo -e "  ${RED}3.${RESET} Login with your username and password"
echo -e "  ${RED}4.${RESET} Run one of these commands:"
echo ""
echo -e "     ${GOLD}sway${RESET}    # Wayland (recommended)"
echo -e "     ${GOLD}i3${RESET}      # X11 (fallback)"
echo ""
echo -e "${SILVER}Note: 'exec sway' only works in your ~/.bash_profile or ~/.zshrc${RESET}"
echo -e "${SILVER}      to auto-start on login. Not from an interactive terminal.${RESET}"
echo ""
echo -e "${SILVER}Commands:${RESET}"
echo -e "  ${GOLD}biblia${RESET} - Read the Bible (47,787 verses)"
echo -e "  ${GOLD}patres${RESET} - Read the Church Fathers"
echo -e "  ${GOLD}sanctum-quote${RESET} - Daily theological quote"
echo ""
echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""
