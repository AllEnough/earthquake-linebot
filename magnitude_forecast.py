import pandas as pd
from pymongo import MongoClient
from pmdarima import auto_arima
import matplotlib.pyplot as plt
import os

# Step 1: MongoDB 連線與資料讀取
client = MongoClient("你的 MongoDB 連線字串")
db = client["你的資料庫"]
collection = db["earthquakes"]

def forecast_magnitude_and_plot(n_periods=5, save_path="static/forecast_magnitude.png"):
    # 1. 讀取資料
    cursor = collection.find({}, {"origin_time": 1, "magnitude": 1, "_id": 0})
    df = pd.DataFrame(list(cursor))
    if df.empty:
        return [], None

    # 2. 前處理
    df["origin_time"] = pd.to_datetime(df["origin_time"], errors='coerce')
    df = df.dropna(subset=["origin_time", "magnitude"])
    df = df.sort_values("origin_time").set_index("origin_time")

    # 3. 模型訓練與預測
    try:
        model = auto_arima(df["magnitude"], seasonal=False, suppress_warnings=True)
        forecast = model.predict(n_periods=n_periods)

        # 4. 畫圖
        plt.figure(figsize=(10, 5))
        df["magnitude"].plot(label="歷史資料")
        forecast_index = pd.date_range(df.index[-1], periods=n_periods + 1, freq='D')[1:]
        pd.Series(forecast, index=forecast_index).plot(label="預測", linestyle="--")
        plt.title("地震規模預測")
        plt.xlabel("時間")
        plt.ylabel("芮氏規模")
        plt.legend()
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        return forecast.tolist(), save_path
    except Exception as e:
        print("❌ 預測錯誤：", e)
        return [], None