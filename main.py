# 主程式入口
from flask import Flask
from quake_import_loop import start_background_quake_import
from earthquake import quake_check_loop
from line_bot import handle_webhook
from quake_import import fetch_and_store_earthquake_data
import threading
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    return handle_webhook()

fetch_and_store_earthquake_data()  # 可整合進定時執行流程中

if __name__ == "__main__":
    start_background_quake_import()  # ✅ 啟動每5分鐘抓一次地震資料並寫入 MongoDB
    threading.Thread(target=quake_check_loop, daemon=True).start()  # ✅ 啟動 LINE 地震推播檢查
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

