from datetime import datetime, timedelta, UTC
from pymongo import MongoClient

# MongoDB 連線
client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
db = client["earthquake_db"]

def fix_origin_time_format():
    """將字串格式的 origin_time 欄位轉換為 datetime"""
    for doc in db["earthquakes"].find({"origin_time": {"$type": "string"}}):
        try:
            new_time = datetime.strptime(doc["origin_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            db["earthquakes"].update_one(
                {"_id": doc["_id"]},
                {"$set": {"origin_time": new_time}}
            )
        except Exception as e:
            print(f"❌ 轉換失敗：{doc['_id']} - {e}")

def get_average_magnitude():
    fix_origin_time_format()
    pipeline = [
        {"$match": {"magnitude": {"$exists": True}}},
        {"$group": {"_id": None, "avg_mag": {"$avg": "$magnitude"}}}
    ]
    result = list(db["earthquakes"].aggregate(pipeline))
    return result[0]['avg_mag'] if result else None

def get_max_magnitude():
    fix_origin_time_format()
    result = db["earthquakes"].find_one(sort=[("magnitude", -1)])
    return result

def get_recent_earthquake_count(days=7):
    fix_origin_time_format()
    start_date = datetime.now(UTC) - timedelta(days=days)
    count = db["earthquakes"].count_documents({"origin_time": {"$gte": start_date}})
    return count
