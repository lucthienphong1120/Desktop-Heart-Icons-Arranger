import win32gui
import win32con
import win32api
import win32process
import math
import time
import ctypes
import bisect

# --- CẤU HÌNH ---
# 1. Cấu hình hiệu ứng xếp hình (Giai đoạn 1)
ANIMATION_SPEED = 0.01       # Tốc độ trượt (càng nhỏ càng nhanh)
STEPS = 30                   # Số bước di chuyển (càng lớn càng mượt nhưng chậm)
SCALE_BASE = 25              # Độ to của trái tim

# 2. Cấu hình xoay vòng (Giai đoạn 2)
ENABLE_ROTATION = True       # Bật/Tắt chế độ xoay vòng sau khi xếp xong
ROTATION_SPEED = 0.005       # Tốc độ xoay (đã chỉnh lại cho phù hợp với logic mới - 0.001 đến 0.01)
REFRESH_RATE = 0.05          # Thời gian nghỉ giữa các khung hình khi xoay (giây)
PAUSE_BEFORE_ROTATION = 1.0  # Thời gian nghỉ trước khi bắt đầu xoay (giây)
# ----------------

# Hằng số Windows API
LVM_GETITEMCOUNT = 0x1004
LVM_SETITEMPOSITION = 0x100F
LVM_GETITEMPOSITION = 0x1010
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def find_desktop_listview_robust():
    """Tìm handle của Desktop ListView"""
    hwnd_listview = None
    def enum_callback(top_hwnd, _):
        nonlocal hwnd_listview
        hwnd_shell = win32gui.FindWindowEx(top_hwnd, 0, "SHELLDLL_DefView", None)
        if hwnd_shell:
            hwnd_lv = win32gui.FindWindowEx(hwnd_shell, 0, "SysListView32", None)
            if hwnd_lv:
                hwnd_listview = hwnd_lv
                return False 
        return True
    win32gui.EnumWindows(enum_callback, None)
    return hwnd_listview

def get_item_position(hwnd, index):
    """
    Đọc vị trí hiện tại của Icon từ bộ nhớ của tiến trình Desktop.
    """
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    
    if not process:
        return None

    virtual_mem = ctypes.windll.kernel32.VirtualAllocEx(process, None, ctypes.sizeof(POINT), MEM_COMMIT, PAGE_READWRITE)
    
    if not virtual_mem:
        ctypes.windll.kernel32.CloseHandle(process)
        return None

    win32gui.SendMessage(hwnd, LVM_GETITEMPOSITION, index, virtual_mem)

    point = POINT()
    ctypes.windll.kernel32.ReadProcessMemory(process, virtual_mem, ctypes.byref(point), ctypes.sizeof(POINT), None)

    ctypes.windll.kernel32.VirtualFreeEx(process, virtual_mem, 0, MEM_RELEASE)
    ctypes.windll.kernel32.CloseHandle(process)

    return (point.x, point.y)

def smooth_move(hwnd, index, start_x, start_y, end_x, end_y):
    """Di chuyển icon từ start đến end theo từng bước nhỏ (Animation)"""
    dx = (end_x - start_x) / STEPS
    dy = (end_y - start_y) / STEPS

    for i in range(1, STEPS + 1):
        cur_x = int(start_x + dx * i)
        cur_y = int(start_y + dy * i)
        
        lparam = win32api.MAKELONG(cur_x, cur_y)
        win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, index, lparam)
        time.sleep(ANIMATION_SPEED)

# --- LOGIC MỚI: TẠO ĐƯỜNG CONG ĐỀU (ARC LENGTH PARAMETERIZATION) ---

def generate_even_heart_path(scale, center_x, center_y, resolution=2000):
    """
    Tạo ra một danh sách các điểm trên hình trái tim có khoảng cách ĐỀU NHAU.
    Khắc phục tình trạng icon bị tụ lại ở đỉnh và đáy.
    """
    path_points = []
    total_length = 0.0
    
    # Bước 1: Tạo các điểm thô và tính tổng độ dài đường cong
    raw_points = []
    prev_x, prev_y = None, None
    
    for i in range(resolution + 1):
        t = i * (2 * math.pi / resolution)
        
        # Công thức trái tim gốc
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        # Scale
        px = center_x + (x * scale)
        py = center_y - (y * scale) # Y ngược
        
        if prev_x is not None:
            dist = math.sqrt((px - prev_x)**2 + (py - prev_y)**2)
            total_length += dist
            
        raw_points.append({'dist': total_length, 'x': px, 'y': py})
        prev_x, prev_y = px, py
        
    # Bước 2: Chuẩn hóa khoảng cách về 0.0 -> 1.0 để dễ tra cứu
    for p in raw_points:
        p['percent'] = p['dist'] / total_length if total_length > 0 else 0
        
    return raw_points

