#!/usr/bin/env python3
"""
Setup Verification Script for Baato.io Ride-Sharing Test Suite
============================================================

This script verifies that all dependencies are properly installed
and the test environment is ready to run.
"""

import sys
import json
import importlib
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    if sys.version_info >= (3, 8):
        return True, f"✅ Python {sys.version.split()[0]} - Compatible"
    else:
        return False, f"❌ Python {sys.version.split()[0]} - Requires Python 3.8+"

def check_required_packages() -> List[Tuple[str, bool, str]]:
    """Check if all required packages are installed."""
    required_packages = [
        'requests',
        'aiohttp', 
        'googlemaps',
        'matplotlib',
        'seaborn',
        'pandas',
        'numpy',
        'plotly',
        'folium',
        'geopy',
        'haversine',
        'tabulate',
        'colorama',
        'tqdm'
    ]
    
    results = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            results.append((package, True, f"✅ {package} - Installed"))
        except ImportError:
            results.append((package, False, f"❌ {package} - Missing"))
    
    return results

def check_config_file() -> Tuple[bool, str, dict]:
    """Check if config file exists and is properly formatted."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check required keys
        required_keys = ['api_keys', 'test_settings', 'test_locations']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            return False, f"❌ Config file missing keys: {missing_keys}", {}
        
        # Check API keys
        api_keys = config.get('api_keys', {})
        baato_key = api_keys.get('baato', '')
        google_key = api_keys.get('google', '')
        
        if baato_key == 'YOUR_BAATO_API_KEY_HERE' or not baato_key:
            return False, "⚠️ Baato.io API key not configured", config
        
        if google_key == 'YOUR_GOOGLE_MAPS_API_KEY_HERE' or not google_key:
            return False, "⚠️ Google Maps API key not configured", config
        
        return True, "✅ Config file properly configured", config
        
    except FileNotFoundError:
        return False, "❌ Config file not found", {}
    except json.JSONDecodeError:
        return False, "❌ Config file has invalid JSON format", {}

def check_main_script() -> Tuple[bool, str]:
    """Check if the main test script exists and is importable."""
    try:
        import baato_rideshare_feasibility_test
        return True, "✅ Main test script available"
    except ImportError as e:
        return False, f"❌ Main test script error: {str(e)}"

def test_basic_functionality() -> Tuple[bool, str]:
    """Test basic functionality without API calls."""
    try:
        # Test creating test data structures
        test_data = {
            'origin': [27.7172, 85.3240],
            'destination': [27.6767, 85.3167],
            'name': 'Test Route'
        }
        
        # Test coordinate validation
        lat, lon = test_data['origin']
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False, "❌ Coordinate validation failed"
        
        return True, "✅ Basic functionality tests passed"
    except Exception as e:
        return False, f"❌ Basic functionality error: {str(e)}"

def run_verification():
    """Run complete verification of the setup."""
    print("🔍 Baato.io Ride-Sharing Test Suite - Setup Verification")
    print("=" * 60)
    
    all_good = True
    
    # Check Python version
    python_ok, python_msg = check_python_version()
    print(f"\n📋 Python Version Check:")
    print(f"   {python_msg}")
    if not python_ok:
        all_good = False
    
    # Check packages
    print(f"\n📦 Package Dependencies Check:")
    package_results = check_required_packages()
    missing_packages = []
    
    for package, installed, msg in package_results:
        print(f"   {msg}")
        if not installed:
            missing_packages.append(package)
            all_good = False
    
    if missing_packages:
        print(f"\n💡 To install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
    
    # Check config file
    print(f"\n⚙️ Configuration Check:")
    config_ok, config_msg, config_data = check_config_file()
    print(f"   {config_msg}")
    if not config_ok:
        all_good = False
        if "not found" in config_msg:
            print(f"   💡 Copy and edit config.json with your API keys")
    
    # Check main script
    print(f"\n🐍 Main Script Check:")
    script_ok, script_msg = check_main_script()
    print(f"   {script_msg}")
    if not script_ok:
        all_good = False
    
    # Test basic functionality
    print(f"\n🧪 Basic Functionality Check:")
    func_ok, func_msg = test_basic_functionality()
    print(f"   {func_msg}")
    if not func_ok:
        all_good = False
    
    # Summary
    print(f"\n{'='*60}")
    if all_good:
        print("🎉 SUCCESS: Your environment is ready!")
        print("\n🚀 Next Steps:")
        print("   1. Run: python baato_rideshare_feasibility_test.py")
        print("   2. Or try: python example_usage.py")
        print("   3. Check QUICKSTART.md for usage examples")
    else:
        print("❌ ISSUES FOUND: Please fix the issues above before proceeding")
        print("\n🔧 Common Solutions:")
        print("   • Install missing packages: pip install -r requirements.txt")
        print("   • Configure API keys in config.json")
        print("   • Ensure you're using Python 3.8+")
    
    print(f"\n📖 For help, see:")
    print(f"   • README.md - Complete documentation")
    print(f"   • QUICKSTART.md - Quick setup guide")
    print(f"   • example_usage.py - Usage examples")
    
    return all_good

def main():
    """Main verification function."""
    try:
        success = run_verification()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Verification failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())