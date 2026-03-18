#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUM OS - COMPLETE ONE-SHOT INSTALLER
# Handles: fresh installs, no user, broken repos, package installation, rice setup
# curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
GREEN='\033[38;5;28m'
RESET='\033[0m'

# Check if root
if [ "$EUID" -eq 0 ]; then
    IS_ROOT=true
else
    IS_ROOT=false
fi

clear
echo -e "${RED}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███╗        ║
║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║        ║
║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║        ║
║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██║╚██╔╝██║        ║
║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║        ║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"
echo -e "${GOLD}Sanctum OS - The Theological Computing Environment${RESET}\n"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: USER SETUP (if root)
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$IS_ROOT" = true ]; then
    echo -e "${GOLD}[!] Running as root${RESET}"
    echo -e "${SILVER}A user account is required to run Sanctum OS${RESET}\n"
    
    # Check for existing users
    EXISTING_USERS=$(awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd | head -5)
    
    if [ -n "$EXISTING_USERS" ]; then
        echo -e "${SILVER}Existing users found:${RESET}"
        echo "$EXISTING_USERS" | while read user; do
            echo -e "  ${GOLD}•${RESET} $user"
        done
        echo ""
        echo -e "${SILVER}Options:${RESET}"
        echo -e "  1) Use existing user (recommended)"
        echo -e "  2) Create new user"
        echo ""
        read -p "Choice [1/2]: " USER_CHOICE
        
        if [ "$USER_CHOICE" = "1" ]; then
            read -p "Username to use: " TARGET_USER
            if ! id "$TARGET_USER" &>/dev/null; then
                echo -e "${RED}[!] User does not exist${RESET}"
                exit 1
            fi
            echo -e "${SILVER}[*] Will install Sanctum OS for user: $TARGET_USER${RESET}"
            echo -e "${SILVER}[*] Run this script again as $TARGET_USER after setup${RESET}"
            echo ""
            read -p "Press Enter to continue with system setup..."
        else
            read -p "Enter new username: " NEW_USER
            read -sp "Enter password: " NEW_PASS
            echo ""
            
            echo -e "${SILVER}[*] Creating user: $NEW_USER${RESET}"
            useradd -m -G wheel,audio,video,input -s /bin/bash "$NEW_USER"
            echo "$NEW_USER:$NEW_PASS" | chpasswd
            echo -e "${GREEN}✓ User created${RESET}"
            TARGET_USER="$NEW_USER"
        fi
    else
        echo -e "${SILVER}No regular users found. Creating one now...${RESET}\n"
        read -p "Enter username: " NEW_USER
        read -sp "Enter password: " NEW_PASS
        echo ""
        
        echo -e "${SILVER}[*] Creating user: $NEW_USER${RESET}"
        useradd -m -G wheel,audio,video,input -s /bin/bash "$NEW_USER"
        echo "$NEW_USER:$NEW_PASS" | chpasswd
        
        # Enable sudo
        echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/wheel
        chmod 440 /etc/sudoers.d/wheel
        
        echo -e "${GREEN}✓ User $NEW_USER created with sudo access${RESET}"
        TARGET_USER="$NEW_USER"
        
        echo ""
        echo -e "${GOLD}╔═══════════════════════════════════════════════════════════╗${RESET}"
        echo -e "${GOLD}║  IMPORTANT: INSTALLATION PAUSED                            ║${RESET}"
        echo -e "${GOLD}╚═══════════════════════════════════════════════════════════╝${RESET}"
        echo ""
        echo -e "${SILVER}Next steps:${RESET}"
        echo -e "  1. Exit root:      ${GOLD}exit${RESET}"
        echo -e "  2. Login as:      ${GOLD}$TARGET_USER${RESET}"
        echo -e "  3. Run installer:  ${GOLD}curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash${RESET}"
        echo ""
        exit 0
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: REPOSITORY FIX (EndeavourOS/Arch)
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${SILVER}[*] Checking repositories...${RESET}"

