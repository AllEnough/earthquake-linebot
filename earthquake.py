# 地震資料相關函式（API 抓取、查詢）
from quake_fetcher import get_latest_quake
from utils import push_messages_to_all_users
from config import db
import time

last_quake_time = None

def quake_check_loop():
    global last_quake_time
    while True:
        quake = get_latest_quake()
        if quake:
            if quake['origin_time'] != last_quake_time:
                last_quake_time = quake['origin_time']

                try:
                    existing = db["earthquakes"].find_one({'origin_time': quake['origin_time']})
                    if not existing:
                        db["earthquakes"].insert_one(quake)
                        print("✅ 新地震資料已儲存到 MongoDB")
                    else:
                        print("ℹ️ 此地震資料已存在於資料庫中")
                except Exception as e:
                    print("⚠️ 儲存地震資料時發生錯誤：", e)

                msg = f"""📢 新地震速報！
時間：{quake['origin_time']}
地點：{quake['epicenter']}
深度：{quake['depth']} 公里
規模：{quake['magnitude']} 芮氏
➡️ 詳情：{quake['link']}
"""
                print("▶️ 發現新地震，開始推播...")
                push_messages_to_all_users(msg)
            else:
                print(f"🔄 尚無新地震，最後地震時間：{last_quake_time}")
        else:
            print("⚠️ 抓取地震資料失敗")

        time.sleep(300)
