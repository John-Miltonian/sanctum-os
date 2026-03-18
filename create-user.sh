#!/bin/bash
# Create user account for Sanctum OS

echo "=== User Account Setup ==="
echo ""
echo "You need a regular user account to run Sanctum OS."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo:"
    echo "  sudo bash create-user.sh"
    exit 1
fi

read -p "Enter username: " USERNAME

# Create user
useradd -m -G wheel,audio,video,input -s /bin/bash "$USERNAME"
passwd "$USERNAME"

# Enable sudo for wheel group
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/wheel

# Set up Sanctum OS for this user
HOME_DIR="/home/$USERNAME"
mkdir -p "$HOME_DIR/.config"/{kitty,sway,i3,waybar,wofi,fastfetch}
mkdir -p "$HOME_DIR/.local"/{bin,share/theology,share/wallpapers}

chown -R "$USERNAME:$USERNAME" "$HOME_DIR/.config"
chown -R "$USERNAME:$USERNAME" "$HOME_DIR/.local"

echo ""
echo "=== User created: $USERNAME ==="
echo ""
echo "To start Sanctum OS:"
echo "  1. Logout: exit"
echo "  2. Login as: $USERNAME"
echo "  3. Run: sway"
echo ""
