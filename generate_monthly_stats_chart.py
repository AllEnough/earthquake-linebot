import matplotlib.pyplot as plt
import pandas as pd
from config import db
from datetime import datetime
import os

def generate_monthly_stats_chart():
    # 取得地震資料
    cursor = db["earthquakes"].find({}, {"origin_time": 1})
    records = list(cursor)

    if not records:
        print("❌ 無地震資料可供統計")
        return

    # 轉換為 DataFrame
    df = pd.DataFrame(records)
    df['origin_time'] = pd.to_datetime(df['origin_time'], errors='coerce')
    df.dropna(subset=['origin_time'], inplace=True)

    # 取出年月統計
    df['year_month'] = df['origin_time'].dt.to_period('M')
    monthly_counts = df['year_month'].value_counts().sort_index()

    # 畫圖
    plt.figure(figsize=(10, 6))
    monthly_counts.plot(kind='bar', color='#4B9CD3')
    plt.title('每月地震次數統計')
    plt.xlabel('月份')
    plt.ylabel('地震次數')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 儲存圖片
    static_path = os.path.join("static", "monthly_chart.png")
    plt.savefig(static_path)
    plt.close()
    print(f"✅ 圖表已儲存至 {static_path}")
