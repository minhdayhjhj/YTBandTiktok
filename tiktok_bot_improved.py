#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TikTok Bot - Improved Version
Chạy ngầm, chạy ẩn với captcha hiện trên tool
Cải thiện tốc độ và hiệu suất
"""

import os
import sys
import time
import random
import threading
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
from colorama import init, Fore, Back, Style
import base64
from io import BytesIO
from PIL import Image
import subprocess
import platform

# Initialize colorama
init(autoreset=True)

# Global variables
driver = None
nreer_driver = None
running = False
likes_count = 0
followers_count = 0
views_count = 0
shares_count = 0
favorites_count = 0
comment_likes_count = 0

# Performance settings
MAX_WORKERS = 5
REQUEST_DELAY = (1, 3)  # Random delay between requests
BROWSER_TIMEOUT = 30
RETRY_ATTEMPTS = 3

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print the main banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    TIKTOK BOT - IMPROVED VERSION                ║
║                        Chạy Ngầm - Chạy Ẩn                      ║
║                    Cải Thiện Tốc Độ & Hiệu Suất                 ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def print_slow(text, delay=0.03):
    """Print text with typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def load_animation(duration=3, message="Loading"):
    """Show loading animation"""
    chars = "|/-\\"
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.YELLOW}{message} {chars[i % len(chars)]}{Style.RESET_ALL}", end="")
        i += 1
        time.sleep(0.1)
    print(f"\r{Fore.GREEN}{message} Complete!{Style.RESET_ALL}")

def clear_status_lines(lines=1):
    """Clear specific number of lines in console"""
    for _ in range(lines):
        sys.stdout.write('\x1b[1A\x1b[2K')

def save_element_image(element, filename):
    """Save element screenshot to file"""
    try:
        # Try to get the image source
        if element.tag_name == 'img':
            src = element.get_attribute('src')
            if src and src.startswith('data:image'):
                # Handle data URL
                header, data = src.split(',', 1)
                image_data = base64.b64decode(data)
                with open(filename, 'wb') as f:
                    f.write(image_data)
                return True
            elif src and not src.startswith('http'):
                # Handle relative URLs
                if src.startswith('/'):
                    src = 'https://zefoy.com' + src
                else:
                    src = 'https://zefoy.com/' + src
                
                response = requests.get(src)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    return True
        else:
            # Take screenshot of the element
            element.screenshot(filename)
            return True
    except Exception as e:
        print(f"{Fore.RED}Error saving image: {e}{Style.RESET_ALL}")
        return False

def wait_any(driver, *conditions, timeout=10):
    """Wait for any of the given conditions"""
    wait = WebDriverWait(driver, timeout)
    for condition in conditions:
        try:
            element = wait.until(condition)
            return element
        except TimeoutException:
            continue
    return None

def safe_click(driver, element, max_attempts=3):
    """Safely click an element with retries"""
    for attempt in range(max_attempts):
        try:
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Try different click methods
            try:
                element.click()
                return True
            except:
                # Try JavaScript click
                driver.execute_script("arguments[0].click();", element)
                return True
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"{Fore.RED}Failed to click element after {max_attempts} attempts: {e}{Style.RESET_ALL}")
                return False
            time.sleep(1)
    return False

def setup_headless_chrome():
    """Setup Chrome with headless mode and anti-detection"""
    options = uc.ChromeOptions()
    
    # Headless mode
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    options.add_argument('--disable-css')
    options.add_argument('--disable-fonts')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-prompt-on-repost')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-translate')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--mute-audio')
    options.add_argument('--no-zygote')
    options.add_argument('--disable-logging')
    options.add_argument('--disable-permissions-api')
    options.add_argument('--disable-presentation-api')
    options.add_argument('--disable-print-preview')
    options.add_argument('--disable-speech-api')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-ipc-flooding-protection')
    
    # Window size for headless
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Performance optimizations
    options.add_argument('--memory-pressure-off')
    options.add_argument('--max_old_space_size=4096')
    
    return options

