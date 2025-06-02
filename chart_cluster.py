# chart_cluster.py
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
import os
from config import db
from logger import logger

def generate_epicenter_cluster_chart(output_path="static/epicenter_clusters.png", clusters=5):
    logger.info("📍 產生震央群聚圖中...")

    cursor = db["earthquakes"].find({"lat": {"$exists": True}, "lon": {"$exists": True}})
    data = [{"lat": q["lat"], "lon": q["lon"]} for q in cursor if isinstance(q.get("lat"), float) and isinstance(q.get("lon"), float)]

    if len(data) < clusters:
        logger.warning("⚠️ 資料過少，無法進行群聚分析")
        return

    df = pd.DataFrame(data)
    kmeans = KMeans(n_clusters=clusters, n_init="auto")
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    plt.figure(figsize=(8, 6))
    for i in range(clusters):
        cluster_data = df[df["cluster"] == i]
        plt.scatter(cluster_data["lon"], cluster_data["lat"], label=f"Cluster {i}")
    plt.title("Epicenter Clusters")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    logger.info(f"✅ 群聚圖儲存成功：{output_path}")
