from flask import Flask, request, abort
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent

from pymongo import MongoClient
from datetime import datetime, UTC
import os

app = Flask(__name__)

# LINE Config
LINE_CHANNEL_SECRET = '7f9ee0dad7c79de9ed2305004c1e090e'
if not LINE_CHANNEL_SECRET:
    print("❌ LINE_CHANNEL_SECRET 未正確設定！請檢查 Railway 環境變數")

LINE_CHANNEL_ACCESS_TOKEN = 'p0Je4vYvQ5A3UhZbxMrqhex1gznrICRHBN7Kd3qcb87HegwHNCVDmqThV1I6VfDt1rsmTFUAiy+ykRXyjnGssJaZJ4Baoz0Z9YBZJ7NDO+K8XytQjxXFkz4TbQTSjhtqZQQX1E+TofEU99qLxLn6nAdB04t89/1O/w1cDnyilFU='

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# MongoDB Config
MONGO_URI = "mongodb+srv://AllEnough:password052619@cluster0.wqlbeek.mongodb.net/?retryWrites=true&w=majority&tls=true"
client = MongoClient(MONGO_URI)
db = client["linebot"]
collection = db["users"]

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
                    {'$setOnInsert': {'user_id': user_id, 'joined_at': datetime.now(UTC), 'message': user_message}},
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
    port = int(os.environ.get("PORT", 8080))  # Railway 會自動設定 PORT 環境變數
    app.run(host="0.0.0.0", port=port)

