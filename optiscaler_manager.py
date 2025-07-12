#!/usr/bin/env python3

import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import configparser

try:
    import requests
except ImportError:
    print("Missing required module: requests")
    print("\nPlease install it using one of these methods:")
    print("1. pip install requests")
    print("2. pip install --user requests")
    print("3. sudo pacman -S python-requests (Arch Linux)")
    print("4. python -m pip install requests")
    sys.exit(1)

class OptiScalerManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "optiscaler_manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.installs_file = self.config_dir / "installations.json"
        self.steam_path = self._find_steam_path()
        self.github_api_url = "https://api.github.com/repos/optiscaler/OptiScaler/releases"
        self.fsr4_dll_path = self._find_fsr4_dll()
        
    def _find_steam_path(self) -> Optional[Path]:
        steam_paths = [
            Path.home() / ".steam" / "steam",
            Path.home() / ".local" / "share" / "Steam",
            Path("/usr/share/steam"),
        ]
        for path in steam_paths:
            if path.exists():
                return path
        return None

    def _find_fsr4_dll(self) -> Optional[Path]:
        # Check config directory first (user's selected version)
        config_dll = self.config_dir / "amdxcffx64.dll"
        if config_dll.exists():
            return config_dll
            
        search_paths = [
            # Current directory
            Path.cwd() / "amdxcffx64.dll",
            # Script directory
            Path(__file__).parent / "amdxcffx64.dll",
            # Common locations
            Path.home() / "Downloads" / "amdxcffx64.dll",
            Path("/usr/lib/amdxcffx64.dll"),
            Path("/usr/local/lib/amdxcffx64.dll"),
            # Search in common FSR directories
            Path.home() / "Documents" / "fsr4" / "FSR 4.0" / "FSR 4.0.1" / "amdxcffx64.dll",
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        # Search for FSR directories and bundled versions
        fsr_search_dirs = [
            Path.cwd() / "fsr4_dlls",  # Bundled with script
            Path(__file__).parent / "fsr4_dlls",  # Script directory
            Path.home() / "Documents" / "fsr4",
            Path.home() / "Downloads",
        ]
        
        for search_dir in fsr_search_dirs:
            if search_dir.exists():
                for fsr_dir in search_dir.rglob("*FSR*"):
                    if fsr_dir.is_dir():
                        dll_file = fsr_dir / "amdxcffx64.dll"
                        if dll_file.exists():
                            return dll_file
        
        return None

    def find_available_fsr4_versions(self) -> Dict[str, Path]:
        versions = {}
        
        # Search for bundled FSR4 DLLs
        fsr_search_dirs = [
            Path.cwd() / "fsr4_dlls",
            Path(__file__).parent / "fsr4_dlls",
            Path.home() / "Documents" / "fsr4",
            Path.home() / "Downloads",
        ]
        
        for search_dir in fsr_search_dirs:
            if not search_dir.exists():
                continue
                
            # Look for version directories
            for version_dir in search_dir.iterdir():
                if version_dir.is_dir():
                    dll_file = version_dir / "amdxcffx64.dll"
                    if dll_file.exists():
                        version_name = version_dir.name
                        versions[version_name] = dll_file
            
            # Also check direct DLL files with version names
            for dll_file in search_dir.glob("**/amdxcffx64*.dll"):
                if dll_file.exists():
                    parent_name = dll_file.parent.name
                    if "4.0" in parent_name or "FSR" in parent_name:
                        versions[parent_name] = dll_file
        
        return versions

    def select_fsr4_version(self) -> bool:
        versions = self.find_available_fsr4_versions()
        
        if not versions:
            print("No FSR4 DLL versions found in bundled directories.")
            return self.download_fsr4_dll()
        
        print("\n=== Available FSR4 DLL Versions ===")
        version_list = list(versions.items())
        
        for i, (version_name, dll_path) in enumerate(version_list, 1):
            print(f"{i}. {version_name}")
            print(f"   Path: {dll_path}")
        
        print(f"{len(version_list) + 1}. Browse for custom DLL")
        print(f"{len(version_list) + 2}. Cancel")
        
        try:
            choice = int(input(f"\nSelect FSR4 version (1-{len(version_list) + 2}): "))
            
            if 1 <= choice <= len(version_list):
                selected_version, selected_path = version_list[choice - 1]
                
                # Copy selected version to config directory
                target_dll = self.config_dir / "amdxcffx64.dll"
                shutil.copy2(selected_path, target_dll)
                
                print(f"✓ Selected FSR4 version: {selected_version}")
                print(f"✓ Copied to: {target_dll}")
                
                self.fsr4_dll_path = target_dll
                return True
                
            elif choice == len(version_list) + 1:
                return self.download_fsr4_dll()
                
            else:
                print("Cancelled FSR4 version selection")
                return False
                
        except (ValueError, IndexError):
            print("Invalid selection")
            return False

    def download_fsr4_dll(self) -> bool:
        print("amdxcffx64.dll not found. This file is required for FSR4 functionality.")
        print("Please obtain amdxcffx64.dll from your system32 folder and place it in one of these locations:")
        print(f"1. Current directory: {Path.cwd()}")
        print(f"2. Script directory: {Path(__file__).parent}")
        print(f"3. Config directory: {self.config_dir}")
        print("\nYou can copy it from: C:\\Windows\\System32\\amdxcffx64.dll (on Windows)")
        print("Or from your Wine prefix system32 folder if you have it installed there.")
        
        choice = input("\nDo you want to specify a custom path to amdxcffx64.dll? (y/n): ").lower()
        if choice == 'y':
            custom_path = input("Enter full path to amdxcffx64.dll: ").strip()
            source_dll = Path(custom_path)
            if source_dll.exists():
                target_dll = self.config_dir / "amdxcffx64.dll"
                try:
                    shutil.copy2(source_dll, target_dll)
                    self.fsr4_dll_path = target_dll
                    print(f"Copied amdxcffx64.dll to {target_dll}")
                    return True
                except Exception as e:
                    print(f"Error copying DLL: {e}")
            else:
                print("File not found at specified path")
        
        return False

    def get_steam_games(self) -> List[Dict]:
        if not self.steam_path:
            print("Steam installation not found")
            return []
        
        games = []
        steamapps_path = self.steam_path / "steamapps"
        
        for manifest_file in steamapps_path.glob("appmanifest_*.acf"):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                app_id = None
                name = None
                install_dir = None
                
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('"appid"'):
                        app_id = line.split('"')[3]
                    elif line.startswith('"name"'):
                        name = line.split('"')[3]
                    elif line.startswith('"installdir"'):
                        install_dir = line.split('"')[3]
                
                if app_id and name and install_dir:
                    game_path = steamapps_path / "common" / install_dir
                    if game_path.exists():
                        games.append({
                            "app_id": app_id,
                            "name": name,
                            "install_dir": install_dir,
                            "path": str(game_path)
                        })
            except Exception as e:
                print(f"Error reading manifest {manifest_file}: {e}")
        
        return sorted(games, key=lambda x: x["name"])

    def find_game_executable_paths(self, game_path: str) -> List[str]:
        game_dir = Path(game_path)
        exe_paths = []
        
        common_exe_patterns = [
            "*.exe",
            "**/Binaries/Win64/*.exe",
            "**/Game/Binaries/Win64/*.exe",
            "**/Content/Engine/Plugins/Runtime/Nvidia/DLSS/Binaries/ThirdParty/Win64",
            "**/*_shipping.exe"
        ]
        
        for pattern in common_exe_patterns:
            for exe_file in game_dir.glob(pattern):
                if exe_file.is_file() and not exe_file.name.startswith("UE"):
                    exe_paths.append(str(exe_file.parent))
        
        return list(set(exe_paths))

    def get_compatdata_path(self, app_id: str) -> Optional[Path]:
        if not self.steam_path:
            return None
        
        compatdata_path = self.steam_path / "steamapps" / "compatdata" / app_id
        if compatdata_path.exists():
            return compatdata_path
        return None

    def copy_fsr4_dll_to_compatdata(self, app_id: str) -> bool:
        if not self.fsr4_dll_path or not self.fsr4_dll_path.exists():
            print("FSR4 DLL not found. Please select a version...")
            if not self.select_fsr4_version():
                return False
        
        compatdata_path = self.get_compatdata_path(app_id)
        if not compatdata_path:
            print(f"Compatdata folder not found for app ID {app_id}")
            return False
        
        system32_path = compatdata_path / "pfx" / "drive_c" / "windows" / "system32"
        system32_path.mkdir(parents=True, exist_ok=True)
        
        target_dll = system32_path / "amdxcffx64.dll"
        
        try:
            shutil.copy2(self.fsr4_dll_path, target_dll)
            print(f"Copied amdxcffx64.dll to {target_dll}")
            return True
        except Exception as e:
            print(f"Error copying FSR4 DLL: {e}")
            return False

    def download_latest_nightly(self) -> Optional[str]:
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            releases = response.json()
            
            for release in releases:
                if release.get("prerelease", False) or release.get("tag_name") == "nightly":
                    for asset in release["assets"]:
                        if asset["name"].endswith((".zip", ".7z")):
                            download_url = asset["browser_download_url"]
                            filename = asset["name"]
                            
                            print(f"Downloading {filename}...")
                            zip_response = requests.get(download_url)
                            zip_response.raise_for_status()
                            
                            download_path = self.config_dir / filename
                            with open(download_path, "wb") as f:
                                f.write(zip_response.content)
                            
                            return str(download_path)
            
            # If no nightly found, try latest stable release
            if releases:
                latest_release = releases[0]
                for asset in latest_release["assets"]:
                    if asset["name"].endswith((".zip", ".7z")):
                        download_url = asset["browser_download_url"]
                        filename = asset["name"]
                        
                        print(f"No nightly found, downloading latest stable: {filename}...")
                        zip_response = requests.get(download_url)
                        zip_response.raise_for_status()
                        
                        download_path = self.config_dir / filename
                        with open(download_path, "wb") as f:
                            f.write(zip_response.content)
                        
                        return str(download_path)
            
            print("No releases found")
            return None
            
        except Exception as e:
            print(f"Error downloading build: {e}")
            return None

    def extract_optiscaler(self, archive_path: str, target_dir: str) -> bool:
        try:
            archive_file = Path(archive_path)
            
            if archive_file.suffix.lower() == '.7z':
                # Use 7z command to extract
                result = subprocess.run(['7z', 'x', archive_path, f'-o{target_dir}', '-y'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"7z extraction failed: {result.stderr}")
                    return False
            else:
                # Use zipfile for .zip files
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
            
            return True
        except FileNotFoundError:
            print("7z command not found. Please install p7zip: sudo pacman -S p7zip")
            return False
        except Exception as e:
            print(f"Error extracting OptiScaler: {e}")
            return False

    def backup_original_files(self, target_dir: str) -> Dict[str, str]:
        backup_map = {}
        target_path = Path(target_dir)
        
        files_to_backup = [
            "nvngx.dll", "libxess.dll", "amd_fidelityfx_fsr2.dll", 
            "amd_fidelityfx_fsr3.dll", "ffx_fsr2_api_x64.dll"
        ]
        
        for filename in files_to_backup:
            original_file = target_path / filename
            if original_file.exists():
                backup_file = target_path / f"{filename}.optiscaler_backup"
                shutil.copy2(original_file, backup_file)
                backup_map[filename] = str(backup_file)
        
        return backup_map

    def install_optiscaler(self, game_info: Dict, exe_path: str, zip_path: str) -> bool:
        target_dir = Path(exe_path)
        
        backup_map = self.backup_original_files(str(target_dir))
        
        if not self.extract_optiscaler(zip_path, str(target_dir)):
            return False
        
        setup_bat = target_dir / "OptiScaler Setup.bat"
        if setup_bat.exists():
            try:
                subprocess.run(["wine", str(setup_bat)], cwd=str(target_dir), check=True)
            except subprocess.CalledProcessError:
                print("Auto-setup failed, manual configuration may be needed")
        
        self.run_optiscaler_setup(str(target_dir))
        
        self.configure_optiscaler_ini(str(target_dir))
        
        fsr4_dll_copied = self.copy_fsr4_dll_to_compatdata(game_info["app_id"])
        
        install_info = {
            "game": game_info,
            "install_path": str(target_dir),
            "timestamp": datetime.now().isoformat(),
            "backup_files": backup_map,
            "zip_source": zip_path,
            "fsr4_dll_copied": fsr4_dll_copied
        }
        
        self.save_installation(install_info)
        return True

    def run_optiscaler_setup(self, install_dir: str):
        install_path = Path(install_dir)
        
        # Look for setup scripts
        setup_scripts = [
            install_path / "setup_linux.sh",
            install_path / "OptiScaler Setup.sh",
            install_path / "setup.sh"
        ]
        
        for setup_script in setup_scripts:
            if setup_script.exists():
                try:
                    print(f"Found OptiScaler setup script: {setup_script.name}")
                    # Make sure it's executable
                    setup_script.chmod(0o755)
                    
                    print("Opening interactive setup window...")
                    print("Please configure your OptiScaler settings in the terminal window that opens.")
                    
                    # Try different terminal emulators in order of preference
                    terminals = [
                        ["konsole", "--workdir", str(install_path), "-e", str(setup_script)],
                        ["gnome-terminal", "--working-directory", str(install_path), "--", str(setup_script)],
                        ["xfce4-terminal", "--working-directory", str(install_path), "-e", str(setup_script)],
                        ["alacritty", "--working-directory", str(install_path), "-e", str(setup_script)],
                        ["kitty", "--directory", str(install_path), str(setup_script)],
                        ["terminator", "--working-directory", str(install_path), "-e", str(setup_script)],
                        ["xterm", "-e", f"cd '{install_path}' && {setup_script}"]
                    ]
                    
                    script_launched = False
                    for terminal_cmd in terminals:
                        try:
                            # Check if terminal exists
                            subprocess.run(["which", terminal_cmd[0]], 
                                         capture_output=True, check=True)
                            
                            # Launch the terminal with the setup script
                            subprocess.Popen(terminal_cmd)
                            print(f"Launched setup script in {terminal_cmd[0]}")
                            script_launched = True
                            
                            # Wait for user to indicate completion
                            input("\nPress Enter after you have completed the OptiScaler setup...")
                            break
                            
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    if not script_launched:
                        print("No suitable terminal emulator found.")
                        print(f"Please manually run: {setup_script}")
                        print("Available terminal commands to try:")
                        print("  konsole --workdir . -e ./setup_linux.sh")
                        print("  gnome-terminal --working-directory . -- ./setup_linux.sh")
                        print("  xterm -e './setup_linux.sh'")
                        
                        choice = input("\nHave you run the setup script manually? (y/n): ").lower()
                        if choice != 'y':
                            print("Please run the setup script before continuing.")
                            return
                    
                except Exception as e:
                    print(f"Error launching setup script: {e}")
                    print(f"Please manually run: {setup_script}")
                
                break
        else:
            print("No OptiScaler setup script found - manual configuration may be needed")

    def configure_optiscaler_ini(self, install_dir: str):
        ini_path = Path(install_dir) / "OptiScaler.ini"
        
        print(f"Configuring OptiScaler.ini at: {ini_path}")
        
        if not ini_path.exists():
            print("Creating new OptiScaler.ini file")
            ini_content = """[OptiScaler]
Fsr4Update=true
Dx12Upscaler=auto
ColorResourceBarrier=auto
MotionVectorResourceBarrier=auto
OverrideNvapiDll=auto
"""
            with open(ini_path, 'w') as f:
                f.write(ini_content)
            print("Created OptiScaler.ini with Fsr4Update=true")
        else:
            print("OptiScaler.ini exists, updating Fsr4Update setting")
            
            # Read the file manually to preserve formatting
            with open(ini_path, 'r') as f:
                lines = f.readlines()
            
            # Find and update the Fsr4Update line
            fsr4_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith('Fsr4Update='):
                    lines[i] = 'Fsr4Update=true\n'
                    fsr4_found = True
                    print("Updated existing Fsr4Update=true")
                    break
            
            # If not found, add it to the OptiScaler section
            if not fsr4_found:
                in_optiscaler_section = False
                for i, line in enumerate(lines):
                    if line.strip() == '[OptiScaler]':
                        in_optiscaler_section = True
                        continue
                    if in_optiscaler_section and (line.startswith('[') or i == len(lines) - 1):
                        # Insert before next section or at end
                        insert_pos = i if line.startswith('[') else i + 1
                        lines.insert(insert_pos, 'Fsr4Update=true\n')
                        print("Added Fsr4Update=true to OptiScaler section")
                        break
                else:
                    # No OptiScaler section found, add it
                    lines.append('\n[OptiScaler]\nFsr4Update=true\n')
                    print("Added new OptiScaler section with Fsr4Update=true")
            
            # Write back to file
            with open(ini_path, 'w') as f:
                f.writelines(lines)
        
        # Verify the setting was applied
        if ini_path.exists():
            with open(ini_path, 'r') as f:
                content = f.read()
                if 'Fsr4Update=true' in content:
                    print("✓ Confirmed: Fsr4Update=true is set in OptiScaler.ini")
                else:
                    print("⚠ Warning: Fsr4Update=true not found in OptiScaler.ini")
                    print("INI content preview:")
                    print(content[:500] + "..." if len(content) > 500 else content)

    def save_installation(self, install_info: Dict):
        installs = self.load_installations()
        installs.append(install_info)
        
        with open(self.installs_file, 'w') as f:
            json.dump(installs, f, indent=2)

    def load_installations(self) -> List[Dict]:
        if self.installs_file.exists():
            with open(self.installs_file, 'r') as f:
                return json.load(f)
        return []

    def uninstall_optiscaler(self, install_info: Dict) -> bool:
        install_path = Path(install_info["install_path"])
        
        # First, try to run the OptiScaler removal script if it exists
        self.run_optiscaler_removal_script(str(install_path))
        
        # Then manually clean up any remaining files
        optiscaler_files = [
            "OptiScaler.dll", "OptiScaler.ini", "OptiScaler Setup.bat",
            "nvngx.dll", "libxess.dll", "amd_fidelityfx_fsr2.dll",
            "amd_fidelityfx_fsr3.dll", "ffx_fsr2_api_x64.dll",
            "setup_linux.sh", "remove_optiscaler.sh"
        ]
        
        print("Cleaning up remaining OptiScaler files...")
        for filename in optiscaler_files:
            file_path = install_path / filename
            if file_path.exists():
                file_path.unlink()
                print(f"Removed: {filename}")
        
        # Restore original backed up files
        print("Restoring original game files...")
        for original_name, backup_path in install_info.get("backup_files", {}).items():
            backup_file = Path(backup_path)
            original_file = install_path / original_name
            
            if backup_file.exists():
                shutil.move(backup_file, original_file)
                print(f"Restored: {original_name}")
        
        # Remove FSR4 DLL from compatdata
        if install_info.get("fsr4_dll_copied", False):
            self.remove_fsr4_dll_from_compatdata(install_info["game"]["app_id"])
        
        return True

    def run_optiscaler_removal_script(self, install_dir: str):
        install_path = Path(install_dir)
        
        # Look for removal scripts
        removal_scripts = [
            install_path / "remove_optiscaler.sh",
            install_path / "uninstall_optiscaler.sh",
            install_path / "remove.sh",
            install_path / "uninstall.sh"
        ]
        
        for removal_script in removal_scripts:
            if removal_script.exists():
                try:
                    print(f"Found OptiScaler removal script: {removal_script.name}")
                    # Make sure it's executable
                    removal_script.chmod(0o755)
                    
                    print("Opening interactive removal window...")
                    print("Please confirm removal options in the terminal window that opens.")
                    
                    # Try different terminal emulators in order of preference
                    terminals = [
                        ["konsole", "--workdir", str(install_path), "-e", str(removal_script)],
                        ["gnome-terminal", "--working-directory", str(install_path), "--", str(removal_script)],
                        ["xfce4-terminal", "--working-directory", str(install_path), "-e", str(removal_script)],
                        ["alacritty", "--working-directory", str(install_path), "-e", str(removal_script)],
                        ["kitty", "--directory", str(install_path), str(removal_script)],
                        ["terminator", "--working-directory", str(install_path), "-e", str(removal_script)],
                        ["xterm", "-e", f"cd '{install_path}' && {removal_script}"]
                    ]
                    
                    script_launched = False
                    for terminal_cmd in terminals:
                        try:
                            # Check if terminal exists
                            subprocess.run(["which", terminal_cmd[0]], 
                                         capture_output=True, check=True)
                            
                            # Launch the terminal with the removal script
                            subprocess.Popen(terminal_cmd)
                            print(f"Launched removal script in {terminal_cmd[0]}")
                            script_launched = True
                            
                            # Wait for user to indicate completion
                            input("\nPress Enter after you have completed the OptiScaler removal...")
                            break
                            
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    if not script_launched:
                        print("No suitable terminal emulator found.")
                        print(f"Please manually run: {removal_script}")
                        print("Available terminal commands to try:")
                        print("  konsole --workdir . -e ./remove_optiscaler.sh")
                        print("  gnome-terminal --working-directory . -- ./remove_optiscaler.sh")
                        print("  xterm -e './remove_optiscaler.sh'")
                        
                        choice = input("\nHave you run the removal script manually? (y/n): ").lower()
                        if choice != 'y':
                            print("Please run the removal script before continuing.")
                            return
                    
                    print("OptiScaler removal script completed.")
                    
                except Exception as e:
                    print(f"Error launching removal script: {e}")
                    print(f"Please manually run: {removal_script}")
                
                break
        else:
            print("No OptiScaler removal script found - proceeding with manual cleanup")

    def remove_fsr4_dll_from_compatdata(self, app_id: str) -> bool:
        compatdata_path = self.get_compatdata_path(app_id)
        if not compatdata_path:
            return False
        
        system32_path = compatdata_path / "pfx" / "drive_c" / "windows" / "system32"
        target_dll = system32_path / "amdxcffx64.dll"
        
        try:
            if target_dll.exists():
                target_dll.unlink()
                print(f"Removed amdxcffx64.dll from {target_dll}")
            return True
        except Exception as e:
            print(f"Error removing FSR4 DLL: {e}")
            return False

    def add_steam_launch_options(self, app_id: str, rdna3_workaround: bool = False):
        print(f"Steam launch options for App ID {app_id}:")
        print("\n=== OptiScaler Basic Setup ===")
        
        # Essential OptiScaler command
        optiscaler_base = 'WINEDLLOVERRIDES="dxgi=n,b"'
        
        if rdna3_workaround:
            basic_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%'
        else:
            basic_cmd = f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 %command%'
        
        print(f"Basic: {basic_cmd}")
        
        print("\n=== OptiScaler Advanced Options ===")
        print("For better performance and compatibility:")
        
        advanced_options = [
            "DXVK_ASYNC=1",
            "PROTON_ENABLE_NVAPI=1", 
            "PROTON_HIDE_NVIDIA_GPU=0",
            "VKD3D_CONFIG=dxr11,dxr",
            "WINE_CPU_TOPOLOGY=4:2"
        ]
        
        if rdna3_workaround:
            full_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc {" ".join(advanced_options)} %command%'
        else:
            full_cmd = f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 {" ".join(advanced_options)} %command%'
        
        print(f"Advanced: {full_cmd}")
        
        print("\n=== OptiScaler Debugging ===")
        if rdna3_workaround:
            debug_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%'
        else:
            debug_cmd = f'{optiscaler_base} PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 %command%'
        print(f"Debug mode: {debug_cmd}")
        
        print("\n=== Anti-Lag 2 (Experimental) ===")
        if rdna3_workaround:
            antilag_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt,nggc %command%'
        else:
            antilag_cmd = f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt %command%'
        print(f"With Anti-Lag 2: {antilag_cmd}")
        
        print("\n=== Game-Specific Tweaks ===")
        print("For Unreal Engine games:")
        ue_cmd = basic_cmd.replace('%command%', '-dx12 %command%')
        print(f"UE + DX12: {ue_cmd}")
        
        print("\nFor games with DLSS Frame Generation issues:")
        no_fg_cmd = basic_cmd.replace('dxgi=n,b', 'dxgi=n,b;nvngx=n,b')
        print(f"Disable DLSS FG: {no_fg_cmd}")
        
        print("\n=== IMPORTANT NOTES ===")
        print("• WINEDLLOVERRIDES=\"dxgi=n,b\" is REQUIRED for OptiScaler to work")
        print("• Start with 'Basic' command first")
        print("• If OptiScaler overlay doesn't appear, try the 'Disable DLSS FG' version")
        print("• Press INSERT in-game to open OptiScaler overlay")
        
        print("\n=== AUTOMATIC APPLICATION ===")
        apply_choice = input("Would you like to automatically apply launch options to Steam? (y/n): ").lower()
        
        if apply_choice == 'y':
            if rdna3_workaround:
                option_choice = input("\nWhich RDNA3 option to apply?\n1. Basic RDNA3 (with DXIL_SPIRV_CONFIG)\n2. Advanced RDNA3\n3. Debug RDNA3\n4. Anti-Lag 2 RDNA3\nEnter choice (1-4): ").strip()
            else:
                option_choice = input("\nWhich option to apply?\n1. Basic\n2. Advanced\n3. Debug\n4. Anti-Lag 2\nEnter choice (1-4): ").strip()
            
            selected_cmd = basic_cmd
            if option_choice == "2":
                selected_cmd = full_cmd
            elif option_choice == "3":
                selected_cmd = debug_cmd
            elif option_choice == "4":
                selected_cmd = antilag_cmd
            
            if self.apply_steam_launch_options(app_id, selected_cmd):
                print("✓ Launch options applied successfully!")
                print("You can now launch the game directly from Steam.")
            else:
                print("⚠ Automatic application failed. Please apply manually:")
                print(f"Launch command: {selected_cmd}")
        else:
            print("\nTo apply manually:")
            print("1. Right-click game in Steam")
            print("2. Properties > General > Launch Options") 
            print("3. Copy and paste ONE of the above commands")
            print("4. Launch game and press INSERT for OptiScaler overlay")

    def apply_steam_launch_options(self, app_id: str, launch_command: str) -> bool:
        try:
            if not self.steam_path:
                print("Steam path not found")
                return False
            
            # Find Steam user directories
            userdata_path = self.steam_path / "userdata"
            if not userdata_path.exists():
                print("Steam userdata directory not found")
                return False
            
            # Look for Steam user ID directories
            user_dirs = [d for d in userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            
            if not user_dirs:
                print("No Steam user directories found")
                return False
            
            # Use the first (or most recent) user directory
            user_dir = max(user_dirs, key=lambda x: x.stat().st_mtime)
            
            # Path to localconfig.vdf
            localconfig_path = user_dir / "config" / "localconfig.vdf"
            
            if not localconfig_path.exists():
                print("Steam localconfig.vdf not found")
                return False
            
            # Read the current config
            with open(localconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                config_content = f.read()
            
            # Look for the app's launch options section
            app_section_start = config_content.find(f'"{app_id}"')
            if app_section_start == -1:
                print(f"Game with App ID {app_id} not found in Steam config")
                return False
            
            # Find the LaunchOptions within this app section
            section_start = config_content.rfind('{', 0, app_section_start)
            section_end = config_content.find('}', app_section_start)
            
            if section_start == -1 or section_end == -1:
                print("Could not locate app section in Steam config")
                return False
            
            app_section = config_content[section_start:section_end + 1]
            
            # Check if LaunchOptions already exists
            launch_options_pattern = r'"LaunchOptions"\s*"([^"]*)"'
            
            import re
            match = re.search(launch_options_pattern, app_section)
            
            if match:
                # Replace existing launch options
                old_options = match.group(1)
                new_section = app_section.replace(f'"LaunchOptions"\t\t"{old_options}"', f'"LaunchOptions"\t\t"{launch_command}"')
                print(f"Replaced existing launch options: '{old_options}' -> '{launch_command}'")
            else:
                # Add new launch options before the closing brace
                insert_pos = app_section.rfind('}')
                new_section = app_section[:insert_pos] + f'\t\t\t"LaunchOptions"\t\t"{launch_command}"\n' + app_section[insert_pos:]
                print(f"Added new launch options: '{launch_command}'")
            
            # Replace the section in the full config
            new_config = config_content[:section_start] + new_section + config_content[section_end + 1:]
            
            # Backup the original file
            backup_path = localconfig_path.with_suffix('.vdf.optiscaler_backup')
            shutil.copy2(localconfig_path, backup_path)
            print(f"Backed up original config to: {backup_path}")
            
            # Write the new config
            with open(localconfig_path, 'w', encoding='utf-8') as f:
                f.write(new_config)
            
            print("Steam configuration updated successfully!")
            print("Note: Steam must be restarted for changes to take effect.")
            
            restart_choice = input("Would you like to restart Steam now? (y/n): ").lower()
            if restart_choice == 'y':
                self.restart_steam()
            
            return True
            
        except Exception as e:
            print(f"Error applying launch options: {e}")
            return False
    
    def restart_steam(self):
        try:
            print("Stopping Steam...")
            subprocess.run(["pkill", "steam"], check=False)
            subprocess.run(["pkill", "Steam"], check=False)
            
            # Wait a moment
            import time
            time.sleep(2)
            
            print("Starting Steam...")
            subprocess.Popen(["steam"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Steam is restarting...")
            
        except Exception as e:
            print(f"Error restarting Steam: {e}")
            print("Please manually restart Steam to apply launch options.")

def main():
    manager = OptiScalerManager()
    
    while True:
        print("\n=== OptiScaler Manager ===")
        print("1. List Steam games")
        print("2. Install OptiScaler")
        print("3. View installations")
        print("4. Uninstall OptiScaler")
        print("5. Download latest nightly")
        print("6. Add Steam launch options")
        print("7. Manage FSR4 DLL")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            games = manager.get_steam_games()
            for i, game in enumerate(games, 1):
                print(f"{i}. {game['name']} (ID: {game['app_id']})")
        
        elif choice == "2":
            games = manager.get_steam_games()
            if not games:
                print("No Steam games found")
                continue
                
            print("\nSelect a game:")
            for i, game in enumerate(games, 1):
                print(f"{i}. {game['name']}")
            
            try:
                game_idx = int(input("Game number: ")) - 1
                selected_game = games[game_idx]
                
                exe_paths = manager.find_game_executable_paths(selected_game["path"])
                if not exe_paths:
                    print("No suitable executable paths found")
                    continue
                
                print("\nSelect installation directory:")
                for i, path in enumerate(exe_paths, 1):
                    print(f"{i}. {path}")
                
                path_idx = int(input("Path number: ")) - 1
                selected_path = exe_paths[path_idx]
                
                zip_path = manager.download_latest_nightly()
                if not zip_path:
                    continue
                
                if manager.install_optiscaler(selected_game, selected_path, zip_path):
                    print("OptiScaler installed successfully!")
                else:
                    print("Installation failed")
                    
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "3":
            installs = manager.load_installations()
            if not installs:
                print("No installations found")
                continue
                
            for i, install in enumerate(installs, 1):
                print(f"{i}. {install['game']['name']} - {install['timestamp']}")
                print(f"   Path: {install['install_path']}")
        
        elif choice == "4":
            installs = manager.load_installations()
            if not installs:
                print("No installations to uninstall")
                continue
                
            print("\nSelect installation to uninstall:")
            for i, install in enumerate(installs, 1):
                print(f"{i}. {install['game']['name']} - {install['timestamp']}")
            
            try:
                install_idx = int(input("Installation number: ")) - 1
                selected_install = installs[install_idx]
                
                if manager.uninstall_optiscaler(selected_install):
                    installs.pop(install_idx)
                    with open(manager.installs_file, 'w') as f:
                        json.dump(installs, f, indent=2)
                    print("OptiScaler uninstalled successfully!")
                else:
                    print("Uninstallation failed")
                    
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "5":
            zip_path = manager.download_latest_nightly()
            if zip_path:
                print(f"Downloaded to: {zip_path}")
        
        elif choice == "6":
            games = manager.get_steam_games()
            if not games:
                print("No Steam games found")
                continue
                
            print("\nSelect a game:")
            for i, game in enumerate(games, 1):
                print(f"{i}. {game['name']}")
            
            try:
                game_idx = int(input("Game number: ")) - 1
                selected_game = games[game_idx]
                
                rdna3 = input("RDNA3 workaround needed? (y/n): ").lower() == 'y'
                manager.add_steam_launch_options(selected_game["app_id"], rdna3)
                
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "7":
            print("\n=== FSR4 DLL Management ===")
            if manager.fsr4_dll_path and manager.fsr4_dll_path.exists():
                print(f"Current FSR4 DLL: {manager.fsr4_dll_path}")
                
                # Try to identify current version
                current_dll = manager.fsr4_dll_path
                version_info = "Unknown"
                
                # Check if it's in a version directory
                if "4.0.1" in str(current_dll):
                    version_info = "FSR 4.0.1"
                elif "4.0" in str(current_dll):
                    version_info = "FSR 4.0"
                
                print(f"Detected version: {version_info}")
                
                print("\n1. Change FSR4 DLL version")
                print("2. View available versions")
                print("3. Use current version")
                
                sub_choice = input("Enter choice (1-3): ").strip()
                
                if sub_choice == "1":
                    manager.select_fsr4_version()
                elif sub_choice == "2":
                    versions = manager.find_available_fsr4_versions()
                    if versions:
                        print("\nAvailable FSR4 versions:")
                        for name, path in versions.items():
                            print(f"- {name}: {path}")
                    else:
                        print("No bundled FSR4 versions found")
                elif sub_choice == "3":
                    print("Continuing with current FSR4 DLL")
            else:
                print("No FSR4 DLL found")
                print("\n1. Select from available versions")
                print("2. Browse for custom DLL")
                
                sub_choice = input("Enter choice (1-2): ").strip()
                
                if sub_choice == "1":
                    manager.select_fsr4_version()
                elif sub_choice == "2":
                    manager.download_fsr4_dll()
        
        elif choice == "8":
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()