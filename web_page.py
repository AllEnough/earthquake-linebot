# web_page.py
from flask import Blueprint, render_template, request, jsonify
from database import get_earthquake_collection
from datetime import datetime, UTC, timedelta
from quake_summary import get_text_summary
from bson.json_util import dumps
from config import GOOGLE_MAPS_API_KEY

web_page = Blueprint('web_page', __name__)
collection = get_earthquake_collection()

@web_page.route('/')
def index():
    keyword = request.args.get('keyword', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    query = {}

    all_epicenters = collection.distinct("epicenter")

    if keyword:
        query["epicenter"] = {"$regex": keyword}
    if start_date_str or end_date_str:
        query["origin_time"] = {}
        if start_date_str:
            try:
                query["origin_time"]["$gte"] = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                pass
        if end_date_str:
            try:
                query["origin_time"]["$lte"] = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                pass

    quakes = collection.find(query).sort('origin_time', -1).limit(50)
    summary = get_text_summary(7)

    line_help = """
🤖 LINE 地震查詢機器人使用說明：

🔍 基本查詢（快速）：
🔹 輸入「地震 花蓮」➡️ 查詢震央包含『花蓮』的地震
🔹 輸入「地震 >5」➡️ 查詢規模大於 5 的地震

📅 進階查詢（條件）：
🔹 「查詢 花蓮」➡️ 查詢花蓮地震紀錄（近 50 筆）
🔹 「查詢 花蓮 2024-05-01 2024-05-31」➡️ 查詢時間區間地震

📊 圖表查詢：
🔹 「地震統計圖」\n🔹 「地震平均規模圖」\n
🔹 「地震最大規模圖」\n🔹 「地震預測圖」\n

📝 文字報告：
🔹 「地震摘要」➡️ 一週地震活動總結
"""

    now = datetime.now(UTC)

    return render_template(
        'index.html',
        quakes=quakes,
        keyword=keyword,
        start_date=start_date_str,
        end_date=end_date_str,
        all_epicenters=sorted(all_epicenters),
        summary=summary,
        line_help=line_help,
        now=now,
        timedelta=timedelta,  # ✅ 加這行
        show_heatmap_button=True  # ✅ 傳給模板啟用熱力圖按鈕
    )

@web_page.route("/map")
def map_page():
    return render_template("map.html", google_maps_key=GOOGLE_MAPS_API_KEY)

@web_page.route("/leaflet-map")
def leaflet_map():
    return render_template("leaflet_map.html")

@web_page.route("/api/earthquakes")
def api_earthquakes():
    query = {"lat": {"$exists": True}, "lon": {"$exists": True}}

    mag_filter = request.args.get("mag")
    place_filter = request.args.get("place")
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    if mag_filter:
        if mag_filter.startswith(">="):
            query["magnitude"] = {"$gte": float(mag_filter[2:])}
        elif mag_filter.startswith("<="):
            query["magnitude"] = {"$lte": float(mag_filter[2:])}
        elif mag_filter.startswith(">"):
            query["magnitude"] = {"$gt": float(mag_filter[1:])}
        elif mag_filter.startswith("<"):
            query["magnitude"] = {"$lt": float(mag_filter[1:])}
        elif mag_filter.startswith("="):
            query["magnitude"] = float(mag_filter[1:])

    if place_filter:
        query["epicenter"] = {"$regex": place_filter}

    if start_date or end_date:
        query["origin_time"] = {}
        if start_date:
            try:
                query["origin_time"]["$gte"] = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            except:
                pass
        if end_date:
            try:
                query["origin_time"]["$lte"] = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)
            except:
                pass

    results = collection.find(query).sort("origin_time", -1).limit(200)
    return dumps(results)
