#!/bin/bash

echo "=== OptiScaler Manager Desktop Integration ==="
echo "Installing desktop entry and creating application launcher..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make scripts executable
chmod +x "$SCRIPT_DIR/run.sh"
chmod +x "$SCRIPT_DIR/launch-gui.sh"
chmod +x "$SCRIPT_DIR/optiscaler_manager.py"

# Create applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Install desktop entry
cp "$SCRIPT_DIR/optiscaler-manager.desktop" ~/.local/share/applications/

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ~/.local/share/applications/
    echo "✓ Desktop database updated"
fi

# Create icon if it doesn't exist
if [ ! -f "$SCRIPT_DIR/optiscaler-icon.svg" ]; then
    echo "Creating application icon..."
    python3 "$SCRIPT_DIR/create-icon.py"
fi

echo "✓ Desktop entry installed to ~/.local/share/applications/"
echo "✓ OptiScaler Manager should now appear in your application menu"
echo "✓ You can also launch it from: Applications > Games > OptiScaler Manager"
echo ""
echo "To uninstall the desktop entry, run:"
echo "rm ~/.local/share/applications/optiscaler-manager.desktop"
echo "update-desktop-database ~/.local/share/applications/"