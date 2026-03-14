import cv2
import time
import os

# 根據分析，LookCam 攝影機 (IP: 192.168.0.35) 的 554 端口已開放，這表示它支援 RTSP 協議。
# 請將以下 'password' 替換為你在 LookCam 軟體中 "Device Setting" -> "Access pwd" -> "Modify" 看到的密碼。
# 如果你沒有設定密碼，請嘗試留空或使用 'admin'。

IP_ADDRESS = "192.168.0.35"
USERNAME = "admin"
PASSWORD = "0525"  # <--- 使用使用者提供的密碼

# 常見的 LookCam / P2P 攝影機 RTSP URL 格式
RTSP_URL_TEMPLATES = [
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/live/ch0",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/onvif1",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/11",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/stream1"
]

def test_rtsp_stream():
    for url in RTSP_URL_TEMPLATES:
        print(f"正在嘗試連接: {url.replace(PASSWORD, '******')}")
        cap = cv2.VideoCapture(url)
        
        if cap.isOpened():
            print(f"成功連接到視訊流！")
            
            # 建立儲存目錄
            if not os.path.exists("captures"):
                os.makedirs("captures")
            
            # 開始捕抓
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"captures/stream_{timestamp}.mp4"
            
            # 設定影片編碼器 (使用 XVID 或 mp4v)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            
            print(f"開始錄製視訊流到: {output_file} (按 'q' 鍵停止)")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("無法讀取影格，視訊流可能已中斷。")
                    break
                
                # 儲存影格
                out.write(frame)
                
                # 顯示視窗 (可選)
                cv2.imshow("LookCam Stream Capture", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            print(f"錄製完成。檔案儲存在: {output_file}")
            return
        else:
            print("連接失敗，嘗試下一個 URL...")
            cap.release()

    print("未能成功連接到任何預設的 RTSP URL。請確認密碼是否正確，或在軟體中確認 RTSP 設定。")

if __name__ == "__main__":
    if PASSWORD == "YOUR_PASSWORD_HERE":
        print("錯誤: 請先在腳本中設定你的攝影機密碼 (PASSWORD)。")
        print("你可以在 LookCam 軟體的 'Device Setting' -> 'Access pwd' 中找到或修改它。")
    else:
        test_rtsp_stream()
