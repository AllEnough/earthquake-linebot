# quake_forecast.py
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, UTC
import os

from database import get_earthquake_collection
from font_utils import use_custom_font_from_file
from logger import logger

from pmdarima import auto_arima

def generate_forecast_chart(days=30, predict_days=3, output_path="static/chart_predict.png"):
    logger.info("🤖 開始訓練 ARIMA 模型進行地震規模預測...")
    use_custom_font_from_file()

    collection = get_earthquake_collection()
    data = []

    cursor = collection.find(
        {"origin_time": {"$exists": True}},
        {"origin_time": 1, "magnitude": 1}
    )

    for doc in cursor:
        try:
            origin_time = doc["origin_time"]
            magnitude = float(doc["magnitude"])
            if isinstance(origin_time, datetime):
                date = origin_time.date()
                data.append({"date": date, "magnitude": magnitude})
        except:
            continue

    if not data:
        logger.warning("⚠️ 無地震資料可訓練預測模型")
        return

    df = pd.DataFrame(data)
    df_grouped = df.groupby("date").max().sort_index()
    df_grouped = df_grouped.tail(days)

    if len(df_grouped) < 10:
        logger.warning("⚠️ 資料太少，無法進行預測")
        return

    series = df_grouped["magnitude"]

    model = auto_arima(series, seasonal=False, suppress_warnings=True)
    forecast = model.predict(n_periods=predict_days)

    future_dates = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=predict_days)

    # 畫圖
    plt.figure(figsize=(10, 5))
    plt.plot(series.index, series.values, label="實際最大規模", marker='o')
    plt.plot(future_dates, forecast, label="預測最大規模", marker='x', linestyle='--')
    plt.title("每日最大地震規模預測")
    plt.xlabel("日期")
    plt.ylabel("地震規模")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 地震預測圖已儲存：{output_path}")
