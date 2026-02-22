#!/usr/bin/env python3
"""
Test script to verify network UI configuration
"""

import os
import sys
from pathlib import Path

def test_streamlit_config():
    """Test that Streamlit config file exists and is valid"""
    config_path = Path('.streamlit/config.toml')
    
    print("🧪 Testing Network UI Configuration")
    print("=" * 50)
    
    # Check config file exists
    if not config_path.exists():
        print("❌ FAIL: .streamlit/config.toml not found")
        return False
    print("✅ PASS: Config file exists")
    
    # Check config content
    with open(config_path, 'r') as f:
        content = f.read()
    
    required_settings = [
        'enableCORS',
        'enableXsrfProtection',
        'headless',
        'port'
    ]
    
    for setting in required_settings:
        if setting in content:
            print(f"✅ PASS: '{setting}' configured")
        else:
            print(f"❌ FAIL: '{setting}' not found in config")
            return False
    
    return True

def test_network_script():
    """Test that network startup script exists and is executable"""
    script_path = Path('start_ui_network.sh')
    
    # Check script exists
    if not script_path.exists():
        print("❌ FAIL: start_ui_network.sh not found")
        return False
    print("✅ PASS: Network startup script exists")
    
    # Check script is executable
    if os.access(script_path, os.X_OK):
        print("✅ PASS: Script is executable")
    else:
        print("⚠️  WARNING: Script not executable (chmod +x start_ui_network.sh)")
    
    return True

def test_ui_app():
    """Test that ui_app.py exists"""
    ui_path = Path('ui_app.py')
    
    if not ui_path.exists():
        print("❌ FAIL: ui_app.py not found")
        return False
    print("✅ PASS: UI app exists")
    
    return True

def test_dependencies():
    """Test that required dependencies are importable"""
    dependencies = {
        'streamlit': 'Streamlit',
        'wellness_buddy': 'Wellness Buddy Core',
        'user_profile': 'User Profile Module',
        'data_store': 'Data Store Module'
    }
    
    all_imported = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ PASS: {name} available")
        except ImportError:
            print(f"❌ FAIL: {name} not available (install requirements.txt)")
            all_imported = False
    
    return all_imported

def main():
    """Run all tests"""
    print("\n🌐 AI Wellness Buddy - Network UI Tests\n")
    
    tests = [
        ("Streamlit Configuration", test_streamlit_config),
        ("Network Startup Script", test_network_script),
        ("UI Application", test_ui_app),
        ("Dependencies", test_dependencies)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Network UI is ready to use.")
        print("\nTo start: bash start_ui_network.sh")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
