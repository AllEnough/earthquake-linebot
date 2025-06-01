import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from pymongo import MongoClient
from datetime import datetime, UTC, timedelta
import pandas as pd
import folium
from folium.plugins import HeatMap
from pmdarima import auto_arima
import os

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

    end_date = datetime.now(UTC)
    start_date = end_date - timedelta(days=days)

    # 初始化每天的計數器
    date_counts = {}
    for i in range(days):
        date = (start_date + timedelta(days=i)).date()
        date_counts[date] = 0

    # MongoDB 連線
    client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
    db = client["earthquake_db"]

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

def generate_avg_magnitude_chart(output_path="static/chart_avg_magnitude.png", days=7):
    print("📊 產生每日平均地震規模圖中...")

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

def generate_max_magnitude_chart(output_path="static/chart_max_magnitude.png", days=7):
    print("📊 產生每日最大地震規模圖中...")

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

def generate_earthquake_heatmap_folium(output_path='static/heatmap.html', days=7):
    print("🗺️ 使用 folium 產生地震熱區 HTML 地圖...")

    # MongoDB 連線
    client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
    db = client["earthquake_db"]

    cutoff_date = datetime.now(UTC) - timedelta(days=days)
    earthquakes = db["earthquakes"].find(
        {"origin_time": {"$gte": cutoff_date}},
        {"latitude": 1, "longitude": 1, "magnitude": 1}
    )

    quake_points = []
    for eq in earthquakes:
        try:
            lat = float(eq["latitude"])
            lon = float(eq["longitude"])
            mag = float(eq["magnitude"])
            quake_points.append([lat, lon, mag])
        except:
            continue

    if not quake_points:
        print("⚠️ 沒有足夠地震資料")
        return

    # 建立地圖（以台灣為中心）
    m = folium.Map(location=[23.5, 121], zoom_start=6)

    # 加上熱區圖層
    HeatMap(quake_points, radius=15, blur=10, max_zoom=13).add_to(m)

    # 儲存地圖 HTML
    os.makedirs("static", exist_ok=True)
    m.save(output_path)
    print(f"✅ 熱區地圖儲存完成：{output_path}")

def forecast_magnitude_and_plot(n_periods=5, save_path="static/forecast_magnitude.png"):
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