# quake_summary.py
from datetime import datetime, timedelta, UTC
from database import get_earthquake_collection
from collections import Counter
from logger import logger

# ✅ 地震資料集合
collection = get_earthquake_collection()

def get_text_summary(days=7):
    logger.info("📝 正在產生地震摘要文字...")

    start_time = datetime.now(UTC) - timedelta(days=days)
    cursor = collection.find({"origin_time": {"$gte": start_time}})

    total = 0
    magnitudes = []
    epicenters = []
    max_quake = None

    for quake in cursor:
        try:
            total += 1
            mag = float(quake.get("magnitude", 0))
            magnitudes.append(mag)
            epicenter = quake.get("epicenter", "")
            if epicenter:
                epicenters.append(epicenter)

            if not max_quake or mag > max_quake["magnitude"]:
                max_quake = {
                    "magnitude": mag,
                    "origin_time": quake.get("origin_time"),
                    "epicenter": epicenter
                }
        except Exception as e:
            continue

    if total == 0:
        return f"在過去 {days} 天內，查無地震資料。"

    # 統計規模區間
    low = sum(1 for m in magnitudes if m < 3)
    mid = sum(1 for m in magnitudes if 3 <= m < 5)
    high = sum(1 for m in magnitudes if m >= 5)

    # 統計最常發生的震央
    epicenter_count = Counter(epicenters)
    most_common_epicenter, count = epicenter_count.most_common(1)[0]

    # 組裝報告文字
    max_text = (
        f"最大地震規模為 {max_quake['magnitude']}，"
        f"發生於 {max_quake['origin_time'].strftime('%m月%d日 %H:%M')}，"
        f"震央位於 {max_quake['epicenter']}。"
    )

    summary = (
        f"📊 在過去 {days} 天內，台灣共發生 {total} 起地震。\n"
        f"{max_text}\n"
        f"其中規模 3 級以下有 {low} 起，3～5 級有 {mid} 起，5 級以上有 {high} 起。\n"
        f"震央最常出現在「{most_common_epicenter}」（共 {count} 次）。"
    )

    return summary
