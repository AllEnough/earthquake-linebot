# backfill_coordinates.py
from database import get_earthquake_collection
from geocode_utils import get_coordinates_from_text
from logger import logger


def backfill_missing_coordinates():
    collection = get_earthquake_collection()
    missing = collection.find({
        "$or": [
            {"lat": {"$exists": False}},
            {"lon": {"$exists": False}},
            {"lat": None},
            {"lon": None}
        ]
    })

    updated_count = 0
    skipped = 0

    for doc in missing:
        epicenter = doc.get("epicenter")
        if not epicenter:
            skipped += 1
            continue

        lat, lon = get_coordinates_from_text(epicenter)
        if lat and lon:
            result = collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"lat": lat, "lon": lon}}
            )
            if result.modified_count:
                logger.info(f"✅ 補上經緯度：{epicenter} → ({lat}, {lon})")
                updated_count += 1
        else:
            logger.warning(f"⚠️ 無法取得經緯度：{epicenter}")
            skipped += 1

    logger.info(f"✅ 經緯度補全完成：{updated_count} 筆成功，{skipped} 筆跳過")


if __name__ == "__main__":
    backfill_missing_coordinates()
