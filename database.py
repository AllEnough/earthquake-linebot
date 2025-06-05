# database.py
# ✅ MongoDB 初始化與集合操作工具

from config import client, db

# ✅ 建立資料庫連線並回傳 db 實例
def get_db():
    return db

# ✅ 使用者集合
def get_user_collection():
    return db["users"]

# ✅ 地震資料集合
def get_earthquake_collection():
    return db["earthquakes"]

# ✅ 位置座標集合
def get_location_collection():
    return db["locations"]
