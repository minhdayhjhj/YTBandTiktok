#!/usr/bin/env python3
"""
Quick Start Script for TikTok Auto Upload Tool
Script khởi động nhanh với kiểm tra tự động
"""

import os
import sys
import subprocess
import platform

def check_and_install_dependencies():
    """Check and install dependencies if needed"""
    print("🔍 Checking dependencies...")
    
    try:
        import selenium
        import webdriver_manager
        import requests
        import schedule
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

def check_chrome_browser():
    """Check if Chrome browser is installed"""
    print("🌐 Checking Chrome browser...")
    
    system = platform.system().lower()
    
    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    elif system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser"
        ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print("✅ Chrome browser found!")
            return True
    
    print("⚠️  Chrome browser not found!")
    print("Please install Google Chrome from: https://www.google.com/chrome/")
    return False

def run_application():
    """Run the TikTok Auto Upload Tool"""
    print("🚀 Starting TikTok Auto Upload Tool...")
    
    try:
        # Import and run the main application
        from tiktok_auto_uploader import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        print("Make sure tiktok_auto_uploader.py is in the current directory.")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False
    
    return True

def main():
    """Main quick start function"""
    print("🎬 TikTok Auto Upload Tool - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        return False
    
    # Check Chrome browser
    if not check_chrome_browser():
        print("⚠️  Chrome browser is required but not found.")
        print("Please install Chrome and try again.")
        return False
    
    # Run the application
    print("\n🎉 All checks passed! Starting application...")
    return run_application()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Quick start failed. Please check the errors above.")
            input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")