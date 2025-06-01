# earthquake.py
import time
from datetime import datetime
from quake_api import fetch_latest_quake
from line_push_utils import push_messages_to_all_users
from config import db
from logger import logger

# 用於記錄最後推播的時間，避免重複推播
last_quake_time = None

def quake_check_loop():
    global last_quake_time

    while True:
        try:
            quake = fetch_latest_quake()
            if not quake:
                logger.warning("⚠️ 無法取得地震資料")
                time.sleep(300)
                continue

            if "origin_time" not in quake:
                logger.warning("⚠️ 地震資料缺少 origin_time，跳過")
                time.sleep(300)
                continue

            if quake["origin_time"] != last_quake_time:
                last_quake_time = quake["origin_time"]

                # 檢查資料庫是否已有此筆紀錄
                try:
                    existing = db["earthquakes"].find_one({'origin_time': quake['origin_time']})
                    if not existing:
                        db["earthquakes"].insert_one(quake)
                        logger.info("✅ 新地震資料已儲存到 MongoDB")
                    else:
                        logger.info("ℹ️ 此地震資料已存在於資料庫中")
                except Exception as e:
                    logger.error(f"⚠️ 儲存地震資料時發生錯誤：{e}")

                # 建立推播訊息
                msg = f"""📢 新地震速報！
時間：{quake['origin_time'].strftime('%Y-%m-%d %H:%M:%S')}
地點：{quake['epicenter']}
深度：{quake['depth']} 公里
規模：芮氏 {quake['magnitude']}
➡️ 詳情：{quake['link']}
"""
                logger.info("▶️ 發現新地震，開始推播...")
                push_messages_to_all_users(msg)
            else:
                logger.info(f"🔄 尚無新地震，最後地震時間：{last_quake_time}")

        except Exception as e:
            logger.error(f"❌ earthquake.py 主迴圈錯誤：{e}")

        time.sleep(300)  # 每 5 分鐘執行一次
