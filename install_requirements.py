#!/usr/bin/env python3
"""
Script tự động cài đặt requirements cho TikTok Auto Upload Tool
"""

import subprocess
import sys
import os

def install_package(package):
    """Cài đặt package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 TikTok Auto Upload Tool - Auto Installer")
    print("=" * 50)
    
    # Danh sách packages cần cài đặt
    packages = [
        "selenium==4.15.2",
        "webdriver-manager==4.0.1", 
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "Pillow==10.1.0",
        "moviepy==1.0.3"
    ]
    
    print("📦 Đang cài đặt các package cần thiết...")
    print()
    
    success_count = 0
    for package in packages:
        print(f"⏳ Cài đặt {package}...", end=" ")
        if install_package(package):
            print("✅ Thành công")
            success_count += 1
        else:
            print("❌ Thất bại")
    
    print()
    print("=" * 50)
    print(f"📊 Kết quả: {success_count}/{len(packages)} packages đã cài đặt thành công")
    
    if success_count == len(packages):
        print("🎉 Cài đặt hoàn tất! Bạn có thể chạy tool ngay bây giờ.")
        print()
        print("🚀 Để chạy tool:")
        print("   python tiktok_auto_upload.py")
    else:
        print("⚠️  Một số package cài đặt thất bại. Vui lòng cài đặt thủ công:")
        print("   pip install -r requirements.txt")
    
    input("\nNhấn Enter để thoát...")

if __name__ == "__main__":
    main()