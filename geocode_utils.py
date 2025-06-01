# geocode_utils.py
import requests
import time
from logger import logger

# 用於避免重複查詢同一地名
_geocode_cache = {}

def get_coordinates_from_text(location_name):
    if location_name in _geocode_cache:
        return _geocode_cache[location_name]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_name,
        "format": "json",
        "limit": 1,
        "accept-language": "zh-TW"
    }
    headers = {
        "User-Agent": "earthquake-line-bot/1.0 (sodiqademolaolagunju@gmail.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            _geocode_cache[location_name] = (lat, lon)
            logger.info(f"📍 已解析地點：{location_name} → ({lat}, {lon})")
            time.sleep(1)  # 避免觸發 API 限速
            return lat, lon
        else:
            logger.warning(f"⚠️ 找不到地點：{location_name}")
    except Exception as e:
        logger.error(f"❌ 地理位置查詢失敗：{e}")

    _geocode_cache[location_name] = (None, None)
    return None, None
