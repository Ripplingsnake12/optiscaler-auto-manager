#!/bin/bash

echo "=== OptiScaler FSR4 Setup ==="
echo "This script helps you set up the required amdxcffx64.dll for FSR4 functionality"
echo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/optiscaler_manager"

mkdir -p "$CONFIG_DIR"

echo "Searching for amdxcffx64.dll in common locations..."

# Search paths
SEARCH_PATHS=(
    "$SCRIPT_DIR/amdxcffx64.dll"
    "$HOME/Downloads/amdxcffx64.dll"
    "$HOME/Documents/fsr4/FSR 4.0/FSR 4.0.1/amdxcffx64.dll"
    "/usr/lib/amdxcffx64.dll"
    "/usr/local/lib/amdxcffx64.dll"
)

# Check search paths
FOUND_DLL=""
for path in "${SEARCH_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "Found: $path"
        FOUND_DLL="$path"
        break
    fi
done

if [ -n "$FOUND_DLL" ]; then
    echo "Copying amdxcffx64.dll to config directory..."
    cp "$FOUND_DLL" "$CONFIG_DIR/amdxcffx64.dll"
    echo "Setup complete! amdxcffx64.dll is now available for OptiScaler."
else
    echo "amdxcffx64.dll not found in common locations."
    echo
    echo "To complete setup, you need to obtain amdxcffx64.dll from one of these sources:"
    echo "1. Copy from Windows system32 folder: C:\\Windows\\System32\\amdxcffx64.dll"
    echo "2. Extract from Wine prefix system32 folder if you have it"
    echo "3. Download from AMD driver package"
    echo
    echo "Once you have the file, place it in one of these locations:"
    echo "- Current directory: $SCRIPT_DIR/amdxcffx64.dll"
    echo "- Config directory: $CONFIG_DIR/amdxcffx64.dll"
    echo "- Downloads: $HOME/Downloads/amdxcffx64.dll"
    echo
    
    read -p "Do you want to specify a custom path to amdxcffx64.dll? (y/n): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        read -p "Enter full path to amdxcffx64.dll: " custom_path
        if [ -f "$custom_path" ]; then
            cp "$custom_path" "$CONFIG_DIR/amdxcffx64.dll"
            echo "Copied amdxcffx64.dll to config directory."
            echo "Setup complete!"
        else
            echo "File not found at specified path: $custom_path"
            exit 1
        fi
    else
        echo "Please obtain amdxcffx64.dll and run this script again."
        exit 1
    fi
fi

echo
echo "You can now run the OptiScaler manager:"
echo "python3 optiscaler_manager.py"