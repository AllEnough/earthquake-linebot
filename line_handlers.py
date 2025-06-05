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
from geocode_utils import get_coordinates_from_text


DOMAIN = getenv("DOMAIN", "https://your-domain")


def handle_query_help():
    text = (
        "🤖 地震查詢機器人使用說明：\n"
        "\n🔍 基本查詢（快速）：\n"
        "🔹 輸入「地震 花蓮」➡️ 查詢震央包含『花蓮』的地震\n"
        "🔹 輸入「地震 >5」➡️ 查詢規模大於 5 的地震\n"
        "🔹 輸入「最新」➡️ 查詢最新的一筆地震資料\n"
        "\n📅 進階查詢（支援條件）：\n"
        "🔹 輸入「查詢 花蓮」➡️ 查詢花蓮所有地震紀錄（近 50 筆）\n"
        "🔹 輸入「查詢 花蓮 2024-05-01 2024-05-31」➡️ 查詢時間區間地震\n"
        "\n📊 圖表查詢：\n"
        "🔹 「地震統計圖」➡️ 每日次數圖\n"
        "🔹 「地震平均規模圖」\n"
        "🔹 「地震最大規模圖」\n"
        "🔹 「地震預測圖」➡️ AI 模型預測最大規模\n"
        "\n📝 文字報告：\n"
        "🔹 「地震摘要」➡️ 一週地震活動總結\n"
        "\n⚙️ 推播設定：\n"
        "🔹 「推播條件 [震度] [地區]」➡️ 自訂地震推播條件\n"
        "🔹 「所在區域 [地點]」➡️ 設定個人位置以篩選推播\n"
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


def handle_summary_text():
    summary = get_text_summary(days=7)
    return [TextMessage(text=summary)]


def handle_summary_text():
    summary = get_text_summary(days=7)
    return [TextMessage(text=summary)]


def handle_location_settings(user_id, user_message):
    parts = user_message.strip().split(maxsplit=1)
    if len(parts) == 1:
        user = db["users"].find_one({"user_id": user_id})
        if not user or user.get("home_lat") is None or user.get("home_lon") is None:
            return [TextMessage(text="⚠️ 尚未設定所在區域。使用：所在區域 [地點]")]
        lat = user.get("home_lat")
        lon = user.get("home_lon")
        return [TextMessage(text=f"📌 目前所在區域：{lat}, {lon}")]

    if parts[1] in ["取消", "重置"]:
        db["users"].update_one({"user_id": user_id}, {"$set": {"home_lat": None, "home_lon": None}})
        return [TextMessage(text="✅ 已取消所在區域設定")]

    location = parts[1].strip()
    lat, lon = get_coordinates_from_text(location)
    if lat is None or lon is None:
        return [TextMessage(text="⚠️ 無法解析地點，請嘗試更精確的地址")]
    db["users"].update_one({"user_id": user_id}, {"$set": {"home_lat": lat, "home_lon": lon}})
    return [TextMessage(text="✅ 已更新所在區域")]


def handle_push_settings(user_id, user_message):
    parts = user_message.strip().split()

    if len(parts) == 1:
        user = db["users"].find_one({"user_id": user_id})
        if not user:
            return [TextMessage(text="⚠️ 無法取得使用者資料。")]
        mag = user.get("magnitude_threshold")
        loc = user.get("location_filter")
        text = "📌 目前推播條件：\n"
        if mag is not None:
            text += f"震度門檻：{mag}\n"
        if loc:
            text += f"地區關鍵字：{loc}\n"
        if mag is None and not loc:
            text += "無（接收所有地震通知）"
        return [TextMessage(text=text)]

    if len(parts) >= 2 and parts[1] in ["取消", "重置"]:
        db["users"].update_one(
            {"user_id": user_id},
            {"$set": {"magnitude_threshold": None, "location_filter": None}},
        )
        return [TextMessage(text="✅ 已取消推播條件，將接收所有地震通知。")]

    mag = None
    location = None
    for p in parts[1:]:
        try:
            mag = float(p)
        except ValueError:
            location = p

    update = {}
    if mag is not None:
        update["magnitude_threshold"] = mag
    if location is not None:
        update["location_filter"] = location

    if update:
        db["users"].update_one({"user_id": user_id}, {"$set": update})
        return [TextMessage(text="✅ 推播條件已更新")]

    return [TextMessage(text="⚠️ 格式錯誤，請使用：推播條件 [震度] [地區]")]


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
