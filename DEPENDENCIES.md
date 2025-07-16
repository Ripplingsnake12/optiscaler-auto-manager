# Dependency Management Guide

The OptiScaler Manager has been enhanced with automatic dependency detection and installation capabilities. This ensures that all required tools are available for optimal functionality.

## Features

### Automatic System Detection
- **Package Manager Detection**: Automatically detects your Linux distribution's package manager
- **Distribution Detection**: Identifies your Linux distribution for optimal package selection
- **Display Server Detection**: Detects X11 vs Wayland for appropriate clipboard utility selection

### Supported Package Managers
- **apt/apt-get** (Debian, Ubuntu, Linux Mint)
- **pacman** (Arch Linux, Manjaro, EndeavourOS)
- **dnf/yum** (Fedora, CentOS, RHEL)
- **zypper** (openSUSE)
- **emerge** (Gentoo)
- **apk** (Alpine Linux)
- **xbps-install** (Void Linux)
- **pkg** (FreeBSD)
- **brew** (macOS/Linux)

### Dependency Categories

#### Critical Dependencies
- **Python requests module**: Required for downloading OptiScaler releases
  - Auto-installs via pip or system package manager
  - Program will exit if this cannot be installed

#### System Tools
- **7z (p7zip)**: For extracting .7z archives
- **git**: For version control operations
- **wine**: For running Windows applications
- **curl/wget**: For downloading files

#### Clipboard Applications
The program automatically detects your display server and recommends the appropriate clipboard utility:

**For X11 Systems:**
- **xclip** (recommended): Simple and widely supported
- **xsel**: Alternative clipboard utility

**For Wayland Systems:**
- **wl-copy** (recommended): Native Wayland clipboard support

#### Terminal Emulators
Checks for common terminal emulators needed for OptiScaler setup scripts:
- konsole, gnome-terminal, xfce4-terminal
- alacritty, kitty, terminator, xterm

## Usage

### Automatic Startup Check
When you run the program, it automatically performs a quick dependency check:

```bash
python3 optiscaler_manager.py
```

### Manual Dependency Check
Use menu option 9 to run a comprehensive dependency check:

```
9. Check/Install dependencies
```

This will:
1. Display detailed system information
2. Check all Python modules
3. Scan for system tools
4. Set up clipboard functionality
5. Verify terminal emulators

### Clipboard Setup
If no clipboard application is found, the program will:
1. Detect your display server (X11 or Wayland)
2. Recommend the appropriate clipboard utility
3. Offer to install your choice automatically
4. Provide option to install all clipboard apps

## Installation Examples

### Ubuntu/Debian
```bash
# Automatic installation
sudo apt install python3-requests p7zip-full git wine curl wget xclip

# Manual clipboard selection
sudo apt install xclip      # X11 systems
sudo apt install wl-clipboard  # Wayland systems
```

### Arch Linux
```bash
# Automatic installation
sudo pacman -S python-requests p7zip git wine curl wget xclip

# Manual clipboard selection
sudo pacman -S xclip        # X11 systems
sudo pacman -S wl-clipboard # Wayland systems
```

### Fedora
```bash
# Automatic installation
sudo dnf install python3-requests p7zip git wine curl wget xclip

# Manual clipboard selection
sudo dnf install xclip      # X11 systems
sudo dnf install wl-clipboard  # Wayland systems
```

## Troubleshooting

### Package Manager Not Detected
If your package manager isn't detected:
1. Check if it's in the supported list above
2. Install dependencies manually using your package manager
3. The program will still work with missing optional dependencies

### Permission Issues
If you get permission errors:
1. Make sure you can run `sudo` commands
2. Check if your user is in the appropriate groups
3. For Arch Linux, ensure you're in the `wheel` group

### Python Module Issues
If Python modules can't be installed:
1. Try installing via system package manager instead of pip
2. Check if you have python3-dev/python3-devel installed
3. Verify pip is installed and working

### Missing Dependencies
If some tools are missing after installation:
1. Check if the package names are correct for your distribution
2. Try installing manually with your package manager
3. Some tools may have different names on different distributions

## Configuration

### Skipping Dependency Checks
To run the program without dependency checks, you can modify the startup behavior by commenting out the dependency check in the main function.

### Custom Package Mappings
The dependency manager supports custom package mappings for different distributions. If your distribution uses different package names, you can modify the `package_mappings` dictionary in the `DependencyManager` class.

## Testing

Run the test suite to verify dependency management:

```bash
python3 test_dependencies.py
```

This will test:
- System detection capabilities
- Python module availability
- System tool detection
- Clipboard application detection

## Support

If you encounter issues with dependency management:
1. Check the troubleshooting section above
2. Run the test suite to identify specific issues
3. Manually install missing dependencies
4. Report issues with specific distribution/package manager combinations