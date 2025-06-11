# line_handlers.py
from linebot.v3.messaging.models import TextMessage, ImageMessage
from datetime import datetime, UTC
import re
from os import getenv

from config import db, DOMAIN

from chart_daily import generate_daily_count_chart
from chart_avg import generate_avg_magnitude_chart
from chart_max import generate_max_magnitude_chart
from quake_forecast import generate_forecast_chart
from quake_summary import get_text_summary
from quake_map import generate_static_map
from quake_map import generate_static_map
from text_utils import normalize_tai


def handle_query_help():
    text = (
        "🤖 地震查詢機器人使用說明：\n"
        "\n🔍 基本查詢：\n"
        "🔹 輸入「地震 花蓮」➡️ 查詢震央包含『花蓮』的地震\n"
        "🔹 輸入「地震 >5」➡️ 查詢規模大於 5 的地震\n"
        "🔹 輸入「地震 花蓮 >5」➡️ 同時篩選地點與規模\n"
        "🔹 輸入「地震 花蓮 2024-05-01 2024-05-31」➡️ 查詢指定日期區間\n"
        "🔹 輸入「最新」➡️ 查詢最新的一筆地震資料\n"
        "\n📊 圖表查詢：\n"
        "🔹 「地震統計圖」➡️ 每日次數圖\n"
        "🔹 「地震平均規模圖」\n"
        "🔹 「地震最大規模圖」\n"
        "🔹 「地震預測圖」➡️ AI 模型預測最大規模\n"
        "\n📝 文字報告：\n"
        "🔹 「地震摘要」➡️ 一週地震活動總結\n"
    )
    return [TextMessage(text=text)]


def handle_query_latest():
    latest = db["earthquakes"].find_one(sort=[("origin_time", -1)])
    messages = []
    if latest:
        text = (
            f"📍 最新地震資訊：\n"
            f"時間：{latest.get('origin_time', '未知')}\n"
            f"震央：{latest.get('epicenter', '未知')}\n"
            f"深度：{latest.get('depth', '未知')} 公里\n"
            f"規模：芮氏 {latest.get('magnitude', '未知')}"
        )
        messages.append(TextMessage(text=text))
        if latest.get("lat") and latest.get("lon"):
            map_path = generate_static_map(latest["lat"], latest["lon"])
            if map_path:
                url = f"{DOMAIN}/static/map_latest.png"
                messages.append(ImageMessage(original_content_url=url, preview_image_url=url))
    else:
        messages.append(TextMessage(text="⚠️ 查無最新地震資料。"))
    return messages



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

def handle_summary_text():
    summary = get_text_summary(days=7)
    return [TextMessage(text=summary)]


def _query_and_format(query, limit=5):
    """Fetch earthquakes by query and format as TextMessage list."""
    results = list(db["earthquakes"].find(query).sort("origin_time", -1).limit(limit))
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



def handle_query_custom(user_message):
    # 支援查詢格式：
    # 1. 地震 >5
    # 2. 地震 宜蘭
    # 3. 地震 宜蘭 >5
    # 4. 地震 宜蘭 2024-05-01 2024-05-31

    # 地震 宜蘭 >5
    pattern_loc_mag = re.match(
        r"地震\s+([^><=]+?)\s*([><=])\s*(\d+(?:\.\d+)?)$", user_message
    )
    # 地震 >5
    pattern_mag = re.match(r"地震\s*([><=])\s*(\d+(?:\.\d+)?)$", user_message)
    # 地震 宜蘭 2024-05-01 2024-05-31
    pattern_loc_dates = re.match(
        r"地震\s+([^\s]+)\s+(\d{4}-\d{2}-\d{2})\s+(\d{4}-\d{2}-\d{2})$",
        user_message,
    )
    # 地震 宜蘭
    pattern_epicenter = re.match(r"地震\s+(.+)$", user_message)

    query = {}
    if pattern_loc_dates:
        location = normalize_tai(pattern_loc_dates.group(1))
        start_date = pattern_loc_dates.group(2)
        end_date = pattern_loc_dates.group(3)
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)
        except Exception:
            return [TextMessage(text="⚠️ 日期格式錯誤，請使用 YYYY-MM-DD")]
        query = {
            "epicenter": {"$regex": location},
            "origin_time": {"$gte": start, "$lte": end},
        }
    elif pattern_loc_mag:
        location = normalize_tai(pattern_loc_mag.group(1).strip())
        op = pattern_loc_mag.group(2)
        value = float(pattern_loc_mag.group(3))
        query["epicenter"] = {"$regex": location}
        if op == ">":
            query["magnitude"] = {"$gt": value}
        elif op == "<":
            query["magnitude"] = {"$lt": value}
        elif op == "=":
            query["magnitude"] = value
    elif pattern_mag:
        op, value = pattern_mag.group(1), float(pattern_mag.group(2))
        if op == ">":
            query["magnitude"] = {"$gt": value}
        elif op == "<":
            query["magnitude"] = {"$lt": value}
        elif op == "=":
            query["magnitude"] = value
    elif pattern_epicenter:
        keyword = normalize_tai(pattern_epicenter.group(1).strip())
        query["epicenter"] = {"$regex": keyword}

    return _query_and_format(query)


def handle_query_advanced(user_message):
    parts = user_message.strip().split()

    if len(parts) == 2:
        location = normalize_tai(parts[1])
        query = {"epicenter": {"$regex": location}}
    elif len(parts) == 4:
        location = normalize_tai(parts[1])
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

    return _query_and_format(query)


def handle_unknown():
    return [TextMessage(text="⚠️ 無法識別的指令，請輸入「幫助」查看使用說明。")]
