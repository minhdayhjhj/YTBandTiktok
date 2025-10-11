#!/usr/bin/env python3
"""
TikTok Auto Upload Tool - Single File
Công cụ tự động đăng video lên TikTok - Tất cả trong 1 file
"""

import os
import time
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading

class TikTokUploaderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok Auto Upload Tool")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variables
        self.driver = None
        self.video_path = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.caption = tk.StringVar()
        self.hashtags = tk.StringVar()
        self.is_uploading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Tạo giao diện người dùng"""
        # Title
        title_label = tk.Label(self.root, text="🎬 TikTok Auto Upload Tool", 
                              font=("Arial", 16, "bold"), fg="#ff0050")
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video selection
        video_frame = ttk.LabelFrame(main_frame, text="📁 Chọn Video", padding="10")
        video_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(video_frame, text="File Video:").pack(anchor=tk.W)
        video_path_frame = ttk.Frame(video_frame)
        video_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(video_path_frame, textvariable=self.video_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(video_path_frame, text="Browse", command=self.browse_video).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Login info
        login_frame = ttk.LabelFrame(main_frame, text="🔐 Thông tin đăng nhập", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Username:").pack(anchor=tk.W)
        ttk.Entry(login_frame, textvariable=self.username, width=50).pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(login_frame, text="Password:").pack(anchor=tk.W)
        ttk.Entry(login_frame, textvariable=self.password, show="*", width=50).pack(fill=tk.X, pady=(2, 0))
        
        # Video details
        details_frame = ttk.LabelFrame(main_frame, text="📝 Chi tiết video", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(details_frame, text="Caption:").pack(anchor=tk.W)
        ttk.Entry(details_frame, textvariable=self.caption, width=50).pack(fill=tk.X, pady=(2, 5))
        
        ttk.Label(details_frame, text="Hashtags (cách nhau bởi dấu phẩy):").pack(anchor=tk.W)
        ttk.Entry(details_frame, textvariable=self.hashtags, width=50).pack(fill=tk.X, pady=(2, 0))
        
        # Upload button
        self.upload_btn = ttk.Button(main_frame, text="🚀 BẮT ĐẦU UPLOAD", 
                                    command=self.start_upload, style="Accent.TButton")
        self.upload_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng upload video...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_video(self):
        """Chọn file video"""
        filetypes = [
            ("Video files", "*.mp4 *.mov *.avi *.mkv"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Chọn video để upload",
            filetypes=filetypes
        )
        if filename:
            self.video_path.set(filename)
            self.log(f"✅ Đã chọn video: {os.path.basename(filename)}")
    
    def log(self, message):
        """Thêm log vào text area"""
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def setup_driver(self):
        """Thiết lập Chrome WebDriver"""
        try:
            self.log("🔧 Đang thiết lập browser...")
            
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.log("✅ Browser đã sẵn sàng!")
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi thiết lập browser: {str(e)}")
            return False
    
    def login_tiktok(self):
        """Đăng nhập TikTok"""
        try:
            self.log("🔐 Đang đăng nhập TikTok...")
            
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
            
            # Nhập username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
            )
            username_input.clear()
            username_input.send_keys(self.username.get())
            time.sleep(1)
            
            # Nhập password
            password_input = self.driver.find_element(By.XPATH, "//input[@name='password']")
            password_input.clear()
            password_input.send_keys(self.password.get())
            time.sleep(1)
            
            # Click đăng nhập
            login_submit = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_submit.click()
            
            # Chờ đăng nhập thành công
            WebDriverWait(self.driver, 30).until(
                lambda driver: "tiktok.com" in driver.current_url and "login" not in driver.current_url
            )
            
            self.log("✅ Đăng nhập thành công!")
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi đăng nhập: {str(e)}")
            return False
    
    def upload_video(self):
        """Upload video lên TikTok"""
        try:
            self.log("📤 Đang upload video...")
            
            # Truy cập trang upload
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(5)
            
            # Upload file
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(self.video_path.get()))
            
            self.log("⏳ Video đang được xử lý...")
            time.sleep(10)
            
            # Nhập caption
            if self.caption.get():
                caption_textarea = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-text='true']"))
                )
                caption_textarea.click()
                caption_textarea.send_keys(self.caption.get())
                time.sleep(2)
            
            # Thêm hashtags
            if self.hashtags.get():
                hashtag_text = " ".join([f"#{tag.strip()}" for tag in self.hashtags.get().split(',')])
                caption_textarea = self.driver.find_element(By.XPATH, "//div[@data-text='true']")
                caption_textarea.send_keys(f" {hashtag_text}")
                time.sleep(2)
            
            # Click Post
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
            )
            post_button.click()
            
            self.log("✅ Video đã được đăng thành công!")
            return True
            
        except Exception as e:
            self.log(f"❌ Lỗi upload video: {str(e)}")
            return False
    
    def upload_worker(self):
        """Worker thread cho upload"""
        try:
            self.is_uploading = True
            self.upload_btn.config(state='disabled')
            self.progress.start()
            
            # Kiểm tra input
            if not self.video_path.get():
                messagebox.showerror("Lỗi", "Vui lòng chọn file video!")
                return
            
            if not self.username.get() or not self.password.get():
                messagebox.showerror("Lỗi", "Vui lòng nhập username và password!")
                return
            
            if not os.path.exists(self.video_path.get()):
                messagebox.showerror("Lỗi", "File video không tồn tại!")
                return
            
            # Setup driver
            if not self.setup_driver():
                return
            
            # Login
            if not self.login_tiktok():
                return
            
            # Upload
            if self.upload_video():
                messagebox.showinfo("Thành công", "Video đã được upload thành công!")
                self.status_var.set("Upload hoàn tất!")
            else:
                messagebox.showerror("Lỗi", "Upload video thất bại!")
                
        except Exception as e:
            self.log(f"❌ Lỗi không mong muốn: {str(e)}")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
        finally:
            self.is_uploading = False
            self.upload_btn.config(state='normal')
            self.progress.stop()
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def start_upload(self):
        """Bắt đầu upload trong thread riêng"""
        if self.is_uploading:
            return
            
        # Chạy upload trong thread riêng để không block UI
        upload_thread = threading.Thread(target=self.upload_worker)
        upload_thread.daemon = True
        upload_thread.start()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

def main():
    """Hàm main"""
    print("🎬 TikTok Auto Upload Tool")
    print("=" * 40)
    print("Đang khởi động giao diện...")
    
    try:
        app = TikTokUploaderGUI()
        app.run()
    except Exception as e:
        print(f"❌ Lỗi khởi động: {str(e)}")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()