# 地震 LINE Bot 系統

這是一個以 Python 撰寫的全功能地震查詢與推播程式，結合 LINE Bot 與簡易網頁，協助您即時掌握台灣地震資訊。地震資料來源為中央氣象局開放資料，並儲存在 MongoDB 中。

## 主要特色

- **自動資料匯入** ：背景服務每1分鐘抓取一次中央氣象局最新地震資料並存入資料庫，包含顯著的地震來源。
- **LINE Bot 查詢**：支援快速查詢最新地震、指定地區與規模篩選、地震圖表，以及一週摘要文字報告。
- **即時推播**：偵測到新地震時立即推播至所有用戶，可搭配 Google Maps Static API 顯示震央地圖。
- **互動式網頁**：內建簡易網頁(Flask)展示近期地震列表、統計圖表及互動地圖。
- **地震預測**：使用 ARIMA 模型預估未來幾天可能出現的最大地震規模並產生圖表。

## 參考網頁

https://earthquake-linebot-production.up.railway.app

## 安裝步驟

1. 下載或複製此專案。
2. 安裝 Python 相依套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 建立 `.env` 並設定下列環境變數：
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `MONGO_URI`：MongoDB 連線字串
   - `CWA_API_KEY`：中央氣象局 API 金鑰
   - `DOMAIN`：外部可存取的網址 (產生圖表或地圖連結用)
   - `GOOGLE_MAPS_API_KEY`：Google Maps Static API 金鑰

## 執行方式

啟動主程式即可同時啟動 LINE webhook 與網頁服務：
```bash
python main.py
```
啟動後將於背景持續更新地震資料並推播最新資訊。

若資料庫出現重複紀錄，可使用：
```bash
python remove_duplicates.py
```

也可利用 `Dockerfile` 建立容器環境執行。

## 基本指令摘要

在 LINE 對話視窗中輸入下列關鍵字即可互動：
- `最新`：取得最新一筆地震資訊
- `地震 花蓮 >5`：查詢震央含「花蓮」且規模大於 5 的紀錄
- `地震統計圖`、`地震平均規模圖`、`地震最大規模圖`、`地震預測圖`
- `地震摘要`：取得近一週地震活動報告
- `幫助`：列出完整指令說明

## 授權

本專案採用 MIT License 發布，歡迎自由使用與修改。
