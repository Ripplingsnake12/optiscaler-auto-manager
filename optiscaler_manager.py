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
            Path.home() / ".steam" / "root",
            Path.home() / "snap" / "steam" / "common" / ".steam" / "steam",
            Path("/var/lib/flatpak/app/com.valvesoftware.Steam/home/.steam/steam"),
            Path.home() / ".var" / "app" / "com.valvesoftware.Steam" / "home" / ".steam" / "steam",
        ]
        for path in steam_paths:
            if path.exists():
                print(f"Found Steam at: {path}")
                return path
        print("Steam installation not found in standard locations")
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

    def find_game_executable_paths(self, game_path: str) -> List[Dict[str, str]]:
        """Find all possible executable locations with details about what's in each folder"""
        game_dir = Path(game_path)
        exe_locations = []
        
        # Find all executable files and analyze them
        for exe_file in game_dir.rglob("*.exe"):
            if not exe_file.is_file():
                continue
                
            # Skip obvious non-game executables
            skip_paths = ["engine", "redist", "directx", "vcredist", "_commonredist", "tools", "crash"]
            skip_names = ["unins", "setup", "launcher", "redist", "vcredist", "directx", "crash"]
            
            path_str = str(exe_file.parent).lower()
            name_str = exe_file.name.lower()
            
            # Skip if in excluded paths or has excluded names
            if (any(skip in path_str for skip in skip_paths) or 
                any(skip in name_str for skip in skip_names)):
                continue
            
            # Determine the type/priority of this executable
            exe_type = "Other"
            priority = 3
            
            if exe_file.parent == game_dir:
                exe_type = "Main Game Directory"
                priority = 1
            elif "_shipping" in name_str:
                exe_type = "Shipping Executable (UE)"
                priority = 1
            elif any(folder in str(exe_file.parent).lower() for folder in ["bin/x64", "retail", "binaries/win64"]):
                exe_type = "Common Game Folder"
                priority = 2
            elif "ue4" in name_str or "ue5" in name_str:
                continue  # Skip UE engine executables
            
            # Create location info
            location_info = {
                "path": str(exe_file.parent),
                "exe_name": exe_file.name,
                "type": exe_type,
                "priority": priority,
                "relative_path": str(exe_file.parent.relative_to(game_dir))
            }
            
            # Check if we already have this path
            existing = next((loc for loc in exe_locations if loc["path"] == location_info["path"]), None)
            if existing:
                # If we find a better executable in the same folder, update it
                if priority < existing["priority"]:
                    existing.update(location_info)
            else:
                exe_locations.append(location_info)
        
        # Sort by priority (lower number = higher priority) then by path depth
        exe_locations.sort(key=lambda x: (x["priority"], len(Path(x["path"]).parts), x["path"]))
        
        return exe_locations

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

    def install_optiscaler(self, game_info: Dict, exe_location: Dict, zip_path: str) -> bool:
        target_dir = Path(exe_location["path"])
        
        print(f"Installing OptiScaler to: {target_dir}")
        print(f"Target executable: {exe_location['exe_name']}")
        print(f"Location type: {exe_location['type']}")
        
        backup_map = self.backup_original_files(str(target_dir))
        
        if not self.extract_optiscaler(zip_path, str(target_dir)):
            return False
        
        # Try to run Windows batch setup first if available
        setup_bat = target_dir / "OptiScaler Setup.bat"
        if setup_bat.exists():
            try:
                subprocess.run(["wine", str(setup_bat)], cwd=str(target_dir), check=True)
                print("Windows setup completed successfully")
            except subprocess.CalledProcessError:
                print("Windows auto-setup failed, proceeding with Linux setup")
        
        # Run Linux setup script in the correct directory
        self.run_optiscaler_setup(str(target_dir))
        
        # Configure INI file
        self.configure_optiscaler_ini(str(target_dir))
        
        # Copy FSR4 DLL to compatdata
        fsr4_dll_copied = self.copy_fsr4_dll_to_compatdata(game_info["app_id"])
        
        install_info = {
            "game": game_info,
            "install_path": str(target_dir),
            "exe_location": exe_location,
            "timestamp": datetime.now().isoformat(),
            "backup_files": backup_map,
            "zip_source": zip_path,
            "fsr4_dll_copied": fsr4_dll_copied
        }
        
        self.save_installation(install_info)
        return True

    def run_optiscaler_setup(self, install_dir: str):
        install_path = Path(install_dir)
        
        # Look for setup scripts (prioritize setup_linux.sh as it's the official name)
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
                    
                    print(f"Running setup script in directory: {install_path}")
                    
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
            "OptiScaler.dll", "OptiScaler.ini", "OptiScaler.log", "OptiScaler Setup.bat",
            "setup_linux.sh", "setup_windows.bat", "remove_optiscaler.sh",
            # Possible renamed OptiScaler DLL files
            "dxgi.dll", "winmm.dll", "version.dll", "dbghelp.dll", 
            "d3d12.dll", "wininet.dll", "winhttp.dll", "OptiScaler.asi",
            # Other DLSS/FSR files that might get installed
            "nvngx.dll", "libxess.dll", "amd_fidelityfx_fsr2.dll",
            "amd_fidelityfx_fsr3.dll", "ffx_fsr2_api_x64.dll"
        ]
        
        # Also remove directories created by OptiScaler
        optiscaler_dirs = [
            "D3D12_Optiscaler", "DlssOverrides", "Licenses"
        ]
        
        print("Cleaning up remaining OptiScaler files...")
        for filename in optiscaler_files:
            file_path = install_path / filename
            if file_path.exists():
                file_path.unlink()
                print(f"Removed: {filename}")
        
        # Remove OptiScaler directories
        for dirname in optiscaler_dirs:
            dir_path = install_path / dirname
            if dir_path.exists() and dir_path.is_dir():
                import shutil
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dirname}")
        
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
        
        # Look for removal scripts (prioritize remove_optiscaler.sh as it's created by setup_linux.sh)
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
                    
                    print(f"Running removal script in directory: {install_path}")
                    
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
        print(f"With MangoHUD: mangohud {basic_cmd}")
        
        print("\n=== OptiScaler Advanced Options ===")
        print("For better performance and compatibility:")
        print("Note: The setup_linux.sh script may have specified additional DLL overrides")
        
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
        print(f"Advanced + MangoHUD: mangohud {full_cmd}")
        
        print("\n=== OptiScaler Debugging ===")
        if rdna3_workaround:
            debug_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc %command%'
        else:
            debug_cmd = f'{optiscaler_base} PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 %command%'
        print(f"Debug mode: {debug_cmd}")
        print(f"Debug + MangoHUD: mangohud {debug_cmd}")
        
        print("\n=== Anti-Lag 2 (Experimental) ===")
        if rdna3_workaround:
            antilag_cmd = f'{optiscaler_base} DXIL_SPIRV_CONFIG=wmma_rdna3_workaround PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt,nggc %command%'
        else:
            antilag_cmd = f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt %command%'
        print(f"With Anti-Lag 2: {antilag_cmd}")
        print(f"Anti-Lag 2 + MangoHUD: mangohud {antilag_cmd}")
        
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
            # Ask about MangoHUD
            mangohud_choice = input("Include MangoHUD for performance monitoring? (y/n): ").lower()
            mangohud_prefix = "mangohud " if mangohud_choice == 'y' else ""
            
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
            
            # Add mangohud prefix if requested
            if mangohud_prefix:
                selected_cmd = mangohud_prefix + selected_cmd
            
            if self.apply_steam_launch_options(app_id, selected_cmd):
                print("✓ Launch options applied successfully!")
                print("You can now launch the game directly from Steam.")
            else:
                print("⚠ Automatic application failed. Trying to copy to clipboard...")
                try:
                    import subprocess
                    # Try to copy to clipboard using xclip or xsel
                    clipboard_commands = [
                        ['xclip', '-selection', 'clipboard'],
                        ['xsel', '--clipboard', '--input'],
                        ['wl-copy']  # Wayland
                    ]
                    
                    copied = False
                    for cmd in clipboard_commands:
                        try:
                            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
                            proc.communicate(input=selected_cmd.encode())
                            if proc.returncode == 0:
                                print(f"✓ Launch command copied to clipboard using {cmd[0]}!")
                                copied = True
                                break
                        except FileNotFoundError:
                            continue
                    
                    if not copied:
                        print("❌ Could not copy to clipboard (xclip/xsel/wl-copy not found)")
                except Exception as e:
                    print(f"❌ Clipboard copy failed: {e}")
                
                print("Please apply manually:")
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
                print("❌ Steam path not found. Please ensure Steam is installed.")
                return False
            
            print(f"🔍 Using Steam path: {self.steam_path}")
            
            # Find Steam user directories
            userdata_path = self.steam_path / "userdata"
            if not userdata_path.exists():
                print(f"❌ Steam userdata directory not found at: {userdata_path}")
                return False
            
            print(f"✓ Found userdata directory: {userdata_path}")
            
            # Look for Steam user ID directories
            user_dirs = [d for d in userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            
            if not user_dirs:
                print("❌ No Steam user directories found")
                available_dirs = list(userdata_path.iterdir())
                print(f"Available directories in userdata: {[d.name for d in available_dirs]}")
                return False
            
            print(f"✓ Found {len(user_dirs)} user directory(ies)")
            
            # Use the first (or most recent) user directory
            user_dir = max(user_dirs, key=lambda x: x.stat().st_mtime)
            print(f"🔍 Using user directory: {user_dir}")
            
            # Path to localconfig.vdf
            localconfig_path = user_dir / "config" / "localconfig.vdf"
            
            if not localconfig_path.exists():
                print(f"❌ Steam localconfig.vdf not found at: {localconfig_path}")
                config_dir = user_dir / "config"
                if config_dir.exists():
                    available_files = list(config_dir.iterdir())
                    print(f"Available files in config: {[f.name for f in available_files]}")
                return False
            
            print(f"✓ Found localconfig.vdf: {localconfig_path}")
            
            # Check if Steam is running (warn user but continue)
            import subprocess
            try:
                result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("⚠️ Warning: Steam appears to be running. Consider closing Steam first.")
                    print("   Steam may overwrite the changes when it exits.")
            except:
                pass  # pgrep not available or other error, continue anyway
            
            # Read the current config
            try:
                with open(localconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                    config_content = f.read()
            except PermissionError:
                print(f"❌ Permission denied reading {localconfig_path}")
                print("   Try running with sudo or change file permissions")
                return False
            except Exception as e:
                print(f"❌ Error reading config file: {e}")
                return False
            
            print(f"✓ Config file read successfully ({len(config_content)} characters)")
            
            # Look for the apps section first, then the specific app ID
            apps_section_start = config_content.find('"apps"')
            if apps_section_start == -1:
                print("❌ apps section not found in Steam config")
                print("   This may not be a valid Steam localconfig.vdf file")
                return False
            
            # Search for the app ID within the apps section
            app_section_start = config_content.find(f'"{app_id}"', apps_section_start)
            if app_section_start == -1:
                print(f"❌ Game with App ID {app_id} not found in Steam config")
                print("   Make sure the game is in your Steam library and has been launched at least once")
                return False
            
            print(f"✓ Found game with App ID {app_id} in apps section")
            
            # Find the opening brace after the app ID
            brace_start = config_content.find('{', app_section_start)
            if brace_start == -1:
                print("Could not find opening brace for app section")
                return False
            
            # Find the matching closing brace by counting braces
            brace_count = 0
            brace_end = -1
            for i in range(brace_start, len(config_content)):
                if config_content[i] == '{':
                    brace_count += 1
                elif config_content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        brace_end = i
                        break
            
            if brace_end == -1:
                print("Could not find closing brace for app section")
                return False
            
            # Extract the app section content (between braces)
            app_section_start_pos = brace_start + 1
            app_section_content = config_content[app_section_start_pos:brace_end]
            print(f"🔍 App section content preview (first 300 chars):")
            print(repr(app_section_content[:300]))
            
            # Debug: Check if this section already has the expected structure
            if '"LaunchOptions"' in app_section_content:
                print("✓ LaunchOptions field already exists in this section")
            else:
                print("ℹ LaunchOptions field not found, will add new one")
            
            # Check if LaunchOptions already exists
            launch_options_pattern = r'"LaunchOptions"\s*"([^"]*)"'
            
            import re
            match = re.search(launch_options_pattern, app_section_content)
            
            # Escape quotes in the launch command for VDF format
            escaped_command = launch_command.replace('"', '\\"')
            
            if match:
                # Replace existing launch options
                old_options = match.group(1)
                new_app_content = re.sub(launch_options_pattern, f'"LaunchOptions"\t\t"{escaped_command}"', app_section_content)
                print(f"✓ Replaced existing launch options: '{old_options}' -> '{launch_command}'")
            else:
                # Add new launch options at the end
                # Use the exact Steam VDF indentation (6 tabs for app properties)
                indent = '\t\t\t\t\t\t'  # Steam uses exactly 6 tabs for app properties
                
                new_app_content = app_section_content.rstrip() + f'\n{indent}"LaunchOptions"\t\t"{escaped_command}"'
                print(f"✓ Added new launch options: '{launch_command}'")
            
            # Replace the app section content in the full config
            new_config = config_content[:app_section_start_pos] + new_app_content + config_content[brace_end:]
            
            # Backup the original file
            backup_path = localconfig_path.with_suffix('.vdf.optiscaler_backup')
            try:
                shutil.copy2(localconfig_path, backup_path)
                print(f"✓ Backed up original config to: {backup_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create backup: {e}")
                print("   Continuing anyway...")
            
            # Write the new config
            try:
                with open(localconfig_path, 'w', encoding='utf-8') as f:
                    f.write(new_config)
                print("✅ Steam configuration updated successfully!")
                
                # Verify the changes were written correctly
                with open(localconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                    verification_content = f.read()
                
                if f'"{app_id}"' in verification_content and escaped_command in verification_content:
                    print("✅ Verification: Launch options successfully written to config")
                else:
                    print("⚠️ Warning: Could not verify launch options in updated config")
                    print("   The changes may not have been applied correctly")
                    # Debug: show what was actually written
                    app_pos = verification_content.find(f'"{app_id}"')
                    if app_pos != -1:
                        debug_section = verification_content[app_pos:app_pos+500]
                        print(f"   Debug - App section: {repr(debug_section)}")
                
                print("   You can now launch the game directly from Steam.")
            except PermissionError:
                print(f"❌ Permission denied writing to {localconfig_path}")
                print("   Try running with sudo or change file permissions")
                return False
            except Exception as e:
                print(f"❌ Error writing config file: {e}")
                return False
            print("\n" + "="*60)
            print("✅ LAUNCH OPTIONS APPLIED SUCCESSFULLY!")
            print("="*60)
            print("⚠️  IMPORTANT: Steam must be restarted for changes to take effect.")
            print("   - Close Steam completely (including Steam client)")
            print("   - Restart Steam")
            print("   - Check game properties to verify launch options are visible")
            print("="*60)
            
            restart_choice = input("\nWould you like to restart Steam automatically? (y/n): ").lower()
            if restart_choice == 'y':
                self.restart_steam()
            else:
                print("Please manually restart Steam to apply the launch options.")
            
            return True
            
        except Exception as e:
            print(f"Error applying launch options: {e}")
            return False
    
    def restart_steam(self):
        try:
            print("🔄 Stopping Steam...")
            # More thorough Steam stopping
            subprocess.run(["pkill", "-f", "steam"], check=False)
            subprocess.run(["pkill", "-f", "Steam"], check=False)
            subprocess.run(["killall", "steam"], check=False, stderr=subprocess.DEVNULL)
            subprocess.run(["killall", "Steam"], check=False, stderr=subprocess.DEVNULL)
            
            # Wait for Steam to fully close
            import time
            print("⏳ Waiting for Steam to close completely...")
            time.sleep(5)
            
            # Verify Steam is closed
            result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True)
            if result.returncode == 0:
                print("⚠️  Steam processes still running. Waiting longer...")
                time.sleep(3)
            
            print("🚀 Starting Steam...")
            # Try multiple ways to start Steam
            start_commands = [
                ["steam"],
                ["/usr/bin/steam"],
                ["flatpak", "run", "com.valvesoftware.Steam"],
                ["snap", "run", "steam"]
            ]
            
            steam_started = False
            for cmd in start_commands:
                try:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    steam_started = True
                    print(f"✅ Steam started using: {' '.join(cmd)}")
                    break
                except FileNotFoundError:
                    continue
            
            if not steam_started:
                print("❌ Could not start Steam automatically")
                print("Please manually start Steam from your applications menu")
            else:
                print("✅ Steam is restarting...")
                print("   Please wait for Steam to fully load, then check your game's launch options")
            
        except Exception as e:
            print(f"❌ Error restarting Steam: {e}")
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
                
                print(f"\nAnalyzing game directory: {selected_game['name']}")
                print("Searching for executable locations...")
                
                exe_locations = manager.find_game_executable_paths(selected_game["path"])
                if not exe_locations:
                    print("No suitable executable locations found")
                    print("This game may not be compatible or may have an unusual directory structure")
                    continue
                
                print(f"\nFound {len(exe_locations)} possible installation location(s):")
                print("=" * 80)
                
                for i, location in enumerate(exe_locations, 1):
                    print(f"{i}. {location['type']}")
                    print(f"   Executable: {location['exe_name']}")
                    print(f"   Path: {location['relative_path'] if location['relative_path'] != '.' else 'Game Root Directory'}")
                    print(f"   Full Path: {location['path']}")
                    print()
                
                print("Choose the installation location:")
                print("- Main Game Directory is usually the best choice")
                print("- Shipping Executable locations work well for UE games")
                print("- Choose based on where the main game .exe file is located")
                
                path_idx = int(input(f"\nInstallation location (1-{len(exe_locations)}): ")) - 1
                selected_location = exe_locations[path_idx]
                
                print(f"\nSelected: {selected_location['type']}")
                print(f"Installing to: {selected_location['path']}")
                
                zip_path = manager.download_latest_nightly()
                if not zip_path:
                    continue
                
                if manager.install_optiscaler(selected_game, selected_location, zip_path):
                    print("\n✓ OptiScaler installed successfully!")
                    print(f"Installation directory: {selected_location['path']}")
                    print("\nNext steps:")
                    print("1. The setup_linux.sh script should have been executed")
                    print("2. Configure launch options in Steam for the game")
                    print("3. Launch the game and press INSERT to open OptiScaler overlay")
                else:
                    print("✗ Installation failed")
                    
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "3":
            installs = manager.load_installations()
            if not installs:
                print("No installations found")
                continue
                
            print("\nCurrent OptiScaler Installations:")
            print("=" * 60)
            for i, install in enumerate(installs, 1):
                print(f"{i}. {install['game']['name']}")
                print(f"   Installed: {install['timestamp']}")
                print(f"   Path: {install['install_path']}")
                
                # Show exe location details if available
                if 'exe_location' in install:
                    exe_loc = install['exe_location']
                    print(f"   Type: {exe_loc['type']}")
                    print(f"   Executable: {exe_loc['exe_name']}")
                
                # Show FSR4 status
                fsr4_status = "✓ FSR4 DLL copied" if install.get('fsr4_dll_copied', False) else "✗ FSR4 DLL not copied"
                print(f"   FSR4: {fsr4_status}")
                print()
        
        elif choice == "4":
            installs = manager.load_installations()
            if not installs:
                print("No installations to uninstall")
                continue
                
            print("\nSelect installation to uninstall:")
            print("=" * 60)
            for i, install in enumerate(installs, 1):
                print(f"{i}. {install['game']['name']}")
                print(f"   Installed: {install['timestamp']}")
                print(f"   Path: {install['install_path']}")
                
                if 'exe_location' in install:
                    exe_loc = install['exe_location']
                    print(f"   Type: {exe_loc['type']}")
                    print(f"   Executable: {exe_loc['exe_name']}")
                print()
            
            try:
                install_idx = int(input(f"Installation to uninstall (1-{len(installs)}): ")) - 1
                selected_install = installs[install_idx]
                
                print(f"\nUninstalling OptiScaler from: {selected_install['game']['name']}")
                print(f"Directory: {selected_install['install_path']}")
                
                confirmation = input("Are you sure you want to uninstall? (y/n): ").lower()
                if confirmation != 'y':
                    print("Uninstall cancelled")
                    continue
                
                if manager.uninstall_optiscaler(selected_install):
                    installs.pop(install_idx)
                    with open(manager.installs_file, 'w') as f:
                        json.dump(installs, f, indent=2)
                    print("✓ OptiScaler uninstalled successfully!")
                else:
                    print("✗ Uninstallation failed")
                    
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