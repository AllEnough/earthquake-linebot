# 主程式入口
from flask import Flask, send_file
from quake_import_loop import start_background_quake_import
from earthquake import quake_check_loop
from line_bot import handle_webhook
from quake_import import fetch_and_store_earthquake_data
from web_page import web_page

from flask import jsonify
from earthquake_analysis import get_average_magnitude, get_max_magnitude, get_recent_earthquake_count

import threading
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
app.register_blueprint(web_page) # 註冊網頁藍圖


@app.route("/line", methods=['POST'])
def webhook():
    return handle_webhook()

@app.route("/", methods=["GET"])
def index():
    return "✅ 伺服器正常啟動中"

@app.route("/test", methods=["GET"])
def test():
    fetch_and_store_earthquake_data()   # 可整合進定時執行流程中
    return "✅ 手動執行地震資料抓取完成"

if __name__ == "__main__":
    start_background_quake_import()  # ✅ 啟動每5分鐘抓一次地震資料並寫入 MongoDB
    threading.Thread(target=quake_check_loop, daemon=True).start()  # ✅ 啟動 LINE 地震推播檢查
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

