# line_push_utils.py
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest, ImageMessage
from config import configuration, collection
from logger import logger


def should_push_to_user(user, quake):
    """Return True if the quake satisfies user's custom conditions."""
    if quake is None:
        return True

    mag_th = user.get("magnitude_threshold")
    if mag_th is not None and quake.get("magnitude") is not None:
        try:
            if float(quake["magnitude"]) < float(mag_th):
                return False
        except Exception:
            pass

    loc_kw = user.get("location_filter")
    if loc_kw:
        epicenter = quake.get("epicenter", "")
        if loc_kw not in epicenter:
            return False

    return True



def push_messages_to_all_users(message_text, quake=None):
    try:
        users = list(collection.find({}, {"user_id": 1, "magnitude_threshold": 1, "location_filter": 1}))

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            for user in users:
                if not should_push_to_user(user, quake):
                    continue

                push_message = PushMessageRequest(
                    to=user["user_id"],
                    messages=[TextMessage(text=message_text)]
                )
                messaging_api.push_message(push_message)
                logger.info(f"✅ 已推播訊息給 user_id: {user['user_id']}")

    except Exception as e:
        logger.error(f"❌ 推播訊息發生錯誤：{e}")


def push_image_to_all_users(image_url, alt_text="地震位置圖", quake=None):
    try:
        users = list(collection.find({}, {"user_id": 1, "magnitude_threshold": 1, "location_filter": 1}))

        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)

            for user in users:
                if not should_push_to_user(user, quake):
                    continue

                messaging_api.push_message(PushMessageRequest(
                    to=user["user_id"],
                    messages=[
                        TextMessage(text=alt_text),
                        ImageMessage(original_content_url=image_url, preview_image_url=image_url),
                    ]
                ))
                logger.info(f"✅ 已推播圖片給 user_id: {user['user_id']}")
    except Exception as e:
        logger.error(f"❌ 推播圖片發生錯誤：{e}")