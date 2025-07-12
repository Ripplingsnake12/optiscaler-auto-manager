# OptiScaler Auto Manager for Arch Linux

A comprehensive tool to automatically manage OptiScaler installations on Steam games with FSR4 support, interactive setup, and Steam launch options configuration.

## 🚀 Features

### ⚡ **Core Functionality**
- **Automatic OptiScaler Downloads** - Latest nightly builds from GitHub
- **Interactive Installation** - Runs OptiScaler setup scripts in terminal windows
- **Steam Game Detection** - Automatic discovery of installed Steam games
- **Smart Path Detection** - Finds correct installation directories for different game engines
- **Complete Uninstall** - Restores original files with interactive removal scripts

### 🎮 **FSR4 Support**
- **Multiple FSR4 Versions** - Bundled FSR 4.0 and FSR 4.0.1 DLLs
- **Version Selection** - Switch between FSR4 versions easily
- **Steam Compatdata Integration** - Automatic DLL installation to Wine prefixes
- **RDNA3 Workaround** - Full support with `DXIL_SPIRV_CONFIG=wmma_rdna3_workaround`

### 🔧 **Steam Integration**
- **Automatic Launch Options** - Direct Steam configuration modification
- **RDNA3 Optimized Commands** - Specialized launch options for RDNA3 GPUs
- **Multiple Option Sets** - Basic, Advanced, Debug, and Anti-Lag 2 configurations
- **Steam Restart Management** - Optional automatic Steam restart

### 📋 **Comprehensive Launch Commands**

#### Standard GPU Options:
```bash
# Basic
WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%

# Advanced
WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%
```

#### RDNA3 GPU Options:
```bash
# Basic RDNA3
WINEDLLOVERRIDES="dxgi=n,b" DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%

# Advanced RDNA3
WINEDLLOVERRIDES="dxgi=n,b" DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%
```

## 📦 Installation

### Prerequisites
```bash
sudo pacman -S python-requests p7zip steam
```

### Quick Start
```bash
# Extract package
tar -xzf auto_fsr4_package.tar.gz
cd auto_fsr4

# Auto-install dependencies and run
./run.sh

# Or run manually
python3 optiscaler_manager.py
```

## 🎯 Usage

### Main Menu Options
1. **List Steam Games** - View all detected Steam games
2. **Install OptiScaler** - Full installation with interactive setup
3. **View Installations** - Show current OptiScaler installations
4. **Uninstall OptiScaler** - Complete removal with interactive scripts
5. **Download Latest Nightly** - Get newest OptiScaler build
6. **Add Steam Launch Options** - Configure and auto-apply launch commands
7. **Manage FSR4 DLL** - Select between FSR 4.0 and 4.0.1 versions
8. **Exit**

### Installation Process
1. **Select Game** - Choose from detected Steam games
2. **Choose Install Path** - Smart detection of game engine directories
3. **Interactive Setup** - OptiScaler configuration in terminal window
4. **Auto-Configure** - Sets `Fsr4Update=true` in OptiScaler.ini
5. **FSR4 Integration** - Copies selected FSR4 DLL to compatdata
6. **Steam Launch Options** - Optional automatic application

## 🎮 Game Engine Support

### Unreal Engine Games
- `Game/Binaries/Win64/`
- `Content/Engine/Plugins/Runtime/Nvidia/DLSS/Binaries/ThirdParty/Win64/`

### Other Engines
- Main executable directory
- Auto-detected based on file patterns

## 🔧 Configuration

### OptiScaler.ini Settings
```ini
[OptiScaler]
Fsr4Update=true
Dx12Upscaler=auto
ColorResourceBarrier=auto
MotionVectorResourceBarrier=auto
OverrideNvapiDll=auto
```

### FSR4 DLL Versions Included
- **FSR 4.0** - Original FSR4 release
- **FSR 4.0.1** - Updated version with improvements

## 📂 Package Structure
```
auto_fsr4/
├── optiscaler_manager.py          # Main application
├── requirements.txt               # Python dependencies
├── README.md                      # Full documentation
├── INSTALL.txt                    # Quick install guide
├── run.sh                         # Auto-install and run script
├── setup_fsr4.sh                 # FSR4 DLL setup helper
├── create_fsr4_structure.sh       # Directory structure creator
└── fsr4_dlls/                     # Bundled FSR4 versions
    ├── FSR 4.0/
    │   └── amdxcffx64.dll
    └── FSR 4.0.1/
        └── amdxcffx64.dll
```

## 🔄 Uninstall Process

### Complete Restoration
1. **Interactive Removal** - Runs `remove_optiscaler.sh` in terminal
2. **Manual Cleanup** - Removes remaining OptiScaler files
3. **File Restoration** - Restores original backed-up game DLLs
4. **FSR4 Cleanup** - Removes FSR4 DLL from Steam compatdata
5. **Tracking Cleanup** - Removes from installation database

## ⚠️ Important Notes

- **Required:** `WINEDLLOVERRIDES="dxgi=n,b"` is essential for OptiScaler
- **FSR4 Support:** Requires RDNA4 GPU (RX 9000 series) for full FSR4
- **RDNA3 Cards:** Need specific workarounds included in the tool
- **Steam Restart:** Required after applying launch options
- **Backup Safety:** All original files are backed up before installation

## 🐛 Troubleshooting

### FSR4 DLL Issues
- Use Menu Option 7 to select/change FSR4 version
- Ensure correct GPU architecture (RDNA4 for FSR4)
- Check Steam compatdata folder permissions

### OptiScaler Not Working
- Verify `WINEDLLOVERRIDES="dxgi=n,b"` in launch options
- Press INSERT in-game to open OptiScaler overlay
- Try "Disable DLSS FG" launch option variant

### Steam Games Not Detected
- Verify Steam installation paths
- Check manifest files in steamapps directory
- Ensure Steam is properly installed

## 📋 Requirements

- **OS:** Arch Linux (or compatible)
- **GPU:** AMD RDNA3/RDNA4 for FSR4 features
- **Software:** Steam, Python 3.6+, python-requests, p7zip
- **Games:** Steam games with DLSS/FSR2+ support

## 🤝 Contributing

This tool is designed for Arch Linux users who want easy OptiScaler management. Feel free to report issues or suggest improvements.

## 📄 License

This project is provided as-is for educational and personal use. OptiScaler is developed by the OptiScaler team. FSR4 DLLs are provided by AMD.

## 🔗 Related Projects

- [OptiScaler](https://github.com/optiscaler/OptiScaler) - The core OptiScaler project
- [AMD FidelityFX](https://github.com/GPUOpen-Effects/FidelityFX-FSR) - AMD's FSR technology

---

**Made for Arch Linux users who want hassle-free OptiScaler management with FSR4 support! 🚀**