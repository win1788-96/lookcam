# LookCam 異動偵測與監控工具 (LookCam Motion Monitor)

這是一個針對 LookCam 攝影機軟體開發的輔助工具，旨在提供更低負擔、自動化的異動偵測與截圖保存功能。

## 🌟 核心功能

- **整合視窗監控**：直接擷取 LookCam 視窗畫面，支援硬體加速視窗，即使被其他視窗遮擋也不受干擾。
- **智慧異動偵測 (Motion Detection)**：
  - 採用「背景平均法」自動過濾光影雜訊。
  - 「侵蝕與膨脹」演算法有效過濾數位噪點，專注於人體等大面積變動。
- **繁體中文介面**：即時顯示監控狀態、靈敏度與截圖間隔。
- **高度客製化設定**：
  - **靈敏度 (Sensitivity)**：1-100 自由調整（預設 5），數值愈小愈不靈敏。
  - **掃描間隔 (Interval)**：0.1 秒至 1.0 秒（預設 0.2 秒）。
- **背景執行與防止休眠**：自動設定 Windows 執行狀態，防止電腦在監控期間進入休眠。
- **CPU 優化**：縮小運算畫面並控制取樣率，大幅降低處理器負擔。

## 🛠️ 安裝需求

請確保您的電腦已安裝 Python 3.x，並執行以下指令安裝必要套件：

```powershell
pip install numpy opencv-python mss pygetwindow pypiwin32 Pillow
```

## 🚀 快速開始

1. 開啟 **LookCam** 官方軟體並進入攝影機監控畫面。
2. 執行監控腳本：
   ```powershell
   python window_capture.py
   ```
3. 在彈出的「LookCam Motion Monitor」視窗中調整滑桿以達到最佳效果：
   - **Sensitivity**：若光影誤報太多，請向左調低。
   - **Interval**：調整偵測到異動後的存檔冷卻時間。
4. 偵測到的照片將自動儲存在 `motion_captures/` 資料夾下。

## 📂 檔案說明

- `window_capture.py`：主程式，包含 UI、移動偵測與視窗擷取邏輯。
- `capture_stream.py`：RTSP 視訊流捕抓測試腳本。
- `check_rtsp.py` / `check_onvif.py`：攝影機通訊協議診斷工具。
- `.gitignore`：已配置排除個人設定與截圖檔，保護隱私。

## ⚠️ 注意事項

- 請確保 LookCam 軟體視窗**未最小化**（縮小到系統匣將無法擷取）。
- 本工具僅供學術研究與個人監控輔助使用，請遵守相關隱私法規。