def get_pos_from_path(path, progress):
    """
    Lấy tọa độ (x, y) dựa trên phần trăm quãng đường (0.0 -> 1.0).
    Sử dụng tìm kiếm nhị phân để tối ưu tốc độ.
    """
    # Đảm bảo progress luôn nằm trong khoảng 0->1 (xoay vòng)
    progress = progress % 1.0
    
    # Tìm điểm gần nhất trong danh sách đã tạo sẵn
    # (Đây là kỹ thuật Look-up Table)
    idx = bisect.bisect_left([p['percent'] for p in path], progress)
    if idx >= len(path):
        idx = len(path) - 1
        
    p = path[idx]
    return int(p['x']), int(p['y'])

# -------------------------------------------------------------------

def arrange_and_rotate():
    hwnd_lv = find_desktop_listview_robust()
    if not hwnd_lv:
        print("❌ Không tìm thấy Desktop. Hãy tắt Wallpaper Engine.")
        return

    count = win32gui.SendMessage(hwnd_lv, LVM_GETITEMCOUNT, 0, 0)
    print(f"✅ Đã tìm thấy {count} icons.")
    if count == 0: return

    # Thông số màn hình
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    center_x = screen_width // 2
    center_y = screen_height // 2 - 50
    
    # Điều chỉnh scale
    scale = SCALE_BASE if count > 15 else 10

    # TẠO ĐƯỜNG DẪN ĐỀU (Chỉ tính toán 1 lần)
    print("🔄 Đang tính toán đường dẫn đều (Anti-clustering)...")
    heart_path = generate_even_heart_path(scale, center_x, center_y)

    print("🎬 GIAI ĐOẠN 1: Xếp hình trái tim (Smooth Animation)...")
    print("-" * 40)
    
    # GIAI ĐOẠN 1: Xếp tĩnh
    for i in range(count):
        # Tính phần trăm quãng đường thay vì góc (0.0 đến 1.0)
        progress = i / count
        target_x, target_y = get_pos_from_path(heart_path, progress)
        
        current_pos = get_item_position(hwnd_lv, i)
        
        if current_pos:
            start_x, start_y = current_pos
            print(f"✨ Icon {i+1}/{count}: Di chuyển...")
            smooth_move(hwnd_lv, i, start_x, start_y, target_x, target_y)
        else:
            lparam = win32api.MAKELONG(target_x, target_y)
            win32gui.SendMessage(hwnd_lv, LVM_SETITEMPOSITION, i, lparam)
            time.sleep(0.05)
    
    win32gui.UpdateWindow(hwnd_lv)
    print("-" * 40)
    print("❤️  Đã xếp xong! Các icon đã được chia đều khoảng cách.")
    
    if not ENABLE_ROTATION:
        return

    print(f"⏳ Nghỉ {PAUSE_BEFORE_ROTATION}s trước khi bắt đầu xoay...")
    time.sleep(PAUSE_BEFORE_ROTATION) 

    print("\n🔄 GIAI ĐOẠN 2: Bắt đầu xoay vòng (Nhấn Ctrl + C để dừng)...")
    
    current_offset = 0.0 # Đơn vị: % quãng đường (0.0 -> 1.0)
    try:
        while True:
            current_offset += ROTATION_SPEED
            
            # Cập nhật vị trí
            for i in range(count):
                # Vị trí của mỗi icon = (vị trí gốc + offset xoay) % 1 vòng
                progress = (i / count + current_offset)
                px, py = get_pos_from_path(heart_path, progress)
                
                lparam = win32api.MAKELONG(px, py)
                win32gui.SendMessage(hwnd_lv, LVM_SETITEMPOSITION, i, lparam)
            
            win32gui.UpdateWindow(hwnd_lv)
            time.sleep(REFRESH_RATE)

    except KeyboardInterrupt:
        print("\n🛑 Đã dừng xoay.")

if __name__ == "__main__":
    try:
        arrange_and_rotate()
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
