#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUM OS - ONE-SHOT INSTALLER
# curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
RESET='\033[0m'

# Configuration
REPO_URL="${SANCTUM_REPO:-https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz}"
TEMP_DIR=$(mktemp -d)
SANCTUM_DIR="$HOME/.sanctum-install"

# Banner
echo -e "${RED}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███╗            ║
║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║            ║
║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║            ║
║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██║╚██╔╝██║            ║
║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║            ║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"
echo -e "${GOLD}Sanctum OS v1.0 - The Theological Computing Environment${RESET}\n"

# Detect if running from local directory
if [ -f "./install/install.sh" ] && [ -d "./theology-db" ]; then
    echo -e "${SILVER}[*] Running from local directory...${RESET}"
    SANCTUM_DIR="$(pwd)"
    LOCAL_INSTALL=true
else
    LOCAL_INSTALL=false
fi

# Pre-flight checks
echo -e "${SILVER}[*] Pre-flight checks...${RESET}"

# Check for Arch Linux
if [ ! -f "/etc/arch-release" ]; then
    echo -e "${RED}[!] Warning: This rice is designed for Arch Linux${RESET}"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for internet (if not local)
if [ "$LOCAL_INSTALL" = false ]; then
    if ! ping -c 1 archlinux.org &> /dev/null; then
        echo -e "${RED}[!] No internet connection detected${RESET}"
        echo -e "${SILVER}    Download the rice locally and run from the directory${RESET}"
        exit 1
    fi
fi

# Create backup function
backup_config() {
    local config_path="$1"
    if [ -e "$config_path" ] && [ ! -L "$config_path" ]; then
        local backup_name="${config_path}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${SILVER}    Backing up ${config_path} → ${backup_name}${RESET}"
        mv "$config_path" "$backup_name"
    fi
}

# Download rice if not local
if [ "$LOCAL_INSTALL" = false ]; then
    echo -e "${SILVER}[*] Downloading Sanctum OS...${RESET}"
    cd "$TEMP_DIR"
    
    # Try to download, fall back to local if available
    if command -v curl &> /dev/null; then
        curl -fsSL "$REPO_URL" -o sanctum-os.tar.gz 2>/dev/null || {
            echo -e "${RED}[!] Could not download. Please run from local directory.${RESET}"
            exit 1
        }
    elif command -v wget &> /dev/null; then
        wget -q "$REPO_URL" -O sanctum-os.tar.gz 2>/dev/null || {
            echo -e "${RED}[!] Could not download. Please run from local directory.${RESET}"
            exit 1
        }
    else
        echo -e "${RED}[!] Neither curl nor wget found${RESET}"
        exit 1
    fi
    
    tar -xzf sanctum-os.tar.gz
    SANCTUM_DIR="$(find . -maxdepth 1 -type d -name 'sanctum-os*' | head -1)"
fi

cd "$SANCTUM_DIR"

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALL PACKAGES
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Installing packages...${RESET}"

# Core packages for Hyprland/Sway rice
PACKAGES=(
    # Window managers
    hyprland waybar wofi
    # Terminal
    kitty
    # System tools
    fastfetch neofetch
    # Fonts
    ttf-jetbrains-mono-nerd noto-fonts noto-fonts-cjk noto-fonts-emoji
    # Audio
    pipewire pipewire-pulse wireplumber pamixer
    # Brightness
    brightnessctl
    # File manager
    nautilus
    # Browser
    firefox
    # Editor
    neovim
    # Utilities
    wl-clipboard grim slurp mako libnotify
    # Database
    sqlite
    # Python
    python python-pip
)

# Install packages
if command -v pacman &> /dev/null; then
    echo -e "${SILVER}    Updating package database...${RESET}"
    sudo pacman -Sy --noconfirm 2>/dev/null || true
    
    for pkg in "${PACKAGES[@]}"; do
        if ! pacman -Q "$pkg" &> /dev/null; then
            echo -e "${SILVER}    Installing ${pkg}...${RESET}"
            sudo pacman -S --noconfirm "$pkg" 2>/dev/null || {
                echo -e "${GOLD}    Note: ${pkg} not in official repos, may need AUR${RESET}"
            }
        fi
    done
fi

# Install yay if not present and needed packages from AUR
AUR_PACKAGES=(
    ttf-jetbrains-mono-nerd
)

if ! command -v yay &> /dev/null; then
    echo -e "${SILVER}[*] Installing yay (AUR helper)...${RESET}"
    cd /tmp
    git clone https://aur.archlinux.org/yay.git 2>/dev/null || true
    cd yay 2>/dev/null && makepkg -si --noconfirm 2>/dev/null || true
    cd "$SANCTUM_DIR"
fi

if command -v yay &> /dev/null; then
    for pkg in "${AUR_PACKAGES[@]}"; do
        if ! pacman -Q "$pkg" &> /dev/null; then
            echo -e "${SILVER}    Installing ${pkg} from AUR...${RESET}"
            yay -S --noconfirm "$pkg" 2>/dev/null || true
        fi
    done
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP DIRECTORIES
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Creating directories...${RESET}"

mkdir -p ~/.config/{hypr,kitty,waybar,wofi,fastfetch,neofetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers/sanctum-os}
mkdir -p ~/.local/share/applications

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACT THEOLOGY DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Extracting theological database...${RESET}"

