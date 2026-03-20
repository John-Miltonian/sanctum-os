#!/bin/bash
# Sanctum OS Installer
set -e

# Simple color codes
R='\033[0;31m'
G='\033[0;32m'
Y='\033[1;33m'
NC='\033[0m'

echo -e "${R}Sanctum OS${NC} - Theological Computing Environment"
echo ""

# Check root
if [ "$(id -u)" = "0" ]; then
    echo "Running as root. Creating user account..."
    echo ""
    printf "Username: "
    read USERNAME
    printf "Password: "
    read -s PASSWORD
    echo ""
    
    useradd -m -G wheel,audio,video,input -s /bin/bash "$USERNAME"
    echo "$USERNAME:$PASSWORD" | chpasswd
    echo "%wheel ALL=(ALL) ALL" > /etc/sudoers.d/wheel
    chmod 440 /etc/sudoers.d/wheel
    
    echo ""
    echo "User created. Now login as $USERNAME and run:"
    echo "curl -fsSL https://raw.githubusercontent.com/John-Miltonian/sanctum-os/main/sanctum-install.sh | bash"
    echo ""
    exit 0
fi

# Check internet
echo "Checking internet..."
if ! curl -s google.com > /dev/null; then
    echo "No internet. Please connect and retry."
    exit 1
fi
echo -e "${G}OK${NC}"

# Fix repos if needed
if [ ! -f /etc/pacman.conf ]; then
    echo "Missing pacman.conf. Cannot continue."
    exit 1
fi

# Create temp dir
cd /tmp
rm -rf sanctum-install 2>/dev/null || true
mkdir sanctum-install
cd sanctum-install

# Download rice
echo "Downloading Sanctum OS..."
curl -fsL https://github.com/John-Miltonian/sanctum-os/archive/main.tar.gz | tar xz

# Setup directories
echo "Creating directories..."
mkdir -p ~/.config/{kitty,sway,i3,waybar,wofi}
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/{theology,wallpapers}

# Copy configs
echo "Installing configs..."
cp sanctum-os-main/config/kitty/kitty.conf ~/.config/kitty/ 2>/dev/null || true
cp sanctum-os-main/config/sway/sway.config ~/.config/sway/config 2>/dev/null || true
cp sanctum-os-main/config/waybar/* ~/.config/waybar/ 2>/dev/null || true
cp sanctum-os-main/config/wofi/* ~/.config/wofi/ 2>/dev/null || true

# Copy scripts
echo "Installing CLI tools..."
cp sanctum-os-main/scripts/biblia ~/.local/bin/ 2>/dev/null || true
cp sanctum-os-main/scripts/patres ~/.local/bin/ 2>/dev/null || true
cp sanctum-os-main/scripts/sanctum-quote ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true

# Copy wallpapers
cp sanctum-os-main/wallpapers/*.png ~/.local/share/wallpapers/ 2>/dev/null || true

# Extract theology database
echo "Extracting theology library..."
if [ -f sanctum-os-main/theology-db/extract_embedded.py ]; then
    python3 sanctum-os-main/theology-db/extract_embedded.py 2>/dev/null || echo "Database extraction skipped"
fi

# Install packages if possible
echo "Installing packages (may need sudo)..."
for pkg in sway kitty waybar wofi python sqlite; do
    sudo pacman -S --noconfirm "$pkg" 2>/dev/null || true
done

# Add to PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# Cleanup
cd /tmp
rm -rf sanctum-install

echo ""
echo -e "${Y}Sanctum OS installed!${NC}"
echo ""
echo "Commands:"
echo "  biblia      - Bible search"
echo "  patres      - Church Fathers"
echo "  sway        - Start Wayland session"
echo ""
