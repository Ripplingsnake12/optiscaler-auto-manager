#!/bin/bash

# GUI launcher for OptiScaler Manager
cd "$(dirname "$0")"

# Try to launch in different terminal emulators
TERMINALS=(
    "konsole --workdir $(pwd) -e ./run.sh"
    "gnome-terminal --working-directory=$(pwd) -- ./run.sh"  
    "xfce4-terminal --working-directory=$(pwd) -e ./run.sh"
    "alacritty --working-directory=$(pwd) -e ./run.sh"
    "kitty --directory=$(pwd) ./run.sh"
    "terminator --working-directory=$(pwd) -e ./run.sh"
    "xterm -e 'cd $(pwd) && ./run.sh'"
)

# Try each terminal until one works
for terminal_cmd in "${TERMINALS[@]}"; do
    terminal_name=$(echo "$terminal_cmd" | cut -d' ' -f1)
    if command -v "$terminal_name" >/dev/null 2>&1; then
        echo "Launching OptiScaler Manager in $terminal_name..."
        eval "$terminal_cmd" &
        exit 0
    fi
done

# Fallback: try to run directly if no terminal found
echo "No terminal emulator found. Trying to run directly..."
./run.sh