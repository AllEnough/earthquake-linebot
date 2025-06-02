# web_page.py
from flask import Blueprint, render_template, request
from database import get_earthquake_collection
from datetime import datetime, UTC
from quake_summary import get_text_summary

web_page = Blueprint('web_page', __name__)
collection = get_earthquake_collection()

@web_page.route('/')
def index():
    keyword = request.args.get('keyword', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    query = {}

    # 地區選單用：抓出所有已知震央文字
    all_epicenters = collection.distinct("epicenter")

    # 條件組合查詢
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

    # 查詢地震資料（最多 50 筆）
    quakes = collection.find(query).sort('origin_time', -1).limit(50)

    # 產生 7 日摘要
    summary = get_text_summary(7)

    # LINE Bot 使用說明（可用於首頁或 help.html）
    line_help = """
🤖 LINE 地震查詢機器人使用說明：

🔍 基本查詢（快速）：
🔹 輸入「地震 花蓮」➡️ 查詢震央包含『花蓮』的地震
🔹 輸入「地震 >5」➡️ 查詢規模大於 5 的地震

📅 進階查詢（條件）：
🔹 「查詢 花蓮」➡️ 查詢花蓮地震紀錄（近 50 筆）
🔹 「查詢 花蓮 2024-05-01 2024-05-31」➡️ 查詢時間區間地震

📊 圖表查詢：
🔹 「地震統計圖」\n🔹 「地震平均規模圖」\n🔹 「地震最大規模圖」
🔹 「地震預測圖」\n🔹 「地震熱區圖」\n🔹 「震央群聚圖」

📝 文字報告：
🔹 「地震摘要」➡️ 一週地震活動總結
"""

    return render_template(
        'index.html',
        quakes=quakes,
        keyword=keyword,
        start_date=start_date_str,
        end_date=end_date_str,
        all_epicenters=sorted(all_epicenters),
        summary=summary,
        line_help=line_help,
        cluster_chart_url="/static/epicenter_clusters.png",
        heatmap_chart_url="/static/heatmap.png"
    )

