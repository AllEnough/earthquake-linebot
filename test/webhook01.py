from flask import Flask, request, abort
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest, PushMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent

from pymongo import MongoClient
import certifi
from datetime import datetime, UTC
import os

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


app = Flask(__name__)

# LINE Config
LINE_CHANNEL_SECRET = '7f9ee0dad7c79de9ed2305004c1e090e'
LINE_CHANNEL_ACCESS_TOKEN = 'p0Je4vYvQ5A3UhZbxMrqhex1gznrICRHBN7Kd3qcb87HegwHNCVDmqThV1I6VfDt1rsmTFUAiy+ykRXyjnGssJaZJ4Baoz0Z9YBZJ7NDO+K8XytQjxXFkz4TbQTSjhtqZQQX1E+TofEU99qLxLn6nAdB04t89/1O/w1cDnyilFU='

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# MongoDB Config
try:
    MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true"
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    db = client["linebot"]
    collection = db["users"]
    print("✅ 成功連線到 MongoDB")
except Exception as e:
    print("❌ MongoDB 連線失敗：", e)

# 推播函式：發送訊息給所有使用者
def push_messages_to_all_users(message_text):
    print(f"訊息類型: {type(message_text)}")
    print(f"訊息內容: {message_text}")
    try:
        # 從 MongoDB 取得所有 user_id
        user_ids = [user['user_id'] for user in collection.find({}, {'user_id': 1})]

        configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            for user_id in user_ids:
                # 保證訊息是 str 且使用 UTF-8 編碼
                if isinstance(message_text, bytes):
                    message_text = message_text.decode('utf-8')

            for user_id in user_ids:
                push_message = PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=str(message_text))]
                )
                messaging_api.push_message(push_message)
                print(f"✅ 已推播訊息給 user_id: {user_id}")

    except Exception as e:
        print("❌ 推播訊息發生錯誤：", e)

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
                user_message = event.message.text.strip()

                 # 新使用者儲存
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

                    # 如果收到「近5次地震」指令
                    if "地震" in user_message:
                        history = db["earthquakes"].find().sort("origin_time", -1).limit(5)
                        lines = ["📚 近5次地震紀錄："]
                        for idx, quake in enumerate(history, start=1):
                            time_str = quake['origin_time']
                            location = quake['location']
                            mag = quake['magnitude']
                            lines.append(f"{idx}️⃣ {time_str} / {location} / 芮氏 {mag}")
                        reply_text = "\n".join(lines)
                    else:
                        reply_text = "👋 你已成功加入地震推播清單！\n輸入「近5次地震」可以查看地震紀錄。"

                    # 回覆用戶
                    reply = ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                    line_bot_api.reply_message(reply)


    except Exception as e:
        print("❌ 處理訊息時發生錯誤：", e)
        return 'Error occurred', 500

    return 'OK', 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway 會自動設定 PORT 環境變數
    app.run(host="0.0.0.0", port=port)

