#!/usr/bin/env python3
"""
TikTok Auto Upload Tool - Enhanced Version
Công cụ tự động đăng video lên TikTok với tính năng nâng cao
"""

import os
import time
import random
import json
import logging
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests
from dataclasses import dataclass
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_uploader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UploadTask:
    """Represents a video upload task"""
    video_path: str
    caption: str
    hashtags: List[str]
    schedule_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"  # pending, uploading, completed, failed

class TikTokUploaderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 TikTok Auto Upload Tool - Enhanced")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.driver = None
        self.video_path = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.caption = tk.StringVar()
        self.hashtags = tk.StringVar()
        self.is_uploading = False
        self.upload_tasks: List[UploadTask] = []
        self.cookies_file = "tiktok_cookies.json"
        self.config_file = "tiktok_config.json"
        self.log_file = "tiktok_uploader.log"
        
        # Load saved configuration
        self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def load_config(self):
        """Load saved configuration and cookies"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.username.set(config.get('username', ''))
                    self.password.set(config.get('password', ''))
                    self.caption.set(config.get('caption', ''))
                    self.hashtags.set(config.get('hashtags', ''))
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
    
    def save_config(self):
        """Save current configuration"""
        try:
            config = {
                'username': self.username.get(),
                'password': self.password.get(),
                'caption': self.caption.get(),
                'hashtags': self.hashtags.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def setup_ui(self):
        """Create enhanced user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Success.TLabel', foreground='#00ff00')
        style.configure('Error.TLabel', foreground='#ff0000')
        style.configure('Warning.TLabel', foreground='#ffaa00')
        style.configure('Accent.TButton', foreground='#ffffff', background='#ff0050')
        
        # Title
        title_label = tk.Label(self.root, text="🎬 TikTok Auto Upload Tool - Enhanced", 
                              font=("Arial", 18, "bold"), fg="#ff0050")
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Single Upload Tab
        single_frame = ttk.Frame(notebook)
        notebook.add(single_frame, text="📤 Single Upload")
        self.setup_single_upload_tab(single_frame)
        
        # Batch Upload Tab
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="📂 Batch Upload")
        self.setup_batch_upload_tab(batch_frame)
        
        # Schedule Tab
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="🕓 Schedule")
        self.setup_schedule_tab(schedule_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        self.setup_settings_tab(settings_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng upload video...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_single_upload_tab(self, parent):
        """Setup single upload tab"""
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video selection
        video_frame = ttk.LabelFrame(main_frame, text="📁 Chọn Video", padding="10")
        video_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(video_frame, text="File Video:").pack(anchor=tk.W)
        video_path_frame = ttk.Frame(video_frame)
        video_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(video_path_frame, textvariable=self.video_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(video_path_frame, text="Browse", command=self.browse_video).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Login info
        login_frame = ttk.LabelFrame(main_frame, text="🔐 Thông tin đăng nhập", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Username:").pack(anchor=tk.W)
        ttk.Entry(login_frame, textvariable=self.username, width=60).pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(login_frame, text="Password:").pack(anchor=tk.W)
        ttk.Entry(login_frame, textvariable=self.password, show="*", width=60).pack(fill=tk.X, pady=(2, 0))
        
        # Video details
        details_frame = ttk.LabelFrame(main_frame, text="📝 Chi tiết video", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(details_frame, text="Caption:").pack(anchor=tk.W)
        caption_entry = ttk.Entry(details_frame, textvariable=self.caption, width=60)
        caption_entry.pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(details_frame, text="Hashtags (cách nhau bởi dấu phẩy):").pack(anchor=tk.W)
        ttk.Entry(details_frame, textvariable=self.hashtags, width=60).pack(fill=tk.X, pady=(2, 5))
        
        # AI Caption Generation
        ai_frame = ttk.Frame(details_frame)
        ai_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(ai_frame, text="🤖 Generate AI Caption", command=self.generate_ai_caption).pack(side=tk.LEFT)
        ttk.Button(ai_frame, text="💾 Save Config", command=self.save_config).pack(side=tk.RIGHT)
        
        # Upload button
        self.upload_btn = ttk.Button(main_frame, text="🚀 BẮT ĐẦU UPLOAD", 
                                    command=self.start_single_upload, style="Accent.TButton")
        self.upload_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_batch_upload_tab(self, parent):
        """Setup batch upload tab"""
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Chọn Thư Mục Video", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_path = tk.StringVar()
        folder_path_frame = ttk.Frame(folder_frame)
        folder_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(folder_path_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_path_frame, text="Browse Folder", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Batch settings
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài Đặt Batch", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Delay between uploads
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, pady=(2, 5))
        ttk.Label(delay_frame, text="Delay giữa các upload (giây):").pack(side=tk.LEFT)
        self.batch_delay = tk.StringVar(value="30")
        ttk.Entry(delay_frame, textvariable=self.batch_delay, width=10).pack(side=tk.RIGHT)
        
        # Auto caption
        self.auto_caption = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Tự động tạo caption cho mỗi video", 
                       variable=self.auto_caption).pack(anchor=tk.W, pady=2)
        
        # Batch upload button
        self.batch_upload_btn = ttk.Button(main_frame, text="📂 BẮT ĐẦU BATCH UPLOAD", 
                                          command=self.start_batch_upload, style="Accent.TButton")
        self.batch_upload_btn.pack(pady=20)
        
        # Batch progress
        self.batch_progress = ttk.Progressbar(main_frame, mode='determinate')
        self.batch_progress.pack(fill=tk.X, pady=(0, 10))
        
        # Batch log
        batch_log_frame = ttk.LabelFrame(main_frame, text="📋 Batch Log", padding="10")
        batch_log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.batch_log_text = scrolledtext.ScrolledText(batch_log_frame, height=8, width=80)
        self.batch_log_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_schedule_tab(self, parent):
        """Setup scheduling tab"""
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Schedule settings
        schedule_frame = ttk.LabelFrame(main_frame, text="🕓 Lập Lịch Upload", padding="10")
        schedule_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Time selection
        time_frame = ttk.Frame(schedule_frame)
        time_frame.pack(fill=tk.X, pady=(2, 5))
        ttk.Label(time_frame, text="Thời gian upload:").pack(side=tk.LEFT)
        self.schedule_time = tk.StringVar(value="09:00")
        ttk.Entry(time_frame, textvariable=self.schedule_time, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Date selection
        date_frame = ttk.Frame(schedule_frame)
        date_frame.pack(fill=tk.X, pady=(2, 5))
        ttk.Label(date_frame, text="Ngày upload:").pack(side=tk.LEFT)
        self.schedule_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(date_frame, textvariable=self.schedule_date, width=15).pack(side=tk.LEFT, padx=(5, 0))
        
        # Schedule button
        ttk.Button(schedule_frame, text="📅 Lên Lịch Upload", command=self.schedule_upload).pack(pady=10)
        
        # Scheduled tasks list
        tasks_frame = ttk.LabelFrame(main_frame, text="📋 Danh Sách Lịch", padding="10")
        tasks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for scheduled tasks
        columns = ('Video', 'Caption', 'Schedule Time', 'Status')
        self.tasks_tree = ttk.Treeview(tasks_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.tasks_tree.heading(col, text=col)
            self.tasks_tree.column(col, width=150)
        
        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        
    def setup_settings_tab(self, parent):
        """Setup settings tab"""
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(main_frame, text="🌐 Proxy Settings", padding="10")
        proxy_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.use_proxy = tk.BooleanVar()
        ttk.Checkbutton(proxy_frame, text="Sử dụng Proxy", variable=self.use_proxy).pack(anchor=tk.W)
        
        proxy_config_frame = ttk.Frame(proxy_frame)
        proxy_config_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(proxy_config_frame, text="Proxy URL:").pack(side=tk.LEFT)
        self.proxy_url = tk.StringVar()
        ttk.Entry(proxy_config_frame, textvariable=self.proxy_url, width=40).pack(side=tk.LEFT, padx=(5, 0))
        
        # User Agent settings
        ua_frame = ttk.LabelFrame(main_frame, text="🕵️ User Agent", padding="10")
        ua_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.random_ua = tk.BooleanVar(value=True)
        ttk.Checkbutton(ua_frame, text="Random User Agent", variable=self.random_ua).pack(anchor=tk.W)
        
        # AI Settings
        ai_frame = ttk.LabelFrame(main_frame, text="🤖 AI Settings", padding="10")
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ai_frame, text="OpenAI API Key:").pack(anchor=tk.W)
        self.openai_key = tk.StringVar()
        ttk.Entry(ai_frame, textvariable=self.openai_key, show="*", width=50).pack(fill=tk.X, pady=(2, 5))
        
        # Save settings
        ttk.Button(main_frame, text="💾 Save Settings", command=self.save_settings).pack(pady=20)
        
    def browse_video(self):
        """Browse for video file"""
        filetypes = [
            ("Video files", "*.mp4 *.mov *.avi *.mkv *.webm"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Chọn video để upload",
            filetypes=filetypes
        )
        if filename:
            self.video_path.set(filename)
            self.log(f"✅ Đã chọn video: {os.path.basename(filename)}")
    
    def browse_folder(self):
        """Browse for folder containing videos"""
        folder = filedialog.askdirectory(title="Chọn thư mục chứa video")
        if folder:
            self.folder_path.set(folder)
            self.batch_log(f"✅ Đã chọn thư mục: {folder}")
    
    def log(self, message, level="INFO"):
        """Add log message to single upload tab"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
        # Also log to file
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def batch_log(self, message, level="INFO"):
        """Add log message to batch upload tab"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.batch_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.batch_log_text.see(tk.END)
        self.root.update()
        
        # Also log to file
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def get_random_user_agent(self):
        """Get random user agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        return random.choice(user_agents)
    
    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced options"""
        try:
            self.log("🔧 Đang thiết lập browser...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-default-apps")
            
            # Random user agent
            if self.random_ua.get():
                ua = self.get_random_user_agent()
                chrome_options.add_argument(f"--user-agent={ua}")
                self.log(f"🕵️ Using User Agent: {ua[:50]}...")
            
            # Proxy settings
            if self.use_proxy.get() and self.proxy_url.get():
                chrome_options.add_argument(f"--proxy-server={self.proxy_url.get()}")
                self.log(f"🌐 Using Proxy: {self.proxy_url.get()}")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.get_random_user_agent()
            })
            
            self.log("✅ Browser đã sẵn sàng!")
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi thiết lập browser: {str(e)}", "ERROR")
            return False
    
    def load_cookies(self):
        """Load saved cookies"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    for cookie in cookies:
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            logger.warning(f"Could not add cookie: {e}")
                self.log("🍪 Đã load cookies từ file")
                return True
        except Exception as e:
            self.log(f"⚠️ Không thể load cookies: {e}", "WARNING")
        return False
    
    def save_cookies(self):
        """Save current cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            self.log("🍪 Đã lưu cookies")
        except Exception as e:
            self.log(f"⚠️ Không thể lưu cookies: {e}", "WARNING")
    
    def login_tiktok(self):
        """Login to TikTok with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.log(f"🔐 Đang đăng nhập TikTok... (Lần thử {attempt + 1}/{max_retries})")
                
                # Try to load cookies first
                if self.load_cookies():
                    self.driver.get("https://www.tiktok.com")
                    time.sleep(3)
                    
                    # Check if already logged in
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'avatar')]"))
                        )
                        self.log("✅ Đã đăng nhập bằng cookies!")
                        return True
                    except TimeoutException:
                        self.log("⚠️ Cookies không hợp lệ, đăng nhập thủ công...")
                
                # Manual login
                self.driver.get("https://www.tiktok.com/login")
                time.sleep(3)
                
                # Click login with username/password
                try:
                    login_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone / email / username')]"))
                    )
                    login_button.click()
                    time.sleep(2)
                except TimeoutException:
                    pass
                
                # Enter username
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
                )
                username_input.clear()
                username_input.send_keys(self.username.get())
                time.sleep(1)
                
                # Enter password
                password_input = self.driver.find_element(By.XPATH, "//input[@name='password']")
                password_input.clear()
                password_input.send_keys(self.password.get())
                time.sleep(1)
                
                # Click login
                login_submit = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_submit.click()
                
                # Wait for login success
                WebDriverWait(self.driver, 30).until(
                    lambda driver: "tiktok.com" in driver.current_url and "login" not in driver.current_url
                )
                
                # Save cookies for next time
                self.save_cookies()
                
                self.log("✅ Đăng nhập thành công!")
                return True
                
            except Exception as e:
                self.log(f"❌ Lỗi đăng nhập lần {attempt + 1}: {str(e)}", "ERROR")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                else:
                    return False
        
        return False
    
    def upload_video_with_retry(self, task: UploadTask):
        """Upload video with retry logic"""
        for attempt in range(task.max_retries):
            try:
                task.status = "uploading"
                self.log(f"📤 Đang upload video: {os.path.basename(task.video_path)} (Lần thử {attempt + 1}/{task.max_retries})")
                
                # Navigate to upload page
                self.driver.get("https://www.tiktok.com/upload")
                time.sleep(5)
                
                # Wait for file input with dynamic wait
                file_input = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                
                # Upload file
                file_input.send_keys(os.path.abspath(task.video_path))
                
                self.log("⏳ Video đang được xử lý...")
                
                # Wait for video processing with dynamic wait
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-text='true']"))
                )
                
                time.sleep(5)  # Additional wait for processing
                
                # Enter caption
                if task.caption:
                    caption_textarea = self.driver.find_element(By.XPATH, "//div[@data-text='true']")
                    caption_textarea.click()
                    caption_textarea.send_keys(task.caption)
                    time.sleep(2)
                
                # Add hashtags
                if task.hashtags:
                    hashtag_text = " ".join([f"#{tag.strip()}" for tag in task.hashtags])
                    caption_textarea = self.driver.find_element(By.XPATH, "//div[@data-text='true']")
                    caption_textarea.send_keys(f" {hashtag_text}")
                    time.sleep(2)
                
                # Click Post with dynamic wait
                post_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
                )
                post_button.click()
                
                # Wait for upload completion
                WebDriverWait(self.driver, 60).until(
                    lambda driver: "tiktok.com" in driver.current_url and "upload" not in driver.current_url
                )
                
                task.status = "completed"
                self.log(f"✅ Video đã được đăng thành công: {os.path.basename(task.video_path)}")
                return True
                
            except Exception as e:
                task.retry_count += 1
                self.log(f"❌ Lỗi upload lần {attempt + 1}: {str(e)}", "ERROR")
                if attempt < task.max_retries - 1:
                    time.sleep(10)  # Wait before retry
                else:
                    task.status = "failed"
                    return False
        
        return False
    
    def generate_ai_caption(self):
        """Generate AI-powered caption"""
        if not self.openai_key.get():
            messagebox.showwarning("Warning", "Vui lòng nhập OpenAI API Key trong Settings!")
            return
        
        try:
            self.log("🤖 Đang tạo caption bằng AI...")
            
            # Simple AI caption generation (you can enhance this with actual OpenAI API)
            video_name = os.path.basename(self.video_path.get()) if self.video_path.get() else "video"
            
            # Mock AI generation for demo
            ai_captions = [
                f"Check out this amazing {video_name}! 🔥 #viral #trending #fyp",
                f"Just created this epic content! What do you think? 💯 #content #creator #fyp",
                f"This is going viral! 🚀 #viral #trending #fyp #amazing",
                f"New video alert! 🎬 #new #video #content #fyp #trending"
            ]
            
            generated_caption = random.choice(ai_captions)
            self.caption.set(generated_caption)
            self.log(f"✅ Đã tạo caption: {generated_caption}")
            
        except Exception as e:
            self.log(f"❌ Lỗi tạo caption: {str(e)}", "ERROR")
    
    def start_single_upload(self):
        """Start single video upload"""
        if self.is_uploading:
            return
        
        # Validate inputs
        if not self.video_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
            return
        
        if not self.username.get() or not self.password.get():
            messagebox.showerror("Lỗi", "Vui lòng nhập username và password!")
            return
        
        if not os.path.exists(self.video_path.get()):
            messagebox.showerror("Lỗi", "File video không tồn tại!")
            return
        
        # Create upload task
        hashtags = [tag.strip() for tag in self.hashtags.get().split(',') if tag.strip()]
        task = UploadTask(
            video_path=self.video_path.get(),
            caption=self.caption.get(),
            hashtags=hashtags
        )
        
        # Start upload in separate thread
        upload_thread = threading.Thread(target=self.single_upload_worker, args=(task,))
        upload_thread.daemon = True
        upload_thread.start()
    
    def single_upload_worker(self, task: UploadTask):
        """Worker thread for single upload"""
        try:
            self.is_uploading = True
            self.upload_btn.config(state='disabled')
            self.progress.start()
            self.status_var.set("Đang upload video...")
            
            # Setup driver
            if not self.setup_driver():
                return
            
            # Login
            if not self.login_tiktok():
                messagebox.showerror("Lỗi", "Đăng nhập thất bại!")
                return
            
            # Upload video
            if self.upload_video_with_retry(task):
                messagebox.showinfo("Thành công", "Video đã được upload thành công!")
                self.status_var.set("Upload hoàn tất!")
            else:
                messagebox.showerror("Lỗi", "Upload video thất bại!")
                
        except Exception as e:
            self.log(f"❌ Lỗi không mong muốn: {str(e)}", "ERROR")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
        finally:
            self.is_uploading = False
            self.upload_btn.config(state='normal')
            self.progress.stop()
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def start_batch_upload(self):
        """Start batch upload"""
        if not self.folder_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục chứa video!")
            return
        
        if not os.path.exists(self.folder_path.get()):
            messagebox.showerror("Lỗi", "Thư mục không tồn tại!")
            return
        
        # Find video files
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        video_files = []
        
        for file in os.listdir(self.folder_path.get()):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(self.folder_path.get(), file))
        
        if not video_files:
            messagebox.showerror("Lỗi", "Không tìm thấy file video nào trong thư mục!")
            return
        
        # Create batch tasks
        self.upload_tasks = []
        for video_file in video_files:
            hashtags = [tag.strip() for tag in self.hashtags.get().split(',') if tag.strip()]
            caption = self.caption.get()
            
            # Generate AI caption if enabled
            if self.auto_caption.get():
                caption = f"Check out this amazing {os.path.basename(video_file)}! 🔥 #viral #trending #fyp"
            
            task = UploadTask(
                video_path=video_file,
                caption=caption,
                hashtags=hashtags
            )
            self.upload_tasks.append(task)
        
        # Start batch upload
        batch_thread = threading.Thread(target=self.batch_upload_worker)
        batch_thread.daemon = True
        batch_thread.start()
    
    def batch_upload_worker(self):
        """Worker thread for batch upload"""
        try:
            self.batch_upload_btn.config(state='disabled')
            self.batch_progress.config(maximum=len(self.upload_tasks))
            
            # Setup driver
            if not self.setup_driver():
                return
            
            # Login
            if not self.login_tiktok():
                self.batch_log("❌ Đăng nhập thất bại!", "ERROR")
                return
            
            # Upload each video
            for i, task in enumerate(self.upload_tasks):
                self.batch_log(f"📤 Uploading {i+1}/{len(self.upload_tasks)}: {os.path.basename(task.video_path)}")
                
                if self.upload_video_with_retry(task):
                    self.batch_log(f"✅ Thành công: {os.path.basename(task.video_path)}")
                else:
                    self.batch_log(f"❌ Thất bại: {os.path.basename(task.video_path)}", "ERROR")
                
                # Update progress
                self.batch_progress.config(value=i+1)
                
                # Delay between uploads
                if i < len(self.upload_tasks) - 1:
                    delay = int(self.batch_delay.get())
                    self.batch_log(f"⏳ Chờ {delay} giây trước khi upload video tiếp theo...")
                    time.sleep(delay)
            
            # Show completion message
            completed = sum(1 for task in self.upload_tasks if task.status == "completed")
            failed = len(self.upload_tasks) - completed
            
            self.batch_log(f"🎉 Hoàn thành batch upload! Thành công: {completed}, Thất bại: {failed}")
            messagebox.showinfo("Batch Upload", f"Hoàn thành! Thành công: {completed}, Thất bại: {failed}")
                
        except Exception as e:
            self.batch_log(f"❌ Lỗi batch upload: {str(e)}", "ERROR")
            messagebox.showerror("Lỗi", f"Batch upload thất bại: {str(e)}")
        finally:
            self.batch_upload_btn.config(state='normal')
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def schedule_upload(self):
        """Schedule video upload"""
        if not self.video_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
            return
        
        try:
            # Parse schedule time
            schedule_time_str = f"{self.schedule_date.get()} {self.schedule_time.get()}"
            schedule_time = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M")
            
            if schedule_time <= datetime.now():
                messagebox.showerror("Lỗi", "Thời gian lên lịch phải trong tương lai!")
                return
            
            # Create scheduled task
            hashtags = [tag.strip() for tag in self.hashtags.get().split(',') if tag.strip()]
            task = UploadTask(
                video_path=self.video_path.get(),
                caption=self.caption.get(),
                hashtags=hashtags,
                schedule_time=schedule_time
            )
            
            self.upload_tasks.append(task)
            
            # Add to treeview
            self.tasks_tree.insert('', 'end', values=(
                os.path.basename(task.video_path),
                task.caption[:30] + "..." if len(task.caption) > 30 else task.caption,
                schedule_time.strftime("%Y-%m-%d %H:%M"),
                "Scheduled"
            ))
            
            messagebox.showinfo("Thành công", f"Đã lên lịch upload vào {schedule_time.strftime('%Y-%m-%d %H:%M')}")
            
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng thời gian không hợp lệ!")
    
    def run_scheduler(self):
        """Run the scheduler in background"""
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def save_settings(self):
        """Save application settings"""
        try:
            settings = {
                'use_proxy': self.use_proxy.get(),
                'proxy_url': self.proxy_url.get(),
                'random_ua': self.random_ua.get(),
                'openai_key': self.openai_key.get()
            }
            
            with open('tiktok_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    print("🎬 TikTok Auto Upload Tool - Enhanced Version")
    print("=" * 50)
    print("Đang khởi động giao diện...")
    
    try:
        app = TikTokUploaderGUI()
        app.run()
    except Exception as e:
        print(f"❌ Lỗi khởi động: {str(e)}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()