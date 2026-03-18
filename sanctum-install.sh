#!/bin/bash
# Sanctum OS One-Shot Installer
# Works on Arch Linux, EndeavourOS, and derivatives

set -e

# Colors
RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
RESET='\033[0m'

# GitHub username
GITHUB_USER="John-Miltonian"
REPO_NAME="sanctum-os"

echo -e "${RED}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║           SANCTUM OS - The Theological Computing Environment      ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"

# Detect install method
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/theology-db/theology_data_embedded.py" ]; then
    echo -e "${SILVER}[*] Local install detected${RESET}"
    SOURCE_DIR="$SCRIPT_DIR"
    LOCAL_INSTALL=true
else
    echo -e "${SILVER}[*] Remote install - downloading...${RESET}"
    LOCAL_INSTALL=false
    SOURCE_DIR="$HOME/.sanctum-install"
    rm -rf "$SOURCE_DIR" 2>/dev/null || true
    
    # Try git clone first, fallback to curl
    if command -v git &>/dev/null; then
        git clone --depth 1 "https://github.com/${GITHUB_USER}/${REPO_NAME}.git" "$SOURCE_DIR" 2>/dev/null || {
            echo -e "${RED}[!] Failed to clone repository${RESET}"
            exit 1
        }
    else
        mkdir -p "$SOURCE_DIR"
        curl -fsSL "https://github.com/${GITHUB_USER}/${REPO_NAME}/archive/refs/heads/main.tar.gz" | tar -xz -C "$SOURCE_DIR" --strip-components=1 2>/dev/null || {
            echo -e "${RED}[!] Failed to download${RESET}"
            exit 1
        }
    fi
fi

# Detect distribution
if [ -f "/etc/arch-release" ] || [ -f "/etc/endeavouros-release" ]; then
    echo -e "${SILVER}[*] Arch-based distribution detected${RESET}"
    INSTALL_PACKAGES=true
else
    echo -e "${GOLD}[!] Non-Arch distribution detected${RESET}"
    echo -e "${SILVER}    Package installation will be skipped${RESET}"
    echo -e "${SILVER}    Install these manually: kitty, waybar, wofi, hyprland, starship${RESET}"
    INSTALL_PACKAGES=false
fi

# Install packages if on Arch/EndeavourOS
if [ "$INSTALL_PACKAGES" = true ]; then
    echo -e "${SILVER}[*] Installing packages...${RESET}"
    
    # Official repo packages
    PACMAN_PKGS="kitty waybar wofi hyprland fastfetch neofetch zsh bash-completion sqlite python tk"
    
    # AUR packages (optional but recommended)
    AUR_PKGS="starship"
    
    # Check if running as root or with sudo
    if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
        echo -e "${SILVER}  → Installing official packages...${RESET}"
        sudo pacman -Sy --needed --noconfirm $PACMAN_PKGS 2>/dev/null || {
            echo -e "${GOLD}[!] Some packages may need manual installation${RESET}"
        }
        
        # Try to install AUR packages
        if command -v yay &>/dev/null; then
            echo -e "${SILVER}  → Installing AUR packages with yay...${RESET}"
            yay -S --needed --noconfirm $AUR_PKGS 2>/dev/null || true
        elif command -v paru &>/dev/null; then
            echo -e "${SILVER}  → Installing AUR packages with paru...${RESET}"
            paru -S --needed --noconfirm $AUR_PKGS 2>/dev/null || true
        else
            echo -e "${GOLD}[!] AUR helper not found. Install yay or paru for:${RESET}"
            echo -e "${SILVER}    $AUR_PKGS${RESET}"
        fi
    else
        echo -e "${GOLD}[!] Skipping package installation (no sudo access)${RESET}"
        echo -e "${SILVER}    Required packages: $PACMAN_PKGS${RESET}"
        echo -e "${SILVER}    AUR packages: $AUR_PKGS${RESET}"
    fi
fi

# Create directories
echo -e "${SILVER}[*] Setting up directories...${RESET}"
mkdir -p ~/.config/{kitty,hypr,waybar,wofi,fastfetch,neofetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers/sanctum-os}

# Copy configs
echo -e "${SILVER}[*] Installing configurations...${RESET}"
cp "$SOURCE_DIR/config/kitty/kitty.conf" ~/.config/kitty/ 2>/dev/null || true
cp "$SOURCE_DIR/config/hypr/hyprland.conf" ~/.config/hypr/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/config" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/style.css" ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/config" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/sanctum.css" ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/fastfetch/config.jsonc" ~/.config/fastfetch/ 2>/dev/null || true
cp "$SOURCE_DIR/config/neofetch/config.conf" ~/.config/neofetch/ 2>/dev/null || true

# Install scripts
echo -e "${SILVER}[*] Installing CLI tools...${RESET}"
cp "$SOURCE_DIR/scripts/biblia" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/patres" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-quote" ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/sanctum-help" ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true

# Install wallpapers
echo -e "${SILVER}[*] Installing wallpapers...${RESET}"
cp "$SOURCE_DIR/wallpapers/"*.png ~/.local/share/wallpapers/sanctum-os/ 2>/dev/null || true

# Extract theology database
echo -e "${SILVER}[*] Extracting theological library...${RESET}"
if [ -f "$SOURCE_DIR/theology-db/extract_embedded.py" ]; then
    python3 "$SOURCE_DIR/theology-db/extract_embedded.py" 2>/dev/null || {
        echo -e "${GOLD}[!] Database extraction failed${RESET}"
    }
else
    echo -e "${GOLD}[!] Database extractor not found${RESET}"
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# Set kitty as default terminal if available
if command -v kitty &>/dev/null; then
    export TERMINAL=kitty
fi

echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║                  INSTALLATION COMPLETE                            ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${SILVER}Commands available:${RESET}"
echo -e "  ${GOLD}biblia${RESET} - Search and read the Bible (47,787 verses)"
echo -e "  ${GOLD}patres${RESET} - Read the Church Fathers"
echo -e "  ${GOLD}sanctum-quote${RESET} - Display daily theological quotes"
echo -e "  ${GOLD}sanctum-help${RESET} - Show help and information"
echo ""
echo -e "${SILVER}Keybindings (Hyprland):${RESET}"
echo -e "  ${GOLD}Super+Enter${RESET} - Open terminal"
echo -e "  ${GOLD}Super+D${RESET} - Open launcher (wofi)"
echo -e "  ${GOLD}Super+Q${RESET} - Close window"
echo -e "  ${GOLD}Super+1-9${RESET} - Switch workspace (Genesis-Revelation)"
echo ""
echo -e "${SILVER}To start Hyprland:${RESET} ${GOLD}exec Hyprland${RESET}"
echo ""
echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""

# Cleanup if remote install
if [ "$LOCAL_INSTALL" = false ]; then
    rm -rf "$SOURCE_DIR" 2>/dev/null || true
fi

exit 0
