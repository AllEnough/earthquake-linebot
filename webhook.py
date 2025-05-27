from flask import Flask, request, abort
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.webhook.models import MessageEvent
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest

from pymongo import MongoClient
import os

app = Flask(__name__)

# LINE Config
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

# MongoDB Config
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["linebot"]
collection = db["users"]

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        print("Webhook 驗證錯誤：", e)
        abort(400)

    for event in events:
        if isinstance(event, MessageEvent):
            user_id = event.source.user_id
            if collection.find_one({'user_id': user_id}) is None:
                collection.insert_one({'user_id': user_id})
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

    return 'OK'
