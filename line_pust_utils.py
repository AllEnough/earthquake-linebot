# line_push_utils.py
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
from config import configuration, collection
from logger import logger


def push_messages_to_all_users(message_text):
    try:
        # 從 users 集合取得所有 user_id
        user_ids = [user['user_id'] for user in collection.find({}, {'user_id': 1})]

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            for user_id in user_ids:
                push_message = PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message_text)]
                )
                messaging_api.push_message(push_message)
                logger.info(f"✅ 已推播訊息給 user_id: {user_id}")

    except Exception as e:
        logger.error(f"❌ 推播訊息發生錯誤：{e}")
