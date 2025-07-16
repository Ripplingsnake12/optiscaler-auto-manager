#!/bin/bash

echo "=== OptiScaler Auto Manager ==="
echo "Checking dependencies..."

# Check if python-requests is installed
if ! pacman -Q python-requests &>/dev/null; then
    echo "Installing python-requests..."
    sudo pacman -S --noconfirm python-requests
fi

# Check if p7zip and wl-copy is installed
if ! pacman -Q p7zip &>/dev/null; then
    echo "Installing p7zip..."
    sudo pacman -S --noconfirm p7zip 
    yay -S  --noconfirm wl-copy
fi

echo "Dependencies verified!"

# Check if desktop entry is installed
if [ ! -f ~/.local/share/applications/optiscaler-manager.desktop ]; then
    echo "Desktop integration not found. Would you like to install it? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./install-desktop-entry.sh
        echo ""
    fi
fi

echo "Starting OptiScaler Manager..."
echo

python3 optiscaler_manager.py
