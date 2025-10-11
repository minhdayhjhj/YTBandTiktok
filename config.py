import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Cấu hình cho TikTok Uploader"""
    
    # TikTok credentials
    TIKTOK_USERNAME = os.getenv('TIKTOK_USERNAME', '')
    TIKTOK_PASSWORD = os.getenv('TIKTOK_PASSWORD', '')
    
    # Default settings
    DEFAULT_CAPTION = os.getenv('DEFAULT_CAPTION', 'Check out this amazing video! #viral #fyp')
    DEFAULT_HASHTAGS = os.getenv('DEFAULT_HASHTAGS', 'viral,fyp,trending,funny').split(',')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    WAIT_TIMEOUT = int(os.getenv('WAIT_TIMEOUT', '30'))
    
    # Upload settings
    MAX_VIDEO_SIZE_MB = int(os.getenv('MAX_VIDEO_SIZE_MB', '500'))
    SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv']