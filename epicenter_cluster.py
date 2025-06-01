# epicenter_cluster.py
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime, timedelta, UTC
import os

from database import get_earthquake_collection
from font_utils import set_chinese_font
from logger import logger


def generate_epicenter_cluster_chart(days=30, k=4, output_path="static/epicenter_clusters.png"):
    logger.info("🔬 開始進行震央群聚分析...")
    set_chinese_font()

    collection = get_earthquake_collection()
    start_time = datetime.now(UTC) - timedelta(days=days)

    lats, lons = [], []
    for doc in collection.find({"origin_time": {"$gte": start_time}}):
        report = doc.get("report", "")
        try:
            if "北緯" in report and "東經" in report:
                lat = float(report.split("北緯")[1].split("度")[0])
                lon = float(report.split("東經")[1].split("度")[0])
                lats.append(lat)
                lons.append(lon)
        except Exception:
            continue

    if len(lats) < k:
        logger.warning("⚠️ 資料不足，無法進行群聚分析")
        return

    coords = np.array(list(zip(lats, lons)))
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(coords)
    centers = kmeans.cluster_centers_

    # 畫圖
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(lons, lats, c=labels, cmap='tab10', s=40, alpha=0.7)
    plt.scatter(centers[:,1], centers[:,0], c='red', marker='X', s=200, label='群聚中心')
    plt.xlabel("經度")
    plt.ylabel("緯度")
    plt.title(f"台灣近 {days} 天震央聚類分析 (KMeans k={k})")
    plt.legend()
    plt.grid(True)

    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"✅ 群聚分析圖已儲存：{output_path}")
