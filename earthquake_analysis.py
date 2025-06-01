from datetime import datetime, timedelta, UTC
from pymongo import MongoClient
# MongoDB 連線
client = MongoClient("mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true")
db = client["earthquake_db"]

def get_average_magnitude():
    pipeline = [
        {"$match": {"magnitude": {"$exists": True}}},
        {"$group": {"_id": None, "avg_mag": {"$avg": "$magnitude"}}}
    ]
    result = list(db["earthquakes"].aggregate(pipeline))
    return result[0]['avg_mag'] if result else None

def get_max_magnitude():
    result = db["earthquakes"].find_one(sort=[("magnitude", -1)])
    return result

def get_recent_earthquake_count(days=7):
    start_date = datetime.now(UTC) - timedelta(days=days)
    count = db["earthquakes"].count_documents({"origin_time": {"$gte": start_date}})
    return count
