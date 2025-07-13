# OptiScaler Auto Manager

A comprehensive Python-based tool for automatically managing OptiScaler installations on Steam games in Linux. OptiScaler enables FSR4, DLSS, and other upscaling technologies on games that don't natively support them.

![OptiScaler Manager](optiscaler-icon.svg)

## Features

- 🎮 **Steam Integration**: Automatically detects Steam games and installation paths
- 🚀 **Auto Installation**: Downloads and installs the latest OptiScaler nightly builds
- ⚙️ **Smart Configuration**: Automatically configures OptiScaler.ini with optimal settings
- 🖥️ **Desktop Integration**: GUI launcher with application menu integration
- 📊 **MangoHUD Support**: Optional performance monitoring overlay
- 🔧 **Launch Options**: Automatically applies Steam launch options with proper VDF formatting
- 🗂️ **FSR4 Management**: Manages multiple FSR4 DLL versions
- 📦 **Backup System**: Creates backups before making changes
- 🔄 **Uninstaller**: Clean removal of OptiScaler installations

## Quick Start

### Option 1: GUI Launch (Recommended)
1. Run `./install-desktop-entry.sh` to install desktop integration
2. Launch from Applications menu: **Games > OptiScaler Manager**
3. Or double-click `launch-gui.sh`

### Option 2: Terminal Launch
```bash
./run.sh
```

## Installation

### Prerequisites
- **Linux Distribution**: Arch Linux, Bazzite, or compatible
- **Steam**: Installed and configured
- **Python 3**: With requests module
- **p7zip**: For archive extraction

### Automatic Setup
The script automatically installs missing dependencies:
```bash
git clone <repository-url>
cd optiscaler-auto-manager
chmod +x run.sh
./run.sh
```

### Manual Dependency Installation
```bash
# Arch Linux / Bazzite
sudo pacman -S python-requests p7zip

# Ubuntu / Debian
sudo apt install python3-requests p7zip-full

# Fedora
sudo dnf install python3-requests p7zip
```

## Usage Guide

### 1. Install OptiScaler on a Game
1. Launch OptiScaler Manager
2. Select **"2. Install OptiScaler"**
3. Choose your game from the Steam library
4. Select installation location (usually "Main Game Directory")
5. The tool will:
   - Download latest OptiScaler nightly
   - Extract to game directory
   - Run setup scripts
   - Configure OptiScaler.ini
   - Copy FSR4 DLL to compatibility data

### 2. Configure Steam Launch Options
1. Select **"6. Add Steam launch options"**
2. Choose your game
3. Select if you need RDNA3 workarounds
4. Choose to include MangoHUD (performance monitoring)
5. Pick launch option type:
   - **Basic**: Essential OptiScaler setup
   - **Advanced**: Additional performance optimizations
   - **Debug**: Detailed logging for troubleshooting
   - **Anti-Lag 2**: Experimental latency reduction

### 3. Manage FSR4 DLL Versions
1. Select **"7. Manage FSR4 DLL"**
2. Choose from bundled FSR4 versions or browse for custom DLL
3. The selected version will be used for all future installations

### 4. View and Uninstall
- **View installations**: Option 3 shows all current OptiScaler installations
- **Uninstall**: Option 4 cleanly removes OptiScaler and restores original files

## Launch Command Examples

### Basic OptiScaler
```bash
WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%
```

### With MangoHUD Performance Monitoring
```bash
mangohud WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%
```

### RDNA3 GPU Workaround
```bash
WINEDLLOVERRIDES="dxgi=n,b" DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%
```

### Advanced with Performance Optimizations
```bash
WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%
```

## File Structure

```
optiscaler-auto-manager/
├── optiscaler_manager.py          # Main application
├── run.sh                         # Terminal launcher with dependency check
├── launch-gui.sh                  # GUI launcher for desktop integration
├── install-desktop-entry.sh       # Desktop integration installer
├── optiscaler-manager.desktop     # Desktop entry file
├── create-icon.py                 # Icon generator
├── optiscaler-icon.svg           # Application icon
├── test_steam_fix.py             # Steam VDF testing utility
├── test_hunt.py                  # Hunt: Showdown testing utility
└── README.md                     # This file
```

## Configuration Files

### User Configuration
- **Installations**: `~/.config/optiscaler_manager/installations.json`
- **FSR4 DLL**: `~/.config/optiscaler_manager/amdxcffx64.dll`
- **Desktop Entry**: `~/.local/share/applications/optiscaler-manager.desktop`

### Steam Integration
- **Config Path**: `~/.steam/steam/userdata/[USER_ID]/config/localconfig.vdf`
- **Backups**: Automatic backups created before modifications

## Supported Games

OptiScaler works with most DirectX 11/12 games. Tested and verified with:
- Hunt: Showdown
- Stellar Blade
- Cyberpunk 2077
- Elden Ring
- And many more...

## GPU Compatibility

### AMD GPUs
- **RDNA3** (RX 7000 series): Use RDNA3 workaround options
- **RDNA2** (RX 6000 series): Standard options work
- **RDNA1** (RX 5000 series): Basic OptiScaler support

### NVIDIA GPUs
- **RTX 40 series**: Full DLSS/FSR support
- **RTX 30/20 series**: DLSS + FSR support
- **GTX series**: FSR support only

### Intel GPUs
- **Arc GPUs**: Basic FSR support

## Troubleshooting

### OptiScaler Overlay Not Appearing
1. Try the "Disable DLSS FG" launch option variant
2. Ensure `WINEDLLOVERRIDES="dxgi=n,b"` is present
3. Check game logs for DLL loading errors

### Steam Launch Options Not Applying
1. Restart Steam completely after applying options
2. Check Steam game properties to verify options are visible
3. Restore from backup if VDF corruption occurs

### Performance Issues
1. Enable MangoHUD to monitor performance
2. Try different OptiScaler presets (Performance vs Quality)
3. Use DXVK_ASYNC=1 for better frame pacing

### FSR4 Not Working
1. Verify amdxcffx64.dll is in compatdata/[APPID]/pfx/drive_c/windows/system32/
2. Check OptiScaler.ini has `Fsr4Update=true`
3. Ensure game supports FSR4 requirements

## Advanced Configuration

### Custom OptiScaler.ini Settings
Edit the generated OptiScaler.ini in your game directory:
```ini
[OptiScaler]
Fsr4Update=true
Dx12Upscaler=auto
ColorResourceBarrier=auto
MotionVectorResourceBarrier=auto
OverrideNvapiDll=auto
```

### Custom Launch Options
You can manually add these environment variables:
- `DXVK_ASYNC=1` - Async shader compilation
- `PROTON_ENABLE_NVAPI=1` - Enable NVIDIA API
- `VKD3D_CONFIG=dxr11,dxr` - DirectX Raytracing support
- `WINE_CPU_TOPOLOGY=4:2` - CPU topology override

## Development

### Testing Steam VDF Integration
```bash
python3 test_steam_fix.py    # Test VDF parsing
python3 test_hunt.py         # Test with specific game
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test with multiple games and GPU types
4. Submit pull request

## License

This project is open source. OptiScaler itself is developed by the OptiScaler team.

## Acknowledgments

- **OptiScaler Team**: For the amazing upscaling technology
- **Valve**: For Steam and Proton
- **AMD**: For FSR technology
- **Community**: For testing and feedback

## Support

For issues and support:
1. Check the troubleshooting section above
2. Enable debug launch options for detailed logs
3. Create an issue with system information and logs
4. Join the OptiScaler community forums

---

**Enjoy enhanced gaming with OptiScaler! 🎮✨**