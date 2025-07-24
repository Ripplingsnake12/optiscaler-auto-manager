#!/bin/bash

echo "=== OptiScaler Auto Manager ==="
echo "Checking dependencies..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we can run the dependency manager
if ! python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from optiscaler_manager import dep_manager" 2>/dev/null; then
    echo "⚠️ Unable to load dependency manager. Trying basic dependency check..."
    
    # Fallback: Basic python3 and requests check
    if ! python3 -c "import requests" 2>/dev/null; then
        echo "❌ Python requests module not found."
        echo "Please install it manually for your distribution:"
        echo "  Arch/Manjaro: sudo pacman -S python-requests"
        echo "  Ubuntu/Debian: sudo apt install python3-requests"
        echo "  Fedora: sudo dnf install python3-requests"
        echo "  openSUSE: sudo zypper install python3-requests"
        echo ""
        echo "Or install via pip: pip3 install --user requests"
        echo ""
        read -p "Press Enter to continue anyway or Ctrl+C to exit..."
    fi
else
    # Use the comprehensive dependency manager
    echo "🔍 Running comprehensive dependency check..."
    python3 -c "
import sys
import os
sys.path.insert(0, '$SCRIPT_DIR')

try:
    from optiscaler_manager import dep_manager
    
    # Check critical dependencies
    print('Checking Python modules...')
    requests_ok = dep_manager.check_python_module('requests')
    
    print('\\nChecking system tools...')
    p7zip_ok = dep_manager.check_system_tool('7z', 'p7zip', auto_install=False)
    
    # Check other important tools quietly
    tools_status = []
    for tool in ['git', 'curl', 'wget']:
        try:
            import subprocess
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                tools_status.append(f'✅ {tool}')
            else:
                tools_status.append(f'❌ {tool} (optional)')
        except:
            tools_status.append(f'❌ {tool} (optional)')
    
    print('\\nOptional tools status:')
    for status in tools_status:
        print(f'  {status}')
    
    # Check clipboard functionality
    print('\\nChecking clipboard functionality...')
    clipboard_apps = ['xclip', 'xsel', 'wl-copy']
    clipboard_found = False
    
    for app in clipboard_apps:
        try:
            import subprocess
            result = subprocess.run(['which', app], capture_output=True, text=True)
            if result.returncode == 0:
                print(f'  ✅ {app} found')
                clipboard_found = True
                break
        except:
            pass
    
    if not clipboard_found:
        print('  ⚠️ No clipboard app found (launch commands won\\'t be copied automatically)')
        print('  Install one of: xclip, xsel, or wl-copy')
    
    if not requests_ok:
        print('\\n❌ Critical: Python requests module is required')
        print('Please install it and restart the program')
        sys.exit(1)
    
    if not p7zip_ok:
        print('\\n⚠️ Warning: p7zip not found - OptiScaler archive extraction may fail')
        print('Consider installing p7zip for your distribution')
    
    print('\\n✅ Dependency check complete!')
    
except Exception as e:
    print(f'❌ Error during dependency check: {e}')
    print('Continuing with basic functionality...')
"

    # Check the exit code of the dependency check
    if [ $? -ne 0 ]; then
        echo "❌ Dependency check failed. Please resolve the issues above."
        exit 1
    fi
fi

echo ""
echo "Dependencies verified!"

# Check if desktop entry is installed
if [ ! -f ~/.local/share/applications/optiscaler-manager.desktop ]; then
    echo "Desktop integration not found. Would you like to install it? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        "$SCRIPT_DIR/install-desktop-entry.sh"
        echo ""
    fi
fi

echo "Starting OptiScaler Manager..."
echo ""

# Change to script directory to ensure relative paths work
cd "$SCRIPT_DIR"
python3 optiscaler_manager.py
