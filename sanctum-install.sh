#!/bin/bash
set -e

echo "Sanctum OS Installer"
echo ""

# Check root
if [ "$EUID" -eq 0 ]; then
    echo "Running as root. Checking for users..."
    
    # Find users
    for user in $(cut -d: -f1 /etc/passwd); do
        uid=$(id -u "$user" 2>/dev/null || echo "0")
        if [ "$uid" -ge 1000 ] && [ "$uid" -lt 65534 ]; then
            echo "Found user: $user"
            USER_EXISTS=1
        fi
    done
    
    if [ -z "$USER_EXISTS" ]; then
        echo "No regular users found."
        echo "Create a user first:"
        echo "  useradd -m -G wheel -s /bin/bash USERNAME"
        echo "  passwd USERNAME"
        echo "Then run this script as that user."
        exit 0
    fi
    
    echo "Run this script as a regular user, not root."
    exit 0
fi

echo "Installing packages..."
sudo pacman -Sy --noconfirm || true

for pkg in sway swaylock swayidle waybar wofi kitty foot fastfetch neofetch zsh python sqlite; do
    sudo pacman -S --noconfirm "$pkg" || echo "Note: $pkg may need manual install"
done

echo "Downloading Sanctum OS..."
cd "$HOME"
curl -fsSL "https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz" -o sanctum-os.tar.gz
tar -xzf sanctum-os.tar.gz

echo "Installing configs..."
mkdir -p ~/.config/sway ~/.config/waybar ~/.config/wofi ~/.config/kitty ~/.local/bin

cp sanctum-os-main/config/sway/sway.config ~/.config/sway/config 2>/dev/null || echo "Sway config not found"
cp sanctum-os-main/config/waybar/config ~/.config/waybar/ 2>/dev/null || true
cp sanctum-os-main/config/waybar/style.css ~/.config/waybar/ 2>/dev/null || true
cp sanctum-os-main/config/wofi/config ~/.config/wofi/ 2>/dev/null || true
cp sanctum-os-main/config/wofi/sanctum.css ~/.config/wofi/ 2>/dev/null || true
cp sanctum-os-main/config/kitty/kitty.conf ~/.config/kitty/ 2>/dev/null || true

echo "Installing scripts..."
cp sanctum-os-main/scripts/* ~/.local/bin/ 2>/dev/null || true
chmod +x ~/.local/bin/* 2>/dev/null || true

echo "Extracting Bible database..."
python3 sanctum-os-main/theology-db/extract_embedded.py 2>/dev/null || echo "Database extraction skipped"

echo ""
echo "Sanctum OS installed!"
echo "To start Sway: sway"
echo "Commands: biblia, patres, sanctum-help"
