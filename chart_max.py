# chart_max.py
from datetime import datetime, UTC
import matplotlib.pyplot as plt
import pandas as pd
import os

from config import db
from font_utils import use_custom_font_from_file
from logger import logger


def generate_max_magnitude_chart(output_path="static/chart_max_magnitude.png", days=7):
    logger.info("📊 產生每日最大地震規模圖中...")
    use_custom_font_from_file()

    earthquakes = db["earthquakes"].find(
        {"origin_time": {"$exists": True, "$ne": None}},
        {"origin_time": 1, "magnitude": 1}
    )

    data = []
    for eq in earthquakes:
        try:
            origin_time = eq["origin_time"]
            magnitude = float(eq["magnitude"])
            if isinstance(origin_time, datetime):
                date = origin_time.date()
                data.append({"date": date, "magnitude": magnitude})
        except:
            continue

    if not data:
        logger.warning("⚠️ 沒有地震資料可繪圖")
        return

    df = pd.DataFrame(data)
    max_per_day = df.groupby("date").max().reset_index()
    max_per_day = max_per_day.sort_values("date").tail(days)

    plt.figure(figsize=(10, 5))
    plt.plot(
        max_per_day["date"],
        max_per_day["magnitude"],
        marker='s',
        color='green'
    )
    plt.title("Max Magnitude")
    plt.xlabel("Date")
    plt.ylabel("Magnitude")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 圖表已儲存：{output_path}")