def openZefoy():
    """Open Zefoy and Nreer with headless mode"""
    global driver, nreer_driver
    
    print(f"{Fore.YELLOW}Initializing headless browsers...{Style.RESET_ALL}")
    load_animation(2, "Setting up browsers")
    
    try:
        # Setup Chrome options
        options = setup_headless_chrome()
        
        # Initialize drivers
        print(f"{Fore.CYAN}Starting Zefoy browser...{Style.RESET_ALL}")
        driver = uc.Chrome(options=options, version_main=None)
        
        print(f"{Fore.CYAN}Starting Nreer browser...{Style.RESET_ALL}")
        nreer_driver = uc.Chrome(options=options, version_main=None)
        
        # Enable CDP for ad blocking
        driver.execute_cdp_cmd('Network.setBlockedURLs', {
            "urls": [
                "*://*.googleadservices.com/*",
                "*://*.googlesyndication.com/*",
                "*://*.doubleclick.net/*",
                "*://*.facebook.com/tr*",
                "*://*.google-analytics.com/*"
            ]
        })
        driver.execute_cdp_cmd('Network.enable', {})
        
        nreer_driver.execute_cdp_cmd('Network.setBlockedURLs', {
            "urls": [
                "*://*.googleadservices.com/*",
                "*://*.googlesyndication.com/*",
                "*://*.doubleclick.net/*",
                "*://*.facebook.com/tr*",
                "*://*.google-analytics.com/*"
            ]
        })
        nreer_driver.execute_cdp_cmd('Network.enable', {})
        
        # Navigate to Zefoy
        print(f"{Fore.CYAN}Navigating to Zefoy...{Style.RESET_ALL}")
        driver.get("https://zefoy.com")
        time.sleep(3)
        
        # Navigate to Nreer
        print(f"{Fore.CYAN}Navigating to Nreer...{Style.RESET_ALL}")
        nreer_driver.get("https://nreer.com")
        time.sleep(3)
        
        # Handle Zefoy captcha
        print(f"{Fore.YELLOW}Handling Zefoy captcha...{Style.RESET_ALL}")
        captcha_solved = solve_captcha(driver, "zefoy")
        if not captcha_solved:
            print(f"{Fore.RED}Failed to solve Zefoy captcha{Style.RESET_ALL}")
            return False
        
        # Handle Nreer captcha
        print(f"{Fore.YELLOW}Handling Nreer captcha...{Style.RESET_ALL}")
        captcha_solved = solve_captcha(nreer_driver, "nreer")
        if not captcha_solved:
            print(f"{Fore.RED}Failed to solve Nreer captcha{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.GREEN}✓ Browsers initialized successfully in headless mode!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Captcha images saved as: captcha.png and captcha2.png{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error initializing browsers: {e}{Style.RESET_ALL}")
        return False

def solve_captcha(driver, site_name):
    """Solve captcha for the given site"""
    try:
        # Find captcha image
        captcha_selectors = [
            "img[src*='captcha']",
            "img[alt*='captcha']",
            "img[class*='captcha']",
            "img[id*='captcha']",
            ".captcha img",
            "#captcha img"
        ]
        
        captcha_img = None
        for selector in captcha_selectors:
            try:
                captcha_img = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not captcha_img:
            print(f"{Fore.YELLOW}No captcha found on {site_name}, continuing...{Style.RESET_ALL}")
            return True
        
        # Save captcha image
        filename = "captcha.png" if site_name == "zefoy" else "captcha2.png"
        if save_element_image(captcha_img, filename):
            print(f"{Fore.CYAN}Captcha image saved as {filename}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please solve the captcha in {filename} and enter the result below:{Style.RESET_ALL}")
            
            # Open image for user
            try:
                if platform.system() == "Windows":
                    os.startfile(filename)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", filename])
                else:  # Linux
                    subprocess.run(["xdg-open", filename])
            except:
                print(f"{Fore.YELLOW}Please manually open {filename} to solve the captcha{Style.RESET_ALL}")
            
            # Get user input
            captcha_text = input(f"{Fore.GREEN}Enter captcha text: {Style.RESET_ALL}").strip()
            
            if not captcha_text:
                print(f"{Fore.RED}No captcha text entered{Style.RESET_ALL}")
                return False
            
            # Find and fill captcha input
            captcha_input_selectors = [
                "input[name*='captcha']",
                "input[placeholder*='captcha']",
                "input[class*='captcha']",
                "input[id*='captcha']",
                ".captcha input[type='text']",
                "#captcha input"
            ]
            
            captcha_input = None
            for selector in captcha_input_selectors:
                try:
                    captcha_input = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if captcha_input:
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                time.sleep(1)
                
                # Find and click submit button
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Submit')",
                    "button:contains('Send')",
                    "button:contains('Verify')",
                    ".btn-primary",
                    ".btn-submit"
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        safe_click(driver, submit_btn)
                        break
                    except:
                        continue
                
                time.sleep(3)
                print(f"{Fore.GREEN}Captcha submitted for {site_name}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}Could not find captcha input field{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.RED}Could not save captcha image{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}Error solving captcha: {e}{Style.RESET_ALL}")
        return False

