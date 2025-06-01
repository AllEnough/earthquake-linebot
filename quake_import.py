# quake_import.py
import requests
from config import CWA_API_KEY
from database import get_earthquake_collection
from quake_parser import parse_quake_record
from logger import logger

# ✅ API 來源網址
url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={CWA_API_KEY}'

# ✅ 地震資料集合
collection = get_earthquake_collection()

def fetch_and_store_earthquake_data():
    logger.info("🌐 嘗試連線中央氣象局 API 抓取所有地震資料...")
    try:
        response = requests.get(url)
        data = response.json()
        records = data['records']['Earthquake']
        logger.info(f"✅ 成功抓取 {len(records)} 筆地震資料")
    except Exception as e:
        logger.error(f"❌ 抓取或解析 API 資料失敗：{e}")
        return

    count = 0
    for eq in records:
        quake = parse_quake_record(eq)
        if quake is None:
            continue
        if collection.count_documents({'origin_time': quake['origin_time']}) == 0:
            try:
                collection.insert_one(quake)
                count += 1
            except Exception as e:
                logger.error(f"❌ 寫入 MongoDB 錯誤：{e}")

    logger.info(f"✅ 資料庫更新完成，共新增 {count} 筆地震資料")


# ✅ 可直接執行本檔進行一次性匯入
if __name__ == "__main__":
    fetch_and_store_earthquake_data()
