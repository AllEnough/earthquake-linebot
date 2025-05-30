def generate_chart():
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt
    from pymongo import MongoClient
    from datetime import datetime
    import os

    # 字體設定
    font_path = "fonts/static/NotoSansTC-Regular.ttf"
    if os.path.exists(font_path):
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        print(f"✅ 使用中文字體：{font_prop.get_name()}")
    else:
        plt.rcParams['font.family'] = 'sans-serif'
        print("⚠️ 找不到字體，使用預設字型")

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
