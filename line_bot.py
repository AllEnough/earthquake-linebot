# 處理 LINE webhook、推播、使用者處理
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.webhook import WebhookParser
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from config import configuration, collection
from database import get_user_collection
from earthquake import get_latest_quake, save_quake_if_new, build_quake_message, query_quakes
from linebot.v3.models import PushMessageRequest, TextMessage
configuration = configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(channel_secret=LINE_CHANNEL_SECRET)

def push_messages_to_all_users(message):
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

def handle_webhook_request(request):
    # 驗證簽名，解析 event，
    # 儲存使用者，判斷是否為查詢關鍵字，並回覆結果
    ...

#def quake_check_loop():
    # 每 5 分鐘檢查是否有新地震資料並推播
    ...
