# geocode_utils.py
import requests
import time
from logger import logger

# 用於避免重複查詢同一地名
_geocode_cache = {}

def clean_location_name(name: str) -> str:
    name = name.strip()
    # 移除「位於」開頭
    if name.startswith("位於"):
        name = name[2:]
    # 排除難以地理定位的描述
    if any(keyword in name for keyword in ["海域", "近海", "公里", "公尺", "方", "附近"]):
        return ""
    if "(" in name and ")" in name:
        try:
            return name.split("(", 1)[-1].split(")", 1)[0].strip()
        except:
            pass
    return name.strip()
    


def get_coordinates_from_text(location_name):
    """
    使用 Nominatim API 將中文地點轉換為 (lat, lon)
    """
    location_name = clean_location_name(location_name)
    location_name = location_name.replace("台", "臺")

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
        "User-Agent": "earthquake-line-bot/1.0 (your@email.com)"
    }
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                _geocode_cache[location_name] = (lat, lon)
                logger.info(f"📍 已解析地點：{location_name} → ({lat}, {lon})")
                time.sleep(1)  # 尊重 API 限速
                return lat, lon
            else:
                logger.warning(f"⚠️ 找不到地點：{location_name}")
        except Exception as e:
            logger.error(f"❌ 地理位置查詢失敗：{e}")

    _geocode_cache[location_name] = (None, None)
    return None, None
