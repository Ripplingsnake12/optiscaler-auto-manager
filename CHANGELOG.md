# Changelog

All notable changes to OptiScaler Auto Manager will be documented in this file.

## [1.0.0] - 2025-07-12

### Added
- **Initial Release** - Complete OptiScaler management system for Arch Linux
- **OptiScaler Integration** - Download latest nightly builds automatically
- **Interactive Setup** - Terminal-based OptiScaler configuration
- **FSR4 DLL Management** - Support for FSR 4.0 and FSR 4.0.1 versions
- **Steam Game Detection** - Automatic discovery of installed Steam games
- **Smart Installation Paths** - Auto-detection of game engine directories
- **Steam Launch Options** - Automatic configuration with Steam integration
- **RDNA3 Workaround Support** - Full DXIL_SPIRV_CONFIG implementation
- **Complete Uninstall** - Interactive removal with file restoration
- **Backup System** - Automatic backup of original game files
- **Compatdata Integration** - FSR4 DLL installation to Wine prefixes

### Features
- **8 Main Menu Options** - Complete OptiScaler lifecycle management
- **7z Archive Support** - Handle OptiScaler's native archive format
- **Version Selection** - Switch between FSR4 DLL versions
- **Steam Restart Management** - Optional automatic Steam restart
- **Terminal Emulator Support** - Works with Konsole, GNOME Terminal, Alacritty, etc.
- **Error Handling** - Comprehensive error checking and fallbacks
- **Installation Tracking** - JSON-based installation database

### Launch Commands
- **Basic OptiScaler** - Essential WINEDLLOVERRIDES and FSR4 activation
- **Advanced Performance** - DXVK async, NVAPI, VKD3D optimizations
- **RDNA3 Specialized** - Complete RDNA3 workaround implementation
- **Debug Mode** - Full logging for troubleshooting
- **Anti-Lag 2** - Experimental low-latency support

### Bundled Content
- **FSR 4.0 DLL** - Original FSR4 release
- **FSR 4.0.1 DLL** - Updated FSR4 with improvements
- **Setup Scripts** - FSR4 DLL management helpers
- **Documentation** - Complete installation and usage guides

### Technical Details
- **Python 3.6+ Compatible** - Modern Python with type hints
- **Arch Linux Optimized** - Designed specifically for Arch/Manjaro
- **Steam VDF Parsing** - Direct Steam configuration modification
- **Regex-based Config** - Safe Steam launch option modification
- **Path Resolution** - Smart Steam and game directory detection

### Requirements
- Arch Linux or compatible distribution
- Python 3.6+ with requests module
- p7zip for archive extraction
- Steam installation
- AMD RDNA3/RDNA4 GPU (for FSR4 features)

---

**Note:** This is the initial release based on extensive research of OptiScaler installation requirements, Steam integration needs, and FSR4 compatibility requirements for Linux gaming.