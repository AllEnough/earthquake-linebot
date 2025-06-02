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

# 自訂補丁：無法被 Nominatim 解析的地名
manual_fix = {
    "花蓮縣近海": (23.8, 121.6),
    "臺灣東部海域": (24.0, 122.2),
    "臺灣東南部海域": (22.5, 122.0),
    "花蓮縣秀林鄉": (24.1, 121.6),
    "屏東縣三地門鄉": (22.8, 120.7),
    "高雄市那瑪夏區": (23.3, 120.8),
    "臺東縣海端鄉": (23.0, 121.1),
    "苗栗縣南庄鄉": (24.6, 121.0),
}

def get_coordinates_from_text(location_name):
    """
    使用 Nominatim API 將中文地點轉換為 (lat, lon)
    """
    location_name = clean_location_name(location_name)
    location_name = location_name.replace("台", "臺")

    if not location_name:
        return None, None

    # 優先查找手動修正表
    if location_name in manual_fix:
        lat, lon = manual_fix[location_name]
        logger.info(f"📍 已從補丁表解析地點：{location_name} → ({lat}, {lon})")
        return lat, lon

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