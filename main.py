from flask import Flask, request
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest, PushMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent

from pymongo import MongoClient
import certifi
from datetime import datetime, UTC
import os
import requests
import threading
import time

app = Flask(__name__)

# LINE Config
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '你的LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '你的LINE_CHANNEL_ACCESS_TOKEN')

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# MongoDB Config
MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
db = client["linebot"]
collection = db["users"]

print("✅ 成功連線到 MongoDB")

# 紀錄最後一次推播的地震時間
last_quake_time = None

def get_latest_quake():
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization=CWA-9A20417D-4DB8-4A27-A638-1814ECE1CBAF'
    response = requests.get(url)
    data = response.json()

    try:
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
        user_ids = [user['user_id'] for user in collection.find({}, {'user_id': 1})]

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            for user_id in user_ids:
                push_message = PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message_text)]
                )
                messaging_api.push_message(push_message)
                print(f"✅ 已推播訊息給 user_id: {user_id}")

    except Exception as e:
        print("❌ 推播訊息發生錯誤：", e)

def quake_check_loop():
    global last_quake_time
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
                print("▶️ 發現新地震，開始推播...")
                push_messages_to_all_users(msg)
            else:
                print(f"🔄 尚無新地震，最後地震時間：{last_quake_time}")
        else:
            print("⚠️ 抓取地震資料失敗")

        time.sleep(300)  # 每5分鐘檢查一次

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    print("📥 收到 LINE 請求！")
    print("📦 請求內容：", body)

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        print("❌ Webhook 驗證失敗：", e)
        return 'Signature verification failed', 400

    try:
        for event in events:
            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                user_id = event.source.user_id
                user_message = event.message.text

                result = collection.update_one(
                    {'user_id': user_id},
                    {'$setOnInsert': {'user_id': user_id, 'joined_at': datetime.now(UTC)}},
                    upsert=True
                )

                if result.upserted_id is not None:
                    print(f"✅ 新使用者註冊：{user_id}")
                else:
                    print(f"🌀 使用者已存在：{user_id}")

                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    reply = ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="👋 你已成功加入地震推播清單！")]
                    )
                    line_bot_api.reply_message(reply)

    except Exception as e:
        print("❌ 處理訊息時發生錯誤：", e)
        return 'Error occurred', 500

    return 'OK', 200

if __name__ == "__main__":
    # 啟動背景執行緒，持續偵測地震並推播
    threading.Thread(target=quake_check_loop, daemon=True).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
