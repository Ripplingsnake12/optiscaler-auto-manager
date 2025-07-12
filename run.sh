#!/bin/bash

echo "=== OptiScaler Auto Manager ==="
echo "Checking dependencies..."

# Check if python-requests is installed
if ! pacman -Q python-requests &>/dev/null; then
    echo "Installing python-requests..."
    sudo pacman -S --noconfirm python-requests
fi

# Check if p7zip is installed
if ! pacman -Q p7zip &>/dev/null; then
    echo "Installing p7zip..."
    sudo pacman -S --noconfirm p7zip
fi

echo "Dependencies verified!"
echo "Starting OptiScaler Manager..."
echo

python3 optiscaler_manager.py