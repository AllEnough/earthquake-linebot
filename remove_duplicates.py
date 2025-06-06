from database import get_earthquake_collection
from logger import logger


def remove_duplicate_earthquakes():
    """Remove duplicate earthquake documents based on origin_time."""
    coll = get_earthquake_collection()
    pipeline = [
        {"$group": {"_id": "$origin_time", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]

    duplicates = list(coll.aggregate(pipeline))
    removed = 0

    for doc in duplicates:
        # Keep the first document and remove the rest
        ids_to_remove = doc["ids"][1:]
        if not ids_to_remove:
            continue
        result = coll.delete_many({"_id": {"$in": ids_to_remove}})
        removed += result.deleted_count
        logger.info(f"🗑️ 刪除 {result.deleted_count} 筆與 {doc['_id']} 重複的地震資料")

    logger.info(f"✅ 重複地震資料清理完成，總共刪除 {removed} 筆")


if __name__ == "__main__":
    remove_duplicate_earthquakes()