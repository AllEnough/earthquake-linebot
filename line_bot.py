# 處理 LINE webhook、推播、使用者處理
from flask import request
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from config import parser, configuration, collection, db
from linebot.v3.messaging.models import ImageMessage
from generate_chart import generate_chart, generate_daily_count_chart, generate_avg_magnitude_chart, generate_max_magnitude_chart
from earthquake_analysis import get_average_magnitude, get_max_magnitude, get_recent_earthquake_count
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
                    if user_message.lower() in ["查詢功能"]:
                        reply_text = (
                            "🤖 地震查詢機器人使用說明：\n"
                            "🔹 輸入「地震」：查詢最近的地震資料\n"
                            "🔹 輸入「地震 花蓮」：查詢花蓮地區的地震\n"
                            "🔹 輸入「地震 >5」：查詢規模大於5的地震\n"
                            "🔹 輸入「最新」：查詢最新一筆地震紀錄\n"
                            "🔹 輸入「地震地圖」：查詢最近的地震規模折線圖\n"
                            "🔹 更多功能開發中，敬請期待！"
                        )
                        messages = [TextMessage(text=reply_text)]
                    elif user_message == "最新":
                        latest = db["earthquakes"].find_one(sort=[("origin_time", -1)])
                        if latest:
                            reply_text = (
                                f"📍 最新地震資訊：\n"
                                f"時間：{latest.get('origin_time', '未知')}\n"
                                f"震央：{latest.get('epicenter', '未知')}\n"
                                f"深度：{latest.get('depth', '未知')} 公里\n"
                                f"規模：芮氏 {latest.get('magnitude', '未知')}"
                            )
                        else:
                            reply_text = "⚠️ 查無最新地震資料。"
                        messages = [TextMessage(text=reply_text)]
                    
                    # 分析地震查詢
                    elif user_message == "地震":
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
                                origin_time = quake.get('origin_time', '未知時間')
                                epicenter = quake.get('epicenter', '未知震央')
                                magnitude = quake.get('magnitude', '未知')
                                lines.append(f"{idx}️⃣ {origin_time} / {epicenter} / 芮氏 {magnitude}")
                            reply_text = "\n".join(lines)
                        else:
                            reply_text = "❌ 查無符合條件的地震紀錄。"
                        messages = [TextMessage(text=reply_text)]
                    
                    elif user_message == "地震地圖":
                        generate_chart()
                        image_url = 'https://earthquake-linebot-production.up.railway.app/static/chart.png'
                        messages = [
                            ImageMessage(
                                original_content_url=image_url,
                                preview_image_url=image_url
                            )
                        ]
                    
                    elif user_message == "地震統計":
                        avg_mag = get_average_magnitude()
                        max_quake = get_max_magnitude()
                        recent_count = get_recent_earthquake_count()

                        reply_text = (
                            f"📊 地震資料統計分析：\n"
                            f"🔸 最近 7 天地震次數：{recent_count} 次\n"
                            f"🔸 平均地震規模：{round(avg_mag, 2) if avg_mag else '無資料'}\n"
                        )

                        if max_quake:
                            reply_text += (
                                f"🔸 最大地震：\n"
                                f"  - 規模：{max_quake['magnitude']}\n"
                                f"  - 震央：{max_quake['epicenter']}\n"
                                f"  - 時間：{max_quake['origin_time']}\n"
                            )
                        else:
                            reply_text += "🔸 查無最大地震資料。\n"
                        messages = [TextMessage(text=reply_text)]
                    
                    elif user_message == "地震統計圖":
                        generate_daily_count_chart()
                        image_url = 'https://earthquake-linebot-production.up.railway.app/static/chart_daily_count.png'
                        messages = [
                            ImageMessage(
                                original_content_url=image_url,
                                preview_image_url=image_url
                            )
                        ]
                    
                    elif user_message == "地震平均規模圖":
                        generate_avg_magnitude_chart()
                        image_url = "https://earthquake-linebot-production.up.railway.app/static/chart_avg_magnitude.png"
                        messages = [
                            ImageMessage(
                                original_content_url=image_url,
                                preview_image_url=image_url
                            )
                        ]

                    elif user_message == "地震最大規模圖":
                        generate_max_magnitude_chart()
                        image_url = "https://earthquake-linebot-production.up.railway.app/static/chart_max_magnitude.png"
                        messages = [
                            ImageMessage(
                                original_content_url=image_url,
                                preview_image_url=image_url
                            )
                        ]
                    
                    elif user_message == "地震熱區圖":
                        heatmap_url = "https://earthquake-linebot-production.up.railway.app/heatmap"
                        reply_text = f"🔍 點擊下方連結查看互動式地震熱區圖：\n{heatmap_url}"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextMessage(text=reply_text)
                        )



                    else:
                        reply_text = "⚠️ 無法識別的指令，請輸入「幫助」查看使用說明。"
                        messages = [TextMessage(text=reply_text)]

                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=messages
                        )
                    )



    except Exception as e:
        print("❌ 處理訊息時發生錯誤：", e)
        traceback.print_exc()
        return 'Error occurred', 500

    print("✅ LINE webhook 處理成功")
    return 'OK', 200
