# line_bot.py
from flask import request
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest

from config import parser, configuration, collection
from line_handlers import (
    handle_query_help,
    handle_query_latest,
    handle_chart_daily,
    handle_chart_avg,
    handle_chart_max,
    handle_chart_forecast,
    handle_summary_text,
    handle_query_custom,
    handle_query_advanced,
    handle_location_settings,
    handle_push_settings,
    handle_unknown
)

import traceback
from datetime import datetime, UTC
from logger import logger


def handle_webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    logger.info("📥 收到 LINE 請求")
    logger.info(f"📦 請求內容：{body}")

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        logger.error(f"❌ Webhook 驗證失敗：{e}")
        return 'Signature verification failed', 400

    try:
        for event in events:
            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                user_id = event.source.user_id
                user_message = event.message.text.strip()

                # ✅ 使用者註冊或更新
                result = collection.update_one(
                    {'user_id': user_id},
                    {
                        '$setOnInsert': {
                            'user_id': user_id,
                            'joined_at': datetime.now(UTC),
                            'magnitude_threshold': None,
                            'location_filter': None,
                            'home_lat': None,
                            'home_lon': None,
                        }
                    },
                    upsert=True
                )
                if result.upserted_id:
                    logger.info(f"✅ 新使用者註冊：{user_id}")
                else:
                    logger.info(f"🌀 使用者已存在：{user_id}")

                # ✅ 指令分流處理
                if user_message in ["幫助", "指令", "?", "help", "Help"]:
                    messages = handle_query_help()
                elif user_message == "最新":
                    messages = handle_query_latest()
                elif user_message == "地震統計圖":
                    messages = handle_chart_daily()
                elif user_message == "地震平均規模圖":
                    messages = handle_chart_avg()
                elif user_message == "地震最大規模圖":
                    messages = handle_chart_max()
                elif user_message == "地震預測圖":
                    messages = handle_chart_forecast()
                elif user_message in ["地震摘要", "地震報告"]:
                    messages = handle_summary_text()
                elif user_message.startswith("所在區域"):
                    messages = handle_location_settings(user_id, user_message)
                elif user_message.startswith("推播條件"):
                    messages = handle_push_settings(user_id, user_message)
                elif user_message.startswith("查詢"):
                    messages = handle_query_advanced(user_message)
                elif user_message.startswith("地震"):
                    messages = handle_query_custom(user_message)
                else:
                    messages = handle_unknown()

                # ✅ 回覆使用者訊息
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=messages
                        )
                    )

    except Exception as e:
        logger.error(f"❌ 處理訊息時發生錯誤：{e}")
        traceback.print_exc()
        return 'Error occurred', 500

    logger.info("✅ LINE webhook 處理成功")
    return 'OK', 200