# Check if repos are configured
if ! grep -q "^\[core\]" /etc/pacman.conf 2>/dev/null || ! grep -q "^\[extra\]" /etc/pacman.conf 2>/dev/null; then
    echo -e "${GOLD}[!] Pacman repositories not properly configured${RESET}"
    echo -e "${SILVER}[*] Fixing repository configuration...${RESET}"
    
    # Backup
    sudo cp /etc/pacman.conf /etc/pacman.conf.backup.$(date +%Y%m%d) 2>/dev/null || true
    
    # Fix mirrorlist
    if [ ! -f "/etc/pacman.d/mirrorlist" ] || [ ! -s "/etc/pacman.d/mirrorlist" ]; then
        echo -e "${SILVER}  → Installing reflector and updating mirrors...${RESET}"
        sudo pacman -Sy --noconfirm reflector 2>/dev/null || true
        sudo reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist 2>/dev/null || {
            # Fallback mirrors
            sudo tee /etc/pacman.d/mirrorlist > /dev/null << 'MIRRORLIST'
Server = https://archlinux.mirror.rafal.ca/$repo/os/$arch
Server = https://mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch
MIRRORLIST
        }
    fi
    
    # Enable repos
    sudo sed -i 's/^#\[core\]/[core]/' /etc/pacman.conf
    sudo sed -i 's/^#\[extra\]/[extra]/' /etc/pacman.conf
    sudo sed -i 's/^#\[community\]/[community]/' /etc/pacman.conf
    sudo sed -i '/^\[core\]/,/^\[/ { /^#Include/s/^#// }' /etc/pacman.conf
    sudo sed -i '/^\[extra\]/,/^\[/ { /^#Include/s/^#// }' /etc/pacman.conf
    
    echo -e "${GREEN}✓ Repositories configured${RESET}"
fi

