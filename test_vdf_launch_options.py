#!/usr/bin/env python3

"""
Test script for VDF launch options modification functionality
Tests the OptiScaler Manager's ability to modify Steam VDF files correctly
"""

import sys
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from optiscaler_manager import OptiScalerManager

def create_test_vdf_content(app_id="12345"):
    """Create a sample VDF content for testing"""
    return f'''
"UserLocalConfigStore"
{{
    "Software"
    {{
        "Valve"
        {{
            "Steam"
            {{
                "apps"
                {{
                    "{app_id}"
                    {{
                        "name"        "Test Game"
                        "LastUpdated" "1234567890"
                        "SizeOnDisk"  "1000000"
                        "tool"        "0"
                    }}
                    "54321"
                    {{
                        "name"        "Another Game"
                        "LastUpdated" "1234567891"
                        "LaunchOptions"    "existing_option"
                    }}
                }}
            }}
        }}
    }}
}}
'''

def test_vdf_modification():
    """Test VDF modification functionality"""
    print("=== Testing VDF Launch Options Modification ===")
    
    # Create a temporary directory for testing
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test VDF file
        test_vdf_path = temp_path / "test_localconfig.vdf"
        test_app_id = "12345"
        test_command = 'WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%'
        
        with open(test_vdf_path, 'w', encoding='utf-8') as f:
            f.write(create_test_vdf_content(test_app_id))
        
        print(f"✓ Created test VDF file: {test_vdf_path}")
        
        # Create OptiScaler manager instance
        manager = OptiScalerManager()
        
        # Test 1: Add launch options to app without existing options
        print(f"\nTest 1: Adding launch options to app {test_app_id}")
        
        # Read original content
        with open(test_vdf_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Modify the VDF
        success = manager._modify_vdf_launch_options(original_content, test_vdf_path, test_app_id, test_command)
        
        if success:
            print("✅ Test 1 PASSED: Launch options added successfully")
            
            # Verify the modification
            with open(test_vdf_path, 'r', encoding='utf-8') as f:
                modified_content = f.read()
            
            if 'LaunchOptions' in modified_content and test_command.replace('"', '\\"') in modified_content:
                print("✅ Verification: Launch options found in modified VDF")
            else:
                print("❌ Verification FAILED: Launch options not found in modified VDF")
                
        else:
            print("❌ Test 1 FAILED: Could not add launch options")
            return False
        
        # Test 2: Replace existing launch options
        print(f"\nTest 2: Replacing existing launch options for app 54321")
        
        test_app_id_2 = "54321"
        new_test_command = 'mangohud WINEDLLOVERRIDES="dxgi=n,b" PROTON_FSR4_UPGRADE=1 %command%'
        
        with open(test_vdf_path, 'r', encoding='utf-8') as f:
            content_before_replace = f.read()
        
        success = manager._modify_vdf_launch_options(content_before_replace, test_vdf_path, test_app_id_2, new_test_command)
        
        if success:
            print("✅ Test 2 PASSED: Existing launch options replaced successfully")
            
            # Verify the modification
            with open(test_vdf_path, 'r', encoding='utf-8') as f:
                final_content = f.read()
            
            if new_test_command.replace('"', '\\"') in final_content and 'existing_option' not in final_content:
                print("✅ Verification: Old options replaced with new ones")
            else:
                print("❌ Verification FAILED: Old options not properly replaced")
                
        else:
            print("❌ Test 2 FAILED: Could not replace existing launch options")
            return False
        
        # Test 3: Test VDF syntax preservation
        print(f"\nTest 3: Checking VDF syntax preservation")
        
        with open(test_vdf_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        # Check for proper VDF structure
        syntax_checks = [
            ('"UserLocalConfigStore"' in final_content, "Root section preserved"),
            ('"Software"' in final_content, "Software section preserved"),
            ('"Valve"' in final_content, "Valve section preserved"),
            ('"Steam"' in final_content, "Steam section preserved"),
            ('"apps"' in final_content, "Apps section preserved"),
            (final_content.count('{') == final_content.count('}'), "Braces balanced"),
            ('LaunchOptions' in final_content, "LaunchOptions added"),
        ]
        
        all_syntax_passed = True
        for check, description in syntax_checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_syntax_passed = False
        
        if all_syntax_passed:
            print("✅ Test 3 PASSED: VDF syntax properly preserved")
        else:
            print("❌ Test 3 FAILED: VDF syntax issues detected")
            return False
        
        # Test 4: Test escape handling
        print(f"\nTest 4: Testing quote escaping in launch options")
        
        tricky_command = 'WINEDLLOVERRIDES="dxgi=n,b;nvngx=n,b" PROTON_FSR4_UPGRADE=1 -some_arg="value with spaces" %command%'
        
        with open(test_vdf_path, 'r', encoding='utf-8') as f:
            content_before_escape = f.read()
        
        success = manager._modify_vdf_launch_options(content_before_escape, test_vdf_path, test_app_id, tricky_command)
        
        if success:
            with open(test_vdf_path, 'r', encoding='utf-8') as f:
                escaped_content = f.read()
            
            # Check that quotes are properly escaped
            if tricky_command.replace('"', '\\"') in escaped_content:
                print("✅ Test 4 PASSED: Quotes properly escaped in VDF")
            else:
                print("❌ Test 4 FAILED: Quote escaping not working correctly")
                return False
        else:
            print("❌ Test 4 FAILED: Could not apply command with quotes")
            return False
        
        print(f"\n✅ ALL TESTS PASSED! VDF modification functionality is working correctly.")
        
        # Show final VDF content for manual inspection
        print(f"\nFinal VDF content:")
        print("=" * 50)
        with open(test_vdf_path, 'r', encoding='utf-8') as f:
            print(f.read())
        print("=" * 50)
        
        return True

def test_launch_options_catalog():
    """Test the launch options catalog functionality"""
    print("\n=== Testing Launch Options Catalog ===")
    
    manager = OptiScalerManager()
    
    # Test basic catalog
    catalog = manager.get_launch_options_catalog(rdna3_workaround=False, include_mangohud=True)
    
    print(f"✓ Generated catalog with {len(catalog)} options")
    
    # Test categories
    categories = set(option["category"] for option in catalog.values())
    expected_categories = {"basic", "advanced", "debug", "experimental", "fsr4", "game_specific", "compatibility"}
    
    if expected_categories.issubset(categories):
        print("✅ All expected categories present")
    else:
        missing = expected_categories - categories
        print(f"❌ Missing categories: {missing}")
        return False
    
    # Test RDNA3 variants
    catalog_rdna3 = manager.get_launch_options_catalog(rdna3_workaround=True, include_mangohud=True)
    
    rdna3_options = [k for k in catalog_rdna3.keys() if "rdna3" in k]
    if rdna3_options:
        print(f"✅ RDNA3 variants generated: {len(rdna3_options)} options")
    else:
        print("❌ No RDNA3 variants found")
        return False
    
    # Test MangoHUD filtering
    catalog_no_mangohud = manager.get_launch_options_catalog(rdna3_workaround=False, include_mangohud=False)
    
    mangohud_options = [k for k in catalog_no_mangohud.keys() if "mangohud" in k]
    if not mangohud_options:
        print("✅ MangoHUD filtering working correctly")
    else:
        print(f"❌ MangoHUD options found when they should be filtered: {mangohud_options}")
        return False
    
    print("✅ Launch options catalog tests passed!")
    return True

def main():
    """Main test function"""
    print("OptiScaler Manager VDF Launch Options Test Suite")
    print("=" * 60)
    
    try:
        # Test VDF modification
        if not test_vdf_modification():
            print("❌ VDF modification tests failed!")
            return 1
        
        # Test launch options catalog
        if not test_launch_options_catalog():
            print("❌ Launch options catalog tests failed!")
            return 1
        
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The VDF launch options functionality is working correctly.")
        return 0
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())