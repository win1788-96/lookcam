import cv2
import time

IP_ADDRESS = "192.168.0.35"
USERNAME = "admin"
PASSWORD = "0525"

RTSP_URL_TEMPLATES = [
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/live/ch0",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/onvif1",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/11",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:554/stream1"
]

def check_rtsp():
    for url in RTSP_URL_TEMPLATES:
        masked_url = url.replace(PASSWORD, "******")
        print(f"正在測試: {masked_url}")
        cap = cv2.VideoCapture(url)
        
        if cap.isOpened():
            print(f"成功！連接到 {masked_url}")
            ret, frame = cap.read()
            if ret:
                print("成功讀取到影格！")
                cap.release()
                return True
            else:
                print("連接成功但無法讀取影格。")
        else:
            print(f"無法連接到 {masked_url}")
        cap.release()
    return False

if __name__ == "__main__":
    check_rtsp()
