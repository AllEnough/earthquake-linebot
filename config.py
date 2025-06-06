# config.py
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration
from logger import logger

# ✅ 載入 .env 檔案
load_dotenv()

def clean_env(key):
    val = os.getenv(key)
    if val is None:
        return None
    return val.strip().strip('"').strip("'")

# ✅ 環境變數
LINE_CHANNEL_SECRET = clean_env("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = clean_env("LINE_CHANNEL_ACCESS_TOKEN")
MONGO_URI = clean_env("MONGO_URI")
CWA_API_KEY = clean_env("CWA_API_KEY")
DOMAIN = clean_env("DOMAIN")  # ✅ 用於圖表網址等地方
GOOGLE_MAPS_API_KEY = clean_env("GOOGLE_MAPS_API_KEY")

# ✅ 檢查環境變數是否齊全
required_vars = [
    LINE_CHANNEL_SECRET,
    LINE_CHANNEL_ACCESS_TOKEN,
    MONGO_URI,
    CWA_API_KEY,
    DOMAIN,
    GOOGLE_MAPS_API_KEY
]

if not all(required_vars):
    raise EnvironmentError("❌ 缺少必要的 .env 環境變數設定，請檢查 .env 檔案")

# ✅ LINE Messaging API 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# ✅ MongoDB 初始化
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
db = client["linebot"]            # 資料庫名稱：linebot
collection = db["users"]          # 使用者資料集合

logger.info("✅ 成功連線到 MongoDB")
