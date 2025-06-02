# quake_map.py
import os
import requests

from logger import logger

def generate_static_map(lat, lon, output_path="static/map_latest.png", zoom=7):
    """
    使用 Google Maps Static API 產生震央靜態地圖圖片
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("\u26a0\ufe0f 缺少 GOOGLE_MAPS_API_KEY")
        return None

    url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lon}&zoom={zoom}&size=600x400&maptype=roadmap"
        f"&markers=color:red%7Clabel:E%7C{lat},{lon}"
        f"&key={api_key}"
    )

    try:
        os.makedirs("static", exist_ok=True)
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            logger.info(f"\u2705 地圖圖片已儲存：{output_path}")
            return output_path
        else:
            logger.error(f"\u274c 地圖圖片請求失敗，狀態碼：{response.status_code}")
    except Exception as e:
        logger.error(f"\u274c 地圖圖片產生錯誤：{e}")

    return None
