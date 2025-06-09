# line_push_utils.py
from linebot.v3.messaging import MessagingApi, ApiClient
from linebot.v3.messaging.models import (
    TextMessage,
    PushMessageRequest,
    ImageMessage,
)
from config import configuration, collection
from logger import logger
import math


def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in kilometers."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


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

    home_lat = user.get("home_lat")
    home_lon = user.get("home_lon")
    if (
        home_lat is not None
        and home_lon is not None
        and quake.get("lat") is not None
        and quake.get("lon") is not None
    ):
        try:
            dist = haversine_km(float(home_lat), float(home_lon), float(quake["lat"]), float(quake["lon"]))
            if dist > 150:
                return False
        except Exception:
            pass

    return True


def push_messages_to_all_users(message_text, quake=None):
    try:
        users = list(
            collection.find(
                {},
                {
                    "user_id": 1,
                    "magnitude_threshold": 1,
                    "location_filter": 1,
                    "home_lat": 1,
                    "home_lon": 1,
                },
            )
        )
        if not users:
            logger.warning("⚠️ 無使用者可推播")

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
        users = list(
            collection.find(
                {},
                {
                    "user_id": 1,
                    "magnitude_threshold": 1,
                    "location_filter": 1,
                    "home_lat": 1,
                    "home_lon": 1,
                },
            )
        )
        if not users:
            logger.warning("⚠️ 無使用者可推播")

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