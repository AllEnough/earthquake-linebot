import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pymongo import MongoClient
from datetime import datetime
import os

# 1. 中文字體支援：指定 Noto Sans CJK TC 字體（你可以換成其他字體）
# 若 Railway 沒安裝中文字型，請將字型檔案放入 fonts 目錄
font_path = "fonts/static/NotoSansTC-Regular.ttf"
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    # Fallback（系統內建中文字體）
    plt.rcParams['font.family'] = 'Microsoft JhengHei'

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
plt.figure(figsize=(10, 5))
plt.plot(times, magnitudes, marker='o', linestyle='-', color='royalblue')
plt.title("最近10筆地震規模變化")
plt.xlabel("發生時間")
plt.ylabel("芮氏規模")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# 儲存成圖片
os.makedirs("static", exist_ok=True)
plt.savefig("static/chart.png")
print("✅ 圖表已儲存為 static/chart.png")
