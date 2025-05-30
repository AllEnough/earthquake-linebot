import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pymongo import MongoClient
from datetime import datetime

# 連接 MongoDB
client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
db = client["earthquake_db"]
collection = db["earthquakes"]

# 抓取最近10筆地震資料
records = list(collection.find().sort("origin_time", -1).limit(10))[::-1]  # 反轉順序：由舊到新

# 解析資料
times = [datetime.strptime(r["origin_time"], "%Y-%m-%d %H:%M:%S") for r in records]
magnitudes = [r["magnitude"] for r in records]

# 畫圖

# 嘗試加載支援中文字體（你可以根據部署環境更換字體名稱）
plt.rcParams['font.family'] = 'Noto Sans CJK TC'  # 或 Microsoft JhengHei, SimHei 等
plt.title("地震發生時間與規模")
plt.figure(figsize=(10, 5))
plt.plot(times, magnitudes, marker='o', linestyle='-', color='royalblue')
plt.title("最近10筆地震規模變化")
plt.xlabel("發生時間")
plt.ylabel("芮氏規模")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# 儲存成圖片
plt.savefig("static/chart.png")
print("✅ 圖表已儲存為 static/chart.png")
