#!/usr/bin/env python3
"""
Build script for TikTok Auto Upload Tool
Tạo file .exe từ source code
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build executable using PyInstaller"""
    print("🔨 Building TikTok Auto Upload Tool executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name=TikTok_Auto_Uploader",
        "--icon=icon.ico",  # Add icon if available
        "--add-data=requirements.txt;.",
        "tiktok_auto_uploader.py"
    ]
    
    try:
        # Run PyInstaller
        subprocess.run(cmd, check=True)
        
        print("✅ Build completed successfully!")
        print("📁 Executable location: dist/TikTok_Auto_Uploader.exe")
        
        # Create distribution folder
        dist_folder = Path("dist")
        if dist_folder.exists():
            print(f"📦 Distribution folder: {dist_folder.absolute()}")
            
            # List files in dist folder
            for file in dist_folder.iterdir():
                print(f"  - {file.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it first:")
        print("   pip install pyinstaller")
        return False
    
    return True

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove build directories
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  - Removed {folder}/")
    
    # Remove .spec file
    spec_file = "TikTok_Auto_Uploader.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  - Removed {spec_file}")

if __name__ == "__main__":
    print("🎬 TikTok Auto Upload Tool - Build Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
    else:
        if build_executable():
            print("\n🎉 Build completed successfully!")
            print("You can now distribute the executable file.")
        else:
            print("\n❌ Build failed. Please check the errors above.")