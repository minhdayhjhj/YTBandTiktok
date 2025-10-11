# TikTok Bot - Improved Version

## 🚀 Tính năng chính

- **Chạy ngầm, chạy ẩn** - Browser hoạt động trong chế độ headless (không hiển thị cửa sổ)
- **Captcha hiện trên tool** - Tự động lưu hình captcha và cho phép nhập thủ công
- **Tốc độ cao** - Tối ưu hóa hiệu suất với multi-threading và request pooling
- **Mạnh mẽ** - Xử lý lỗi tốt hơn và retry mechanism

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Chrome/Chromium browser
- Windows/Linux/macOS

## 🛠️ Cài đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd tiktok-bot-improved
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

3. **Chạy bot:**
```bash
python tiktok_bot_improved.py
```

## 🎯 Các tính năng

### 1. Tăng Followers
- Sử dụng `tikfollowers.com` (Server 2)
- Hỗ trợ nhiều username cùng lúc
- Multi-threading để tăng tốc độ

### 2. Tăng Likes
- Sử dụng `zefoy.com` và `nreer.com`
- Kết hợp với `tikfollowers.com` (Server 2)
- Hỗ trợ nhiều video cùng lúc

### 3. Tăng Views
- Sử dụng `zefoy.com`
- Tối ưu hóa cho tốc độ cao

### 4. Tăng Shares, Favorites, Comment Likes
- Sử dụng `zefoy.com` và `nreer.com`
- Hỗ trợ nhiều video cùng lúc

### 5. Combined Features
- Chạy nhiều tính năng cùng lúc
- Tự động cycle qua danh sách video/username
- Hiển thị thống kê real-time

## 🔧 Cải tiến so với phiên bản cũ

### 1. Chạy ngầm (Headless Mode)
- Browser hoạt động hoàn toàn ẩn
- Không hiển thị cửa sổ browser
- Tiết kiệm tài nguyên hệ thống

### 2. Captcha Handling
- Tự động lưu hình captcha vào file
- Tự động mở hình captcha cho user
- Hỗ trợ cả `zefoy.com` và `nreer.com`

### 3. Performance Optimizations
- Multi-threading cho followers
- Request pooling và connection reuse
- Random delays để tránh detection
- Memory optimization

### 4. Error Handling
- Retry mechanism cho failed requests
- Better exception handling
- Graceful degradation

### 5. User Experience
- Colored console output
- Real-time statistics
- Progress indicators
- Better menu system

## 📖 Hướng dẫn sử dụng

### 1. Khởi động bot
```bash
python tiktok_bot_improved.py
```

### 2. Chọn tính năng
- **Single Mode**: Tăng cho 1 video/username
- **Multi Mode**: Tăng cho nhiều video/username
- **Combined Mode**: Chạy nhiều tính năng cùng lúc

### 3. Xử lý Captcha
- Bot sẽ tự động lưu hình captcha
- Mở hình captcha để bạn giải
- Nhập kết quả vào console

### 4. Theo dõi tiến trình
- Xem thống kê real-time
- Theo dõi số lượng đã gửi
- Kiểm tra trạng thái hoạt động

## ⚙️ Cấu hình

### Performance Settings
```python
MAX_WORKERS = 5  # Số thread tối đa
REQUEST_DELAY = (1, 3)  # Delay giữa các request (giây)
BROWSER_TIMEOUT = 30  # Timeout cho browser (giây)
RETRY_ATTEMPTS = 3  # Số lần retry khi lỗi
```

### Browser Settings
- Headless mode enabled
- Ad blocking enabled
- Memory optimization
- User agent spoofing

## 🚨 Lưu ý quan trọng

1. **Sử dụng có trách nhiệm** - Không lạm dụng bot
2. **Tuân thủ ToS** - Kiểm tra Terms of Service của các platform
3. **Rate limiting** - Bot có built-in delays để tránh spam
4. **Captcha solving** - Cần giải captcha thủ công
5. **Network stability** - Đảm bảo kết nối internet ổn định

## 🔍 Troubleshooting

### Lỗi thường gặp

1. **Chrome not found**
   - Cài đặt Chrome/Chromium
   - Cập nhật ChromeDriver

2. **Captcha không hiển thị**
   - Kiểm tra file `captcha.png` và `captcha2.png`
   - Mở file thủ công nếu cần

3. **Connection timeout**
   - Kiểm tra kết nối internet
   - Thử lại sau vài phút

4. **Element not found**
   - Website có thể đã thay đổi
   - Cập nhật selectors nếu cần

### Debug Mode
Để debug, comment out headless mode:
```python
# options.add_argument('--headless=new')
```

## 📊 Statistics

Bot sẽ hiển thị thống kê real-time:
- Followers sent
- Likes sent
- Views sent
- Shares sent
- Favorites sent
- Comment likes sent

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết

## ⚠️ Disclaimer

Tool này chỉ dành cho mục đích giáo dục và nghiên cứu. Người dùng chịu trách nhiệm về việc sử dụng tool này. Tác giả không chịu trách nhiệm về bất kỳ hậu quả nào phát sinh từ việc sử dụng tool này.

---

**Happy Botting! 🚀**