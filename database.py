# database.py
# ✅ MongoDB 初始化與集合操作工具

from pymongo import MongoClient
import certifi
from config import MONGO_URI

# ✅ 建立資料庫連線並回傳 db 實例
def get_db():
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000
    )
    db = client["linebot"]  # ✅ 資料庫名稱固定為 linebot
    return db

# ✅ 使用者集合
def get_user_collection():
    return get_db()["users"]

# ✅ 地震資料集合
def get_earthquake_collection():
    return get_db()["earthquakes"]
