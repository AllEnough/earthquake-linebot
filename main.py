# 主程式入口
from flask import Flask, request, abort
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

@app.route("/analyze", methods=["GET"])
def analyze():
    avg = get_average_magnitude()
    max_quake = get_max_magnitude()
    recent = get_recent_earthquake_count()

    return jsonify({
        "平均規模": round(avg, 2) if avg else "無資料",
        "最大地震": {
            "時間": max_quake["origin_time"],
            "震央": max_quake["epicenter"],
            "規模": max_quake["magnitude"]
        } if max_quake else "無資料",
        "最近7天地震次數": recent
    })

if __name__ == "__main__":
    start_background_quake_import()  # ✅ 啟動每5分鐘抓一次地震資料並寫入 MongoDB
    threading.Thread(target=quake_check_loop, daemon=True).start()  # ✅ 啟動 LINE 地震推播檢查
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

