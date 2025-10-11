import os
import time
import json
import random
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import click
from dotenv import load_dotenv

load_dotenv()

class TikTokUploader:
    def __init__(self, headless: bool = False):
        """
        Khởi tạo TikTok Uploader
        
        Args:
            headless: Chạy browser ở chế độ ẩn (không hiển thị cửa sổ)
        """
        self.driver = None
        self.headless = headless
        self.wait_timeout = 30
        
    def setup_driver(self):
        """Thiết lập Chrome WebDriver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Các tùy chọn để tránh bị phát hiện là bot
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Tự động tải ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Ẩn thuộc tính webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self, username: str, password: str) -> bool:
        """
        Đăng nhập vào TikTok
        
        Args:
            username: Tên đăng nhập TikTok
            password: Mật khẩu TikTok
            
        Returns:
            bool: True nếu đăng nhập thành công
        """
        try:
            if not self.driver:
                self.setup_driver()
                
            # Truy cập trang đăng nhập TikTok
            self.driver.get("https://www.tiktok.com/login")
            time.sleep(3)
            
            # Tìm và click vào nút đăng nhập bằng email/username
            try:
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone / email / username')]"))
                )
                login_button.click()
                time.sleep(2)
            except TimeoutException:
                pass  # Có thể đã ở trang đăng nhập rồi
            
            # Nhập username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username']"))
            )
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)
            
            # Nhập password
            password_input = self.driver.find_element(By.XPATH, "//input[@name='password']")
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            # Click đăng nhập
            login_submit = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_submit.click()
            
            # Chờ đăng nhập thành công (kiểm tra URL thay đổi)
            WebDriverWait(self.driver, 30).until(
                lambda driver: "tiktok.com" in driver.current_url and "login" not in driver.current_url
            )
            
            print("✅ Đăng nhập thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi đăng nhập: {str(e)}")
            return False
    
    def upload_video(self, video_path: str, caption: str = "", hashtags: List[str] = None) -> bool:
        """
        Upload video lên TikTok
        
        Args:
            video_path: Đường dẫn đến file video
            caption: Mô tả video
            hashtags: Danh sách hashtags
            
        Returns:
            bool: True nếu upload thành công
        """
        try:
            if not os.path.exists(video_path):
                print(f"❌ File video không tồn tại: {video_path}")
                return False
            
            # Truy cập trang upload
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(5)
            
            # Tìm input file upload
            file_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            # Upload file
            file_input.send_keys(os.path.abspath(video_path))
            print("📤 Đang upload video...")
            
            # Chờ video được xử lý
            time.sleep(10)
            
            # Nhập caption nếu có
            if caption:
                caption_textarea = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-text='true']"))
                )
                caption_textarea.click()
                caption_textarea.send_keys(caption)
                time.sleep(2)
            
            # Thêm hashtags nếu có
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                caption_textarea = self.driver.find_element(By.XPATH, "//div[@data-text='true']")
                caption_textarea.send_keys(f" {hashtag_text}")
                time.sleep(2)
            
            # Click nút Post
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
            )
            post_button.click()
            
            print("✅ Video đã được đăng thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi upload video: {str(e)}")
            return False
    
    def close(self):
        """Đóng browser"""
        if self.driver:
            self.driver.quit()

@click.command()
@click.option('--username', '-u', required=True, help='Tên đăng nhập TikTok')
@click.option('--password', '-p', required=True, help='Mật khẩu TikTok')
@click.option('--video', '-v', required=True, help='Đường dẫn đến file video')
@click.option('--caption', '-c', default='', help='Mô tả video')
@click.option('--hashtags', '-h', default='', help='Hashtags (cách nhau bởi dấu phẩy)')
@click.option('--headless', is_flag=True, help='Chạy ở chế độ ẩn')
def main(username, password, video, caption, hashtags, headless):
    """Công cụ tự động đăng video lên TikTok"""
    
    # Xử lý hashtags
    hashtag_list = [tag.strip() for tag in hashtags.split(',')] if hashtags else []
    
    uploader = TikTokUploader(headless=headless)
    
    try:
        # Đăng nhập
        if not uploader.login(username, password):
            return
        
        # Upload video
        uploader.upload_video(video, caption, hashtag_list)
        
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng chương trình")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
    finally:
        uploader.close()

if __name__ == "__main__":
    main()