# Update package database
echo -e "${SILVER}[*] Updating package database...${RESET}"
sudo pacman -Sy --noconfirm 2>/dev/null || {
    echo -e "${RED}[!] Failed to update packages. Check your internet connection.${RESET}"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: PACKAGE INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${SILVER}[*] Installing packages...${RESET}"

# Install yay if not present (needed for AUR)
if ! command -v yay &>/dev/null && ! command -v paru &>/dev/null; then
    echo -e "${SILVER}[*] Installing yay (AUR helper)...${RESET}"
    
    # Install base-devel and git
    sudo pacman -S --needed --noconfirm base-devel git 2>/dev/null || true
    
    # Build yay in /tmp
    cd /tmp
    git clone https://aur.archlinux.org/yay.git 2>/dev/null || true
    if [ -d "yay" ]; then
        cd yay
        makepkg -si --noconfirm 2>/dev/null || {
            echo -e "${GOLD}[!] yay build failed, continuing without AUR${RESET}"
        }
    fi
    cd ~
fi

# Core packages (official repos)
PACKAGES="sway swaylock swayidle waybar wofi kitty foot fastfetch neofetch zsh python sqlite"

echo -e "${SILVER}[*] Installing core packages...${RESET}"
for pkg in $PACKAGES; do
    if ! pacman -Q "$pkg" &>/dev/null; then
        echo -e "${SILVER}  → Installing $pkg...${RESET}"
        sudo pacman -S --noconfirm "$pkg" 2>/dev/null || {
            echo -e "${GOLD}    ! $pkg failed${RESET}"
        }
    else
        echo -e "${GREEN}  ✓ $pkg already installed${RESET}"
    fi
done

# AUR packages (starship prompt)
if command -v yay &>/dev/null; then
    echo -e "${SILVER}[*] Installing AUR packages...${RESET}"
    yay -S --needed --noconfirm starship 2>/dev/null || {
        echo -e "${GOLD}[!] starship failed (optional)${RESET}"
    }
fi

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: DOWNLOAD SANCTUM OS RICE
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${SILVER}[*] Downloading Sanctum OS...${RESET}"

SANCTUM_DIR="$HOME/.sanctum-install"
mkdir -p "$SANCTUM_DIR"
cd "$SANCTUM_DIR"

# Download latest
REPO_URL="https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz"
if command -v curl &>/dev/null; then
    curl -fsSL "$REPO_URL" -o sanctum-os.tar.gz
elif command -v wget &>/dev/null; then
    wget -q "$REPO_URL" -O sanctum-os.tar.gz
else
    echo -e "${RED}[!] Need curl or wget to download${RESET}"
    exit 1
fi

# Extract
tar -xzf sanctum-os.tar.gz
SOURCE_DIR="$(find . -maxdepth 1 -type d -name 'sanctum-os*' | head -1)"
cd ~

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5: INSTALL RICE
# ═══════════════════════════════════════════════════════════════════════════════

echo -e "${SILVER}[*] Installing Sanctum OS configurations...${RESET}"

# Create directories
mkdir -p ~/.config/{sway,waybar,wofi,kitty,fastfetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers/sanctum-os}

# Install configs
cp "$SANCTUM_DIR/$SOURCE_DIR/config/sway/sway.config" ~/.config/sway/config 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/waybar/config" ~/.config/waybar/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/waybar/style.css" ~/.config/waybar/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/wofi/config" ~/.config/wofi/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/wofi/sanctum.css" ~/.config/wofi/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/kitty/kitty.conf" ~/.config/kitty/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/config/fastfetch/config.jsonc" ~/.config/fastfetch/ 2>/dev/null || true

# Install scripts
cp "$SANCTUM_DIR/$SOURCE_DIR/scripts/biblia" ~/.local/bin/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/scripts/patres" ~/.local/bin/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/scripts/sanctum-quote" ~/.local/bin/ 2>/dev/null || true
cp "$SANCTUM_DIR/$SOURCE_DIR/scripts/sanctum-help" ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/*

# Extract theology database
echo -e "${SILVER}[*] Extracting theological library (47,787 verses)...${RESET}"
if [ -f "$SANCTUM_DIR/$SOURCE_DIR/theology-db/extract_embedded.py" ]; then
    python3 "$SANCTUM_DIR/$SOURCE_DIR/theology-db/extract_embedded.py" 2>/dev/null || {
        echo -e "${GOLD}[!] Database extraction failed${RESET}"
    }
else
    echo -e "${GOLD}[!] Database files not found${RESET}"
fi

# Install wallpapers
cp "$SANCTUM_DIR/$SOURCE_DIR/wallpapers/"*.png ~/.local/share/wallpapers/sanctum-os/ 2>/dev/null || true

# Add to PATH
if ! grep -q "$HOME/.local/bin" ~/.bashrc 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════════════════════

clear
echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║           SANCTUM OS INSTALLATION COMPLETE                        ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${SILVER}Theological Library:${RESET}"
echo -e "  ${GOLD}biblia${RESET}      - Search and read the Bible (47,787 verses)"
echo -e "  ${GOLD}patres${RESET}      - Read the Church Fathers"
echo -e "  ${GOLD}sanctum-quote${RESET} - Daily theological quote"
echo ""
echo -e "${SILVER}Commands:${RESET}"
echo -e "  ${GOLD}sway${RESET}        - Start Sanctum OS (Wayland)"
echo -e "  ${GOLD}sanctum-help${RESET} - Show help and keybindings"
echo ""
echo -e "${SILVER}First time setup:${RESET}"
echo -e "  1. ${GOLD}Logout${RESET} (exit your current session)"
echo -e "  2. Press ${GOLD}Ctrl+Alt+F3${RESET} to switch to TTY"
echo -e "  3. Login and type: ${GOLD}sway${RESET}"
echo ""
echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""

# Cleanup
rm -rf "$SANCTUM_DIR" 2>/dev/null || true

exit 0
