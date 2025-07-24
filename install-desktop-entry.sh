#!/bin/bash

echo "=== OptiScaler Manager Desktop Integration ==="
echo "Installing desktop entry and creating application launcher..."

# Get the script directory (where the repo is actually located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📁 Using repository location: $SCRIPT_DIR"

# Make scripts executable
chmod +x "$SCRIPT_DIR/run.sh"
chmod +x "$SCRIPT_DIR/launch-gui.sh"
chmod +x "$SCRIPT_DIR/optiscaler_manager.py"

# Create applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Create desktop entry with dynamic paths
echo "🔧 Creating desktop entry with correct paths..."
cat > ~/.local/share/applications/optiscaler-manager.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OptiScaler Manager
Comment=Manage OptiScaler installations for Steam games
GenericName=Game Enhancement Manager
Icon=$SCRIPT_DIR/optiscaler-icon.svg
Exec=sh -c "$SCRIPT_DIR/launch-gui.sh"
Terminal=false
StartupNotify=true
Categories=Game;Utility;
Keywords=optiscaler;fsr;dlss;steam;gaming;upscaling;
Path=$SCRIPT_DIR
EOF

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
echo "📍 Desktop entry points to: $SCRIPT_DIR"
echo ""
echo "To uninstall the desktop entry, run:"
echo "rm ~/.local/share/applications/optiscaler-manager.desktop"
echo "update-desktop-database ~/.local/share/applications/"
