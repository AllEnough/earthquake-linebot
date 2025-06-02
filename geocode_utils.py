import requests
import time
import os
from logger import logger

# 用於避免重複查詢同一地名
_geocode_cache = {}

def clean_location_name(name: str) -> str:
    name = name.strip()
    if name.startswith("位於"):
        name = name[2:]
    if any(keyword in name for keyword in ["海域", "近海", "公里", "公尺", "方", "附近"]):
        return ""
    if "(" in name and ")" in name:
        try:
            inside = name.split("(", 1)[-1].split(")", 1)[0].strip()
            if inside.startswith("位於"):
                name = inside[2:]
        except:
            pass
    return name.strip()

manual_fix = {
    "花蓮縣近海": (23.8, 121.6),
    "臺灣東部海域": (24.0, 122.2),
    "臺灣東南部海域": (22.5, 122.0),
    "花蓮縣秀林鄉": (24.1, 121.6),
    "屏東縣三地門鄉": (22.8, 120.7),
    "高雄市那瑪夏區": (23.3, 120.8),
    "臺東縣海端鄉": (23.0, 121.1),
    "苗栗縣南庄鄉": (24.6, 121.0),
    "臺南市東山區": (23.3, 120.5),
    "宜蘭縣宜蘭市": (24.75, 121.75),
    "嘉義縣大埔鄉": (23.3, 120.6)
}

def get_coordinates_from_text(location_name):
    location_name = clean_location_name(location_name)
    location_name = location_name.replace("台", "臺")

    if not location_name:
        return None, None

    if location_name in manual_fix:
        lat, lon = manual_fix[location_name]
        logger.info(f"📍 已從補丁表解析地點：{location_name} → ({lat}, {lon})")
        return lat, lon

    if location_name in _geocode_cache:
        return _geocode_cache[location_name]

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("⚠️ 缺少 GOOGLE_MAPS_API_KEY")
        return None, None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "language": "zh-TW",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            location = result["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            _geocode_cache[location_name] = (lat, lon)
            logger.info(f"📍 已解析地點（Google）：{location_name} → ({lat}, {lon})")
            return lat, lon
        else:
            logger.warning(f"⚠️ Google Geocoding 無結果：{location_name} - {data.get('status')}")
    except Exception as e:
        logger.error(f"❌ Google Geocoding 錯誤：{e}")

    _geocode_cache[location_name] = (None, None)
    return None, None
