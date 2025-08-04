# OptiScaler Manager Streamlined

A streamlined Python-based tool for automatically managing OptiScaler installations on Steam games in Linux. This version reduces complexity while maintaining full functionality.

![OptiScaler Manager](optiscaler-icon.svg)

## Features

- 🎮 **Streamlined Interface**: Just 3 menu options - Install, Manage, Exit
- 🚀 **Auto Installation**: Downloads latest OptiScaler → Installs → Configures FSR4 → Applies launch options
- ⚙️ **Smart Configuration**: Automatically sets up everything needed for optimal performance
- 🖥️ **Desktop Integration**: GUI launcher with application menu integration
- 🗂️ **FSR4 Auto-Setup**: Automatically configures FSR4 DLL during installation
- 📦 **Backup System**: Creates backups before making changes
- 🔄 **Clean Management**: View installations, uninstall, or check launch options

## What's Streamlined

**Old version**: 11 menu options requiring multiple steps
**New version**: 3 menu options with automated workflow

### Automated Features
- ✅ Dependencies check on startup
- ✅ Latest nightly download during install
- ✅ FSR4 DLL configuration after install
- ✅ Steam launch options applied automatically
- ✅ Drive scanning in background

### Menu Options
1. **Install OptiScaler** - Complete automated installation
2. **Manage installed games** - View, uninstall, or check launch options
3. **Exit**

## Quick Start

### Option 1: GUI Launch (Recommended)
1. Run `./install-desktop-entry.sh` to install desktop integration
2. Launch from Applications menu: **Games > OptiScaler Manager Streamlined**
3. Or double-click `launch-gui.sh`

### Option 2: Terminal Launch
```bash
./run.sh
```

## Installation

### Prerequisites
- **Linux Distribution**: Arch Linux, Cachyos, or compatible
- **Steam**: Installed and configured
- **Python 3**: With requests module
- **p7zip**: For archive extraction

### Automatic Setup
The script automatically installs missing dependencies:
```bash
git clone <repository-url>
cd optiscaler-manager-streamlined
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

### Install OptiScaler (Option 1)
1. Select "1. Install OptiScaler"
2. Choose your game from the Steam library
3. Select installation location
4. **Everything else is automated**:
   - Downloads latest OptiScaler nightly
   - Installs to game directory
   - Configures FSR4 DLL
   - Applies Steam launch options
   - Shows Proton version recommendations

### Manage Games (Option 2)
1. Select "2. Manage installed games"
2. View all installations with FSR4 status
3. Choose action:
   - **Uninstall**: Remove OptiScaler from a game
   - **View launch options**: See launch commands for a game
   - **Back to main menu**

## Proton Version Recommendations

For best compatibility, use these custom Proton versions:
- **ProtonPlus** (recommended)
- **CachyOS Proton** 
- **EM Proton**
- **Bleeding Edge Proton Experimental**

Configure in Steam > Properties > Compatibility > Force specific Steam Play tool

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
optiscaler-manager-streamlined/
├── optiscaler_manager.py          # Main application (streamlined)
├── run.sh                         # Terminal launcher
├── launch-gui.sh                  # GUI launcher
├── install-desktop-entry.sh       # Desktop integration installer
├── optiscaler-manager.desktop     # Desktop entry file
├── create-icon.py                 # Icon generator
├── optiscaler-icon.svg           # Application icon
├── test_dependencies.py          # Dependency testing
├── test_vdf_launch_options.py    # VDF testing utility
├── fsr4_dlls/                    # FSR4 DLL versions
│   ├── FSR 4.0.1/
│   └── FSR 4.0/
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

## What's Different from Original

### Removed/Automated Features
- ❌ Manual dependency installation (now automatic)
- ❌ Manual latest nightly download (now automatic)
- ❌ Separate FSR4 DLL management (now automatic)
- ❌ Separate launch options menu (now automatic)
- ❌ Drive/library scan details (now background)
- ❌ VDF testing menu (now automatic)

### New Features
- ✅ Proton version recommendations
- ✅ Complete automation workflow
- ✅ Streamlined 3-option menu
- ✅ Auto-dependency check on startup

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
