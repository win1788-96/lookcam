import pygetwindow as gw
import numpy as np
import cv2
import time
import os
import win32gui
import win32con
import win32ui
import ctypes
from PIL import Image, ImageDraw, ImageFont

# --- 1. 防止系統休眠 ---
def prevent_sleep():
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001 | 0x00000040)
    except Exception as e:
        print(f"無法設定防止休眠: {e}")

# --- 2. DPI 感知處理 ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- 3. 繪製繁體中文函式 ---
def draw_chinese_text(img, text, position, font_size=20, color=(255, 255, 255)):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype("msjh.ttc", font_size)
    except:
        font = ImageFont.load_default()
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# --- 4. 強化視窗擷取 (使用 BitBlt 解決硬體加速黑畫面問題) ---
def capture_hwnd_direct(hwnd, width, height):
    """使用 BitBlt 強行擷取視窗內容，包含硬體加速層"""
    try:
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)

        # 使用 BitBlt 搭配 CAPTUREBLT 標籤 (0x40000000)
        # 這能擷取大多數硬體加速視窗，且只針對該視窗區域
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY | 0x40000000)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # 清理資源
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"擷取失敗: {e}")
    return None

def get_window_rect(hwnd):
    """獲取視窗精確座標 (不含陰影)"""
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
        if f:
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            res = f(ctypes.wintypes.HWND(hwnd),
                    ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                    ctypes.byref(rect),
                    ctypes.sizeof(rect))
            if res == 0:
                return rect.left, rect.top, rect.right, rect.bottom
    except:
        pass
    return win32gui.GetWindowRect(hwnd)

def on_change(x):
    pass

# --- 5. 主程式 ---
def capture_lookcam_window():
    print("正在搜尋 LookCam 視窗...")
    target_title = None
    for t in gw.getAllTitles():
        if "lookcam" in t.lower() and "monitor" not in t.lower() and "trae" not in t.lower():
            target_title = t
            break
    
    if not target_title:
        print("找不到 LookCam 視窗。")
        return

    hwnd = win32gui.FindWindow(None, target_title)
    if not hwnd: return

    print(f"已成功鎖定: {target_title}")
    prevent_sleep()

    if not os.path.exists("motion_captures"):
        os.makedirs("motion_captures")

    # --- 建立視窗 ---
    main_win = "LookCam Motion Monitor"
    cv2.namedWindow(main_win, cv2.WINDOW_AUTOSIZE)
    
    # 預設值調整：靈敏度 5 (極低)，間隔 0.2s
    cv2.createTrackbar("Sensitivity", main_win, 5, 100, on_change)
    cv2.createTrackbar("Interval", main_win, 2, 10, on_change)
    
    avg_frame = None
    last_save_time = 0
    
    print("\n[監控中] 已強化人體偵測與雜訊過濾。按 'q' 鍵停止。")
    
    try:
        while True:
            if not win32gui.IsWindow(hwnd):
                print("LookCam 視窗已關閉。")
                break
            
            # --- 新增：檢查視窗是否最小化 ---
            if win32gui.IsIconic(hwnd):
                # 視窗最小化時，擷取不到有效內容，暫停監控
                time.sleep(1.0)
                continue

            # 讀取設定
            sensitivity = cv2.getTrackbarPos("Sensitivity", main_win)
            # 重新設計靈敏度公式：數值愈小面積門檻愈大 (靈敏度 1 時要求約 1/4 畫面變動才觸發)
            min_area_base = max(200, (101 - sensitivity) ** 2 * 1.5)
            
            interval_raw = cv2.getTrackbarPos("Interval", main_win)
            save_cooldown = max(0.1, interval_raw / 10.0)

            # 獲取視窗座標
            left, top, right, bottom = get_window_rect(hwnd)
            w, h = right - left, bottom - top
            if w <= 0 or h <= 0:
                time.sleep(0.2)
                continue

            # --- 擷取視窗影像 ---
            frame = capture_hwnd_direct(hwnd, w, h)
            if frame is None:
                time.sleep(0.1)
                continue

            # CPU 優化與預處理
            scale = 300 / w
            new_w, new_h = 300, int(h * scale)
            small_frame = cv2.resize(frame, (new_w, new_h))
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            # 增加模糊強度 (從 21 增加到 31) 以過濾細微閃爍
            gray = cv2.GaussianBlur(gray, (31, 31), 0)

            # --- 修正：處理視窗縮放導致的尺寸不匹配 ---
            if avg_frame is not None:
                # 檢查目前影格尺寸是否與平均背景一致
                if gray.shape != avg_frame.shape:
                    print(f"偵測到視窗尺寸變更 ({avg_frame.shape} -> {gray.shape})，重置監控背景...")
                    avg_frame = None

            # 背景平均法
            if avg_frame is None:
                avg_frame = gray.copy().astype("float")
                continue

            # 加快背景更新速度 (0.2) 以適應緩慢的光影漂移
            cv2.accumulateWeighted(gray, avg_frame, 0.2)
            frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
            
            # 提高差異門檻 (從 35 提高到 45) 以過濾大部分光影
            thresh = cv2.threshold(frame_delta, 45, 255, cv2.THRESH_BINARY)[1]
            
            # --- 新增：侵蝕處理 (Erode) ---
            # 這能徹底消除掉微小的雜點，只保留大面積的連通區域
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.erode(thresh, kernel, iterations=1)
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for c in contours:
                if cv2.contourArea(c) < (min_area_base * scale * scale):
                    continue
                motion_detected = True
                (x, y, cw, ch) = cv2.boundingRect(c)
                cv2.rectangle(frame, (int(x/scale), int(y/scale)), 
                              (int((x+cw)/scale), int((y+ch)/scale)), (0, 255, 0), 2)

            now = time.time()
            if motion_detected and (now - last_save_time > save_cooldown):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = f"motion_captures/motion_{timestamp}.jpg"
                cv2.imwrite(save_path, frame)
                print(f"[{time.strftime('%H:%M:%S')}] 偵測到大面積異動！存檔: {save_path}")
                last_save_time = now

            # 繪製繁體中文狀態列
            status_zh = "偵測到異動 !!!" if motion_detected else "監控中..."
            info_line = f"狀態: {status_zh} | 靈敏度: {sensitivity} | 間隔: {save_cooldown}秒"
            cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)
            frame = draw_chinese_text(frame, info_line, (10, 8), font_size=20, color=(0, 255, 255))
            frame = draw_chinese_text(frame, "按 'q' 鍵退出", (w - 120, h - 30), font_size=16, color=(255, 255, 255))

            cv2.imshow(main_win, frame)

            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"程式執行異常: {e}")
    finally:
        cv2.destroyAllWindows()
        print("監控已結束。")

if __name__ == "__main__":
    capture_lookcam_window()
