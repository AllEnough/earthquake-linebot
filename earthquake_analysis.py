# earthquake_analysis.py
from datetime import datetime, timedelta, UTC
from database import get_earthquake_collection
from logger import logger

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ✅ 統一取得地震資料集合
collection = get_earthquake_collection()

def fix_origin_time_format():
    """將 origin_time 欄位從字串轉換為 datetime 格式（若尚未轉換）"""
    for doc in collection.find({"origin_time": {"$type": "string"}}):
        try:
            new_time = datetime.strptime(doc["origin_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"origin_time": new_time}}
            )
        except Exception as e:
            logger.error(f"❌ 轉換失敗：{doc['_id']} - {e}")

def get_average_magnitude():
    """計算所有地震的平均規模"""
    fix_origin_time_format()
    pipeline = [
        {"$match": {"magnitude": {"$exists": True}}},
        {"$group": {"_id": None, "avg_mag": {"$avg": "$magnitude"}}}
    ]
    result = list(collection.aggregate(pipeline))
    return result[0]["avg_mag"] if result else None

def get_max_magnitude():
    """取得最大規模的地震紀錄"""
    fix_origin_time_format()
    return collection.find_one(sort=[("magnitude", -1)])

def get_recent_earthquake_count(days=7):
    """統計最近 N 天的地震次數"""
    fix_origin_time_format()
    start_date = datetime.now(UTC) - timedelta(days=days)
    return collection.count_documents({"origin_time": {"$gte": start_date}})
