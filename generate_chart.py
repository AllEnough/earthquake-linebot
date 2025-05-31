import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, UTC, timedelta
from mpl_toolkits.basemap import Basemap
import pandas as pd
import os
from config import db

def generate_chart():
    # 字體設定
    base_dir = os.path.dirname(__file__)  # 取得當前檔案所在資料夾
    font_path = os.path.join(base_dir, "fonts/NotoSansTC-Regular.ttf")

    fm.fontManager.addfont(font_path)
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()


    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        print(f"✅ 使用中文字體：{font_prop.get_name()}")
    else:
        print("⚠️ 找不到字體：", font_path)
        plt.rcParams['font.family'] = 'sans-serif'

    # MongoDB 連線
    client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
    db = client["earthquake_db"]
    collection = db["earthquakes"]

    # 抓取資料
    records = list(collection.find().sort("origin_time", -1).limit(10))[::-1]
    times = [datetime.strptime(r["origin_time"], "%Y-%m-%d %H:%M:%S") for r in records]
    magnitudes = [r["magnitude"] for r in records]

    # 畫圖
    plt.figure(figsize=(10, 5))
    plt.plot(times, magnitudes, marker='o', linestyle='-', color='royalblue')
    plt.title("最近10筆地震規模變化")
    plt.xlabel("發生時間")
    plt.ylabel("芮氏規模")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 儲存圖表
    os.makedirs("static", exist_ok=True)
    plt.savefig("static/chart.png")
    plt.close()
    print("✅ 圖表已儲存為 static/chart.png")


def generate_daily_count_chart(days=7, output_path="static/chart_daily_count.png"):
    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    # 初始化每天的計數器
    date_counts = {}
    for i in range(days):
        date = (start_date + timedelta(days=i)).date()
        date_counts[date] = 0

    # 查詢資料
    results = db["earthquakes"].find({"origin_time": {"$gte": start_date}})
    for quake in results:
        origin_time = quake.get("origin_time")
        if origin_time:
            date = origin_time.date()
            if date in date_counts:
                date_counts[date] += 1

    # 轉換成列表
    dates = list(date_counts.keys())
    counts = list(date_counts.values())

    # 畫圖
    plt.figure(figsize=(10, 4))
    plt.plot(dates, counts, marker='o', linestyle='-', color='blue')
    plt.title("每日地震次數統計")
    plt.xlabel("日期")
    plt.ylabel("地震次數")
    plt.grid(True)
    plt.tight_layout()

    # 儲存圖片
    plt.savefig(output_path)
    plt.close()

def generate_avg_magnitude_chart(db, output_path="static/chart_avg_magnitude.png", days=7):
    print("📊 產生每日平均地震規模圖中...")

    # 取出最近 N 天的地震資料
    earthquakes = db["earthquakes"].find(
        {"origin_time": {"$exists": True, "$ne": None}},
        {"origin_time": 1, "magnitude": 1}
    )

    data = []
    for eq in earthquakes:
        if "origin_time" in eq and "magnitude" in eq:
            try:
                date = eq["origin_time"].date() if isinstance(eq["origin_time"], datetime) else datetime.fromisoformat(eq["origin_time"]).date()
                data.append({"date": date, "magnitude": float(eq["magnitude"])})
            except:
                continue

    if not data:
        print("⚠️ 沒有可用資料")
        return

    df = pd.DataFrame(data)
    avg_magnitude_per_day = df.groupby("date").mean().reset_index()
    avg_magnitude_per_day = avg_magnitude_per_day.sort_values("date").tail(days)

    # 畫圖
    plt.figure(figsize=(10, 5))
    plt.plot(avg_magnitude_per_day["date"], avg_magnitude_per_day["magnitude"], marker='o', color='tomato')
    plt.xticks(rotation=45)
    plt.title("每日地震平均規模")
    plt.xlabel("日期")
    plt.ylabel("平均規模")
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"✅ 圖表已儲存：{output_path}")

def generate_max_magnitude_chart(db, output_path="static/chart_max_magnitude.png", days=7):
    print("📊 產生每日最大地震規模圖中...")

    earthquakes = db["earthquakes"].find(
        {"origin_time": {"$exists": True, "$ne": None}},
        {"origin_time": 1, "magnitude": 1}
    )

    data = []
    for eq in earthquakes:
        try:
            date = eq["origin_time"].date() if isinstance(eq["origin_time"], datetime) else datetime.fromisoformat(eq["origin_time"]).date()
            magnitude = float(eq["magnitude"])
            data.append({"date": date, "magnitude": magnitude})
        except:
            continue

    if not data:
        print("⚠️ 沒有可用資料")
        return

    df = pd.DataFrame(data)
    max_magnitude_per_day = df.groupby("date").max().reset_index()
    max_magnitude_per_day = max_magnitude_per_day.sort_values("date").tail(days)

    plt.figure(figsize=(10, 5))
    plt.plot(max_magnitude_per_day["date"], max_magnitude_per_day["magnitude"], marker='s', color='green')
    plt.xticks(rotation=45)
    plt.title("每日最大地震規模")
    plt.xlabel("日期")
    plt.ylabel("最大規模")
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"✅ 圖表已儲存：{output_path}")

def generate_earthquake_heatmap(db, output_path="static/chart_heatmap.png", days=7):
    print("🗺️ 產生地震分布熱點圖中...")

    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    earthquakes = db["earthquakes"].find(
        {"origin_time": {"$gte": cutoff_date}},
        {"latitude": 1, "longitude": 1, "magnitude": 1}
    )

    latitudes = []
    longitudes = []
    magnitudes = []

    for eq in earthquakes:
        try:
            lat = float(eq["latitude"])
            lon = float(eq["longitude"])
            mag = float(eq["magnitude"])
            latitudes.append(lat)
            longitudes.append(lon)
            magnitudes.append(mag)
        except:
            continue

    if not latitudes:
        print("⚠️ 沒有足夠地震資料")
        return

    plt.figure(figsize=(10, 8))
    m = Basemap(projection='merc', llcrnrlat=20, urcrnrlat=26, llcrnrlon=119, urcrnrlon=123.5, resolution='i')
    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='beige', lake_color='lightblue')
    m.drawparallels(range(20, 27, 1), labels=[1,0,0,0])
    m.drawmeridians(range(119, 125, 1), labels=[0,0,0,1])

    x, y = m(longitudes, latitudes)
    scatter = m.scatter(x, y, c=magnitudes, cmap='Reds', alpha=0.7, edgecolors='k', s=[m**2 for m in magnitudes])

    plt.colorbar(scatter, label='Magnitude')
    plt.title("地震熱區分布圖（近一週）")
    plt.tight_layout()
    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"✅ 熱區圖儲存完成：{output_path}")