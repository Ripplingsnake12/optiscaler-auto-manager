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

class DependencyManager:
    """Manages automatic detection and installation of dependencies."""
    
    def __init__(self):
        self.package_managers = {
            'apt': ['apt', 'apt-get'],
            'pacman': ['pacman'],
            'dnf': ['dnf', 'yum'],
            'zypper': ['zypper'],
            'emerge': ['emerge'],
            'apk': ['apk'],
            'xbps': ['xbps-install'],
            'pkg': ['pkg'],
            'brew': ['brew']
        }
        self.detected_pm = None
        self.clipboard_apps = {
            'xclip': {
                'name': 'xclip',
                'description': 'Simple clipboard utility (most common)',
                'packages': {
                    'apt': 'xclip',
                    'pacman': 'xclip',
                    'dnf': 'xclip',
                    'zypper': 'xclip',
                    'emerge': 'x11-misc/xclip',
                    'apk': 'xclip',
                    'xbps': 'xclip',
                    'pkg': 'xclip'
                }
            },
            'xsel': {
                'name': 'xsel',
                'description': 'Alternative clipboard utility',
                'packages': {
                    'apt': 'xsel',
                    'pacman': 'xsel',
                    'dnf': 'xsel',
                    'zypper': 'xsel',
                    'emerge': 'x11-misc/xsel',
                    'apk': 'xsel',
                    'xbps': 'xsel',
                    'pkg': 'xsel'
                }
            },
            'wl-copy': {
                'name': 'wl-copy',
                'description': 'Wayland clipboard utility',
                'packages': {
                    'apt': 'wl-clipboard',
                    'pacman': 'wl-clipboard',
                    'dnf': 'wl-clipboard',
                    'zypper': 'wl-clipboard',
                    'emerge': 'gui-apps/wl-clipboard',
                    'apk': 'wl-clipboard',
                    'xbps': 'wl-clipboard',
                    'pkg': 'wl-clipboard'
                }
            }
        }
        
    def detect_package_manager(self) -> Optional[str]:
        """Detect the system's package manager."""
        if self.detected_pm:
            return self.detected_pm
            
        for pm_name, commands in self.package_managers.items():
            for cmd in commands:
                try:
                    result = subprocess.run(['which', cmd], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.detected_pm = pm_name
                        return pm_name
                except Exception:
                    continue
        return None
    
    def detect_distro(self) -> str:
        """Detect Linux distribution."""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'ID=' in content:
                    for line in content.split('\n'):
                        if line.startswith('ID='):
                            return line.split('=')[1].strip('"')
        except:
            pass
        return "unknown"
    
    def is_wayland(self) -> bool:
        """Check if running on Wayland."""
        return os.environ.get('WAYLAND_DISPLAY') is not None
    
    def install_package(self, package_name: str, pm_name: str = None) -> bool:
        """Install a package using the system package manager."""
        if not pm_name:
            pm_name = self.detect_package_manager()
            
        if not pm_name:
            print("❌ No supported package manager found")
            return False
            
        print(f"🔧 Installing {package_name} using {pm_name}...")
        
        install_commands = {
            'apt': ['sudo', 'apt', 'install', '-y', package_name],
            'pacman': ['sudo', 'pacman', '-S', '--noconfirm', package_name],
            'dnf': ['sudo', 'dnf', 'install', '-y', package_name],
            'zypper': ['sudo', 'zypper', 'install', '-y', package_name],
            'emerge': ['sudo', 'emerge', package_name],
            'apk': ['sudo', 'apk', 'add', package_name],
            'xbps': ['sudo', 'xbps-install', '-y', package_name],
            'pkg': ['sudo', 'pkg', 'install', '-y', package_name],
            'brew': ['brew', 'install', package_name]
        }
        
        if pm_name not in install_commands:
            print(f"❌ Package manager {pm_name} not supported")
            return False
            
        try:
            result = subprocess.run(install_commands[pm_name], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Successfully installed {package_name}")
                return True
            else:
                print(f"❌ Failed to install {package_name}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing {package_name}: {e}")
            return False
    
    def check_python_module(self, module_name: str, pip_name: str = None) -> bool:
        """Check if a Python module is available and install if needed."""
        if not pip_name:
            pip_name = module_name
            
        try:
            __import__(module_name)
            return True
        except ImportError:
            print(f"❌ Missing Python module: {module_name}")
            
            pip_commands = ['pip3', 'pip', 'python3 -m pip', 'python -m pip']
            
            for pip_cmd in pip_commands:
                try:
                    # Check if pip command exists
                    check_cmd = pip_cmd.split()[0] if ' ' not in pip_cmd else pip_cmd.split()[-1]
                    result = subprocess.run(['which', check_cmd], capture_output=True)
                    if result.returncode != 0:
                        continue
                    
                    print(f"🔧 Installing {pip_name} using {pip_cmd}...")
                    
                    # Try installing with pip
                    install_cmd = f"{pip_cmd} install --user {pip_name}".split()
                    result = subprocess.run(install_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully installed {pip_name}")
                        # Try importing again
                        try:
                            __import__(module_name)
                            return True
                        except ImportError:
                            print("⚠️ Module installed but still not importable, may need to restart")
                            return False
                    else:
                        print(f"❌ Failed with {pip_cmd}: {result.stderr}")
                        
                except Exception as e:
                    print(f"❌ Error with {pip_cmd}: {e}")
                    continue
            
            # If pip installation failed, try system package manager
            pm = self.detect_package_manager()
            if pm:
                python_packages = {
                    'requests': {
                        'apt': 'python3-requests',
                        'pacman': 'python-requests',
                        'dnf': 'python3-requests',
                        'zypper': 'python3-requests',
                        'emerge': 'dev-python/requests',
                        'apk': 'py3-requests',
                        'xbps': 'python3-requests'
                    }
                }
                
                if pip_name in python_packages and pm in python_packages[pip_name]:
                    package_name = python_packages[pip_name][pm]
                    return self.install_package(package_name, pm)
            
            return False
    
    def check_system_tool(self, tool_name: str, package_name: str = None, auto_install: bool = False) -> bool:
        """Check if a system tool is available and install if needed."""
        if not package_name:
            package_name = tool_name
            
        try:
            result = subprocess.run(['which', tool_name], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except Exception:
            pass
        
        print(f"❌ Missing system tool: {tool_name}")
        
        # Ask user if they want to install (unless auto_install is True)
        if auto_install:
            choice = 'y'
        else:
            choice = input(f"Install {tool_name}? (y/n): ").lower()
            
        if choice == 'y':
            pm = self.detect_package_manager()
            if pm:
                # Map some common package names
                package_mappings = {
                    '7z': {
                        'apt': 'p7zip-full',
                        'pacman': 'p7zip',
                        'dnf': 'p7zip',
                        'zypper': 'p7zip',
                        'emerge': 'app-arch/p7zip',
                        'apk': 'p7zip',
                        'xbps': 'p7zip'
                    },
                    'git': {
                        'apt': 'git',
                        'pacman': 'git',
                        'dnf': 'git',
                        'zypper': 'git',
                        'emerge': 'dev-vcs/git',
                        'apk': 'git',
                        'xbps': 'git'
                    },
                    'wine': {
                        'apt': 'wine',
                        'pacman': 'wine',
                        'dnf': 'wine',
                        'zypper': 'wine',
                        'emerge': 'app-emulation/wine-vanilla',
                        'apk': 'wine',
                        'xbps': 'wine'
                    },
                    'curl': {
                        'apt': 'curl',
                        'pacman': 'curl',
                        'dnf': 'curl',
                        'zypper': 'curl',
                        'emerge': 'net-misc/curl',
                        'apk': 'curl',
                        'xbps': 'curl'
                    },
                    'wget': {
                        'apt': 'wget',
                        'pacman': 'wget',
                        'dnf': 'wget',
                        'zypper': 'wget',
                        'emerge': 'net-misc/wget',
                        'apk': 'wget',
                        'xbps': 'wget'
                    }
                }
                
                if tool_name in package_mappings and pm in package_mappings[tool_name]:
                    package_name = package_mappings[tool_name][pm]
                
                return self.install_package(package_name, pm)
        
        return False
    
    def setup_clipboard_app(self) -> bool:
        """Set up clipboard functionality by installing a clipboard app."""
        # Check if any clipboard app is already installed
        installed_apps = []
        for app_name, app_info in self.clipboard_apps.items():
            try:
                result = subprocess.run(['which', app_name], capture_output=True, text=True)
                if result.returncode == 0:
                    installed_apps.append(app_name)
            except Exception:
                pass
        
        if installed_apps:
            print(f"✅ Found clipboard app(s): {', '.join(installed_apps)}")
            return True
        
        print("❌ No clipboard application found")
        print("Clipboard functionality is needed for copying Steam launch commands")
        
        # Recommend based on display server
        if self.is_wayland():
            print("🔍 Detected Wayland - recommending wl-copy")
            recommended = 'wl-copy'
        else:
            print("🔍 Detected X11 - recommending xclip")
            recommended = 'xclip'
        
        print("\nAvailable clipboard applications:")
        for i, (app_name, app_info) in enumerate(self.clipboard_apps.items(), 1):
            marker = " (recommended)" if app_name == recommended else ""
            print(f"{i}. {app_info['name']}: {app_info['description']}{marker}")
        
        print(f"{len(self.clipboard_apps) + 1}. Install all clipboard apps")
        print(f"{len(self.clipboard_apps) + 2}. Skip clipboard setup")
        
        try:
            choice = int(input(f"\nSelect clipboard app (1-{len(self.clipboard_apps) + 2}): "))
            
            if choice == len(self.clipboard_apps) + 2:
                print("⚠️ Skipping clipboard setup - launch commands won't be copied automatically")
                return False
            elif choice == len(self.clipboard_apps) + 1:
                # Install all
                pm = self.detect_package_manager()
                if not pm:
                    print("❌ No package manager detected")
                    return False
                
                success = True
                for app_name, app_info in self.clipboard_apps.items():
                    if pm in app_info['packages']:
                        package_name = app_info['packages'][pm]
                        if not self.install_package(package_name, pm):
                            success = False
                return success
            elif 1 <= choice <= len(self.clipboard_apps):
                # Install selected app
                app_name = list(self.clipboard_apps.keys())[choice - 1]
                app_info = self.clipboard_apps[app_name]
                
                pm = self.detect_package_manager()
                if not pm:
                    print("❌ No package manager detected")
                    return False
                
                if pm in app_info['packages']:
                    package_name = app_info['packages'][pm]
                    return self.install_package(package_name, pm)
                else:
                    print(f"❌ Package not available for {pm}")
                    return False
            else:
                print("❌ Invalid selection")
                return False
                
        except ValueError:
            print("❌ Invalid input")
            return False
    
    def check_all_dependencies(self) -> bool:
        """Check and install all required dependencies."""
        print("🔍 Checking dependencies...")
        
        # Detect system info
        pm = self.detect_package_manager()
        distro = self.detect_distro()
        is_wayland = self.is_wayland()
        
        print(f"📊 System Info:")
        print(f"   Distribution: {distro}")
        print(f"   Package Manager: {pm or 'Not detected'}")
        print(f"   Display Server: {'Wayland' if is_wayland else 'X11'}")
        
        all_ok = True
        
        # Check Python modules
        print("\n🐍 Checking Python modules...")
        if not self.check_python_module('requests'):
            all_ok = False
        
        # Check system tools
        print("\n🔧 Checking system tools...")
        system_tools = {
            '7z': 'p7zip',
            'git': 'git',
            'wine': 'wine',
            'curl': 'curl',
            'wget': 'wget'
        }
        
        missing_tools = []
        for tool_name, package_name in system_tools.items():
            try:
                result = subprocess.run(['which', tool_name], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool_name} found")
                else:
                    missing_tools.append((tool_name, package_name))
                    print(f"❌ {tool_name} not found")
            except Exception:
                missing_tools.append((tool_name, package_name))
                print(f"❌ {tool_name} not found")
        
        if missing_tools:
            print(f"\n🔧 Found {len(missing_tools)} missing tools")
            choice = input("Install all missing tools automatically? (y/n): ").lower()
            if choice == 'y':
                for tool_name, package_name in missing_tools:
                    self.check_system_tool(tool_name, package_name, auto_install=True)
            else:
                print("⚠️ Some tools are missing - you can install them individually later")
        
        # Check clipboard apps
        print("\n📋 Checking clipboard functionality...")
        if not self.setup_clipboard_app():
            print("⚠️ Clipboard functionality limited")
        
        # Check terminal emulators
        print("\n💻 Checking terminal emulators...")
        terminal_found = False
        terminals = ['konsole', 'gnome-terminal', 'xfce4-terminal', 'alacritty', 'kitty', 'terminator', 'xterm']
        
        for terminal in terminals:
            try:
                result = subprocess.run(['which', terminal], capture_output=True, text=True)
                if result.returncode == 0:
                    terminal_found = True
                    print(f"✅ Found terminal: {terminal}")
                    break
            except Exception:
                pass
        
        if not terminal_found:
            print("⚠️ No common terminal emulator found - OptiScaler setup scripts may need manual execution")
        
        return all_ok

# Initialize dependency manager
dep_manager = DependencyManager()

# Check dependencies at startup
if not dep_manager.check_python_module('requests'):
    print("❌ Critical dependency 'requests' could not be installed")
    print("Please install it manually and restart the program")
    sys.exit(1)

# Now we can safely import requests
import requests

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

    def _find_all_steam_libraries(self) -> List[Path]:
        """Find all Steam library folders across all drives including external and NTFS."""
        libraries = []
        
        # Start with the main Steam installation
        if self.steam_path:
            libraries.append(self.steam_path)
            
            # Check for libraryfolders.vdf which lists additional Steam libraries
            library_config = self.steam_path / "steamapps" / "libraryfolders.vdf"
            if library_config.exists():
                try:
                    with open(library_config, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse VDF format to find library paths
                    import re
                    path_matches = re.findall(r'"path"\s*"([^"]+)"', content)
                    for path_str in path_matches:
                        library_path = Path(path_str)
                        if library_path.exists() and library_path not in libraries:
                            libraries.append(library_path)
                            print(f"Found additional Steam library: {library_path}")
                except Exception as e:
                    print(f"Error reading libraryfolders.vdf: {e}")
        
        # Scan all mounted drives for Steam libraries
        additional_libraries = self._scan_all_drives_for_steam()
        for lib in additional_libraries:
            if lib not in libraries:
                libraries.append(lib)
        
        return libraries
    
    def _scan_all_drives_for_steam(self) -> List[Path]:
        """Scan all mounted drives for Steam installations and libraries."""
        steam_libraries = []
        
        # Get all mounted filesystems
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True)
            mount_lines = result.stdout.split('\n')
            
            mount_points = []
            for line in mount_lines:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == 'on':
                    mount_point = parts[2]
                    # Include common mount points and external drives
                    if (mount_point.startswith('/mnt/') or 
                        mount_point.startswith('/media/') or 
                        mount_point.startswith('/run/media/') or
                        mount_point == '/' or
                        mount_point.startswith('/home')):
                        mount_points.append(Path(mount_point))
            
            # Also check common external drive locations
            external_locations = [
                Path('/mnt'),
                Path('/media'),
                Path('/run/media'),
            ]
            
            for ext_path in external_locations:
                if ext_path.exists():
                    try:
                        for subdir in ext_path.iterdir():
                            if subdir.is_dir():
                                mount_points.append(subdir)
                                # Check subdirectories for user folders
                                try:
                                    for user_dir in subdir.iterdir():
                                        if user_dir.is_dir():
                                            mount_points.append(user_dir)
                                except PermissionError:
                                    pass
                    except PermissionError:
                        pass
            
            # Search each mount point for Steam-related directories
            for mount_point in mount_points:
                steam_dirs = self._find_steam_dirs_in_path(mount_point)
                steam_libraries.extend(steam_dirs)
                
        except Exception as e:
            print(f"Error scanning drives: {e}")
        
        return steam_libraries
    
    def _find_steam_dirs_in_path(self, search_path: Path) -> List[Path]:
        """Find Steam directories in a given path."""
        steam_dirs = []
        
        if not search_path.exists():
            return steam_dirs
            
        try:
            # Common Steam directory patterns
            steam_patterns = [
                "Steam",
                "steam", 
                ".steam",
                ".local/share/Steam",
                "SteamLibrary",
                "Games/Steam",
                "Program Files/Steam",
                "Program Files (x86)/Steam",
            ]
            
            # Search for Steam directories
            for pattern in steam_patterns:
                potential_steam = search_path / pattern
                if potential_steam.exists():
                    # Check if it's a valid Steam directory
                    steamapps_path = potential_steam / "steamapps"
                    if steamapps_path.exists():
                        steam_dirs.append(potential_steam)
                        print(f"Found Steam library at: {potential_steam}")
            
            # Also do a broader search for steamapps folders
            try:
                for item in search_path.iterdir():
                    if item.is_dir() and item.name.lower() in ['steamapps', 'steam']:
                        parent = item.parent
                        if parent not in steam_dirs:
                            # Verify it's a Steam directory
                            if (item / "common").exists() or (parent / "steam.exe").exists():
                                steam_dirs.append(parent)
                                print(f"Found Steam directory via steamapps: {parent}")
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
                
        except (PermissionError, OSError):
            # Skip paths we can't access
            pass
            
        return steam_dirs
    
    def _is_ntfs_drive(self, path: Path) -> bool:
        """Check if a path is on an NTFS filesystem."""
        try:
            result = subprocess.run(['stat', '-f', '-c', '%T', str(path)], 
                                  capture_output=True, text=True)
            return 'ntfs' in result.stdout.lower()
        except Exception:
            return False
    
    def _safe_case_insensitive_glob(self, path: Path, pattern: str) -> List[Path]:
        """Perform case-insensitive glob for NTFS drives."""
        matches = []
        
        # Regular glob first
        matches.extend(path.glob(pattern))
        
        # If on NTFS, also try case variations
        if self._is_ntfs_drive(path):
            variations = [
                pattern.lower(),
                pattern.upper(),
                pattern.title(),
            ]
            
            for variation in variations:
                try:
                    matches.extend(path.glob(variation))
                except Exception:
                    pass
        
        # Remove duplicates
        return list(set(matches))

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
        
        # Get all Steam library locations
        steam_libraries = self._find_all_steam_libraries()
        
        print(f"Scanning {len(steam_libraries)} Steam libraries for games...")
        
        for library_path in steam_libraries:
            steamapps_path = library_path / "steamapps"
            
            if not steamapps_path.exists():
                continue
                
            print(f"Scanning library: {library_path}")
            
            # Find all manifest files in this library (with NTFS support)
            manifest_files = self._safe_case_insensitive_glob(steamapps_path, "appmanifest_*.acf")
            
            for manifest_file in manifest_files:
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
                            # Check if we already have this game from another library
                            existing_game = next((g for g in games if g["app_id"] == app_id), None)
                            if not existing_game:
                                games.append({
                                    "app_id": app_id,
                                    "name": name,
                                    "install_dir": install_dir,
                                    "path": str(game_path),
                                    "library_path": str(library_path)
                                })
                            else:
                                # Game exists in multiple libraries, keep the one with more recent activity
                                try:
                                    existing_mtime = Path(existing_game["path"]).stat().st_mtime
                                    current_mtime = game_path.stat().st_mtime
                                    if current_mtime > existing_mtime:
                                        # Replace with more recent version
                                        for i, game in enumerate(games):
                                            if game["app_id"] == app_id:
                                                games[i] = {
                                                    "app_id": app_id,
                                                    "name": name,
                                                    "install_dir": install_dir,
                                                    "path": str(game_path),
                                                    "library_path": str(library_path)
                                                }
                                                break
                                except OSError:
                                    pass  # Can't get mtime, keep existing
                                    
                except Exception as e:
                    print(f"Error reading manifest {manifest_file}: {e}")
        
        print(f"Found {len(games)} games across all Steam libraries")
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

    def get_launch_options_catalog(self, rdna3_workaround: bool = False, include_mangohud: bool = True) -> Dict[str, Dict]:
        """Get a comprehensive catalog of launch options with categorization"""
        optiscaler_base = 'WINEDLLOVERRIDES="dxgi=n,b"'
        
        catalog = {
            "basic": {
                "name": "Basic OptiScaler",
                "description": "Essential OptiScaler setup - recommended starting point",
                "command": f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 %command%',
                "category": "basic",
                "compatibility": "All games",
                "requirements": "OptiScaler installed"
            },
            "basic_mangohud": {
                "name": "Basic + MangoHUD",
                "description": "Basic OptiScaler with performance monitoring overlay",
                "command": f'mangohud {optiscaler_base} PROTON_FSR4_UPGRADE=1 %command%',
                "category": "basic",
                "compatibility": "All games",
                "requirements": "OptiScaler installed, MangoHUD"
            },
            "advanced": {
                "name": "Advanced OptiScaler",
                "description": "Enhanced performance and compatibility settings",
                "command": f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%',
                "category": "advanced",
                "compatibility": "Most games",
                "requirements": "OptiScaler installed, DXVK"
            },
            "advanced_mangohud": {
                "name": "Advanced + MangoHUD",
                "description": "Advanced settings with performance monitoring",
                "command": f'mangohud {optiscaler_base} PROTON_FSR4_UPGRADE=1 DXVK_ASYNC=1 PROTON_ENABLE_NVAPI=1 PROTON_HIDE_NVIDIA_GPU=0 VKD3D_CONFIG=dxr11,dxr WINE_CPU_TOPOLOGY=4:2 %command%',
                "category": "advanced",
                "compatibility": "Most games",
                "requirements": "OptiScaler installed, DXVK, MangoHUD"
            },
            "debug": {
                "name": "Debug Mode",
                "description": "Detailed logging for troubleshooting issues",
                "command": f'{optiscaler_base} PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 %command%',
                "category": "debug",
                "compatibility": "All games",
                "requirements": "OptiScaler installed"
            },
            "debug_mangohud": {
                "name": "Debug + MangoHUD",
                "description": "Debug mode with performance monitoring",
                "command": f'mangohud {optiscaler_base} PROTON_LOG=+all WINEDEBUG=+dll PROTON_FSR4_UPGRADE=1 %command%',
                "category": "debug",
                "compatibility": "All games",
                "requirements": "OptiScaler installed, MangoHUD"
            },
            "antilag": {
                "name": "Anti-Lag 2",
                "description": "Experimental latency reduction (AMD only)",
                "command": f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt %command%',
                "category": "experimental",
                "compatibility": "AMD GPUs only",
                "requirements": "OptiScaler installed, AMD GPU"
            },
            "antilag_mangohud": {
                "name": "Anti-Lag 2 + MangoHUD",
                "description": "Anti-Lag 2 with performance monitoring",
                "command": f'mangohud {optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=rt %command%',
                "category": "experimental",
                "compatibility": "AMD GPUs only",
                "requirements": "OptiScaler installed, AMD GPU, MangoHUD"
            },
            "fsr4_enhanced": {
                "name": "FSR4 Enhanced",
                "description": "Optimized FSR4 settings with enhanced performance",
                "command": f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc,rt %command%',
                "category": "fsr4",
                "compatibility": "AMD GPUs (FSR4 capable)",
                "requirements": "OptiScaler installed, AMD GPU, FSR4 DLL"
            },
            "fsr4_enhanced_mangohud": {
                "name": "FSR4 Enhanced + MangoHUD",
                "description": "FSR4 Enhanced with performance monitoring",
                "command": f'mangohud {optiscaler_base} PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc,rt %command%',
                "category": "fsr4",
                "compatibility": "AMD GPUs (FSR4 capable)",
                "requirements": "OptiScaler installed, AMD GPU, FSR4 DLL, MangoHUD"
            },
            "ue_dx12": {
                "name": "Unreal Engine + DX12",
                "description": "Optimized for Unreal Engine games with DirectX 12",
                "command": f'{optiscaler_base} PROTON_FSR4_UPGRADE=1 -dx12 %command%',
                "category": "game_specific",
                "compatibility": "Unreal Engine games",
                "requirements": "OptiScaler installed, UE game"
            },
            "ue_dx12_mangohud": {
                "name": "Unreal Engine + DX12 + MangoHUD",
                "description": "UE DX12 optimization with performance monitoring",
                "command": f'mangohud {optiscaler_base} PROTON_FSR4_UPGRADE=1 -dx12 %command%',
                "category": "game_specific",
                "compatibility": "Unreal Engine games",
                "requirements": "OptiScaler installed, UE game, MangoHUD"
            },
            "no_dlss_fg": {
                "name": "Disable DLSS Frame Generation",
                "description": "For games with DLSS Frame Generation issues",
                "command": f'WINEDLLOVERRIDES="dxgi=n,b;nvngx=n,b" PROTON_FSR4_UPGRADE=1 %command%',
                "category": "compatibility",
                "compatibility": "Games with DLSS FG issues",
                "requirements": "OptiScaler installed"
            },
            "no_dlss_fg_mangohud": {
                "name": "Disable DLSS FG + MangoHUD",
                "description": "DLSS FG disabled with performance monitoring",
                "command": f'mangohud WINEDLLOVERRIDES="dxgi=n,b;nvngx=n,b" PROTON_FSR4_UPGRADE=1 %command%',
                "category": "compatibility",
                "compatibility": "Games with DLSS FG issues",
                "requirements": "OptiScaler installed, MangoHUD"
            }
        }
        
        # Add RDNA3 workaround variants if needed
        if rdna3_workaround:
            rdna3_options = {}
            for key, option in catalog.items():
                if "DXIL_SPIRV_CONFIG=wmma_rdna3_workaround" not in option["command"]:
                    rdna3_key = f"{key}_rdna3"
                    rdna3_cmd = option["command"].replace(
                        'WINEDLLOVERRIDES="dxgi=n,b"',
                        'WINEDLLOVERRIDES="dxgi=n,b" DXIL_SPIRV_CONFIG=wmma_rdna3_workaround'
                    )
                    if "RADV_PERFTEST=" not in rdna3_cmd:
                        rdna3_cmd = rdna3_cmd.replace("PROTON_FSR4_UPGRADE=1", "PROTON_FSR4_UPGRADE=1 RADV_PERFTEST=nggc")
                    else:
                        rdna3_cmd = rdna3_cmd.replace("RADV_PERFTEST=", "RADV_PERFTEST=nggc,")
                    
                    rdna3_options[rdna3_key] = {
                        "name": f"{option['name']} (RDNA3)",
                        "description": f"{option['description']} - RDNA3 GPU workaround",
                        "command": rdna3_cmd,
                        "category": option["category"],
                        "compatibility": "RDNA3 GPUs only",
                        "requirements": f"{option['requirements']}, RDNA3 GPU"
                    }
            catalog.update(rdna3_options)
        
        # Filter out MangoHUD options if not requested
        if not include_mangohud:
            catalog = {k: v for k, v in catalog.items() if "mangohud" not in k}
        
        return catalog

    def add_steam_launch_options(self, app_id: str, rdna3_workaround: bool = False, auto_apply: bool = False):
        """Enhanced launch options with selection and automatic application"""
        # ANSI color codes for highlighting
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        # Check if MangoHUD is available
        mangohud_available = False
        try:
            result = subprocess.run(['which', 'mangohud'], capture_output=True, text=True)
            mangohud_available = result.returncode == 0
        except Exception:
            pass
        
        # Get launch options catalog
        catalog = self.get_launch_options_catalog(rdna3_workaround, mangohud_available)
        
        if not auto_apply:
            # Display mode - show all options with colors
            print(f"Steam launch options for App ID {app_id}:")
            
            # Group by category
            categories = {
                "basic": "Basic Setup",
                "advanced": "Advanced Options", 
                "debug": "Debugging",
                "experimental": "Experimental",
                "fsr4": "FSR4 Specific",
                "game_specific": "Game-Specific Tweaks",
                "compatibility": "Compatibility Fixes"
            }
            
            for cat_key, cat_name in categories.items():
                cat_options = {k: v for k, v in catalog.items() if v["category"] == cat_key}
                if not cat_options:
                    continue
                    
                print(f"\n=== {cat_name} ===")
                for option in cat_options.values():
                    color = CYAN if "basic" in cat_key else YELLOW if "mangohud" in option["name"].lower() else GREEN if "fsr4" in cat_key else RED if "debug" in cat_key else CYAN
                    print(f"{color}{option['name']}{RESET}: {option['command']}")
                    print(f"  {option['description']}")
                    if option['requirements'] != "OptiScaler installed":
                        print(f"  Requirements: {option['requirements']}")
                    print()
            
            self._show_manual_application_instructions()
            
        else:
            # Interactive selection mode
            print(f"\n=== Select Launch Options for App ID {app_id} ===")
            
            # Filter and organize options for selection
            options_list = []
            for key, option in catalog.items():
                options_list.append((key, option))
            
            # Group by category for better organization
            categories = {}
            for key, option in options_list:
                cat = option["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append((key, option))
            
            # Display categorized options
            choice_index = 1
            index_map = {}
            
            for cat_key in ["basic", "advanced", "fsr4", "game_specific", "compatibility", "experimental", "debug"]:
                if cat_key not in categories:
                    continue
                    
                cat_name = {
                    "basic": "Basic Setup",
                    "advanced": "Advanced Options",
                    "fsr4": "FSR4 Specific", 
                    "game_specific": "Game-Specific",
                    "compatibility": "Compatibility",
                    "experimental": "Experimental",
                    "debug": "Debug/Troubleshooting"
                }[cat_key]
                
                print(f"\n{BOLD}{cat_name}{RESET}")
                for key, option in categories[cat_key]:
                    color = CYAN if "basic" in cat_key else GREEN if "fsr4" in cat_key else YELLOW
                    print(f"{choice_index:2d}. {color}{option['name']}{RESET}")
                    print(f"    {option['description']}")
                    print(f"    Compatibility: {option['compatibility']}")
                    if option['requirements'] != "OptiScaler installed":
                        print(f"    Requirements: {option['requirements']}")
                    
                    index_map[choice_index] = (key, option)
                    choice_index += 1
            
            print(f"\n{choice_index}. View all commands without applying")
            print(f"{choice_index + 1}. Cancel")
            
            try:
                choice = int(input(f"\nSelect launch option (1-{choice_index + 1}): "))
                
                if choice == choice_index:
                    # Show all commands
                    self.add_steam_launch_options(app_id, rdna3_workaround, auto_apply=False)
                    return False
                elif choice == choice_index + 1:
                    print("Cancelled launch option selection")
                    return False
                elif choice in index_map:
                    selected_key, selected_option = index_map[choice]
                    print(f"\nSelected: {selected_option['name']}")
                    print(f"Command: {selected_option['command']}")
                    
                    confirm = input(f"\nApply this launch option to App ID {app_id}? (y/n): ").lower()
                    if confirm == 'y':
                        if self.apply_steam_launch_options(app_id, selected_option['command']):
                            print(f"✅ Launch options applied successfully!")
                            return True
                        else:
                            print("❌ Failed to apply launch options")
                            return False
                    else:
                        print("Launch option application cancelled")
                        return False
                else:
                    print("Invalid selection")
                    return False
                    
            except ValueError:
                print("Invalid input")
                return False
                
        return False
    
    def _show_manual_application_instructions(self):
        """Show instructions for manual application"""
        BOLD = '\033[1m'
        RESET = '\033[0m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        
        print("\n=== IMPORTANT NOTES ===")
        print("• WINEDLLOVERRIDES=\"dxgi=n,b\" is REQUIRED for OptiScaler to work")
        print("• Start with 'Basic' command first")
        print("• If OptiScaler overlay doesn't appear, try the 'Disable DLSS FG' version")
        print("• Press INSERT in-game to open OptiScaler overlay")
        print("• Copy and paste commands exactly as shown (they are color-highlighted for easy selection)")
        
        print("\n=== MANUAL APPLICATION ===")
        print("To apply manually:")
        print("1. Right-click game in Steam")
        print("2. Properties > General > Launch Options") 
        print("3. Copy and paste ONE of the above highlighted commands")
        print("4. Launch game and press INSERT for OptiScaler overlay")
        
        print(f"\n{BOLD}TIP:{RESET} Commands are color-highlighted for easy copy-pasting!")
        print(f"  {CYAN}Cyan{RESET} = Basic/Standard commands")
        print(f"  {YELLOW}Yellow{RESET} = MangoHUD variants")
        print(f"  {GREEN}Green{RESET} = Enhanced/FSR4 commands")
        print(f"  {RED}Red{RESET} = Debug commands")

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
            
            # Check if Steam is running - we'll work with it running like Valve does
            steam_running = False
            try:
                result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True)
                if result.returncode == 0:
                    steam_running = True
                    print("✓ Steam is running - will apply changes live")
            except:
                pass  # pgrep not available or other error, continue anyway
            
            # Read the current config with proper error handling
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
            
            # Parse VDF structure more robustly
            success = self._modify_vdf_launch_options(config_content, localconfig_path, app_id, launch_command)
            
            if success:
                print("✅ Launch options applied successfully!")
                
                # If Steam is running, signal it to reload the config
                if steam_running:
                    self._signal_steam_config_reload()
                    print("✅ Steam notified of configuration changes")
                    print("   Launch options are now active - no restart needed!")
                else:
                    print("   Launch options will be active when Steam starts")
                
                return True
            else:
                print("❌ Failed to apply launch options")
                return False
            
        except Exception as e:
            print(f"Error applying launch options: {e}")
            return False
    
    def _modify_vdf_launch_options(self, config_content: str, config_path: Path, app_id: str, launch_command: str) -> bool:
        """Modify VDF file with proper Steam VDF syntax and positioning"""
        try:
            import re
            
            # Look for the apps section first
            apps_section_start = config_content.find('"apps"')
            if apps_section_start == -1:
                print("❌ apps section not found in Steam config")
                return False
            
            # Search for the app ID within the apps section using more robust pattern
            app_pattern = f'"{app_id}"'
            app_section_start = config_content.find(app_pattern, apps_section_start)
            if app_section_start == -1:
                print(f"❌ Game with App ID {app_id} not found in Steam config")
                print("   Make sure the game is in your Steam library and has been launched at least once")
                return False
            
            print(f"✓ Found game with App ID {app_id} in apps section")
            
            # Find the opening brace after the app ID (proper VDF parsing)
            brace_start = config_content.find('{', app_section_start)
            if brace_start == -1:
                print("Could not find opening brace for app section")
                return False
            
            # Find the matching closing brace by counting braces (proper VDF parsing)
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
            
            # Check if LaunchOptions already exists with proper VDF regex
            launch_options_pattern = r'"LaunchOptions"\s+("([^"\\]|\\.)*")'
            
            match = re.search(launch_options_pattern, app_section_content)
            
            # Escape quotes in the launch command for VDF format (like Steam does)
            escaped_command = launch_command.replace('\\', '\\\\').replace('"', '\\"')
            
            if match:
                # Replace existing launch options (preserving exact Steam VDF format)
                old_options = match.group(2) if match.group(2) else ""
                new_launch_line = f'"LaunchOptions"\t\t"{escaped_command}"'
                new_app_content = re.sub(launch_options_pattern, new_launch_line, app_section_content)
                print(f"✓ Replaced existing launch options")
                print(f"   Old: '{old_options}'")
                print(f"   New: '{launch_command}'")
            else:
                # Add new launch options in the correct position (like Steam does)
                # Steam typically places LaunchOptions near the top of the app section
                # Find a good insertion point after any existing high-priority keys
                
                # Look for common Steam app keys to insert after
                insertion_keys = ['"name"', '"LastUpdated"', '"SizeOnDisk"', '"tool"']
                insertion_pos = 0
                
                for key in insertion_keys:
                    key_pos = app_section_content.find(key)
                    if key_pos != -1:
                        # Find the end of this key-value pair
                        line_end = app_section_content.find('\n', key_pos)
                        if line_end != -1:
                            insertion_pos = line_end + 1
                
                # Use exact Steam VDF indentation
                indent = '\t\t\t\t\t\t'  # Steam uses exactly 6 tabs for app properties
                
                # Insert the launch options at the determined position
                new_launch_line = f'{indent}"LaunchOptions"\t\t"{escaped_command}"\n'
                new_app_content = app_section_content[:insertion_pos] + new_launch_line + app_section_content[insertion_pos:]
                print(f"✓ Added new launch options: '{launch_command}'")
            
            # Replace the app section content in the full config
            new_config = config_content[:app_section_start_pos] + new_app_content + config_content[brace_end:]
            
            # Create backup with timestamp (like Steam does)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = config_path.with_suffix(f'.vdf.backup_{timestamp}')
            try:
                shutil.copy2(config_path, backup_path)
                print(f"✓ Backed up original config to: {backup_path}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create backup: {e}")
            
            # Write the new config atomically (like Steam does)
            temp_path = config_path.with_suffix('.vdf.tmp')
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write(new_config)
                
                # Atomic move (like Steam does)
                import os
                os.replace(temp_path, config_path)
                
                print("✅ Steam configuration updated successfully!")
                
                # Verify the changes were written correctly
                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    verification_content = f.read()
                
                if f'"{app_id}"' in verification_content and escaped_command in verification_content:
                    print("✅ Verification: Launch options successfully written to config")
                    return True
                else:
                    print("⚠️ Warning: Could not verify launch options in updated config")
                    return False
                
            except PermissionError:
                print(f"❌ Permission denied writing to {config_path}")
                print("   Try running with sudo or change file permissions")
                return False
            except Exception as e:
                print(f"❌ Error writing config file: {e}")
                return False
            finally:
                # Clean up temp file if it exists
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Error modifying VDF file: {e}")
            return False
    
    def _signal_steam_config_reload(self):
        """Signal Steam to reload configuration (like Valve does internally)"""
        try:
            # Method 1: Touch the config file to update mtime (Steam watches this)
            import os
            import time
            
            # Update the file's modification time
            current_time = time.time()
            
            # Find the config file path
            userdata_path = self.steam_path / "userdata"
            user_dirs = [d for d in userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            
            if user_dirs:
                user_dir = max(user_dirs, key=lambda x: x.stat().st_mtime)
                config_path = user_dir / "config" / "localconfig.vdf"
                
                if config_path.exists():
                    os.utime(config_path, (current_time, current_time))
            
            # Method 2: Send SIGHUP to Steam process (if supported)
            try:
                result = subprocess.run(['pgrep', '-f', 'steam'], capture_output=True, text=True)
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                # Send SIGHUP to request config reload
                                subprocess.run(['kill', '-HUP', pid.strip()], check=False)
                            except:
                                pass
            except:
                pass
                
        except Exception as e:
            print(f"Note: Could not signal Steam for config reload: {e}")
            print("Launch options will still work - Steam will detect changes on next focus")
    
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
    print("=" * 60)
    print("🚀 OptiScaler Manager - Enhanced Version")
    print("=" * 60)
    
    # Run startup dependency check
    print("\n🔍 Running startup dependency check...")
    if not dep_manager.check_python_module('requests'):
        print("❌ Critical dependency missing - exiting")
        sys.exit(1)
    
    # Quick check for common tools
    missing_tools = []
    tools_to_check = ['7z', 'git', 'wine']
    
    for tool in tools_to_check:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode != 0:
                missing_tools.append(tool)
        except Exception:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"⚠️ Optional tools not found: {', '.join(missing_tools)}")
        print("   Use menu option 9 to install missing dependencies")
    else:
        print("✅ All common tools found")
    
    print("\n" + "=" * 60)
    
    manager = OptiScalerManager()
    
    while True:
        print("\n=== OptiScaler Manager ===")
        print("1. List Steam games")
        print("2. Install OptiScaler")
        print("3. View installations")
        print("4. Uninstall OptiScaler")
        print("5. Download latest nightly")
        print("6. Apply Steam launch options (auto-selectable)")
        print("7. Manage FSR4 DLL")
        print("8. Show drive/library scan details")
        print("9. Check/Install dependencies")
        print("10. Test VDF launch options functionality")
        print("11. Exit")
        
        choice = input("\nEnter choice (1-11): ").strip()
        
        if choice == "1":
            games = manager.get_steam_games()
            for i, game in enumerate(games, 1):
                library_info = f" [Library: {game.get('library_path', 'Unknown')}]" if 'library_path' in game else ""
                print(f"{i}. {game['name']} (ID: {game['app_id']}){library_info}")
        
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
                
                print(f"\nSelected game: {selected_game['name']} (App ID: {selected_game['app_id']})")
                
                # Ask for configuration options
                print("\nConfiguration options:")
                print("1. Automatic selection and application")
                print("2. View all launch options (for manual copy-paste)")
                
                config_choice = input("Choose option (1-2): ").strip()
                
                if config_choice == "1":
                    # Interactive mode with automatic application
                    rdna3 = input("RDNA3 GPU workaround needed? (y/n): ").lower() == 'y'
                    manager.add_steam_launch_options(selected_game["app_id"], rdna3, auto_apply=True)
                    
                elif config_choice == "2":
                    # Display mode for manual application
                    rdna3 = input("RDNA3 GPU workaround needed? (y/n): ").lower() == 'y'
                    manager.add_steam_launch_options(selected_game["app_id"], rdna3, auto_apply=False)
                    
                else:
                    print("Invalid option")
                
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
            # Show drive/library scan details
            print("\n=== Drive and Library Scan Details ===")
            
            # Show mounted drives
            print("\n1. Mounted Drives:")
            try:
                result = subprocess.run(['mount'], capture_output=True, text=True)
                mount_lines = result.stdout.split('\n')
                for line in mount_lines:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == 'on':
                        device = parts[0]
                        mount_point = parts[2]
                        fs_type = parts[4] if len(parts) > 4 else "unknown"
                        
                        if (mount_point.startswith('/mnt/') or 
                            mount_point.startswith('/media/') or 
                            mount_point.startswith('/run/media/') or
                            mount_point == '/' or
                            mount_point.startswith('/home')):
                            print(f"   {device} -> {mount_point} ({fs_type})")
            except Exception as e:
                print(f"   Error reading mount info: {e}")
            
            # Show Steam libraries
            print("\n2. Steam Libraries Found:")
            libraries = manager._find_all_steam_libraries()
            for lib in libraries:
                is_ntfs = manager._is_ntfs_drive(lib)
                fs_info = " (NTFS)" if is_ntfs else ""
                print(f"   {lib}{fs_info}")
                
                # Show game count for each library
                steamapps_path = lib / "steamapps"
                if steamapps_path.exists():
                    manifests = manager._safe_case_insensitive_glob(steamapps_path, "appmanifest_*.acf")
                    print(f"     -> {len(manifests)} games")
            
            # Show total games
            games = manager.get_steam_games()
            print(f"\n3. Total Games Found: {len(games)}")
            
            # Show external drive locations checked
            print("\n4. External Drive Locations Checked:")
            external_locations = ["/mnt", "/media", "/run/media"]
            for loc in external_locations:
                if Path(loc).exists():
                    print(f"   ✓ {loc}")
                else:
                    print(f"   ✗ {loc} (not found)")
        
        elif choice == "9":
            # Check/Install dependencies
            print("\n=== Dependency Check and Installation ===")
            dep_manager.check_all_dependencies()
            
            input("\nPress Enter to continue...")
        
        elif choice == "10":
            # Test VDF launch options functionality
            print("\n=== Testing VDF Launch Options Functionality ===")
            try:
                import subprocess
                result = subprocess.run(['python3', 'test_vdf_launch_options.py'], 
                                     capture_output=False, text=True)
                if result.returncode == 0:
                    print("✅ All tests passed!")
                else:
                    print("❌ Some tests failed!")
            except Exception as e:
                print(f"❌ Error running tests: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == "11":
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()