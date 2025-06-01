# hotspot_map.py
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, UTC
import numpy as np
import os

from mpl_toolkits.basemap import Basemap
from database import get_earthquake_collection
from font_utils import use_custom_font_from_file
from logger import logger

def generate_epicenter_heatmap(days=30, output_path="static/heatmap.png"):
    logger.info("📍 開始產生震央熱區圖...")
    use_custom_font_from_file()

    collection = get_earthquake_collection()
    start_time = datetime.now(UTC) - timedelta(days=days)
    cursor = collection.find({"origin_time": {"$gte": start_time}})

    lats = []
    lons = []

    for doc in cursor:
        report = doc.get("report", "")
        try:
            if "北緯" in report and "東經" in report:
                lat_str = report.split("北緯")[1].split("度")[0]
                lon_str = report.split("東經")[1].split("度")[0]
                lat = float(lat_str)
                lon = float(lon_str)
                lats.append(lat)
                lons.append(lon)
        except Exception:
            continue

    if not lats or not lons:
        logger.warning("⚠️ 沒有足夠的震央座標資料")
        return

    fig = plt.figure(figsize=(10, 8))
    m = Basemap(projection='merc',
                llcrnrlat=21.5, urcrnrlat=25.5,
                llcrnrlon=119.5, urcrnrlon=122.5,
                resolution='i')

    m.drawcoastlines()
    m.drawcountries()
    m.drawmapboundary()
    m.drawparallels(np.arange(21.5, 26, 1), labels=[1,0,0,0])
    m.drawmeridians(np.arange(119.5, 123, 1), labels=[0,0,0,1])

    x, y = m(lons, lats)
    sns.kdeplot(x=x, y=y, shade=True, cmap="Reds", bw_adjust=0.5, alpha=0.6, thresh=0.05)

    plt.title("台灣近 30 天地震震央熱區分布")
    os.makedirs("static", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"✅ 熱區圖已儲存：{output_path}")
