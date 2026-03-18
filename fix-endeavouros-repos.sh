#!/bin/bash
# Fix EndeavourOS repository configuration

echo "=== Fixing EndeavourOS Repositories ==="

# 1. Check internet
echo "[*] Checking internet connection..."
if ! ping -c 1 archlinux.org &>/dev/null; then
    echo "[!] No internet connection. Connect to WiFi/Ethernet first."
    exit 1
fi
echo "[✓] Internet connected"

# 2. Update mirror list
echo "[*] Updating mirror list..."
sudo pacman -Sy archlinux-keyring endeavouros-keyring --noconfirm 2>/dev/null || true

# 3. Backup and fix pacman.conf
echo "[*] Checking pacman.conf..."
if [ ! -f /etc/pacman.conf ]; then
    echo "[!] pacman.conf missing! Creating default..."
    sudo tee /etc/pacman.conf > /dev/null << 'EOF'
#
# /etc/pacman.conf
#
[options]
HoldPkg     = pacman glibc
Architecture = auto
CheckSpace
SigLevel    = Required DatabaseOptional
LocalFileSigLevel = Optional

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[community]
Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist
EOF
fi

# 4. Check if extra repo is uncommented
echo "[*] Verifying repositories..."
if grep -q "^#\[extra\]" /etc/pacman.conf; then
    echo "[*] Enabling extra repository..."
    sudo sed -i 's/^#\[extra\]/[extra]/' /etc/pacman.conf
    sudo sed -i '/^\[extra\]/{n;s/^#Include/Include/}' /etc/pacman.conf
fi

# 5. Update mirrorlist if empty
echo "[*] Checking mirror list..."
if [ ! -s /etc/pacman.d/mirrorlist ]; then
    echo "[*] Generating new mirror list..."
    sudo pacman -Sy reflector --noconfirm 2>/dev/null || true
    sudo reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist 2>/dev/null || {
        echo "[*] Using default mirror list..."
        sudo tee /etc/pacman.d/mirrorlist > /dev/null << 'EOF'
Server = https://geo.mirror.pkg.archlinux.org/\$repo/os/\$arch
Server = https://archlinux.mailtunnel.eu/\$repo/os/\$arch
Server = https://mirror.rackspace.com/archlinux/\$repo/os/\$arch
EOF
    }
fi

# 6. Sync databases
echo "[*] Syncing package databases..."
sudo pacman -Syy

# 7. Now try installing Hyprland
echo ""
echo "=== Installing Hyprland ==="
sudo pacman -S hyprland waybar wofi kitty --noconfirm

echo ""
echo "=== Done ==="
echo "If successful, run: exec Hyprland"
