#!/bin/bash
# Sanctum OS Installer - Fixed for EndeavourOS
set -e

RED='\033[38;5;88m'
GOLD='\033[38;5;178m'
SILVER='\033[38;5;250m'
RESET='\033[0m'

echo -e "${RED}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                     SANCTUM OS v1.0                               ║
║              The Theological Computing Environment                ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${RESET}"

# Detect install source
if [ -f "./install/install.sh" ]; then
    LOCAL_INSTALL=true
    SOURCE_DIR="$(pwd)"
    echo -e "${SILVER}[*] Local installation detected${RESET}"
else
    LOCAL_INSTALL=false
    SOURCE_DIR="$(mktemp -d)/sanctum-os"
    echo -e "${SILVER}[*] Remote installation${RESET}"
    
    # Download
    if command -v git &>/dev/null; then
        git clone --depth 1 https://github.com/John-Miltonian/sanctum-os.git "$SOURCE_DIR"
    else
        curl -fsSL https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz | tar -xz -C "$(dirname $SOURCE_DIR)"
        mv "$(dirname $SOURCE_DIR)/sanctum-os-main" "$SOURCE_DIR"
    fi
fi

# Package installation
echo -e "${SILVER}[*] Installing packages...${RESET}"

# Check for AUR helper
AUR_HELPER=""
if command -v yay &>/dev/null; then
    AUR_HELPER="yay"
elif command -v paru &>/dev/null; then
    AUR_HELPER="paru"
fi

# Install packages with better handling
install_pkg() {
    local pkg="$1"
    if pacman -Qi "$pkg" &>/dev/null; then
        echo -e "${SILVER}  ✓ $pkg already installed${RESET}"
        return 0
    fi
    
    echo -e "${SILVER}  → Installing $pkg...${RESET}"
    
    # Try official repo first
    if sudo pacman -S --needed --noconfirm "$pkg" 2>/dev/null; then
        return 0
    fi
    
    # Try AUR if available
    if [ -n "$AUR_HELPER" ]; then
        $AUR_HELPER -S --needed --noconfirm "$pkg" 2>/dev/null && return 0
    fi
    
    echo -e "${GOLD}  ✗ Failed to install $pkg${RESET}"
    return 1
}

# Install each package individually
PACKAGES="kitty waybar wofi hyprland fastfetch neofetch zsh bash-completion sqlite python tk"
FAILED_PKGS=""

for pkg in $PACKAGES; do
    install_pkg "$pkg" || FAILED_PKGS="$FAILED_PKGS $pkg"
done

# Try AUR packages separately
if [ -n "$AUR_HELPER" ]; then
    echo -e "${SILVER}[*] Installing AUR packages...${RESET}"
    $AUR_HELPER -S --needed --noconfirm starship 2>/dev/null || true
fi

# Report failures
if [ -n "$FAILED_PKGS" ]; then
    echo ""
    echo -e "${GOLD}[!] Some packages failed to install:${RESET}"
    echo -e "${SILVER}  $FAILED_PKGS${RESET}"
    echo -e "${SILVER}  Install manually with:${RESET}"
    echo -e "${SILVER}    sudo pacman -S$FAILED_PKGS${RESET}"
    if [ -n "$AUR_HELPER" ]; then
        echo -e "${SILVER}    $AUR_HELPER -S$FAILED_PKGS${RESET}"
    fi
fi

# Verify critical packages
echo ""
echo -e "${SILVER}[*] Verifying installation...${RESET}"
MISSING=""

for pkg in kitty hyprland waybar; do
    if command -v $pkg &>/dev/null || pacman -Qi $pkg &>/dev/null 2>/dev/null; then
        echo -e "${SILVER}  ✓ $pkg found${RESET}"
    else
        echo -e "${GOLD}  ✗ $pkg NOT FOUND${RESET}"
        MISSING="$MISSING $pkg"
    fi
done

# Setup directories
echo -e "${SILVER}[*] Setting up directories...${RESET}"
mkdir -p ~/.config/{kitty,hypr,waybar,wofi,fastfetch,neofetch}
mkdir -p ~/.local/{bin,share/theology,share/wallpapers/sanctum-os}

# Copy configurations
echo -e "${SILVER}[*] Installing configurations...${RESET}"
cp -r "$SOURCE_DIR/config/"* ~/.config/ 2>/dev/null || true
cp "$SOURCE_DIR/scripts/"* ~/.local/bin/ 2>/dev/null || true
cp "$SOURCE_DIR/wallpapers/"* ~/.local/share/wallpapers/sanctum-os/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true

# Extract database
echo -e "${SILVER}[*] Extracting theological library...${RESET}"
if [ -f "$SOURCE_DIR/theology-db/extract_embedded.py" ]; then
    python3 "$SOURCE_DIR/theology-db/extract_embedded.py" 2>/dev/null || {
        echo -e "${GOLD}[!] Database extraction skipped${RESET}"
    }
fi

# Add to PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# Completion message
echo ""
echo -e "${GOLD}╔═══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${GOLD}║              INSTALLATION COMPLETE                                ║${RESET}"
echo -e "${GOLD}╚═══════════════════════════════════════════════════════════════════╝${RESET}"
echo ""

if [ -n "$MISSING" ]; then
    echo -e "${GOLD}[!] Missing critical packages:$MISSING${RESET}"
    echo -e "${SILVER}  Install with:${RESET}"
    echo -e "${SILVER}    sudo pacman -S$MISSING${RESET}"
    if [ -n "$AUR_HELPER" ]; then
        echo -e "${SILVER}    $AUR_HELPER -S$MISSING${RESET}"
    fi
    echo ""
fi

echo -e "${SILVER}Available commands:${RESET}"
echo -e "  ${GOLD}biblia${RESET} - Read the Bible (47,787 verses)"
echo -e "  ${GOLD}patres${RESET} - Read Church Fathers"
echo -e "  ${GOLD}sanctum-help${RESET} - Show help"
echo ""
echo -e "${SILVER}To start Hyprland:${RESET}"
echo -e "  ${GOLD}exec Hyprland${RESET}"
echo ""

# Cleanup
if [ "$LOCAL_INSTALL" = false ]; then
    rm -rf "$SOURCE_DIR" 2>/dev/null || true
fi

echo -e "${GOLD}Gloria Patri, et Filio, et Spiritui Sancto.${RESET}"
echo ""
