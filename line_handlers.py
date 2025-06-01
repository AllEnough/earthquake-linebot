# line_handlers.py
from linebot.v3.messaging.models import TextMessage, ImageMessage
from datetime import datetime, UTC
import re
from os import getenv

from chart_daily import generate_daily_count_chart
from chart_avg import generate_avg_magnitude_chart
from chart_max import generate_max_magnitude_chart
from quake_forecast import generate_forecast_chart
from hotspot_map import generate_epicenter_heatmap
from epicenter_cluster import generate_epicenter_cluster_chart
from quake_summary import get_text_summary
from config import db

DOMAIN = getenv("DOMAIN", "https://your-domain")


def handle_query_help():
    text = (
        "🤖 地震查詢機器人使用說明：\n"
        "\n🔍 基本查詢（快速）：\n"
        "🔹 輸入「地震 花蓮」➡️ 查詢震央包含『花蓮』的地震\n"
        "🔹 輸入「地震 >5」➡️ 查詢規模大於 5 的地震\n"
        "\n📅 進階查詢（支援條件）：\n"
        "🔹 輸入「查詢 花蓮」➡️ 查詢花蓮所有地震紀錄（近 50 筆）\n"
        "🔹 輸入「查詢 花蓮 2024-05-01 2024-05-31」➡️ 查詢時間區間地震\n"
        "\n📊 圖表查詢：\n"
        "🔹 「地震統計圖」➡️ 每日次數圖\n"
        "🔹 「地震平均規模圖」\n"
        "🔹 「地震最大規模圖」\n"
        "🔹 「地震預測圖」➡️ AI 模型預測最大規模\n"
        "🔹 「地震熱區圖」➡️ 震央熱力分布圖\n"
        "🔹 「震央群聚圖」➡️ AI 群聚分析圖\n"
        "\n📝 文字報告：\n"
        "🔹 「地震摘要」➡️ 一週地震活動總結\n"
    )
    return [TextMessage(text=text)]


def handle_query_latest():
    latest = db["earthquakes"].find_one(sort=[("origin_time", -1)])
    if latest:
        text = (
            f"📍 最新地震資訊：\n"
            f"時間：{latest.get('origin_time', '未知')}\n"
            f"震央：{latest.get('epicenter', '未知')}\n"
            f"深度：{latest.get('depth', '未知')} 公里\n"
            f"規模：芮氏 {latest.get('magnitude', '未知')}"
        )
    else:
        text = "⚠️ 查無最新地震資料。"
    return [TextMessage(text=text)]


def handle_chart_daily():
    generate_daily_count_chart()
    url = f"{DOMAIN}/static/chart_daily_count.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_chart_avg():
    generate_avg_magnitude_chart()
    url = f"{DOMAIN}/static/chart_avg_magnitude.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_chart_max():
    generate_max_magnitude_chart()
    url = f"{DOMAIN}/static/chart_max_magnitude.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_chart_forecast():
    generate_forecast_chart()
    url = f"{DOMAIN}/static/chart_predict.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_chart_heatmap():
    generate_epicenter_heatmap()
    url = f"{DOMAIN}/static/heatmap.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_chart_cluster():
    generate_epicenter_cluster_chart()
    url = f"{DOMAIN}/static/epicenter_clusters.png"
    return [ImageMessage(original_content_url=url, preview_image_url=url)]


def handle_summary_text():
    summary = get_text_summary(days=7)
    return [TextMessage(text=summary)]


def handle_query_custom(user_message):
    pattern_mag = re.match(r"地震\s*([><=])\s*(\d+(\.\d+)?)", user_message)
    pattern_epicenter = re.match(r"地震\s+(.+)", user_message)

    query = {}
    if pattern_mag:
        op, value = pattern_mag.group(1), float(pattern_mag.group(2))
        if op == ">":
            query["magnitude"] = {"$gt": value}
        elif op == "<":
            query["magnitude"] = {"$lt": value}
        elif op == "=":
            query["magnitude"] = value
    elif pattern_epicenter:
        keyword = pattern_epicenter.group(1)
        query["epicenter"] = {"$regex": keyword}

    results = list(db["earthquakes"].find(query).sort("origin_time", -1).limit(5))
    if not results:
        return [TextMessage(text="⚠️ 查無符合條件的地震資料。")]


    messages = []
    for quake in results:
        text = (
            f"📍 地震紀錄：\n"
            f"時間：{quake.get('origin_time')}\n"
            f"震央：{quake.get('epicenter')}\n"
            f"深度：{quake.get('depth')} 公里\n"
            f"規模：芮氏 {quake.get('magnitude')}\n"
        )
        messages.append(TextMessage(text=text))
    return messages


def handle_query_advanced(user_message):
    parts = user_message.strip().split()

    if len(parts) == 2:
        location = parts[1]
        query = {"epicenter": {"$regex": location}}
    elif len(parts) == 4:
        location = parts[1]
        start_date = parts[2]
        end_date = parts[3]
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)
            query = {
                "epicenter": {"$regex": location},
                "origin_time": {"$gte": start, "$lte": end}
            }
        except:
            return [TextMessage(text="⚠️ 日期格式錯誤，請使用 YYYY-MM-DD")]
    else:
        return [TextMessage(text="⚠️ 請使用格式：\n查詢 [地點]\n或\n查詢 [地點] [起始日] [結束日]")]

    results = list(db["earthquakes"].find(query).sort("origin_time", -1).limit(5))
    if not results:
        return [TextMessage(text="⚠️ 查無符合條件的地震資料。")]

    messages = []
    for quake in results:
        messages.append(TextMessage(text=(
            f"📍 地震紀錄：\n"
            f"時間：{quake.get('origin_time')}\n"
            f"震央：{quake.get('epicenter')}\n"
            f"深度：{quake.get('depth')} 公里\n"
            f"規模：芮氏 {quake.get('magnitude')}\n"
        )))
    return messages


def handle_unknown():
    return [TextMessage(text="⚠️ 無法識別的指令，請輸入「幫助」查看使用說明。")]
