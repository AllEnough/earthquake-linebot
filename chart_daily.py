# chart_daily.py
from datetime import datetime, UTC, timedelta
import matplotlib.pyplot as plt
import os

from config import db
from logger import logger

def generate_daily_count_chart(days=7, output_path="static/chart_daily_count.png"):
    logger.info("📊 產生每日地震次數統計圖中...")

    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)
    date_counts = {(start_date + timedelta(days=i)).date(): 0 for i in range(days)}

    results = db["earthquakes"].find({"origin_time": {"$gte": start_date}})
    for quake in results:
        origin_time = quake.get("origin_time")
        if isinstance(origin_time, datetime):
            date = origin_time.date()
            if date in date_counts:
                date_counts[date] += 1

    plt.figure(figsize=(10, 4))
    plt.plot(list(date_counts.keys()), list(date_counts.values()), marker='o', linestyle='-', color='blue')
    plt.title("Daily Earthquake Count")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.grid(True)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 圖表已儲存為：{output_path}")
