import time
import requests
from pymongo import MongoClient
import certifi
from datetime import datetime, UTC

from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

# MongoDB Config
MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
db = client["linebot"]
collection = db["users"]

# LINE Config
LINE_CHANNEL_ACCESS_TOKEN = 'p0Je4vYvQ5A3UhZbxMrqhex1gznrICRHBN7Kd3qcb87HegwHNCVDmqThV1I6VfDt1rsmTFUAiy+ykRXyjnGssJaZJ4Baoz0Z9YBZJ7NDO+K8XytQjxXFkz4TbQTSjhtqZQQX1E+TofEU99qLxLn6nAdB04t89/1O/w1cDnyilFU='
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

def get_latest_quake():
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'
    try:
        response = requests.get(url)
        data = response.json()
        eq = data['records']['Earthquake'][0]
        info = eq['EarthquakeInfo']
        return {
            'origin_time': info['OriginTime'],
            'location': info['Epicenter']['Location'],
            'depth': info['FocalDepth'],
            'magnitude': info['EarthquakeMagnitude']['MagnitudeValue'],
            'report': eq['ReportContent'],
            'link': eq['Web']
        }
    except Exception as e:
        print("⚠️ 地震資料解析錯誤：", e)
        return None

def push_messages_to_all_users(message_text):
    try:
        user_cursor = collection.find({}, {"user_id": 1})
        user_ids = [user["user_id"] for user in user_cursor]

        if not user_ids:
            print("⚠️ 沒有使用者資料可推播")
            return

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            for uid in user_ids:
                try:
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=uid,
                            messages=[TextMessage(text=message_text)]
                        )
                    )
                    print(f"✅ 已推播給使用者：{uid}")
                except Exception as e:
                    print(f"❌ 推播給 {uid} 失敗：", e)

    except Exception as e:
        print("❌ 推播時發生錯誤：", e)

if __name__ == "__main__":
    last_quake_time = None

    while True:
        quake = get_latest_quake()
        if quake:
            if quake['origin_time'] != last_quake_time:
                last_quake_time = quake['origin_time']
                msg = f"""📢 新地震速報！
時間：{quake['origin_time']}
地點：{quake['location']}
深度：{quake['depth']} 公里
規模：{quake['magnitude']} 芮氏
➡️ 詳情：{quake['link']}
"""
                print(msg)
                push_messages_to_all_users(msg)
            else:
                print(f"🔄 尚無新地震，最後地震：{last_quake_time}")
        else:
            print("⚠️ 抓取地震資料失敗")

        time.sleep(3600)  # 每1小時檢查一次