# quake_import_loop.py
import time
import threading
import schedule
from logger import logger

from quake_import import fetch_and_store_earthquake_data
from quake_forecast import generate_forecast_chart
from chart_daily import generate_daily_count_chart
from chart_avg import generate_avg_magnitude_chart
from chart_max import generate_max_magnitude_chart
from chart_cluster import generate_epicenter_cluster_chart
from chart_heatmap import generate_heatmap_chart
from quake_summary import get_text_summary
from line_push_utils import push_messages_to_all_users

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ✅ 每 5 分鐘抓資料
def run_quake_import_loop(interval_minutes=5):
    while True:
        logger.info("🌀 執行定期地震資料匯入...")
        fetch_and_store_earthquake_data()
        logger.info(f"⏳ 等待 {interval_minutes} 分鐘後再次執行...\n")
        time.sleep(interval_minutes * 60)

# ✅ 每日更新圖表
def run_daily_forecast_loop():
    while True:
        logger.info("📊 每日更新地震分析圖表中...")
        generate_forecast_chart()
        generate_daily_count_chart()
        generate_avg_magnitude_chart()
        generate_max_magnitude_chart()
        generate_epicenter_cluster_chart()
        generate_heatmap_chart()

        logger.info("✅ 圖表更新完成，等待 24 小時...")
        time.sleep(86400)

# ✅ 每週一上午 9 點推播摘要
def run_weekly_summary_push():
    def job():
        logger.info("📤 每週推播地震摘要中...")
        summary = get_text_summary(7)
        push_messages_to_all_users(summary)
        logger.info("✅ 地震摘要推播完成")

    schedule.every().monday.at("09:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)

# ✅ 啟動所有背景任務（主程式中呼叫）
def start_background_quake_import():
    threading.Thread(target=run_quake_import_loop, daemon=True).start()
    logger.info("🌍 地震資料匯入已在背景中啟動。")

    threading.Thread(target=run_daily_forecast_loop, daemon=True).start()
    logger.info("📈 每日圖表更新已在背景中啟動。")

    threading.Thread(target=run_weekly_summary_push, daemon=True).start()
    logger.info("📝 每週摘要推播已在背景中啟動。")
