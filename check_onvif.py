from onvif import ONVIFCamera
import zeep

IP_ADDRESS = "192.168.0.35"
USERNAME = "admin"
PASSWORD = "0525"

def get_onvif_stream():
    try:
        # 嘗試連接 ONVIF
        print(f"嘗試連接 ONVIF {IP_ADDRESS}:80...")
        mycam = ONVIFCamera(IP_ADDRESS, 80, USERNAME, PASSWORD)
        
        # 獲取媒體服務
        media = mycam.create_media_service()
        
        # 獲取設定檔
        profiles = media.GetProfiles()
        print(f"找到 {len(profiles)} 個 ONVIF 設定檔")
        
        for profile in profiles:
            token = profile.token
            # 獲取串流網址
            obj = media.create_type('GetStreamUri')
            obj.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
            obj.ProfileToken = token
            uri_obj = media.GetStreamUri(obj)
            print(f"設定檔 {token} 的 RTSP 網址: {uri_obj.Uri}")
            
    except Exception as e:
        print(f"ONVIF 連接失敗: {e}")

if __name__ == "__main__":
    get_onvif_stream()
