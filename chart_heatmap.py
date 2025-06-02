# chart_heatmap.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from config import db
from logger import logger

def generate_heatmap_chart(output_path="static/heatmap.png"):
    logger.info("🔥 產生震央熱區圖中...")

    cursor = db["earthquakes"].find({"lat": {"$exists": True}, "lon": {"$exists": True}})
    data = [{"lat": q["lat"], "lon": q["lon"]} for q in cursor if isinstance(q.get("lat"), float) and isinstance(q.get("lon"), float)]

    if not data:
        logger.warning("⚠️ 無資料可產生熱區圖")
        return

    df = pd.DataFrame(data)
    plt.figure(figsize=(8, 6))
    sns.kdeplot(x=df["lon"], y=df["lat"], fill=True, cmap="Reds", bw_adjust=0.5)
    plt.title("Earthquake Heatmap")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 熱區圖儲存成功：{output_path}")

