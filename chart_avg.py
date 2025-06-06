# chart_avg.py
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

from config import db
from logger import logger
from earthquake_analysis import fix_origin_time_format


def generate_avg_magnitude_chart(output_path="static/chart_avg_magnitude.png", days=7):
    logger.info("📊 產生每日平均地震規模圖中...")
    fix_origin_time_format()

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
    avg_per_day = df.groupby("date").mean().reset_index()
    avg_per_day = avg_per_day.sort_values("date").tail(days)

    plt.figure(figsize=(10, 5))
    plt.plot(avg_per_day["date"], avg_per_day["magnitude"], marker='o', color='tomato')
    plt.title("Average Magnitude")
    plt.xlabel("Date")
    plt.ylabel("Magnitude")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 圖表已儲存：{output_path}")
