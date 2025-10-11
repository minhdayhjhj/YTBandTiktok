# 🎬 TikTok Auto Upload Tool - Enhanced

Công cụ tự động đăng video lên TikTok với nhiều tính năng nâng cao và tối ưu hóa.

## ✨ Tính năng chính

### 🚀 Cải thiện tính ổn định
- **Dynamic Wait**: Thay thế `time.sleep()` bằng `WebDriverWait` để chờ động
- **Cookie Management**: Lưu và tải lại session đăng nhập
- **Retry Logic**: Tự động thử lại khi upload thất bại (1-3 lần)
- **Error Handling**: Xử lý lỗi toàn diện với logging chi tiết

### 📂 Upload hàng loạt
- Chọn thư mục chứa nhiều video
- Upload tự động từng video một
- Cài đặt delay giữa các upload
- Tự động tạo caption cho mỗi video

### 🕓 Lập lịch đăng
- Chọn thời gian cụ thể để đăng video
- Quản lý danh sách video đã lên lịch
- Chạy tự động trong background

### 🧠 AI-Powered Features
- Tự động tạo caption bằng AI
- Hỗ trợ OpenAI API
- Caption thông minh dựa trên tên video

### 🛡️ Bảo mật & Ẩn danh
- Random User Agent
- Proxy support
- Anti-detection measures
- Cookie persistence

### 📊 Logging & Monitoring
- Log chi tiết ra file `.txt`
- Progress tracking
- Status monitoring
- Error reporting

## 🚀 Cài đặt

### 1. Cài đặt Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng
```bash
python tiktok_auto_uploader.py
```

### 3. Tạo file .exe (tùy chọn)
```bash
python build_executable.py
```

## 📖 Hướng dẫn sử dụng

### Single Upload
1. Chọn tab "📤 Single Upload"
2. Browse và chọn file video
3. Nhập thông tin đăng nhập TikTok
4. Nhập caption và hashtags
5. Click "🚀 BẮT ĐẦU UPLOAD"

### Batch Upload
1. Chọn tab "📂 Batch Upload"
2. Browse và chọn thư mục chứa video
3. Cài đặt delay giữa các upload
4. Bật/tắt tự động tạo caption
5. Click "📂 BẮT ĐẦU BATCH UPLOAD"

### Schedule Upload
1. Chọn tab "🕓 Schedule"
2. Chọn thời gian và ngày upload
3. Click "📅 Lên Lịch Upload"
4. Video sẽ được upload tự động vào thời gian đã chọn

### Settings
1. Chọn tab "⚙️ Settings"
2. Cấu hình proxy (nếu cần)
3. Bật/tắt random user agent
4. Nhập OpenAI API key cho AI caption
5. Click "💾 Save Settings"

## 🔧 Cấu hình nâng cao

### Proxy Settings
```python
# Trong tab Settings
Use Proxy: ✓
Proxy URL: http://proxy-server:port
```

### User Agent Randomization
```python
# Tự động random user agent để tránh detection
Random User Agent: ✓
```

### AI Caption Generation
```python
# Cần OpenAI API key
OpenAI API Key: sk-...
```

## 📁 Cấu trúc file

```
tiktok_auto_uploader/
├── tiktok_auto_uploader.py    # Main application
├── requirements.txt           # Python dependencies
├── build_executable.py       # Build script
├── README.md                 # Documentation
├── tiktok_cookies.json       # Saved cookies (auto-generated)
├── tiktok_config.json        # Saved config (auto-generated)
├── tiktok_settings.json      # Saved settings (auto-generated)
└── tiktok_uploader.log       # Log file (auto-generated)
```

## 🛠️ Troubleshooting

### Lỗi đăng nhập
- Kiểm tra username/password
- Xóa file `tiktok_cookies.json` và thử lại
- Kiểm tra kết nối internet

### Lỗi upload
- Kiểm tra định dạng video (mp4, mov, avi, mkv, webm)
- Kiểm tra kích thước file (TikTok có giới hạn)
- Thử lại với retry logic

### Lỗi browser
- Cập nhật Chrome browser
- Kiểm tra ChromeDriver compatibility
- Thử với proxy khác

## ⚠️ Lưu ý quan trọng

1. **Tuân thủ Terms of Service**: Sử dụng tool một cách có trách nhiệm
2. **Rate Limiting**: Không upload quá nhiều video trong thời gian ngắn
3. **Content Policy**: Đảm bảo nội dung video tuân thủ quy định TikTok
4. **API Limits**: Chú ý giới hạn API khi sử dụng AI features

## 🔄 Updates & Changelog

### v2.0.0 - Enhanced Version
- ✅ Dynamic wait thay vì time.sleep()
- ✅ Cookie-based session management
- ✅ Retry logic cho failed uploads
- ✅ Batch upload functionality
- ✅ Scheduling system
- ✅ AI-powered caption generation
- ✅ Proxy và user-agent randomization
- ✅ Enhanced logging system
- ✅ Improved UI/UX
- ✅ Executable build support

## 📞 Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log file `tiktok_uploader.log`
2. Đọc troubleshooting section
3. Tạo issue với thông tin chi tiết

## 📄 License

Tool này chỉ dành cho mục đích giáo dục và nghiên cứu. Người dùng chịu trách nhiệm tuân thủ Terms of Service của TikTok.