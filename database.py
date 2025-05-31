# MongoDB 初始化與操作
from pymongo import MongoClient
import certifi
from config import MONGO_URI

def get_db():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    db = client["linebot"]
    return db

def get_user_collection():
    return get_db()["users"]

def get_quake_collection():
    return get_db()["earthquakes"]