# 處理 LINE webhook、推播、使用者處理
from flask import request
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from config import parser, configuration, collection, db
import re
from datetime import datetime, UTC
import traceback

def handle_webhook():
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

                    # 預設回覆
                    reply_text = "請輸入『地震』+關鍵字或數字，例如：地震 台中、地震>5"

                    # 分析地震查詢
                    if "地震" in user_message:
                        query = {}
                        location_keyword = None
                        magnitude_filter = None

                        pattern = r"地震\s*([^\s><=]*)?\s*(?:[>≧]\s*(\d+\.?\d*)?)?"
                        match = re.search(pattern, user_message)

                        if match:
                            location_keyword = match.group(1) if match.group(1) else None
                            magnitude_filter = float(match.group(2)) if match.group(2) else None

                        if location_keyword:
                            query['epicenter'] = {'$regex': location_keyword}

                        if magnitude_filter:
                            query['magnitude'] = {'$gte': magnitude_filter}

                        history = db["earthquakes"].find(query).sort("origin_time", -1).limit(5)
                        results = list(history)

                        if results:
                            lines = [f"📚 查詢結果："]
                            for idx, quake in enumerate(results, start=1):
                                lines.append(f"{idx}️⃣ {quake['origin_time']} / {quake['epicenter']} / 芮氏 {quake['magnitude']}")
                            reply_text = "\n".join(lines)
                        else:
                            reply_text = "❌ 查無符合條件的地震紀錄。"

                    reply = ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                    line_bot_api.reply_message(reply)


    except Exception as e:
        print("❌ 處理訊息時發生錯誤：", e)
        traceback.print_exc()
        return 'Error occurred', 500

    print("✅ LINE webhook 處理成功")
    return 'OK', 200
