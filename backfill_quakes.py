# backfill_quakes.py
from datetime import datetime, timedelta, UTC
import requests
from pymongo import MongoClient
from logger import logger
from quake_parser import parse_quake_record
from config import MONGO_URI, CWA_API_KEY
import certifi

# 初始化 MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["earthquake"]
collection = db["earthquakes"]

# 設定 API
CWB_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001"
HEADERS = {"Authorization": CWA_API_KEY}

# 補抓過去 30 天資料
end_date = datetime.now(UTC)
start_date = end_date - timedelta(days=30)

logger.info("🌐 正在抓取中央氣象局地震資料...")
params = {"format": "JSON"}
resp = requests.get(CWB_API_URL, headers=HEADERS, params=params)
data = resp.json()

count_inserted = 0
count_skipped = 0
count_failed = 0

if "records" in data and "earthquakes" in data["records"]:
    for eq in data["records"]["earthquakes"]:
        quake = parse_quake_record(eq)
        if not quake:
            count_failed += 1
            continue

        quake_time = quake["origin_time"]
        if not (start_date <= quake_time <= end_date):
            continue

        exists = collection.find_one({"origin_time": quake_time})
        if exists:
            count_skipped += 1
            continue

        try:
            collection.insert_one(quake)
            count_inserted += 1
        except Exception as e:
            logger.error(f"❌ 插入地震資料失敗：{e}")
            count_failed += 1

logger.info(f"✅ 補抓完成：新增 {count_inserted} 筆，略過 {count_skipped} 筆，失敗 {count_failed} 筆")
