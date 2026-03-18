#!/bin/bash
# Sanctum OS One-Shot Installer
set -e

RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
RESET='\033[0m'

echo -e "${RED}"
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    SANCTUM OS - The Theological Computing Environment          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

REPO_URL="https://github.com/John-Miltonian/sanctum-os"
TEMP_DIR=$(mktemp -d)
INSTALL_DIR="$HOME/.sanctum-os"

echo -e "${SILVER}[*] Installing Sanctum OS...${RESET}"

# Detect local vs remote install
if [ -f "./theology-db/theology_data_embedded.py" ]; then
    echo -e "${SILVER}[*] Local install detected${RESET}"
    SOURCE_DIR="$(pwd)"
else
    echo -e "${SILVER}[*] Downloading from GitHub...${RESET}"
    cd "$TEMP_DIR"
    
    if command -v git &> /dev/null; then
        git clone --depth 1 "$REPO_URL.git" sanctum-os
        SOURCE_DIR="$TEMP_DIR/sanctum-os"
    elif command -v curl &> /dev/null; then
        curl -fsSL "$REPO_URL/archive/refs/heads/main.tar.gz" -o so.tar.gz
        tar -xzf so.tar.gz
        SOURCE_DIR="$(find . -maxdepth 1 -type d -name 'sanctum-os*' | head -1)"
    else
        echo -e "${RED}[!] Need git or curl installed first${RESET}"
        exit 1
    fi
fi

# Create directories
mkdir -p ~/.config/{kitty,waybar,wofi,hypr,fastfetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers}
mkdir -p ~/.local/share/applications

# Copy configs
echo -e "${SILVER}[*] Installing configurations...${RESET}"
cp "$SOURCE_DIR/config/kitty/kitty.conf" ~/.config/kitty/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/config" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/style.css" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/config" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/sanctum.css" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/hypr/hyprland.conf" ~/.config/hypr/ 2>/dev/null || true
cp "$SOURCE_DIR/config/fastfetch/config.jsonc" ~/.config/fastfetch/ 2>/dev/null || true

# Copy scripts
echo -e "${SILVER}[*] Installing CLI tools...${RESET}"
cp "$SOURCE_DIR/scripts/biblia" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/patres" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-quote" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-help" ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/{biblia,patres,sanctum-quote,sanctum-help} 2>/dev/null || true

# Extract theology database
echo -e "${SILVER}[*] Extracting theological library (47,787 verses)...${RESET}"
cd ~/.local/share/theology
python3 "$SOURCE_DIR/theology-db/theology_data_embedded.py" 2>/dev/null || {
    echo -e "${RED}[!] Database extraction failed${RESET}"
    echo -e "${SILVER}    Run: python3 ~/.local/share/theology/theology_data_embedded.py${RESET}"
}

# Copy wallpapers
cp "$SOURCE_DIR/wallpapers"/*.png ~/.local/share/wallpapers/ 2>/dev/null || true

# Add to PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# Install packages if on Arch
if [ -f "/etc/arch-release" ]; then
    echo -e "${SILVER}[*] Installing packages (may require sudo)...${RESET}"
    sudo pacman -S --needed --noconfirm kitty waybar wofi hyprland fastfetch starship zsh sqlite python 2>/dev/null || {
        echo -e "${SILVER}    Install manually: sudo pacman -S kitty waybar wofi hyprland fastfetch starship zsh sqlite python${RESET}"
    }
fi

echo -e "${GOLD}"
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                           INSTALLATION COMPLETE                                ║"
echo "║                                                                                ║"
echo "║   Commands:  biblia John 3:16    - Read Bible verses                           ║"
echo "║              patres --random     - Church Fathers quotes                       ║"
echo "║              sanctum-help        - Full help                                   ║"
echo "║                                                                                ║"
echo "║   Start Hyprland:  exec Hyprland                                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# Cleanup
rm -rf "$TEMP_DIR"

# Start Hyprland if available and not in TTY
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ] && command -v Hyprland &> /dev/null; then
    echo -e "${SILVER}Starting Hyprland...${RESET}"
    exec Hyprland
fi

exit 0
