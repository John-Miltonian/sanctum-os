#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SANCTUM OS - COMPLETE ONE-SHOT INSTALLER
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
║    ███████╗ █████╗ ███╗   ██╗ ██████╗████████╗██╗   ██╗███╗   ███║        ║
║    ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██║   ██║████╗ ████║        ║
║    ███████╗███████║██╔██╗ ██║██║        ██║   ██║   ██║██╔████╔██║        ║
║    ╚════██║██╔══██║██║╚██╗██║██║        ██║   ██║   ██║██║╚██╔╝██║        ║
║    ███████║██║  ██║██║ ╚████║╚██████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║        ║
║    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"
echo -e "${GOLD}Sanctum OS - The Theological Computing Environment${RESET}\n"

# Check internet with multiple methods
echo -e "${SILVER}[*] Checking internet connection...${RESET}"
INTERNET=false
if curl -fsSL https://google.com > /dev/null 2>&1; then
    INTERNET=true
elif curl -fsSL https://github.com > /dev/null 2>&1; then
    INTERNET=true
elif ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    INTERNET=true
fi

if [ "$INTERNET" = false ]; then
    echo -e "${RED}[!] No internet connection detected${RESET}"
    echo -e "${SILVER}Please connect to the internet and try again.${RESET}"
    exit 1
fi
echo -e "${GREEN}✓ Internet connection confirmed${RESET}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${GOLD}[!] Running as root${RESET}"
    echo -e "${SILVER}Checking for existing users...${RESET}"
    
    EXISTING_USERS=$(awk -F: '$3 >= 1000 && $3 < 65534 {print $1}' /etc/passwd)
    if [ -z "$EXISTING_USERS" ]; then
        echo -e "${SILVER}No regular users found. Creating one now...${RESET}"
        read -p "Enter username: " NEW_USER
        read -sp "Enter password: " NEW_PASS
        echo ""
        useradd -m -G wheel,audio,video,input -s /bin/bash "$NEW_USER"
        echo "$NEW_USER:$NEW_PASS" | chpasswd
        echo "%wheel ALL=(ALL) ALL" > /etc/sudoers.d/wheel
        chmod 440 /etc/sudoers.d/wheel
        echo -e "${GREEN}✓ User $NEW_USER created${RESET}"
        echo ""
        echo -e "${GOLD}Exit root (type: exit) then login as $NEW_USER and run installer again${RESET}"
        exit 0
    else
        echo -e "${SILVER}Existing users: $EXISTING_USERS${RESET}"
        echo -e "${GOLD}Exit root (type: exit) then login as one of these users${RESET}"
        exit 0
    fi
fi

# Check Arch-based system
if [ ! -f "/etc/arch-release" ] && [ ! -f "/etc/endeavouros-release" ]; then
    echo -e "${GOLD}[!] This installer is for Arch Linux based systems${RESET}"
    exit 1
fi

# Fix broken repositories
echo -e "${SILVER}[*] Checking repositories...${RESET}"
if ! grep -q "^Include = /etc/pacman.d/mirrorlist" /etc/pacman.conf 2>/dev/null; then
    echo -e "${GOLD}[!] Repository configuration needs fixing${RESET}"
    sudo cp /etc/pacman.conf /etc/pacman.conf.backup.$(date +%s) 2>/dev/null || true
    sudo tee /etc/pacman.conf > /dev/null << 'PACMANCONF'
[options]
HoldPkg     = pacman glibc
Architecture = auto

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist
PACMANCONF
    echo -e "${GREEN}✓ Repository config fixed${RESET}"
fi

# Update mirrors
echo -e "${SILVER}[*] Updating mirror list...${RESET}"
sudo pacman -Sy --noconfirm reflector 2>/dev/null || true
if command -v reflector &>/dev/null; then
    sudo reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist 2>/dev/null || true
else
    sudo tee /etc/pacman.d/mirrorlist > /dev/null << 'MIRRORS'
Server = https://archlinux.mirror.rafal.ca/$repo/os/$arch
Server = https://mirror.pkgbuild.com/$repo/os/$arch
Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch
MIRRORS
fi
echo -e "${GREEN}✓ Mirrors updated${RESET}"

# Update package database
echo -e "${SILVER}[*] Updating package database...${RESET}"
sudo pacman -Syu --noconfirm || {
    echo -e "${RED}[!] Failed to update packages${RESET}"
    echo -e "${SILVER}This might be a repository issue, not internet${RESET}"
    exit 1
}
echo -e "${GREEN}✓ Package database updated${RESET}"

# Install packages
PACKAGES="sway swaylock swayidle waybar wofi kitty foot fastfetch neofetch zsh python sqlite git base-devel"
echo -e "${SILVER}[*] Installing packages...${RESET}"
for pkg in $PACKAGES; do
    sudo pacman -S --needed --noconfirm "$pkg" 2>/dev/null || echo -e "${GOLD}  ! $pkg skipped${RESET}"
done
echo -e "${GREEN}✓ Packages installed${RESET}"

# Download Sanctum OS rice
echo -e "${SILVER}[*] Downloading Sanctum OS...${RESET}"
SANCTUM_DIR="$HOME/.sanctum-install"
mkdir -p "$SANCTUM_DIR"
cd "$SANCTUM_DIR"
curl -fsSL "https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz" -o sanctum-os.tar.gz
tar -xzf sanctum-os.tar.gz
SOURCE_DIR="$SANCTUM_DIR/sanctum-os-main"
echo -e "${GREEN}✓ Downloaded${RESET}"

# Install configs
echo -e "${SILVER}[*] Installing rice...${RESET}"
mkdir -p ~/.config/{sway,waybar,wofi,kitty,fastfetch,neofesh}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers}
cp "$SOURCE_DIR/config/sway/sway.config" ~/.config/sway/config 2>/dev/null || true
cp "$SOURCE_DIR/config/waybar/"* ~/.config/waybar/ 2>/dev/null || true
cp "$SOURCE_DIR/config/wofi/"* ~/.config/wofi/ 2>/dev/null || true
cp "$SOURCE_DIR/config/kitty/kitty.conf" ~/.config/kitty/ 2>/dev/null || true
cp "$SOURCE_DIR/config/fastfetch/config.jsonc" ~/.config/fastfetch/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/"* ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true
echo -e "${GREEN}✓ Rice installed${RESET}"

# Extract theology database
echo -e "${SILVER}[*] Extracting theological library...${RESET}"
python3 "$SOURCE_DIR/theology-db/extract_embedded.py" 2>/dev/null || echo -e "${GOLD}  ! Database extraction skipped${RESET}"
echo -e "${GREEN}✓ Library ready${RESET}"

# Add to PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║                    INSTALLATION COMPLETE                          ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${SILVER}To start Sanctum OS:${RESET}"
echo -e "  1. Press ${GOLD}Ctrl+Alt+F3${RESET} to switch to a text console"
echo -e "  2. Login with your username/password"
echo -e "  3. Type: ${GOLD}sway${RESET}"
echo ""
echo -e "${SILVER}Commands available:${RESET}"
echo -e "  ${GOLD}biblia${RESET} - Read the Bible"
echo -e "  ${GOLD}patres${RESET} - Read Church Fathers"
echo -e "  ${GOLD}sanctum-quote${RESET} - Daily quote"
echo ""
echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""
rm -rf "$SANCTUM_DIR" 2>/dev/null || true
exit 0
