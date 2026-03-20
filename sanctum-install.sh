#!/bin/sh
set -e

echo Sanctum OS Installer

# Check root
[ "$(id -u)" -eq 0 ] && { echo Run as regular user, not root; exit 0; }

echo Installing packages...
sudo pacman -Sy
sudo pacman -S --noconfirm sway swaylock swayidle waybar wofi kitty foot neofetch zsh python sqlite 2>/dev/null || true

echo Downloading...
cd
curl -fsSL https://github.com/John-Miltonian/sanctum-os/archive/refs/heads/main.tar.gz -o s.tar.gz
tar -xzf s.tar.gz

echo Installing configs...
mkdir -p .config/sway .config/waybar .config/wofi .config/kitty .local/bin
cp sanctum-os-main/config/sway/sway.config .config/sway/config 2>/dev/null || true
cp sanctum-os-main/config/waybar/* .config/waybar/ 2>/dev/null || true
cp sanctum-os-main/config/wofi/* .config/wofi/ 2>/dev/null || true
cp sanctum-os-main/config/kitty/kitty.conf .config/kitty/ 2>/dev/null || true
cp sanctum-os-main/scripts/* .local/bin/ 2>/dev/null || true
chmod +x .local/bin/* 2>/dev/null || true

echo Done. Run: sway
