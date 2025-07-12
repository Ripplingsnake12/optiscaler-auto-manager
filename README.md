# OptiScaler Manager for Arch Linux

A comprehensive tool to manage OptiScaler installations on Steam games with FSR4 support.

## Features

- **Automatic nightly build downloads** from OptiScaler GitHub
- **Steam game detection** and selection
- **Smart installation paths** for different game engines
- **FSR4 DLL management** with automatic compatdata integration  
- **Timestamped installations** with full tracking
- **Complete uninstall** with file restoration
- **Steam launch options** for FSR4/RDNA3 configurations

## Prerequisites

```bash
# Install required packages
sudo pacman -S python-requests p7zip steam

# Or alternatively for Python package
pip install --user requests
```

## Setup

### 1. FSR4 DLL Setup (Required for FSR4)

Multiple FSR4 DLL versions are supported. Create the directory structure:

```bash
./create_fsr4_structure.sh
```

**Directory Structure:**
```
fsr4_dlls/
├── FSR 4.0/
│   └── amdxcffx64.dll
└── FSR 4.0.1/
    └── amdxcffx64.dll
```

**Getting amdxcffx64.dll versions:**
- Copy from Windows: `C:\Windows\System32\amdxcffx64.dll`
- Extract from Wine prefix system32 folder  
- Download from AMD driver packages
- Use bundled versions (if provided)

**Version Selection:**
- **Menu Option 7** - FSR4 DLL Management
- **Automatic detection** of available versions
- **Version switching** between installations
- **Custom DLL browsing** for other versions

### 2. Run OptiScaler Manager

```bash
python3 optiscaler_manager.py
```

## Usage

### Installation Process

1. **List Steam Games** - View all detected Steam games
2. **Install OptiScaler** - Select game and installation path
3. **Auto-configure** - Sets `Fsr4Update=true` in OptiScaler.ini
4. **FSR4 DLL Copy** - Automatically copies to game's compatdata system32 folder

### Steam Launch Options

The tool provides comprehensive launch commands:

**OptiScaler Basic (REQUIRED):**
- Standard: `WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%`
- RDNA3: `WINEDLLOVERRIDES="dxgi=n,b" DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%`

**Advanced Performance:**
- Full: `WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%`

**Game-Specific:**
- Unreal Engine: Add `-dx12` flag  
- DLSS FG Issues: `WINEDLLOVERRIDES="dxgi=n,b;nvngx=n,b"`
- Debugging: `PROTON_LOG=+all WINEDEBUG=+dll`
- Anti-Lag 2: `RADV_PERFTEST=rt,nggc`

**⚠️ CRITICAL:** `WINEDLLOVERRIDES="dxgi=n,b"` is **REQUIRED** for OptiScaler to function!

### Automatic Launch Options

The tool can automatically apply launch options to Steam:
1. **Select preferred option** (Basic, Advanced, Debug, Anti-Lag 2)
2. **Automatic Steam config modification** - Updates `localconfig.vdf`
3. **Steam restart** - Option to restart Steam automatically
4. **Backup creation** - Original config backed up before changes

**RDNA3 Special:** Automatically includes `DXIL_SPIRV_CONFIG=wmma_rdna3_workaround` for proper RDNA3 support.

### Game Engine Support

**Unreal Engine Games:**
- `Game/Binaries/Win64/`
- `Content/Engine/Plugins/Runtime/Nvidia/DLSS/Binaries/ThirdParty/Win64/`

**Other Engines:**
- Main executable directory
- Auto-detected based on file patterns

### Compatdata Integration

For each installation, the tool:
1. Copies `amdxcffx64.dll` to: `~/.steam/steam/steamapps/compatdata/{APP_ID}/pfx/drive_c/windows/system32/`
2. Tracks the copy for proper uninstall
3. Removes during uninstall process

## Configuration

**OptiScaler.ini Settings Applied:**
```ini
[OptiScaler]
Fsr4Update=true
Dx12Upscaler=auto
ColorResourceBarrier=auto
MotionVectorResourceBarrier=auto
OverrideNvapiDll=auto
```

## Installation Tracking

All installations are tracked in `~/.config/optiscaler_manager/installations.json` with:
- Game information and app ID
- Installation path and timestamp  
- Backup file locations
- FSR4 DLL copy status

## Uninstall Process

Complete restoration includes:
1. **Run interactive removal script** - Opens `remove_optiscaler.sh` in terminal window
2. **User confirms removal options** - Interactive menu for selective removal
3. **Manual cleanup** - Remove any remaining OptiScaler files
4. **Restore original files** - Restore backed-up game DLLs
5. **Remove FSR4 DLL** - Clean compatdata system32 folder
6. **Clean installation tracking** - Remove from installations.json

### Interactive Removal Scripts Supported:
- `remove_optiscaler.sh` (primary)
- `uninstall_optiscaler.sh`
- `remove.sh`
- `uninstall.sh`

## Menu Options

1. **List Steam games** - Show all detected games
2. **Install OptiScaler** - Full installation process
3. **View installations** - Show current installs
4. **Uninstall OptiScaler** - Complete removal
5. **Download latest nightly** - Get newest build
6. **Add Steam launch options** - Display launch commands
7. **Manage FSR4 DLL** - Select FSR4 version and manage DLLs
8. **Exit**

### FSR4 DLL Version Management

**Available Options:**
- **View current version** - Shows active FSR4 DLL and detected version
- **Change version** - Select from available FSR 4.0/4.0.1 versions
- **Browse custom** - Use DLL from custom location
- **Version detection** - Automatic identification of current version

**Supported Versions:**
- **FSR 4.0** - Original FSR4 release
- **FSR 4.0.1** - Updated FSR4 with improvements
- **Custom versions** - Any compatible amdxcffx64.dll

## Troubleshooting

**FSR4 DLL not found:**
- Run `./setup_fsr4.sh`
- Use menu option 7 to check status
- Manually place in `~/.config/optiscaler_manager/`

**Steam games not detected:**
- Check Steam installation paths
- Verify manifest files exist

**Installation fails:**
- Check game executable paths
- Ensure write permissions
- Verify OptiScaler download

## File Structure

```
.
├── optiscaler_manager.py      # Main application
├── setup_fsr4.sh            # FSR4 DLL setup
├── create_fsr4_structure.sh  # Create FSR4 directories
├── README.md                 # This file
├── fsr4_dlls/               # Bundled FSR4 versions
│   ├── FSR 4.0/
│   │   └── amdxcffx64.dll
│   └── FSR 4.0.1/
│       └── amdxcffx64.dll
└── ~/.config/optiscaler_manager/
    ├── installations.json    # Installation tracking
    ├── amdxcffx64.dll       # Selected FSR4 DLL
    └── *.7z                 # Downloaded builds
```

## Notes

- Only works with Steam games on Linux
- Requires FSR4 compatible GPU (RDNA4) for FSR4 features  
- RDNA3 cards need workarounds for FSR4
- Backs up original files before installation
- Timestamps all operations for tracking