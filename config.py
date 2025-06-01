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

# ✅ 環境變數
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
CWA_API_KEY = os.getenv("CWA_API_KEY")
DOMAIN = os.getenv("DOMAIN")  # ✅ 用於圖表網址等地方

print("ENV TEST CWA_API_KEY:", repr(os.getenv("CWA_API_KEY")))

# ✅ 檢查環境變數是否齊全
required_vars = [
    LINE_CHANNEL_SECRET,
    LINE_CHANNEL_ACCESS_TOKEN,
    MONGO_URI,
    CWA_API_KEY,
    DOMAIN
]

print("LINE_CHANNEL_SECRET =", repr(LINE_CHANNEL_SECRET))
print("LINE_CHANNEL_ACCESS_TOKEN =", repr(LINE_CHANNEL_ACCESS_TOKEN))
print("MONGO_URI =", repr(MONGO_URI))
print("CWA_API_KEY =", repr(CWA_API_KEY))
print("DOMAIN =", repr(DOMAIN))


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
