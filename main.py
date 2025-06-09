# main.py
# 主程式入口

from flask import Flask
from quake_import_loop import start_background_quake_import
from earthquake import quake_check_loop
from line_bot import handle_webhook
from quake_import import fetch_and_store_earthquake_data
from line_push_utils import push_messages_to_all_users, push_image_to_all_users
from quake_map import generate_static_map
from config import db, DOMAIN
from web_page import web_page

import threading
import os
import sys
import io

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ✅ 修正輸出為 UTF-8（避免 Heroku/Railway log 中文亂碼）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ 建立 Flask 應用
app = Flask(__name__)
app.register_blueprint(web_page)  # 首頁頁面（HTML）

# ✅ LINE Bot webhook 路由
@app.route("/line", methods=["POST"])
def webhook():
    return handle_webhook()

# ✅ 健康檢查（首頁狀態）
@app.route("/", methods=["GET"])
def index():
    return "✅ 伺服器正常啟動中"

# ✅ 測試：手動抓取一次地震資料
@app.route("/test", methods=["GET"])
def test():
    fetch_and_store_earthquake_data()
    return "✅ 手動執行地震資料抓取完成"

# ✅ 測試：強制推播最新地震或純文字
@app.route("/test_push", methods=["GET"])
def test_push():
    try:
        latest = db["earthquakes"].find_one(sort=[("origin_time", -1)])
        if latest:
            msg = (
                f"📢 測試地震推播！\n"
                f"時間：{latest.get('origin_time')}\n"
                f"地點：{latest.get('epicenter')}\n"
                f"深度：{latest.get('depth')} 公里\n"
                f"規模：芮氏 {latest.get('magnitude')}"
            )

            if latest.get("lat") and latest.get("lon"):
                map_path = generate_static_map(latest["lat"], latest["lon"])
                if map_path:
                    img_url = f"{DOMAIN}/static/map_latest.png"
                    push_image_to_all_users(img_url, msg, quake=latest)
                    return "✅ 已推播地圖圖片"

            push_messages_to_all_users(msg, quake=latest)
        else:
            push_messages_to_all_users("📢 這是測試推播訊息")
        return "✅ 已推播測試訊息"
    except Exception as e:
        return f"❌ 推播失敗：{e}", 500

# ✅ 啟動背景服務
if __name__ == "__main__":
    # 每 5 分鐘抓取地震資料 + 每日圖表更新 + 每週摘要推播
    start_background_quake_import()

    # 推播機制（每 5 分鐘比對地震資料，若有新資料則推播）
    threading.Thread(target=quake_check_loop, daemon=True).start()

    # 啟動 Flask 網頁服務
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
