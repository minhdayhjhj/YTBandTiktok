#!/usr/bin/env python3
"""
Test script for TikTok Auto Upload Tool
Kiểm tra cài đặt và dependencies
"""

import sys
import importlib
import subprocess

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'selenium',
        'webdriver_manager', 
        'requests',
        'schedule',
        'tkinter'
    ]
    
    optional_packages = [
        'openai',
        'pyinstaller'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            all_good = False
    
    print("\n🔧 Optional packages:")
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"⚠️  {package} - MISSING (optional)")
    
    return all_good

def test_chrome_driver():
    """Test Chrome WebDriver availability"""
    print("\n🌐 Testing Chrome WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to get ChromeDriver
        service = Service(ChromeDriverManager().install())
        print("✅ ChromeDriver - OK")
        return True
    except Exception as e:
        print(f"❌ ChromeDriver - ERROR: {e}")
        return False

def test_file_structure():
    """Test file structure"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'tiktok_auto_uploader.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_good = True
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                print(f"✅ {file} - OK")
        except FileNotFoundError:
            print(f"❌ {file} - MISSING")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🎬 TikTok Auto Upload Tool - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Chrome WebDriver", test_chrome_driver),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to run TikTok Auto Upload Tool.")
        print("\nTo start the application, run:")
        print("  python tiktok_auto_uploader.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)