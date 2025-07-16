#!/usr/bin/env python3
"""
Test script for dependency management functionality
"""

import sys
from optiscaler_manager import DependencyManager

def test_system_detection():
    """Test system detection capabilities."""
    print("🔍 Testing system detection...")
    
    dep_manager = DependencyManager()
    
    # Test package manager detection
    pm = dep_manager.detect_package_manager()
    print(f"Package manager detected: {pm}")
    
    # Test distro detection
    distro = dep_manager.detect_distro()
    print(f"Distribution detected: {distro}")
    
    # Test display server detection
    wayland = dep_manager.is_wayland()
    print(f"Wayland display server: {wayland}")
    
    return pm is not None

def test_clipboard_detection():
    """Test clipboard app detection."""
    print("\n📋 Testing clipboard detection...")
    
    dep_manager = DependencyManager()
    
    installed_apps = []
    for app_name in dep_manager.clipboard_apps.keys():
        try:
            import subprocess
            result = subprocess.run(['which', app_name], capture_output=True, text=True)
            if result.returncode == 0:
                installed_apps.append(app_name)
                print(f"✅ {app_name} found")
            else:
                print(f"❌ {app_name} not found")
        except Exception:
            print(f"❌ {app_name} not found")
    
    return len(installed_apps) > 0

def test_tool_detection():
    """Test system tool detection."""
    print("\n🔧 Testing system tool detection...")
    
    dep_manager = DependencyManager()
    
    tools = ['7z', 'git', 'wine', 'curl', 'wget']
    found_tools = []
    
    for tool in tools:
        try:
            import subprocess
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                found_tools.append(tool)
                print(f"✅ {tool} found")
            else:
                print(f"❌ {tool} not found")
        except Exception:
            print(f"❌ {tool} not found")
    
    return len(found_tools) > 0

def test_python_modules():
    """Test Python module detection."""
    print("\n🐍 Testing Python module detection...")
    
    dep_manager = DependencyManager()
    
    # Test requests module
    if dep_manager.check_python_module('requests'):
        print("✅ requests module available")
        return True
    else:
        print("❌ requests module not available")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Dependency Management Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("System Detection", test_system_detection()))
    test_results.append(("Python Modules", test_python_modules()))
    test_results.append(("System Tools", test_tool_detection()))
    test_results.append(("Clipboard Apps", test_clipboard_detection()))
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "⚠️ SOME TESTS FAILED"
    print(f"Overall: {overall_status}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())