if [ -f "theology-db/extract_theology.py" ]; then
    cp theology-db/extract_theology.py ~/.local/share/theology/
    cp theology-db/extract_lsv_bible.py ~/.local/share/theology/ 2>/dev/null || true
    cp theology-db/extract_fathers.py ~/.local/share/theology/ 2>/dev/null || true
    cd ~/.local/share/theology
    python3 extract_theology.py 2>/dev/null || {
        echo -e "${GOLD}    Note: Using sample database${RESET}"
    }
    cd "$SANCTUM_DIR"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALL CLI SCRIPTS
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Installing CLI tools...${RESET}"

if [ -d "scripts" ]; then
    cp scripts/biblia ~/.local/bin/
    cp scripts/patres ~/.local/bin/
    cp scripts/sanctum-quote ~/.local/bin/
    cp scripts/sanctum-theme ~/.local/bin/
    cp scripts/sanctum-help ~/.local/bin/
    chmod +x ~/.local/bin/{biblia,patres,sanctum-quote,sanctum-theme,sanctum-help}
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# ═══════════════════════════════════════════════════════════════════════════════
# DEPLOY CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Deploying configurations...${RESET}"

# Hyprland
if [ -f "config/hypr/hyprland.conf" ]; then
    backup_config ~/.config/hypr
    cp -r config/hypr/* ~/.config/hypr/ 2>/dev/null || true
fi

# Kitty
if [ -f "config/kitty/kitty.conf" ]; then
    backup_config ~/.config/kitty
    cp config/kitty/kitty.conf ~/.config/kitty/
fi

# Waybar
if [ -d "config/waybar" ]; then
    backup_config ~/.config/waybar
    cp config/waybar/* ~/.config/waybar/ 2>/dev/null || true
fi

# Wofi
if [ -d "config/wofi" ]; then
    backup_config ~/.config/wofi
    cp config/wofi/* ~/.config/wofi/ 2>/dev/null || true
fi

# Fastfetch
if [ -f "config/fastfetch/config.jsonc" ]; then
    backup_config ~/.config/fastfetch
    cp config/fastfetch/config.jsonc ~/.config/fastfetch/
fi

# Neofetch (legacy)
if [ -f "config/neofetch/config.conf" ]; then
    backup_config ~/.config/neofetch
    cp config/neofetch/config.conf ~/.config/neofetch/
fi

# ═══════════════════════════════════════════════════════════════════════════════
# WALLPAPERS
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Installing wallpapers...${RESET}"

if [ -d "wallpapers" ]; then
    cp wallpapers/*.png ~/.local/share/wallpapers/sanctum-os/ 2>/dev/null || true
    # Set wallpaper (using swaybg for Wayland)
    if command -v swaybg &> /dev/null; then
        pkill swaybg 2>/dev/null || true
        swaybg -i ~/.local/share/wallpapers/sanctum-os/sanctum-wallpaper-01.png -m fill &
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SHELL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${SILVER}[*] Configuring shell...${RESET}"

# Add Sanctum greeting to shell
if ! grep -q "sanctum-quote" ~/.bashrc 2>/dev/null; then
    echo '' >> ~/.bashrc
    echo '# Sanctum OS greeting' >> ~/.bashrc
    echo 'sanctum-quote 2>/dev/null || true' >> ~/.bashrc
fi

if [ -f ~/.zshrc ] && ! grep -q "sanctum-quote" ~/.zshrc 2>/dev/null; then
    echo '' >> ~/.zshrc
    echo '# Sanctum OS greeting' >> ~/.zshrc
    echo 'sanctum-quote 2>/dev/null || true' >> ~/.zshrc
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════
if [ "$LOCAL_INSTALL" = false ]; then
    echo -e "${SILVER}[*] Cleaning up...${RESET}"
    rm -rf "$TEMP_DIR"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "\n${GOLD}═══════════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GOLD}                        SANCTUM OS INSTALLATION COMPLETE${RESET}"
echo -e "${GOLD}═══════════════════════════════════════════════════════════════════════════${RESET}\n"

echo -e "${SILVER}Installed:${RESET}"
echo -e "  • Theological database: ~/.local/share/theology/theology.db"
echo -e "  • CLI tools: ~/.local/bin/{biblia,patres,sanctum-*}"
echo -e "  • Configs: ~/.config/{hypr,kitty,waybar,wofi,fastfetch}"
echo -e "  • Wallpapers: ~/.local/share/wallpapers/sanctum-os/"

echo -e "\n${SILVER}Commands:${RESET}"
echo -e "  ${GOLD}biblia John 3:16${RESET}        - Read Scripture"
echo -e "  ${GOLD}patres --random${RESET}         - Church Father quote"
echo -e "  ${GOLD}sanctum-help${RESET}            - Show help"

echo -e "\n${SILVER}Keybindings:${RESET}"
echo -e "  ${GOLD}Mod+Return${RESET}  - Terminal"
echo -e "  ${GOLD}Mod+D${RESET}       - Launcher"
echo -e "  ${GOLD}Mod+T${RESET}       - Daily scripture"

echo -e "\n${GOLD}Would you like to start Hyprland now? [y/N]${RESET}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v Hyprland &> /dev/null; then
        echo -e "${SILVER}Starting Hyprland...${RESET}"
        exec Hyprland
    else
        echo -e "${RED}Hyprland not found. Please install it manually.${RESET}"
    fi
fi

echo -e "\n${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo -e "${SILVER}Run 'sanctum-help' for more information.${RESET}\n"