def solve_nreer_captcha():
    """Solve Nreer captcha specifically"""
    return solve_captcha(nreer_driver, "nreer")

def increase_likes(video_url):
    """Increase likes for a video using Zefoy and Nreer"""
    global likes_count
    
    print(f"{Fore.CYAN}Increasing likes for: {video_url}{Style.RESET_ALL}")
    
    # Zefoy likes
    try:
        driver.get("https://zefoy.com")
        time.sleep(2)
        
        # Click on likes section
        likes_btn = wait_any(driver, 
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Likes')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='likes']")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn:contains('Likes')"))
        )
        
        if likes_btn and safe_click(driver, likes_btn):
            time.sleep(2)
            
            # Enter video URL
            url_input = wait_any(driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                # Click search/submit
                search_btn = wait_any(driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Send')"))
                )
                
                if search_btn and safe_click(driver, search_btn):
                    likes_count += 1
                    print(f"{Fore.GREEN}✓ Zefoy likes sent! Total: {likes_count}{Style.RESET_ALL}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Zefoy likes: {e}{Style.RESET_ALL}")
    
    # Nreer likes
    try:
        nreer_driver.get("https://nreer.com")
        time.sleep(2)
        
        # Click Use button
        use_btn = wait_any(nreer_driver,
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Use')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Use')"))
        )
        
        if use_btn and safe_click(nreer_driver, use_btn):
            time.sleep(2)
            
            # Enter video URL
            url_input = wait_any(nreer_driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                # Click search
                search_btn = wait_any(nreer_driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(nreer_driver, search_btn):
                    time.sleep(3)
                    
                    # Click like button
                    like_btn = wait_any(nreer_driver,
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Like')")),
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Send')")),
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
                    )
                    
                    if like_btn and safe_click(nreer_driver, like_btn):
                        likes_count += 1
                        print(f"{Fore.GREEN}✓ Nreer likes sent! Total: {likes_count}{Style.RESET_ALL}")
                        time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Nreer likes: {e}{Style.RESET_ALL}")

def increase_likes_server2(video_url):
    """Increase likes using tikfollowers.com (Server 2)"""
    global likes_count
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Get CSRF token
        response = session.get('https://tikfollowers.com/')
        if response.status_code != 200:
            print(f"{Fore.RED}Failed to access tikfollowers.com{Style.RESET_ALL}")
            return
        
        # Extract CSRF token
        csrf_token = None
        if 'csrf_token' in response.text:
            import re
            csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        if not csrf_token:
            print(f"{Fore.RED}Could not find CSRF token{Style.RESET_ALL}")
            return
        
        # Search for video
        search_data = {
            'url': video_url,
            'csrf_token': csrf_token
        }
        
        search_response = session.post('https://tikfollowers.com/search', data=search_data)
        if search_response.status_code != 200:
            print(f"{Fore.RED}Failed to search video{Style.RESET_ALL}")
            return
        
        # Send likes
        like_data = {
            'url': video_url,
            'csrf_token': csrf_token,
            'type': 'likes'
        }
        
        like_response = session.post('https://tikfollowers.com/send', data=like_data)
        if like_response.status_code == 200:
            likes_count += 1
            print(f"{Fore.GREEN}✓ Server 2 likes sent! Total: {likes_count}{Style.RESET_ALL}")
            
            # Check for cooldown
            if 'cooldown' in like_response.text.lower():
                cooldown_match = re.search(r'cooldown[:\s]+(\d+)', like_response.text, re.IGNORECASE)
                if cooldown_match:
                    cooldown_time = int(cooldown_match.group(1))
                    print(f"{Fore.YELLOW}Cooldown: {cooldown_time} seconds{Style.RESET_ALL}")
                    time.sleep(cooldown_time)
        else:
            print(f"{Fore.RED}Failed to send likes via Server 2{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error with Server 2 likes: {e}{Style.RESET_ALL}")

def increase_followers(username):
    """Increase followers for a TikTok username using tikfollowers.com"""
    global followers_count
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Get CSRF token
        response = session.get('https://tikfollowers.com/')
        if response.status_code != 200:
            print(f"{Fore.RED}Failed to access tikfollowers.com{Style.RESET_ALL}")
            return
        
        # Extract CSRF token
        csrf_token = None
        if 'csrf_token' in response.text:
            import re
            csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        if not csrf_token:
            print(f"{Fore.RED}Could not find CSRF token{Style.RESET_ALL}")
            return
        
        # Search for username
        search_data = {
            'username': username,
            'csrf_token': csrf_token
        }
        
        search_response = session.post('https://tikfollowers.com/search', data=search_data)
        if search_response.status_code != 200:
            print(f"{Fore.RED}Failed to search username{Style.RESET_ALL}")
            return
        
        # Send followers
        follow_data = {
            'username': username,
            'csrf_token': csrf_token,
            'type': 'followers'
        }
        
        follow_response = session.post('https://tikfollowers.com/send', data=follow_data)
        if follow_response.status_code == 200:
            followers_count += 1
            print(f"{Fore.GREEN}✓ Followers sent for @{username}! Total: {followers_count}{Style.RESET_ALL}")
            
            # Check for cooldown
            if 'cooldown' in follow_response.text.lower():
                cooldown_match = re.search(r'cooldown[:\s]+(\d+)', follow_response.text, re.IGNORECASE)
                if cooldown_match:
                    cooldown_time = int(cooldown_match.group(1))
                    print(f"{Fore.YELLOW}Cooldown: {cooldown_time} seconds{Style.RESET_ALL}")
                    time.sleep(cooldown_time)
        else:
            print(f"{Fore.RED}Failed to send followers for @{username}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error increasing followers for @{username}: {e}{Style.RESET_ALL}")

def increase_views(video_url):
    """Increase views for a video using Zefoy"""
    global views_count
    
    try:
        driver.get("https://zefoy.com")
        time.sleep(2)
        
        # Click on views section
        views_btn = wait_any(driver,
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Views')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='views']")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn:contains('Views')"))
        )
        
        if views_btn and safe_click(driver, views_btn):
            time.sleep(2)
            
            # Enter video URL
            url_input = wait_any(driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                # Click search/submit
                search_btn = wait_any(driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(driver, search_btn):
                    views_count += 1
                    print(f"{Fore.GREEN}✓ Views sent! Total: {views_count}{Style.RESET_ALL}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error increasing views: {e}{Style.RESET_ALL}")

def increase_shares(video_url):
    """Increase shares for a video using Zefoy and Nreer"""
    global shares_count
    
    # Zefoy shares
    try:
        driver.get("https://zefoy.com")
        time.sleep(2)
        
        shares_btn = wait_any(driver,
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Shares')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='shares']"))
        )
        
        if shares_btn and safe_click(driver, shares_btn):
            time.sleep(2)
            
            url_input = wait_any(driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                search_btn = wait_any(driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(driver, search_btn):
                    shares_count += 1
                    print(f"{Fore.GREEN}✓ Zefoy shares sent! Total: {shares_count}{Style.RESET_ALL}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Zefoy shares: {e}{Style.RESET_ALL}")
    
    # Nreer shares
    try:
        nreer_driver.get("https://nreer.com")
        time.sleep(2)
        
        use_btn = wait_any(nreer_driver,
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Use')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Use')"))
        )
        
        if use_btn and safe_click(nreer_driver, use_btn):
            time.sleep(2)
            
            url_input = wait_any(nreer_driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                search_btn = wait_any(nreer_driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(nreer_driver, search_btn):
                    time.sleep(3)
                    
                    share_btn = wait_any(nreer_driver,
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Share')")),
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Send')"))
                    )
                    
                    if share_btn and safe_click(nreer_driver, share_btn):
                        shares_count += 1
                        print(f"{Fore.GREEN}✓ Nreer shares sent! Total: {shares_count}{Style.RESET_ALL}")
                        time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Nreer shares: {e}{Style.RESET_ALL}")

def increase_favorites(video_url):
    """Increase favorites for a video using Zefoy and Nreer"""
    global favorites_count
    
    # Zefoy favorites
    try:
        driver.get("https://zefoy.com")
        time.sleep(2)
        
        favorites_btn = wait_any(driver,
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Favorites')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='favorites']"))
        )
        
        if favorites_btn and safe_click(driver, favorites_btn):
            time.sleep(2)
            
            url_input = wait_any(driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                search_btn = wait_any(driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(driver, search_btn):
                    favorites_count += 1
                    print(f"{Fore.GREEN}✓ Zefoy favorites sent! Total: {favorites_count}{Style.RESET_ALL}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Zefoy favorites: {e}{Style.RESET_ALL}")
    
    # Nreer favorites
    try:
        nreer_driver.get("https://nreer.com")
        time.sleep(2)
        
        use_btn = wait_any(nreer_driver,
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Use')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Use')"))
        )
        
        if use_btn and safe_click(nreer_driver, use_btn):
            time.sleep(2)
            
            url_input = wait_any(nreer_driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                search_btn = wait_any(nreer_driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(nreer_driver, search_btn):
                    time.sleep(3)
                    
                    favorite_btn = wait_any(nreer_driver,
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Favorite')")),
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Send')"))
                    )
                    
                    if favorite_btn and safe_click(nreer_driver, favorite_btn):
                        favorites_count += 1
                        print(f"{Fore.GREEN}✓ Nreer favorites sent! Total: {favorites_count}{Style.RESET_ALL}")
                        time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error with Nreer favorites: {e}{Style.RESET_ALL}")

def increase_comment_likes(video_url):
    """Increase comment likes for a video using Zefoy"""
    global comment_likes_count
    
    try:
        driver.get("https://zefoy.com")
        time.sleep(2)
        
        comment_likes_btn = wait_any(driver,
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Comment Likes')]")),
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='comment']"))
        )
        
        if comment_likes_btn and safe_click(driver, comment_likes_btn):
            time.sleep(2)
            
            url_input = wait_any(driver,
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='URL']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='url']"))
            )
            
            if url_input:
                url_input.clear()
                url_input.send_keys(video_url)
                time.sleep(1)
                
                search_btn = wait_any(driver,
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Search')"))
                )
                
                if search_btn and safe_click(driver, search_btn):
                    comment_likes_count += 1
                    print(f"{Fore.GREEN}✓ Comment likes sent! Total: {comment_likes_count}{Style.RESET_ALL}")
                    time.sleep(random.uniform(*REQUEST_DELAY))
        
    except Exception as e:
        print(f"{Fore.RED}Error increasing comment likes: {e}{Style.RESET_ALL}")

def run_multi_shares():
    """Run multiple shares for different videos"""
    global running
    
    video_urls = get_url_list()
    if not video_urls:
        return
    
    running = True
    current_index = 0
    count_per_video = 10
    
    print(f"{Fore.CYAN}Starting multi-shares mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Will cycle through {len(video_urls)} videos, {count_per_video} shares each{Style.RESET_ALL}")
    
    try:
        while running:
            video_url = video_urls[current_index]
            print(f"{Fore.CYAN}Processing video {current_index + 1}/{len(video_urls)}: {video_url}{Style.RESET_ALL}")
            
            for i in range(count_per_video):
                if not running:
                    break
                
                increase_shares(video_url)
                time.sleep(random.uniform(2, 5))
            
            current_index = (current_index + 1) % len(video_urls)
            print(f"{Fore.GREEN}Completed cycle for video {current_index}{Style.RESET_ALL}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Multi-shares stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def run_multi_favorites():
    """Run multiple favorites for different videos"""
    global running
    
    video_urls = get_url_list()
    if not video_urls:
        return
    
    running = True
    current_index = 0
    count_per_video = 10
    
    print(f"{Fore.CYAN}Starting multi-favorites mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Will cycle through {len(video_urls)} videos, {count_per_video} favorites each{Style.RESET_ALL}")
    
    try:
        while running:
            video_url = video_urls[current_index]
            print(f"{Fore.CYAN}Processing video {current_index + 1}/{len(video_urls)}: {video_url}{Style.RESET_ALL}")
            
            for i in range(count_per_video):
                if not running:
                    break
                
                increase_favorites(video_url)
                time.sleep(random.uniform(2, 5))
            
            current_index = (current_index + 1) % len(video_urls)
            print(f"{Fore.GREEN}Completed cycle for video {current_index}{Style.RESET_ALL}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Multi-favorites stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def run_multi_comment_likes():
    """Run multiple comment likes for different videos"""
    global running
    
    video_urls = get_url_list()
    if not video_urls:
        return
    
    running = True
    current_index = 0
    count_per_video = 10
    
    print(f"{Fore.CYAN}Starting multi-comment likes mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Will cycle through {len(video_urls)} videos, {count_per_video} comment likes each{Style.RESET_ALL}")
    
    try:
        while running:
            video_url = video_urls[current_index]
            print(f"{Fore.CYAN}Processing video {current_index + 1}/{len(video_urls)}: {video_url}{Style.RESET_ALL}")
            
            for i in range(count_per_video):
                if not running:
                    break
                
                increase_comment_likes(video_url)
                time.sleep(random.uniform(2, 5))
            
            current_index = (current_index + 1) % len(video_urls)
            print(f"{Fore.GREEN}Completed cycle for video {current_index}{Style.RESET_ALL}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Multi-comment likes stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def run_multi_videos(action_type):
    """Run multiple actions for different videos"""
    global running
    
    video_urls = get_url_list()
    if not video_urls:
        return
    
    running = True
    current_index = 0
    count_per_video = 10
    
    print(f"{Fore.CYAN}Starting multi-{action_type} mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Will cycle through {len(video_urls)} videos, {count_per_video} {action_type} each{Style.RESET_ALL}")
    
    try:
        while running:
            video_url = video_urls[current_index]
            print(f"{Fore.CYAN}Processing video {current_index + 1}/{len(video_urls)}: {video_url}{Style.RESET_ALL}")
            
            for i in range(count_per_video):
                if not running:
                    break
                
                if action_type == "likes":
                    increase_likes(video_url)
                    increase_likes_server2(video_url)
                elif action_type == "views":
                    increase_views(video_url)
                
                time.sleep(random.uniform(2, 5))
            
            current_index = (current_index + 1) % len(video_urls)
            print(f"{Fore.GREEN}Completed cycle for video {current_index}{Style.RESET_ALL}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Multi-{action_type} stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def get_url_list():
    """Get list of video URLs from user"""
    print(f"{Fore.CYAN}Enter video URLs (one per line, empty line to finish):{Style.RESET_ALL}")
    urls = []
    while True:
        url = input(f"{Fore.GREEN}URL {len(urls) + 1}: {Style.RESET_ALL}").strip()
        if not url:
            break
        if url.startswith('http'):
            urls.append(url)
        else:
            print(f"{Fore.RED}Invalid URL format{Style.RESET_ALL}")
    
    return urls

def get_usernames():
    """Get list of usernames from user"""
    print(f"{Fore.CYAN}Enter TikTok usernames (one per line, empty line to finish):{Style.RESET_ALL}")
    usernames = []
    while True:
        username = input(f"{Fore.GREEN}Username {len(usernames) + 1}: {Style.RESET_ALL}").strip()
        if not username:
            break
        if username.startswith('@'):
            username = username[1:]
        usernames.append(username)
    
    return usernames

def run_multi_profiles():
    """Run multiple profiles for followers"""
    global running, followers_count
    
    usernames = get_usernames()
    if not usernames:
        return
    
    running = True
    print(f"{Fore.CYAN}Starting multi-profile followers mode...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Will process {len(usernames)} profiles concurrently{Style.RESET_ALL}")
    
    def process_username(username):
        """Process a single username"""
        while running:
            try:
                increase_followers(username)
                time.sleep(random.uniform(3, 8))
            except Exception as e:
                print(f"{Fore.RED}Error processing @{username}: {e}{Style.RESET_ALL}")
                time.sleep(5)
    
    try:
        with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(usernames))) as executor:
            futures = [executor.submit(process_username, username) for username in usernames]
            
            while running:
                time.sleep(1)
                print(f"{Fore.CYAN}Followers sent: {followers_count}{Style.RESET_ALL}", end="\r")
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Multi-profile followers stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def run_combined_features():
    """Run combined features in a loop"""
    global running
    
    print(f"{Fore.CYAN}Combined Features Mode{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Select features to run (comma-separated numbers):{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Followers{Style.RESET_ALL}")
    print(f"{Fore.GREEN}2. Likes{Style.RESET_ALL}")
    print(f"{Fore.GREEN}3. Views{Style.RESET_ALL}")
    print(f"{Fore.GREEN}4. Shares{Style.RESET_ALL}")
    print(f"{Fore.GREEN}5. Favorites{Style.RESET_ALL}")
    print(f"{Fore.GREEN}6. Comment Likes{Style.RESET_ALL}")
    
    try:
        choices = input(f"{Fore.CYAN}Enter choices (e.g., 1,2,3): {Style.RESET_ALL}").strip().split(',')
        choices = [int(c.strip()) for c in choices if c.strip().isdigit()]
        
        if not choices:
            print(f"{Fore.RED}No valid choices selected{Style.RESET_ALL}")
            return
        
        # Get URLs/usernames based on selected features
        video_urls = []
        usernames = []
        
        if any(c in choices for c in [2, 3, 4, 5, 6]):  # Features that need video URLs
            video_urls = get_url_list()
            if not video_urls:
                print(f"{Fore.RED}No video URLs provided{Style.RESET_ALL}")
                return
        
        if 1 in choices:  # Followers feature
            usernames = get_usernames()
            if not usernames:
                print(f"{Fore.RED}No usernames provided{Style.RESET_ALL}")
                return
        
        # Initialize browsers if needed
        if any(c in choices for c in [2, 3, 4, 5, 6]):
            if not openZefoy():
                print(f"{Fore.RED}Failed to initialize browsers{Style.RESET_ALL}")
                return
        
        running = True
        cycle_count = 0
        
        print(f"{Fore.CYAN}Starting combined features...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")
        
        while running:
            cycle_count += 1
            print(f"\n{Fore.CYAN}=== Cycle {cycle_count} ==={Style.RESET_ALL}")
            
            # Followers
            if 1 in choices and usernames:
                for username in usernames:
                    if not running:
                        break
                    increase_followers(username)
                    time.sleep(random.uniform(2, 4))
            
            # Video features
            if video_urls and any(c in choices for c in [2, 3, 4, 5, 6]):
                for video_url in video_urls:
                    if not running:
                        break
                    
                    if 2 in choices:  # Likes
                        increase_likes(video_url)
                        increase_likes_server2(video_url)
                        time.sleep(random.uniform(1, 3))
                    
                    if 3 in choices:  # Views
                        increase_views(video_url)
                        time.sleep(random.uniform(1, 3))
                    
                    if 4 in choices:  # Shares
                        increase_shares(video_url)
                        time.sleep(random.uniform(1, 3))
                    
                    if 5 in choices:  # Favorites
                        increase_favorites(video_url)
                        time.sleep(random.uniform(1, 3))
                    
                    if 6 in choices:  # Comment Likes
                        increase_comment_likes(video_url)
                        time.sleep(random.uniform(1, 3))
            
            # Show statistics
            print(f"\n{Fore.GREEN}=== Statistics ==={Style.RESET_ALL}")
            print(f"{Fore.CYAN}Followers: {followers_count}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Likes: {likes_count}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Views: {views_count}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Shares: {shares_count}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Favorites: {favorites_count}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Comment Likes: {comment_likes_count}{Style.RESET_ALL}")
            
            time.sleep(10)  # Pause between cycles
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Combined features stopped by user{Style.RESET_ALL}")
    finally:
        running = False

def main():
    """Main function"""
    global running
    
    while True:
        clear_screen()
        print_banner()
        
        print(f"{Fore.GREEN}Current Statistics:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Followers: {followers_count} | Likes: {likes_count} | Views: {views_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Shares: {shares_count} | Favorites: {favorites_count} | Comment Likes: {comment_likes_count}{Style.RESET_ALL}")
        print()
        
        print(f"{Fore.YELLOW}Select an option:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Increase Followers (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}2. Increase Likes (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}3. Increase Views (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}4. Increase Shares (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}5. Increase Favorites (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}6. Increase Comment Likes (Single){Style.RESET_ALL}")
        print(f"{Fore.GREEN}7. Multi-Profile Followers{Style.RESET_ALL}")
        print(f"{Fore.GREEN}8. Multi-Video Likes{Style.RESET_ALL}")
        print(f"{Fore.GREEN}9. Multi-Video Views{Style.RESET_ALL}")
        print(f"{Fore.GREEN}10. Multi-Video Shares{Style.RESET_ALL}")
        print(f"{Fore.GREEN}11. Multi-Video Favorites{Style.RESET_ALL}")
        print(f"{Fore.GREEN}12. Multi-Video Comment Likes{Style.RESET_ALL}")
        print(f"{Fore.GREEN}13. Combined Features{Style.RESET_ALL}")
        print(f"{Fore.GREEN}14. Initialize Browsers{Style.RESET_ALL}")
        print(f"{Fore.RED}0. Exit{Style.RESET_ALL}")
        
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}").strip()
            
            if choice == "0":
                print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break
            elif choice == "1":
                username = input(f"{Fore.GREEN}Enter TikTok username: {Style.RESET_ALL}").strip()
                if username.startswith('@'):
                    username = username[1:]
                if username:
                    increase_followers(username)
            elif choice == "2":
                video_url = input(f"{Fore.GREEN}Enter video URL: {Style.RESET_ALL}").strip()
                if video_url:
                    if not driver or not nreer_driver:
                        print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                        if openZefoy():
                            increase_likes(video_url)
                            increase_likes_server2(video_url)
                    else:
                        increase_likes(video_url)
                        increase_likes_server2(video_url)
            elif choice == "3":
                video_url = input(f"{Fore.GREEN}Enter video URL: {Style.RESET_ALL}").strip()
                if video_url:
                    if not driver:
                        print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                        if openZefoy():
                            increase_views(video_url)
                    else:
                        increase_views(video_url)
            elif choice == "4":
                video_url = input(f"{Fore.GREEN}Enter video URL: {Style.RESET_ALL}").strip()
                if video_url:
                    if not driver or not nreer_driver:
                        print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                        if openZefoy():
                            increase_shares(video_url)
                    else:
                        increase_shares(video_url)
            elif choice == "5":
                video_url = input(f"{Fore.GREEN}Enter video URL: {Style.RESET_ALL}").strip()
                if video_url:
                    if not driver or not nreer_driver:
                        print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                        if openZefoy():
                            increase_favorites(video_url)
                    else:
                        increase_favorites(video_url)
            elif choice == "6":
                video_url = input(f"{Fore.GREEN}Enter video URL: {Style.RESET_ALL}").strip()
                if video_url:
                    if not driver:
                        print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                        if openZefoy():
                            increase_comment_likes(video_url)
                    else:
                        increase_comment_likes(video_url)
            elif choice == "7":
                run_multi_profiles()
            elif choice == "8":
                if not driver or not nreer_driver:
                    print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                    if openZefoy():
                        run_multi_videos("likes")
                else:
                    run_multi_videos("likes")
            elif choice == "9":
                if not driver:
                    print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                    if openZefoy():
                        run_multi_videos("views")
                else:
                    run_multi_videos("views")
            elif choice == "10":
                if not driver or not nreer_driver:
                    print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                    if openZefoy():
                        run_multi_shares()
                else:
                    run_multi_shares()
            elif choice == "11":
                if not driver or not nreer_driver:
                    print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                    if openZefoy():
                        run_multi_favorites()
                else:
                    run_multi_favorites()
            elif choice == "12":
                if not driver:
                    print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                    if openZefoy():
                        run_multi_comment_likes()
                else:
                    run_multi_comment_likes()
            elif choice == "13":
                run_combined_features()
            elif choice == "14":
                print(f"{Fore.YELLOW}Initializing browsers...{Style.RESET_ALL}")
                if openZefoy():
                    print(f"{Fore.GREEN}Browsers initialized successfully!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to initialize browsers{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
            
            if choice != "0":
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    # Cleanup
    try:
        if driver:
            driver.quit()
        if nreer_driver:
            nreer_driver.quit()
    except:
        pass

if __name__ == "__main__":
    main()