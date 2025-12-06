import win32gui
import win32con
import win32api
import win32process
import math
import time
import ctypes
from ctypes import wintypes

# --- CẤU HÌNH ---
ANIMATION_SPEED = 0.01 # Tốc độ trượt (càng nhỏ càng nhanh)
STEPS = 30             # Số bước di chuyển (càng lớn càng mượt nhưng chậm)
SCALE_BASE = 20        # Độ to của trái tim
# ----------------

# Các hằng số cần thiết
LVM_GETITEMCOUNT = 0x1004
LVM_SETITEMPOSITION = 0x100F
LVM_GETITEMPOSITION = 0x1010
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04

# Cấu trúc điểm để đọc bộ nhớ
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def find_desktop_listview_robust():
    """Tìm cửa sổ chứa icon Desktop"""
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
    Hàm nâng cao: Đọc vị trí hiện tại của Icon từ bộ nhớ của tiến trình Desktop.
    """
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    
    if not process:
        return None

    # Cấp phát bộ nhớ trong tiến trình Desktop để chứa kết quả trả về
    virtual_mem = ctypes.windll.kernel32.VirtualAllocEx(process, None, ctypes.sizeof(POINT), MEM_COMMIT, PAGE_READWRITE)
    
    if not virtual_mem:
        ctypes.windll.kernel32.CloseHandle(process)
        return None

    # Gửi lệnh lấy vị trí, kết quả sẽ được ghi vào virtual_mem
    win32gui.SendMessage(hwnd, LVM_GETITEMPOSITION, index, virtual_mem)

    # Đọc kết quả từ bộ nhớ đó về Python
    point = POINT()
    ctypes.windll.kernel32.ReadProcessMemory(process, virtual_mem, ctypes.byref(point), ctypes.sizeof(POINT), None)

    # Giải phóng bộ nhớ và đóng handle
    ctypes.windll.kernel32.VirtualFreeEx(process, virtual_mem, 0, MEM_RELEASE)
    ctypes.windll.kernel32.CloseHandle(process)

    return (point.x, point.y)

def smooth_move(hwnd, index, start_x, start_y, end_x, end_y):
    """Di chuyển icon từ A đến B theo từng bước nhỏ"""
    dx = (end_x - start_x) / STEPS
    dy = (end_y - start_y) / STEPS

    for i in range(1, STEPS + 1):
        cur_x = int(start_x + dx * i)
        cur_y = int(start_y + dy * i)
        
        lparam = win32api.MAKELONG(cur_x, cur_y)
        win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, index, lparam)
        time.sleep(ANIMATION_SPEED)

def arrange_heart():
    # 1. Tìm cửa sổ
    hwnd_lv = find_desktop_listview_robust()
    if not hwnd_lv:
        print("❌ Không tìm thấy Desktop. Hãy tắt Wallpaper Engine.")
        return

    # 2. Lấy số lượng icon
    count = win32gui.SendMessage(hwnd_lv, LVM_GETITEMCOUNT, 0, 0)
    print(f"✅ Đã tìm thấy {count} icons.")
    if count == 0: return

    # 3. Tính toán tâm màn hình
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    center_x = screen_width // 2
    center_y = screen_height // 2 - 50
    scale = SCALE_BASE if count > 15 else 10
    
    print("🎬 Action! Bắt đầu xếp hình trái tim (Smooth Animation)...")
    print("-" * 40)

    # 4. Vòng lặp chính
    for i in range(count):
        # Tính đích đến
        t = i * (2 * math.pi / count)
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        
        target_x = int(center_x + (x * scale))
        target_y = int(center_y - (y * scale))
        
        # Lấy vị trí hiện tại để làm điểm xuất phát
        current_pos = get_item_position(hwnd_lv, i)
        
        if current_pos:
            start_x, start_y = current_pos
            print(f"✨ Icon {i+1}: Trượt từ ({start_x},{start_y}) -> ({target_x},{target_y})")
            
            # Gọi hàm di chuyển mượt
            smooth_move(hwnd_lv, i, start_x, start_y, target_x, target_y)
        else:
            # Fallback: Nếu không đọc được vị trí cũ thì nhảy luôn tới đích
            lparam = win32api.MAKELONG(target_x, target_y)
            win32gui.SendMessage(hwnd_lv, LVM_SETITEMPOSITION, i, lparam)
            time.sleep(0.05)

    win32gui.UpdateWindow(hwnd_lv)
    print("-" * 40)
    print("❤️  Hoàn tất! Kiểm tra thành quả nào.")

if __name__ == "__main__":
    try:
        arrange_heart()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng.")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")