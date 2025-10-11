#!/usr/bin/env python3
"""
Ví dụ sử dụng TikTok Uploader Tool
"""

from tiktok_uploader import TikTokUploader
import os

def example_basic_upload():
    """Ví dụ upload cơ bản"""
    print("🚀 Ví dụ upload cơ bản")
    
    uploader = TikTokUploader(headless=False)
    
    try:
        # Đăng nhập
        username = input("Nhập username TikTok: ")
        password = input("Nhập password TikTok: ")
        
        if uploader.login(username, password):
            # Upload video
            video_path = input("Nhập đường dẫn video: ")
            caption = input("Nhập caption (Enter để bỏ qua): ")
            hashtags_input = input("Nhập hashtags (cách nhau bởi dấu phẩy, Enter để bỏ qua): ")
            
            hashtags = [tag.strip() for tag in hashtags_input.split(',')] if hashtags_input else []
            
            uploader.upload_video(video_path, caption, hashtags)
        
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng chương trình")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
    finally:
        uploader.close()

def example_batch_upload():
    """Ví dụ upload nhiều video"""
    print("🚀 Ví dụ upload nhiều video")
    
    uploader = TikTokUploader(headless=True)  # Chạy headless cho batch upload
    
    try:
        # Đăng nhập
        username = input("Nhập username TikTok: ")
        password = input("Nhập password TikTok: ")
        
        if not uploader.login(username, password):
            return
        
        # Danh sách video cần upload
        videos = [
            {
                "path": "/path/to/video1.mp4",
                "caption": "Amazing video 1! #viral #fyp",
                "hashtags": ["viral", "fyp", "trending"]
            },
            {
                "path": "/path/to/video2.mp4", 
                "caption": "Cool video 2! #funny #comedy",
                "hashtags": ["funny", "comedy", "lol"]
            }
        ]
        
        for i, video in enumerate(videos, 1):
            print(f"📤 Uploading video {i}/{len(videos)}: {video['path']}")
            
            if uploader.upload_video(video['path'], video['caption'], video['hashtags']):
                print(f"✅ Video {i} uploaded successfully!")
            else:
                print(f"❌ Failed to upload video {i}")
            
            # Nghỉ giữa các lần upload để tránh bị rate limit
            if i < len(videos):
                print("⏳ Waiting 30 seconds before next upload...")
                import time
                time.sleep(30)
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
    finally:
        uploader.close()

def example_with_config():
    """Ví dụ sử dụng với file config"""
    from config import Config
    
    print("🚀 Ví dụ sử dụng với config")
    
    # Kiểm tra config
    if not Config.TIKTOK_USERNAME or not Config.TIKTOK_PASSWORD:
        print("❌ Vui lòng cấu hình TIKTOK_USERNAME và TIKTOK_PASSWORD trong file .env")
        return
    
    uploader = TikTokUploader(headless=Config.HEADLESS_MODE)
    
    try:
        if uploader.login(Config.TIKTOK_USERNAME, Config.TIKTOK_PASSWORD):
            video_path = input("Nhập đường dẫn video: ")
            
            # Sử dụng config mặc định
            caption = Config.DEFAULT_CAPTION
            hashtags = Config.DEFAULT_HASHTAGS
            
            print(f"Caption: {caption}")
            print(f"Hashtags: {', '.join(hashtags)}")
            
            uploader.upload_video(video_path, caption, hashtags)
    
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
    finally:
        uploader.close()

if __name__ == "__main__":
    print("🎬 TikTok Uploader Tool - Examples")
    print("=" * 40)
    print("1. Upload cơ bản")
    print("2. Upload nhiều video")
    print("3. Upload với config")
    print("=" * 40)
    
    choice = input("Chọn ví dụ (1-3): ")
    
    if choice == "1":
        example_basic_upload()
    elif choice == "2":
        example_batch_upload()
    elif choice == "3":
        example_with_config()
    else:
        print("❌ Lựa chọn không hợp lệ")