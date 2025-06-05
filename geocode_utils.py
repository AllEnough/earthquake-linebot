import requests
import os
from logger import logger

try:
    from database import get_location_collection
    location_collection = get_location_collection()
except Exception as e:
    location_collection = None
    logger.warning(f"⚠️ 無法初始化 MongoDB collection：{e}")

# 用於避免重複查詢同一地名
_geocode_cache = {}

def clean_location_name(name: str) -> str:
    """Normalize an epicenter string for geocoding."""
    name = name.strip()

    # Extract formal location inside parentheses first
    if "(" in name and ")" in name:
        try:
            inside = name.split("(", 1)[-1].split(")", 1)[0].strip()
            if inside:
                name = inside
        except Exception:
            pass

    if name.startswith("位於"):
        name = name[2:]

    # Keep keywords such as "海域" to allow manual_fix matching
    if any(keyword in name for keyword in ["海域", "近海", "公里", "公尺", "方", "附近"]):
        return name

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
        if location_collection:
            try:
                location_collection.update_one(
                    {"name": location_name},
                    {"$set": {"lat": lat, "lon": lon}},
                    upsert=True,
                )
            except Exception as e:
                logger.error(f"⚠️ 寫入座標資料庫失敗：{e}")
        return lat, lon

     # Check MongoDB cache
    if location_collection:
        try:
            doc = location_collection.find_one({"name": location_name})
            if doc and doc.get("lat") is not None and doc.get("lon") is not None:
                lat = doc["lat"]
                lon = doc["lon"]
                _geocode_cache[location_name] = (lat, lon)
                logger.info(
                    f"📍 已從資料庫取得地點：{location_name} → ({lat}, {lon})"
                )
                return lat, lon
        except Exception as e:
            logger.error(f"⚠️ 讀取座標資料庫失敗：{e}")

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
            if location_collection:
                try:
                    location_collection.update_one(
                        {"name": location_name},
                        {"$set": {"lat": lat, "lon": lon}},
                        upsert=True,
                    )
                except Exception as e:
                    logger.error(f"⚠️ 寫入座標資料庫失敗：{e}")
            logger.info(f"📍 已解析地點（Google）：{location_name} → ({lat}, {lon})")
            return lat, lon
        else:
            logger.warning(f"⚠️ Google Geocoding 無結果：{location_name} - {data.get('status')}")
    except Exception as e:
        logger.error(f"❌ Google Geocoding 錯誤：{e}")

    _geocode_cache[location_name] = (None, None)
    return None, None
