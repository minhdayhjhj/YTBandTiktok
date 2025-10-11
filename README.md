# TikTok Auto Uploader Tool

Công cụ tự động đăng video lên TikTok sử dụng Selenium WebDriver.

## ✨ Tính năng

- 🔐 Đăng nhập tự động vào TikTok
- 📤 Upload video với caption và hashtags
- 🎯 Hỗ trợ CLI interface dễ sử dụng
- ⚙️ Cấu hình linh hoạt qua file .env
- 🤖 Chạy ở chế độ headless (không hiển thị browser)

## 📋 Yêu cầu hệ thống

- Python 3.7+
- Google Chrome browser
- Kết nối internet ổn định

## 🚀 Cài đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd tiktok-uploader
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

3. **Cấu hình credentials:**
```bash
cp .env.example .env
# Chỉnh sửa file .env với thông tin đăng nhập TikTok của bạn
```

## 📖 Cách sử dụng

### 1. Sử dụng CLI (Command Line Interface)

**Cú pháp cơ bản:**
```bash
python tiktok_uploader.py -u <username> -p <password> -v <video_path>
```

**Ví dụ:**
```bash
# Upload video cơ bản
python tiktok_uploader.py -u "myusername" -p "mypassword" -v "/path/to/video.mp4"

# Upload với caption và hashtags
python tiktok_uploader.py -u "myusername" -p "mypassword" -v "/path/to/video.mp4" -c "Check out this amazing video!" -h "viral,fyp,trending"

# Chạy ở chế độ headless (không hiển thị browser)
python tiktok_uploader.py -u "myusername" -p "mypassword" -v "/path/to/video.mp4" --headless
```

### 2. Sử dụng như Python module

```python
from tiktok_uploader import TikTokUploader

# Khởi tạo uploader
uploader = TikTokUploader(headless=False)

try:
    # Đăng nhập
    if uploader.login("your_username", "your_password"):
        # Upload video
        uploader.upload_video(
            video_path="/path/to/video.mp4",
            caption="Amazing video! #viral #fyp",
            hashtags=["viral", "fyp", "trending"]
        )
finally:
    uploader.close()
```

## ⚙️ Cấu hình

Tạo file `.env` từ `.env.example` và cấu hình:

```env
# Thông tin đăng nhập TikTok
TIKTOK_USERNAME=your_username_here
TIKTOK_PASSWORD=your_password_here

# Cài đặt mặc định
DEFAULT_CAPTION=Check out this amazing video! #viral #fyp
DEFAULT_HASHTAGS=viral,fyp,trending,funny

# Cài đặt browser
HEADLESS_MODE=False
WAIT_TIMEOUT=30

# Cài đặt upload
MAX_VIDEO_SIZE_MB=500
```

## 📁 Cấu trúc dự án

```
tiktok-uploader/
├── tiktok_uploader.py    # Main uploader class
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (create this)
└── README.md            # This file
```

## 🔧 Tùy chọn CLI

| Tùy chọn | Mô tả | Bắt buộc |
|----------|-------|----------|
| `-u, --username` | Tên đăng nhập TikTok | ✅ |
| `-p, --password` | Mật khẩu TikTok | ✅ |
| `-v, --video` | Đường dẫn đến file video | ✅ |
| `-c, --caption` | Mô tả video | ❌ |
| `-h, --hashtags` | Hashtags (cách nhau bởi dấu phẩy) | ❌ |
| `--headless` | Chạy ở chế độ ẩn | ❌ |

## 📝 Lưu ý quan trọng

1. **Bảo mật**: Không chia sẻ file `.env` chứa thông tin đăng nhập
2. **Video format**: Hỗ trợ MP4, MOV, AVI, MKV
3. **Kích thước**: Video không nên vượt quá 500MB
4. **Rate limiting**: Tránh upload quá nhiều video trong thời gian ngắn
5. **2FA**: Nếu tài khoản có 2FA, cần tắt tạm thời

## 🐛 Xử lý lỗi thường gặp

### Lỗi đăng nhập
- Kiểm tra username/password
- Tắt 2FA tạm thời
- Thử đăng nhập thủ công trước

### Lỗi upload
- Kiểm tra định dạng video
- Kiểm tra kích thước file
- Đảm bảo kết nối internet ổn định

### Lỗi WebDriver
- Cập nhật Chrome browser
- Chạy `pip install --upgrade selenium webdriver-manager`

## ⚠️ Disclaimer

Tool này chỉ dành cho mục đích giáo dục và sử dụng cá nhân. Hãy tuân thủ Terms of Service của TikTok khi sử dụng.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📄 License

MIT License