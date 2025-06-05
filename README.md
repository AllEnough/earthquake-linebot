# 地震 LINE Bot

這是一個使用 Python 撰寫的地震查詢與推播系統，提供 LINE Bot 與網頁介面兩種方式查詢與訂閱地震資訊。地震資料來源為中央氣象局開放資料，並儲存在 MongoDB 中。

## 功能特色

- 透過定時背景服務自動抓取中央氣象局的最新地震資料並寫入資料庫
- LINE Bot 支援指令查詢地震紀錄、統計圖表、文字摘要及自訂推播條件
- 提供地震即時推播，包含靜態地圖圖片（使用 Google Maps Static API）
- 網頁介面可瀏覽近期地震、互動式地圖與各項統計圖表
- 內建 ARIMA 模型預測未來地震最大規模

## 安裝與執行

1. 下載或複製此專案
2. 安裝 Python 依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 建立 `.env` 檔案並設定以下環境變數：
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `MONGO_URI` – MongoDB 連線字串
   - `CWA_API_KEY` – 中央氣象局 API 金鑰
   - `DOMAIN` – 伺服器網址（產生圖表或地圖連結用）
   - `GOOGLE_MAPS_API_KEY` – Google Maps Static API 金鑰
4. 執行主程式：
   ```bash
   python main.py
   ```

亦可使用 `Dockerfile` 建立容器執行。

## 授權

本專案採用 MIT License。
