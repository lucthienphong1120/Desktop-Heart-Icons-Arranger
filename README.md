# ❤️ Desktop Heart Icons Arranger
Một chương trình Python thú vị giúp tự động sắp xếp các icon trên màn hình Desktop Windows của bạn thành hình trái tim với hiệu ứng chuyển động mượt mà (smooth animation).

<img width="720" height="540" alt="{2E618B7A-CA58-4632-86E5-96F8A0537053}" src="https://github.com/user-attachments/assets/7c689142-eba4-435a-8d00-472885fca26e" />

## ✨ Tính năng nổi bật
+ Hình dáng chuẩn: Sử dụng công thức toán học Parametric Heart Equation để tạo hình trái tim cân đối.
+ Hiệu ứng mượt mà (Smooth Animation): Icon sẽ trượt từ vị trí cũ sang vị trí mới thay vì "nhảy" tức thời, tạo cảm giác như có bàn tay vô hình đang sắp xếp.
+ Tương thích cao: Hoạt động tốt trên Windows 10 và Windows 11 nhờ thuật toán tìm kiếm cửa sổ SysListView32 thông minh.
+ Tùy biến: Dễ dàng điều chỉnh tốc độ bay, độ to nhỏ của trái tim ngay trong code.

## 🛠️ Yêu cầu hệ thống
+ Hệ điều hành: Windows 10 hoặc Windows 11.
+ Python 3.x đã được cài đặt.
+ Thư viện hỗ trợ: pywin32.

## 🚀 Cài đặt
1. Cài đặt Python:
Nếu chưa có, hãy tải và cài đặt Python từ python.org.

2. Cài thư viện pywin32:
Mở CMD (Command Prompt) hoặc Terminal và chạy lệnh sau:
```
pip install pywin32
```

3. Tải mã nguồn:
```
git clone https://github.com/lucthienphong1120/Desktop-Heart-Icons-Arranger
```

## 📖 Hướng dẫn sử dụng

### Bước 1: Chuẩn bị Desktop (Quan trọng ⚠️)

Trước khi chạy, bạn BẮT BUỘC phải tắt chế độ tự động sắp xếp của Windows:
+ Click chuột phải vào màn hình Desktop (khoảng trống).
+ Chọn View.
+ Bỏ chọn (Uncheck) dòng Auto arrange icons.
+ Bỏ chọn (Uncheck) dòng Align icons to grid (để hình trái tim mượt hơn, không bị gãy khúc theo lưới).

### Bước 2: Chạy chương trình

Mở CMD hoặc Terminal tại thư mục chứa file và chạy lệnh:
```
python heart_icons.py
```

Sau khi chạy, hãy ngồi thư giãn và xem các icon tự động bay về vị trí hình trái tim! ❤️

## ⚙️ Cấu hình nâng cao

Bạn có thể mở file `heart_icons.py` bằng bất kỳ trình soạn thảo văn bản nào để chỉnh sửa các thông số ở phần đầu file:

```
ANIMATION_SPEED = 0.01 # Tốc độ trượt (càng nhỏ càng nhanh)
STEPS = 15             # Số bước chia nhỏ quãng đường (càng lớn càng mượt nhưng chậm hơn)
SCALE_BASE = 15        # Độ to của trái tim (tăng giảm tùy số lượng icon)
```

## ❓ Khắc phục lỗi thường gặp

1. Lỗi: "Không tìm thấy Desktop ListView"

+ Nguyên nhân: Có thể bạn đang dùng phần mềm hình nền động như Wallpaper Engine.
+ Khắc phục: Hãy tắt hoàn toàn Wallpaper Engine (Quit ở khay hệ thống) rồi chạy lại script.

2. Icon không di chuyển dù chương trình báo thành công

+ Nguyên nhân: Bạn chưa tắt "Auto arrange icons".
+ Khắc phục: Làm lại Bước 1 trong phần Hướng dẫn sử dụng.

3. Lỗi ModuleNotFoundError: No module named 'win32gui'

+ Khắc phục: Bạn chưa cài thư viện. Hãy chạy lại lệnh pip install pywin32.

## 📝 Lưu ý

Chương trình can thiệp vào vị trí icon thông qua Windows API. Nếu muốn khôi phục lại vị trí cũ, bạn chỉ cần click chuột phải Desktop -> View -> Chọn lại Auto arrange icons.

Code này an toàn và không gây hại cho hệ thống.

Chúc bạn có một màn hình Desktop thật ấn tượng!
